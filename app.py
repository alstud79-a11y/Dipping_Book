"""디핑북 Flask 실행 파일.

실제 기능 코드는 controllers.py에 두고, URL 연결은 routes 폴더에서
기능별로 등록합니다. 기존 기능과 화면은 변경하지 않았습니다.
"""

import os

from controllers import app, init_db
from routes import register_routes


register_routes(app)

with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "3000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
