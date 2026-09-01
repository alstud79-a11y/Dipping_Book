# 디핑북 프로젝트 구조 설명

이 버전은 기존 디자인과 기능을 바꾸지 않고, 선생님 예제의 장점인
`기능별 라우트 분리`, `테스트`, `실행 문서`를 적용한 Flask 프로젝트입니다.

## 중요한 파일

```text
app.py                 서버 실행과 라우트 등록
controllers.py         기존 기능의 실제 처리 코드
routes/pages.py        일반 화면 URL
routes/books.py        도서·AI URL
routes/community.py    커뮤니티 URL
routes/auth.py         로그인·회원가입·OAuth URL
book_api_service.py    알라딘 API
gemini_service.py      쉬운 글 생성
flux_service.py        AI 이미지 생성
templates/onepage.html 전체 원페이지 화면
static/css/            기존 디자인 CSS
tests/                 기본 자동 테스트
```

## 라우트와 화면 이동의 차이

- 라우트는 사용자가 특정 URL을 요청했을 때 실행할 Python 함수를 연결합니다.
- 원페이지 이동은 한 HTML 안에서 필요한 화면만 보여줍니다.
- 이 프로젝트는 Flask 라우트와 원페이지 화면 전환을 함께 사용합니다.

## CSS를 유지한 이유

현재 CSS는 여러 파일이지만 모든 디자인을 유지하기 위해 이름과 연결 순서를
변경하지 않았습니다. 발표 전 무리하게 합치면 우선순위가 달라져 화면이 깨질 수
있습니다. 발표 후 공통·페이지·반응형 CSS로 단계적으로 정리할 수 있습니다.

## 실행

```powershell
python app.py
```

브라우저 주소는 반드시 다음 주소를 사용합니다.

```text
http://localhost:3000
```

Google OAuth에서 `localhost`와 `127.0.0.1`을 섞어 사용하지 않습니다.

## 테스트

```powershell
python -m unittest discover -s tests
```

## 발표용 한 문장

> 기존 Flask 기능과 디자인을 유지하면서 URL 라우트를 페이지·도서·커뮤니티·인증으로 분리하고, 구조 테스트와 설명 문서를 추가해 유지보수성을 개선했습니다.
