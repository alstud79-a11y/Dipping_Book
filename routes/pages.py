"""메인·소개·도서 목록·상세·지도·마이페이지 URL."""

import controllers


def register_page_routes(app):
    app.add_url_rule("/", endpoint="home", view_func=controllers.home)
    app.add_url_rule("/about", endpoint="about", view_func=controllers.about)
    app.add_url_rule("/books", endpoint="books", view_func=controllers.books)
    app.add_url_rule("/book/<book_id>", endpoint="book_detail", view_func=controllers.book_detail)
    app.add_url_rule("/nearby", endpoint="nearby", view_func=controllers.nearby)
    app.add_url_rule("/mypage", endpoint="mypage", view_func=controllers.mypage)
