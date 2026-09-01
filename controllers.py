import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from flask import Flask, abort, flash, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from book_api_service import get_bestsellers, get_book, get_books
from gemini_service import make_book_preview, make_easy_text
from flux_service import generate_mood_image


app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET") or os.getenv("SECRET_KEY", "dev-only-change-this-secret")
app.config["DATABASE"] = BASE_DIR / "dippingbook.db"
oauth = OAuth(app)


def configured(value):
    return bool(value and value.strip() and not value.strip().startswith("YOUR_"))


GOOGLE_ENABLED = configured(os.getenv("GOOGLE_CLIENT_ID")) and configured(os.getenv("GOOGLE_CLIENT_SECRET"))
GITHUB_ENABLED = configured(os.getenv("GITHUB_CLIENT_ID")) and configured(os.getenv("GITHUB_CLIENT_SECRET"))

if GOOGLE_ENABLED:
    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

if GITHUB_ENABLED:
    oauth.register(
        name="github",
        client_id=os.getenv("GITHUB_CLIENT_ID"),
        client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "read:user user:email"},
    )


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript((BASE_DIR / "schema.sql").read_text(encoding="utf-8"))
    db.commit()


@app.context_processor
def common_data():
    return {
        "logged_in_user": session.get("username"),
        "google_oauth_enabled": GOOGLE_ENABLED,
        "github_oauth_enabled": GITHUB_ENABLED,
        "kakao_map_app_key": os.getenv("KAKAO_MAP_APP_KEY", "").strip(),
    }


def login_oauth_user(provider, provider_user_id, email, display_name, avatar_url=""):
    db = get_db()
    account = db.execute(
        "SELECT user_id FROM oauth_accounts WHERE provider=? AND provider_user_id=?",
        (provider, str(provider_user_id)),
    ).fetchone()
    if account:
        user = db.execute("SELECT * FROM users WHERE id=?", (account["user_id"],)).fetchone()
    else:
        base = (email.split("@", 1)[0] if email else f"{provider}_{provider_user_id}")[:24] or provider
        username = base
        number = 1
        while db.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
            number += 1
            username = f"{base[:20]}_{number}"
        cursor = db.execute(
            "INSERT INTO users(username, password, name, birth) VALUES (?, ?, ?, '')",
            (username, generate_password_hash(os.urandom(32).hex()), display_name or username),
        )
        user_id = cursor.lastrowid
        db.execute(
            "INSERT INTO oauth_accounts(user_id, provider, provider_user_id, email, avatar_url) VALUES (?, ?, ?, ?, ?)",
            (user_id, provider, str(provider_user_id), email or "", avatar_url or ""),
        )
        db.commit()
        user = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]


def build_onepage_context(view="home", message=""):
    """한 번의 렌더링으로 원페이지에 필요한 데이터를 모두 준비한다."""
    genre = request.args.get("genre", "전체").strip() or "전체"
    query = request.args.get("q", "").strip()
    page_number = max(request.args.get("page", 1, type=int), 1)
    book_list = get_books(genre=genre, query=query, page=page_number, max_results=12)

    db = get_db()
    category = request.args.get("category", "전체")
    if category == "전체":
        posts = db.execute("SELECT * FROM community_posts ORDER BY id DESC").fetchall()
    else:
        posts = db.execute(
            "SELECT * FROM community_posts WHERE category=? ORDER BY id DESC", (category,)
        ).fetchall()
    comment_rows = db.execute("SELECT * FROM community_comments ORDER BY id").fetchall()
    comment_map = {}
    for comment in comment_rows:
        comment_map.setdefault(comment["post_id"], []).append(comment)
    like_rows = db.execute(
        "SELECT post_id, COUNT(*) AS count FROM community_likes GROUP BY post_id"
    ).fetchall()
    like_map = {row["post_id"]: row["count"] for row in like_rows}
    liked_posts = set()
    if session.get("user_id"):
        liked_posts = {
            row["post_id"]
            for row in db.execute(
                "SELECT post_id FROM community_likes WHERE user_id=?",
                (session["user_id"],),
            ).fetchall()
        }

    user = None
    stats = {"posts": 0, "community_comments": 0, "book_comments": 0, "likes": 0}
    recent_posts = []
    if session.get("user_id"):
        user = db.execute(
            "SELECT id, username, name, birth FROM users WHERE id=?", (session["user_id"],)
        ).fetchone()
        if user:
            stats = {
                "posts": db.execute("SELECT COUNT(*) FROM community_posts WHERE user_id=?", (user["id"],)).fetchone()[0],
                "community_comments": db.execute("SELECT COUNT(*) FROM community_comments WHERE user_id=?", (user["id"],)).fetchone()[0],
                "book_comments": db.execute("SELECT COUNT(*) FROM book_comments WHERE user_id=?", (user["id"],)).fetchone()[0],
                "likes": db.execute("SELECT COUNT(*) FROM community_likes WHERE user_id=?", (user["id"],)).fetchone()[0]
                + db.execute("SELECT COUNT(*) FROM book_likes WHERE user_id=?", (user["id"],)).fetchone()[0],
            }
            recent_posts = db.execute(
                "SELECT id, category, title, created_at FROM community_posts WHERE user_id=? ORDER BY id DESC LIMIT 5",
                (user["id"],),
            ).fetchall()

    selected_book = None
    book_comments = []
    book_like_count = 0
    book_liked = False
    selected_book_id = request.args.get("book", "").strip()
    if selected_book_id:
        selected_book = get_book(selected_book_id)
        if selected_book:
            book_comments = db.execute(
                "SELECT * FROM book_comments WHERE book_key=? ORDER BY id DESC",
                (selected_book_id,),
            ).fetchall()
            book_like_count = db.execute(
                "SELECT COUNT(*) FROM book_likes WHERE book_key=?", (selected_book_id,)
            ).fetchone()[0]
            if session.get("user_id"):
                book_liked = db.execute(
                    "SELECT 1 FROM book_likes WHERE book_key=? AND user_id=?",
                    (selected_book_id, session["user_id"]),
                ).fetchone() is not None

    if view == "mypage" and not user:
        view = "login"
        message = message or "마이페이지를 보려면 먼저 로그인해 주세요."
    if view == "detail" and not selected_book:
        view = "books"

    return {
        "page": view,
        "active_view": view,
        "message": message,
        "bestsellers": get_bestsellers(10),
        "books": book_list,
        "genre": genre,
        "query": query,
        "heading": f"‘{query}’ 검색 결과" if query else f"{genre} 도서 목록",
        "page_number": page_number,
        "has_next": len(book_list) == 12,
        "posts": posts,
        "category": category,
        "comment_map": comment_map,
        "like_map": like_map,
        "liked_posts": liked_posts,
        "user": user,
        "stats": stats,
        "recent_posts": recent_posts,
        "selected_book": selected_book,
        "book_comments": book_comments,
        "book_like_count": book_like_count,
        "book_liked": book_liked,
    }


def home():
    return render_template("onepage.html", **build_onepage_context(request.args.get("view", "home")))


def about():
    return redirect(url_for("home", view="about") + "#about")


def books():
    genre = request.args.get("genre", "전체").strip() or "전체"
    query = request.args.get("q", "").strip()
    page_number = max(request.args.get("page", 1, type=int), 1)
    return redirect(url_for("home", view="books", genre=genre, q=query, page=page_number) + "#books")


def book_detail(book_id):
    return redirect(url_for("home", view="detail", book=book_id) + "#detail")


def book_like(book_id):
    if not session.get("user_id"):
        flash("좋아요를 누르려면 먼저 로그인해 주세요.")
        return redirect(url_for("home", view="login") + "#login")
    db = get_db()
    exists = db.execute(
        "SELECT 1 FROM book_likes WHERE book_key=? AND user_id=?",
        (book_id, session["user_id"]),
    ).fetchone()
    if exists:
        db.execute(
            "DELETE FROM book_likes WHERE book_key=? AND user_id=?",
            (book_id, session["user_id"]),
        )
    else:
        db.execute(
            "INSERT INTO book_likes(book_key, user_id) VALUES (?, ?)",
            (book_id, session["user_id"]),
        )
    db.commit()
    return redirect(url_for("home", view="detail", book=book_id) + "#detail")


def book_comment(book_id):
    if not session.get("user_id"):
        flash("댓글을 쓰려면 먼저 로그인해 주세요.")
        return redirect(url_for("home", view="login") + "#login")
    content = request.form.get("content", "").strip()
    if content:
        db = get_db()
        db.execute(
            "INSERT INTO book_comments(book_key, user_id, nickname, content) VALUES (?, ?, ?, ?)",
            (book_id, session["user_id"], session["username"], content),
        )
        db.commit()
    return redirect(url_for("home", view="detail", book=book_id) + "#detail")


def easy_text():
    description = request.get_json(silent=True) or {}
    text = str(description.get("text", "")).strip()
    if not text:
        return jsonify(ok=False, message="바꿀 책 소개가 없습니다."), 400
    result, used_api = make_easy_text(text)
    return jsonify(ok=True, result=result, used_api=used_api)


def ai_preview():
    payload = request.get_json(silent=True) or {}
    book_key = str(payload.get("book_key", "")).strip()
    text = str(payload.get("text", "")).strip()
    if not book_key or not text:
        return jsonify(ok=False, message="책 정보가 없습니다."), 400

    db = get_db()
    cached = db.execute(
        "SELECT * FROM ai_previews WHERE book_key=?", (book_key,)
    ).fetchone()
    old_fallback = (
        cached
        and (
            cached["easy_text"].startswith("쉽게 말하면,")
            or "no text, no letters, no book cover" in cached["visual_prompt"]
        )
    )
    if cached and cached["image_path"] and not old_fallback:
        return jsonify(
            ok=True,
            easy_text=cached["easy_text"],
            visual_prompt=cached["visual_prompt"],
            image_url=cached["image_path"],
            cached=True,
        )

    preview = make_book_preview(text)
    if not preview["used_api"]:
        return jsonify(
            ok=False,
            message="Gemini 쉬운 글 생성에 실패했습니다. 잠시 후 다시 시도해 주세요.",
            easy_text=preview["easy_text"],
            image_url=None,
            used_gemini=False,
            cached=False,
        ), 502
    image_url, image_error = generate_mood_image(
        book_key, preview["visual_prompt"]
    )

    if image_url and preview["used_api"]:
        db.execute(
            """INSERT INTO ai_previews(book_key, easy_text, visual_prompt, image_path)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(book_key) DO UPDATE SET
                 easy_text=excluded.easy_text,
                 visual_prompt=excluded.visual_prompt,
                 image_path=excluded.image_path""",
            (
                book_key,
                preview["easy_text"],
                preview["visual_prompt"],
                image_url,
            ),
        )
        db.commit()

    return jsonify(
        ok=True,
        easy_text=preview["easy_text"],
        visual_prompt=preview["visual_prompt"],
        image_url=image_url,
        image_error=image_error,
        gemini_error=None,
        used_gemini=preview["used_api"],
        cached=False,
    )


def nearby():
    return redirect(url_for("home", view="nearby") + "#nearby")


def mypage():
    if not session.get("user_id"):
        flash("마이페이지를 보려면 먼저 로그인해 주세요.")
        return redirect(url_for("home", view="login") + "#login")
    return redirect(url_for("home", view="mypage") + "#mypage")


def community():
    category = request.args.get("category", "전체")
    db = get_db()
    if category == "전체":
        posts = db.execute("SELECT * FROM community_posts ORDER BY id DESC").fetchall()
    else:
        posts = db.execute(
            "SELECT * FROM community_posts WHERE category=? ORDER BY id DESC", (category,)
        ).fetchall()
    comments = db.execute(
        "SELECT * FROM community_comments ORDER BY id"
    ).fetchall()
    comment_map = {}
    for comment in comments:
        comment_map.setdefault(comment["post_id"], []).append(comment)
    like_rows = db.execute(
        "SELECT post_id, COUNT(*) AS count FROM community_likes GROUP BY post_id"
    ).fetchall()
    like_map = {row["post_id"]: row["count"] for row in like_rows}
    liked_posts = set()
    if session.get("user_id"):
        liked_posts = {
            row["post_id"]
            for row in db.execute(
                "SELECT post_id FROM community_likes WHERE user_id=?",
                (session["user_id"],),
            ).fetchall()
        }
    return redirect(url_for("home", view="community", category=category) + "#community")


def community_new():
    if not session.get("user_id"):
        flash("글을 쓰려면 먼저 로그인해 주세요.")
        return redirect(url_for("home", view="login") + "#login")
    category = request.form.get("category", "감상 나눔")
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    book_title = request.form.get("book_title", "").strip()
    if title and content:
        db = get_db()
        db.execute(
            """INSERT INTO community_posts
               (category, title, content, book_title, user_id, nickname)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (category, title, content, book_title, session["user_id"], session["username"]),
        )
        db.commit()
    return redirect(url_for("home", view="community") + "#community")


def community_comment(post_id):
    if not session.get("user_id"):
        flash("댓글을 쓰려면 먼저 로그인해 주세요.")
        return redirect(url_for("home", view="login") + "#login")
    content = request.form.get("content", "").strip()
    if content:
        db = get_db()
        db.execute(
            """INSERT INTO community_comments(post_id, user_id, nickname, content)
               VALUES (?, ?, ?, ?)""",
            (post_id, session["user_id"], session["username"], content),
        )
        db.commit()
    return redirect(url_for("home", view="community") + "#community")


def community_like(post_id):
    if not session.get("user_id"):
        flash("좋아요를 누르려면 먼저 로그인해 주세요.")
        return redirect(url_for("home", view="login") + "#login")
    db = get_db()
    exists = db.execute(
        "SELECT 1 FROM community_likes WHERE post_id=? AND user_id=?",
        (post_id, session["user_id"]),
    ).fetchone()
    if exists:
        db.execute(
            "DELETE FROM community_likes WHERE post_id=? AND user_id=?",
            (post_id, session["user_id"]),
        )
    elif db.execute("SELECT 1 FROM community_posts WHERE id=?", (post_id,)).fetchone():
        db.execute(
            "INSERT INTO community_likes(post_id, user_id) VALUES (?, ?)",
            (post_id, session["user_id"]),
        )
    db.commit()
    return redirect(url_for("home", view="community") + "#community")


def signup():
    message = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password_check = request.form.get("password_check", "")
        name = request.form.get("name", "").strip()
        birth_year = request.form.get("birth_year", "").strip()
        birth_month = request.form.get("birth_month", "").strip()
        birth_day = request.form.get("birth_day", "").strip()
        birth_parts = (birth_year, birth_month, birth_day)
        birth = "-".join(birth_parts) if all(birth_parts) else ""
        agreed = request.form.get("agreed")

        if len(username) < 3:
            message = "아이디는 3자 이상 입력해 주세요."
        elif len(password) < 4:
            message = "비밀번호는 4자 이상 입력해 주세요."
        elif password != password_check:
            message = "비밀번호 확인이 일치하지 않습니다."
        elif not name:
            message = "이름을 입력해 주세요."
        elif not agreed:
            message = "개인정보 수집 안내에 동의해 주세요."
        else:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO users(username, password, name, birth) VALUES (?, ?, ?, ?)",
                    (username, generate_password_hash(password), name, birth),
                )
                db.commit()
                return redirect(url_for("home", view="signup-complete") + "#signup-complete")
            except sqlite3.IntegrityError:
                message = "이미 사용 중인 아이디입니다."
    if request.method == "GET":
        return redirect(url_for("home", view="signup") + "#signup")
    return render_template("onepage.html", **build_onepage_context("signup", message))


def signup_complete():
    return redirect(url_for("home", view="signup-complete") + "#signup-complete")


def login():
    message = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()
        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("home", view="mypage") + "#mypage")
        message = "아이디 또는 비밀번호를 확인해 주세요."
    if request.method == "GET":
        return redirect(url_for("home", view="login") + "#login")
    return render_template("onepage.html", **build_onepage_context("login", message))


def google_login():
    if not GOOGLE_ENABLED:
        flash("Google 로그인 키를 .env에 입력해 주세요.")
        return redirect(url_for("home", view="login") + "#login")
    callback_host = os.getenv("CALLBACK_URL_HOST", "http://localhost:3000").rstrip("/")
    return oauth.google.authorize_redirect(f"{callback_host}/api/auth/google/callback")


def google_callback():
    if not GOOGLE_ENABLED:
        return redirect(url_for("home", view="login") + "#login")
    try:
        token = oauth.google.authorize_access_token()
        profile = token.get("userinfo") or oauth.google.userinfo(token=token)
        if not profile or not profile.get("sub"):
            raise ValueError("Google 사용자 정보를 확인할 수 없습니다.")
        login_oauth_user("google", profile.get("sub"), profile.get("email", ""), profile.get("name", ""), profile.get("picture", ""))
    except Exception as error:
        app.logger.warning("Google OAuth login failed: %s", error)
        flash("구글 로그인에 실패했습니다. OAuth 콜백 주소와 키를 확인해 주세요.")
        return redirect(url_for("home", view="login") + "#login")
    return redirect(url_for("home", view="mypage") + "#mypage")


def github_login():
    if not GITHUB_ENABLED:
        flash("GitHub 로그인 키를 .env에 입력해 주세요.")
        return redirect(url_for("home", view="login") + "#login")
    callback_host = os.getenv("CALLBACK_URL_HOST", "http://localhost:3000").rstrip("/")
    return oauth.github.authorize_redirect(f"{callback_host}/api/auth/github/callback")


def github_callback():
    if not GITHUB_ENABLED:
        return redirect(url_for("home", view="login") + "#login")
    try:
        token = oauth.github.authorize_access_token()
        profile = oauth.github.get("user", token=token).json()
        if not profile or not profile.get("id"):
            raise ValueError("GitHub 사용자 정보를 확인할 수 없습니다.")
        email = profile.get("email") or ""
        if not email:
            emails = oauth.github.get("user/emails", token=token).json()
            primary = next((item for item in emails if item.get("primary") and item.get("verified")), None)
            email = (primary or next((item for item in emails if item.get("verified")), {})).get("email", "")
        login_oauth_user("github", profile.get("id"), email, profile.get("name") or profile.get("login", ""), profile.get("avatar_url", ""))
    except Exception as error:
        app.logger.warning("GitHub OAuth login failed: %s", error)
        flash("깃허브 로그인에 실패했습니다. OAuth 콜백 주소와 키를 확인해 주세요.")
        return redirect(url_for("home", view="login") + "#login")
    return redirect(url_for("home", view="mypage") + "#mypage")


def logout():
    session.clear()
    return redirect(url_for("home"))


