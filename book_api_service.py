import os

import requests


GOOGLE_BOOKS_KEY = os.getenv("GOOGLE_BOOKS_API_KEY", "")
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"

GENRE_IDS = {
    "전체": 0,
    "소설": 50917,
    "에세이": 55889,
    "자기계발": 336,
    "시": 50940,
    "여행": 1196,
}

SAMPLE_BOOKS = [
    {
        "id": "sample-1", "isbn": "sample-1", "title": "바다의 기억",
        "author": "한지음", "publisher": "디핑출판", "genre": "소설",
        "description": "잊고 있던 여름의 바다로 돌아가 오래된 마음을 만나는 따뜻한 이야기입니다.",
        "cover": "", "pub_date": "2026-03-10", "pages": "320",
    },
    {
        "id": "sample-2", "isbn": "sample-2", "title": "프로젝트 헤일메리",
        "author": "앤디 위어", "publisher": "알에이치코리아", "genre": "소설",
        "description": "우주에서 홀로 깨어난 과학자가 인류를 구하기 위해 문제를 풀어가는 이야기입니다.",
        "cover": "", "pub_date": "2021-05-04", "pages": "692",
    },
    {
        "id": "sample-3", "isbn": "sample-3", "title": "긴긴밤",
        "author": "루리", "publisher": "문학동네", "genre": "에세이",
        "description": "서로 다른 존재가 함께 걷고 서로에게 힘이 되어 주는 과정을 담았습니다.",
        "cover": "", "pub_date": "2021-02-03", "pages": "144",
    },
    {
        "id": "sample-4", "isbn": "sample-4", "title": "마음의 온도",
        "author": "김다온", "publisher": "오늘책", "genre": "시",
        "description": "하루 끝에 천천히 읽기 좋은 짧은 문장과 다정한 위로를 모았습니다.",
        "cover": "", "pub_date": "2025-11-20", "pages": "184",
    },
    {
        "id": "sample-5", "isbn": "sample-5", "title": "아무리 화가 나도",
        "author": "한지음", "publisher": "마음숲", "genre": "자기계발",
        "description": "감정을 알아차리고 마음을 다독이는 쉬운 연습 방법을 소개합니다.",
        "cover": "", "pub_date": "2025-08-14", "pages": "248",
    },
    {
        "id": "sample-6", "isbn": "sample-6", "title": "여름은 오래 그곳에 남아",
        "author": "마쓰이에 마사시", "publisher": "비채", "genre": "소설",
        "description": "한 건축사무소에서 보낸 여름과 그곳에서 만난 사람들을 잔잔하게 그린 소설입니다.",
        "cover": "", "pub_date": "2016-08-19", "pages": "432",
    },
    {
        "id": "sample-7", "isbn": "sample-7", "title": "작은 여행의 시작",
        "author": "박소영", "publisher": "길벗", "genre": "여행",
        "description": "멀리 떠나지 않아도 발견할 수 있는 가까운 여행지를 소개합니다.",
        "cover": "", "pub_date": "2025-04-22", "pages": "276",
    },
    {
        "id": "sample-8", "isbn": "sample-8", "title": "불편한 편의점",
        "author": "김호연", "publisher": "나무옆의자", "genre": "소설",
        "description": "서울역에서 시작된 인연이 작은 편의점 사람들의 일상을 바꾸는 이야기입니다.",
        "cover": "", "pub_date": "2021-04-20", "pages": "268",
    },
    {
        "id": "sample-9", "isbn": "sample-9", "title": "오늘도 잘 살았습니다",
        "author": "정다정", "publisher": "마음책방", "genre": "에세이",
        "description": "평범한 하루에서 발견한 작은 기쁨과 솔직한 마음을 기록했습니다.",
        "cover": "", "pub_date": "2025-09-02", "pages": "224",
    },
    {
        "id": "sample-10", "isbn": "sample-10", "title": "천천히 나를 돌보는 법",
        "author": "이서윤", "publisher": "한빛라이프", "genre": "자기계발",
        "description": "지친 날에도 부담 없이 실천할 수 있는 자기 돌봄 습관을 알려 줍니다.",
        "cover": "", "pub_date": "2026-01-12", "pages": "256",
    },
    {
        "id": "sample-11", "isbn": "sample-11", "title": "계절의 문장",
        "author": "윤하늘", "publisher": "시인의집", "genre": "시",
        "description": "봄부터 겨울까지 계절의 풍경과 마음을 담은 시를 모았습니다.",
        "cover": "", "pub_date": "2025-10-01", "pages": "152",
    },
    {
        "id": "sample-12", "isbn": "sample-12", "title": "주말에 떠나는 도시 산책",
        "author": "최여행", "publisher": "트래블북", "genre": "여행",
        "description": "주말 하루 동안 가볍게 걸을 수 있는 도시 산책 코스를 안내합니다.",
        "cover": "", "pub_date": "2025-06-18", "pages": "304",
    },
]


# 메인 장르별 도서 8권은 API 연결 여부와 관계없이 상세 화면을 엽니다.
CUSTOM_PREVIEW_BOOKS = [
    {"id": "preview-1", "isbn": "preview-1", "title": "달러구트 꿈 백화점", "author": "이미예", "publisher": "팩토리나인", "genre": "소설", "description": "잠들어야만 입장할 수 있는 꿈 백화점에서 벌어지는 신비롭고 따뜻한 이야기를 담은 판타지 소설입니다.", "cover": "/static/images/cover-book1.jpg", "pub_date": "2020-07-08", "pages": "300"},
    {"id": "preview-2", "isbn": "preview-2", "title": "프로젝트 헤일메리", "author": "앤디 위어", "publisher": "알에이치코리아", "genre": "소설", "description": "우주에서 홀로 깨어난 과학자가 인류를 구하기 위해 기억과 과학적 지식을 되찾아 가는 이야기입니다.", "cover": "/static/images/cover-book2.jpg", "pub_date": "2021-05-04", "pages": "692"},
    {"id": "preview-3", "isbn": "preview-3", "title": "긴긴밤", "author": "루리", "publisher": "문학동네", "genre": "에세이", "description": "서로 다른 존재가 긴 밤을 함께 건너며 서로에게 힘이 되어 주는 따뜻한 이야기입니다.", "cover": "/static/images/cover-book3.jpg", "pub_date": "2021-02-03", "pages": "144"},
    {"id": "preview-4", "isbn": "preview-4", "title": "괴테는 모든 것을 말했다", "author": "스즈키 유이", "publisher": "리프", "genre": "소설", "description": "괴테의 문장을 단서로 사람과 기억, 삶의 의미를 따라가는 이야기입니다.", "cover": "/static/images/cover-book4.jpg", "pub_date": "2025-06-25", "pages": "288"},
    {"id": "preview-5", "isbn": "preview-5", "title": "어서 오세요, 휴남동 서점입니다", "author": "황보름", "publisher": "클레이하우스", "genre": "소설", "description": "동네 서점을 찾는 사람들의 일상과 고민이 책을 통해 천천히 이어지는 따뜻한 소설입니다.", "cover": "/static/images/cover-book5.jpg", "pub_date": "2022-01-17", "pages": "364"},
    {"id": "preview-6", "isbn": "preview-6", "title": "노인과 바다", "author": "어니스트 헤밍웨이", "publisher": "민음사", "genre": "소설", "description": "늙은 어부 산티아고가 거대한 물고기와 맞서며 인간의 의지와 존엄을 보여 주는 고전 소설입니다.", "cover": "/static/images/cover-book6.jpg", "pub_date": "2012-01-02", "pages": "160"},
    {"id": "preview-7", "isbn": "preview-7", "title": "방구석 미술관", "author": "조원재", "publisher": "블랙피쉬", "genre": "예술/대중문화", "description": "어렵게 느껴졌던 미술가와 명작의 이야기를 친근한 설명으로 소개하는 미술 교양서입니다.", "cover": "/static/images/cover-book7.jpg", "pub_date": "2018-08-03", "pages": "344"},
    {"id": "preview-8", "isbn": "preview-8", "title": "만희네 집", "author": "권윤덕", "publisher": "길벗어린이", "genre": "유아", "description": "만희가 새로 이사한 집의 여러 공간과 가족의 정겨운 생활 모습을 섬세하게 담은 그림책입니다.", "cover": "/static/images/cover-book8.jpg", "pub_date": "1995-11-01", "pages": "44"},
]


def _request(params):
    options = {**params, "printType": "books"}
    if GOOGLE_BOOKS_KEY:
        options["key"] = GOOGLE_BOOKS_KEY
    try:
        response = requests.get(GOOGLE_BOOKS_URL, params=options, timeout=10)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return None


def _clean_item(item, default_genre="전체"):
    info = item.get("volumeInfo") or {}
    identifiers = info.get("industryIdentifiers") or []
    isbn = next((x.get("identifier") for x in identifiers if x.get("type") == "ISBN_13"), None)
    isbn = isbn or next((x.get("identifier") for x in identifiers if x.get("type") == "ISBN_10"), "")
    google_id = item.get("id", "")
    category = " ".join(info.get("categories") or [])
    genre = default_genre if default_genre != "전체" else _guess_genre(category)
    cover = (info.get("imageLinks") or {}).get("thumbnail", "")
    if cover.startswith("http://"):
        cover = "https://" + cover[7:]
    return {
        "id": google_id, "isbn": isbn or google_id,
        "title": info.get("title") or "제목 정보 없음",
        "author": ", ".join(info.get("authors") or []) or "저자 정보 없음",
        "publisher": info.get("publisher") or "출판사 정보 없음",
        "genre": genre,
        "description": info.get("description") or "등록된 책 소개가 없습니다.",
        "cover": cover, "pub_date": info.get("publishedDate") or "",
        "pages": str(info.get("pageCount") or "-"),
    }


def _guess_genre(category):
    for genre in ["소설", "에세이", "자기계발", "시", "여행"]:
        if genre in category:
            return genre
    return "전체"


def _sample_list(genre="전체", query=""):
    books = SAMPLE_BOOKS
    if genre != "전체":
        books = [book for book in books if book["genre"] == genre]
    if query:
        query_lower = query.lower()
        books = [
            book for book in books
            if query_lower in book["title"].lower() or query_lower in book["author"].lower()
        ]
    return books or SAMPLE_BOOKS

def get_bestsellers(max_results=10):
    data = _request({
        "q": "한국 소설",
        "orderBy": "relevance",
        "maxResults": max_results,
        "langRestrict": "ko",
    })
    if data and data.get("items"):
        return [_clean_item(item) for item in data["items"]]
    return SAMPLE_BOOKS[:max_results]


def get_books(genre="전체", query="", page=1, max_results=12):
    page = max(1, int(page))
    max_results = max(1, min(int(max_results), 40))
    terms = query.strip() if query else ""
    if not terms:
        terms = "한국 소설" if genre == "전체" else genre
    elif genre != "전체":
        terms = f"{terms} {genre}"
    data = _request({
        "q": terms, "startIndex": (page - 1) * max_results,
        "maxResults": max_results, "langRestrict": "ko",
    })
    if data is not None:
        return [_clean_item(item, genre) for item in data.get("items", [])]
    # Preserve existing sample fallback when the external API is unavailable.
    return (_sample_list(genre, query) * 3)[:max_results]


def get_book(book_id):
    for book in CUSTOM_PREVIEW_BOOKS:
        if book["id"] == book_id:
            return book
    for book in SAMPLE_BOOKS:
        if book["id"] == book_id:
            return book
    if not book_id or book_id.startswith(("sample-", "preview-")):
        return None
    # Supports both Google volume IDs and ISBNs from existing links.
    if book_id.isdigit() and len(book_id) in (10, 13):
        data = _request({"q": f"isbn:{book_id}", "maxResults": 1})
        items = (data or {}).get("items") or []
        return _clean_item(items[0]) if items else None
    try:
        options = {"key": GOOGLE_BOOKS_KEY} if GOOGLE_BOOKS_KEY else {}
        response = requests.get(f"{GOOGLE_BOOKS_URL}/{book_id}", params=options, timeout=10)
        response.raise_for_status()
        item = response.json()
        return _clean_item(item) if item.get("volumeInfo") else None
    except (requests.RequestException, ValueError):
        return None
