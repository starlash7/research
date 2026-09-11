# Palette Preview Implementation Plan

**Goal:** 승인된 버밀리언, 라임, 바이올렛 세 후보를 같은 밝은 커버와 추세 차트로 비교한다.

**Architecture:** 기존 렌더러에 선택 `palette_preview`만 추가한다. 이름이 지정된 비교용 팔레트는 넓은 색면, 데이터 선, 작은 텍스트의 색을 정의한다. 기본 블루 및 승인된 커버 출력은 바꾸지 않는다.

**Tech Stack:** 기존 Python/Jinja, HTML/CSS/SVG, Playwright. 새 의존성 없음.

## 승인 범위와 고정 조건

- `vermillion`: 강조 #E4492D, 데이터 #E4492D, 작은 텍스트 #B93822.
- `lime`: 강조 #C7F542, 데이터 및 작은 텍스트 #526B16. 밝은 라임을 흰 바탕의 얇은 선이나 작은 글자에 쓰지 않는다.
- `violet`: 강조, 데이터 및 작은 텍스트 #7546E8.
- 커버 1440×756, 차트 1440×1200. SUIT 500/600/800, 흑백 공식 심볼, 워드마크 #0C1B33, 왼쪽 아래 날짜 #000000 유지.
- 세 후보의 내용과 배치는 동일하다. 색 비교용 커버는 프로젝트 이미지 없이 기존 원형 그래픽을 사용한다. 원본 BTC 자산과 커버는 변경하지 않는다.
- 색 이름과 HEX는 비교판에만 쓰며 개별 이미지의 가시적 카피에 넣지 않는다. 차트의 예시 경고, 출처, 단위, 범례 유지.
- 다른 모든 시리즈는 기존 중립색과 점선으로 유지한다. 상승·하락에 색을 자동 부여하지 않는다.
- 커버의 텍스트 왼쪽 위치는 시안에서만 88px로 맞춰 6% 안전 여백을 지킨다.

## 실행 체크리스트

- [x] `tests/test_palette_preview.py`에 세 색의 선택 시리즈·원본 불변·기본 출력 불변·잘못된 팔레트 거부·6개 예제의 동일 데이터 검증을 작성한다. `.venv/bin/python -m unittest discover -s tests -p test_palette_preview.py -v`가 새 기능 부재로 실패하는지 확인한다.
- [x] `render.py`의 `PALETTE_PREVIEWS`, `validate_document`, `build_context`에 선택형 팔레트를 연결한다. 지원 대상은 `cover-editorial`과 `variant: editorial`인 `figure-data`의 line이며 `accent`와 동시 지정은 거부한다. 팔레트 생략 시 기존 경로를 그대로 쓴다.
- [x] `templates/base.html`에 선택형 클래스·CSS 변수를 전달하고 `assets/styles.css`의 `.palette-preview` 안에서만 색 역할을 적용한다.
- [x] `examples/previews/palettes/{vermillion,lime,violet}-{cover,trend}.json` 6개를 만들고 `docs/IMAGE_SYSTEM.md`에 시안 실행법을 기록한다. `--all`의 기본 예제 목록은 유지한다.
- [x] 전체 unittest, 실제 6장 렌더, `sips` 규격 확인, 로컬 네트워크 요청·글자 영역·색 대비 검사, 원본 및 모바일 육안 검사를 수행한다.
- [x] `out/palette-comparison.png`에 3열 비교판을 출력한다. 승인된 커버와 기존 추세·지표 시안은 재렌더 후 변경 전 PNG SHA-256과 비교한다.

기본 팔레트 교체, 다크 커버 재디자인, 전체 데이터 5종 확장 및 커밋·푸시는 이번 범위 밖이다.
