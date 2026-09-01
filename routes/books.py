"""도서 좋아요·댓글·AI 변환 API URL."""

import controllers


def register_book_routes(app):
    app.add_url_rule(
        "/book/<book_id>/like",
        endpoint="book_like",
        view_func=controllers.book_like,
        methods=["POST"],
    )
    app.add_url_rule(
        "/book/<book_id>/comment",
        endpoint="book_comment",
        view_func=controllers.book_comment,
        methods=["POST"],
    )
    app.add_url_rule(
        "/api/easy-text",
        endpoint="easy_text",
        view_func=controllers.easy_text,
        methods=["POST"],
    )
    app.add_url_rule(
        "/api/ai-preview",
        endpoint="ai_preview",
        view_func=controllers.ai_preview,
        methods=["POST"],
    )
