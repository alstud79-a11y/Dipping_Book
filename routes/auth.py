"""일반 회원가입·로그인과 Google/GitHub OAuth URL."""

import controllers


def register_auth_routes(app):
    app.add_url_rule(
        "/signup",
        endpoint="signup",
        view_func=controllers.signup,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/signup/complete",
        endpoint="signup_complete",
        view_func=controllers.signup_complete,
    )
    app.add_url_rule(
        "/login",
        endpoint="login",
        view_func=controllers.login,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/api/auth/google",
        endpoint="google_login",
        view_func=controllers.google_login,
    )
    app.add_url_rule(
        "/api/auth/google/callback",
        endpoint="google_callback",
        view_func=controllers.google_callback,
    )
    app.add_url_rule(
        "/api/auth/github",
        endpoint="github_login",
        view_func=controllers.github_login,
    )
    app.add_url_rule(
        "/api/auth/github/callback",
        endpoint="github_callback",
        view_func=controllers.github_callback,
    )
    app.add_url_rule("/logout", endpoint="logout", view_func=controllers.logout)
