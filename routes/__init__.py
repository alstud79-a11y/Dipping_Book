"""기능별 라우트 등록 모음."""

from .auth import register_auth_routes
from .books import register_book_routes
from .community import register_community_routes
from .pages import register_page_routes


def register_routes(app):
    """모든 URL을 Flask 앱에 한 번씩 등록합니다."""
    register_page_routes(app)
    register_book_routes(app)
    register_community_routes(app)
    register_auth_routes(app)
