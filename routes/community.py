"""북 커뮤니티 글·댓글·좋아요 URL."""

import controllers


def register_community_routes(app):
    app.add_url_rule("/community", endpoint="community", view_func=controllers.community)
    app.add_url_rule(
        "/community/new",
        endpoint="community_new",
        view_func=controllers.community_new,
        methods=["POST"],
    )
    app.add_url_rule(
        "/community/<int:post_id>/comment",
        endpoint="community_comment",
        view_func=controllers.community_comment,
        methods=["POST"],
    )
    app.add_url_rule(
        "/community/<int:post_id>/like",
        endpoint="community_like",
        view_func=controllers.community_like,
        methods=["POST"],
    )
