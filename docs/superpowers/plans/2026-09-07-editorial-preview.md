# Editorial Preview Implementation Plan

**Goal:** 승인된 블루 기준선·선택적 강조 방향을 추세와 핵심 지표 두 장으로 비교한다.

**Architecture:** 기존 두 템플릿에 선택 `variant: "editorial"`을 연결한다. `focus_index`는 작성자가 지정한 0부터 시작하는 대상 번호이며 생략하면 아무 대상도 자동 선택하지 않는다. 기본 입력, 커버, 나머지 세 데이터 템플릿은 변경하지 않는다.

**Tech Stack:** 기존 Python, Jinja, HTML/CSS/SVG, Playwright. 새 의존성 없음.

## Global Constraints

- 각 PNG 1440×1200, 로컬 SUIT 500/600/800, 카드 반경 28px.
- 흰색 배경, UNIT TX Blue #0064FF, 날짜 검정·왼쪽 아래, 기존 로고·오른쪽 아래.
- 같은 예제 수치·카피를 사용하고 경고·출처를 유지한다. 숫자나 해설을 추가·중복하지 않는다.
- 기본 출력과 비교 시안은 slug를 분리한다. 기본 출력을 시안으로 교체하지 않는다.

## Execution

- [x] `tests/test_editorial_preview.py`: 선택 강조, 미선택 처리, 잘못된 인덱스와 지원하지 않는 조합의 실패를 먼저 검증한다.
- [x] `render.py`: variant 검증과 클래스 컨텍스트를 추가하고, 추세 끝점 숫자를 위한 공간을 확보한다. 기존 chart geometry는 기본 입력에서 유지한다.
- [x] `templates/data-base.html`, `figure-data.html`, `figure-metrics.html`: 공통 구분선과 선택된 대상 클래스만 추가한다.
- [x] `assets/styles.css`: `.editorial-figure`에만 편집형 여백, 차트 선택 강조, 하나의 블루 지표 카드를 적용한다.
- [x] `examples/previews/figure-data-editorial.json`, `figure-metrics-editorial.json`: 기존 데이터와 제목을 그대로 복제한 선택형 시안 입력을 제공한다.
- [x] `.venv/bin/python -m unittest discover -s tests -v` 통과 후 두 JSON을 `render.py`로 렌더한다.
- [x] `sips`로 규격, 실제 PNG와 모바일 축소본으로 텍스트·푸터·강조를 확인한다. 기본 8개 PNG의 SHA-256을 변경 전과 비교한다.
- [x] `out/`에 전후 비교 이미지를 만들고, 사용 방법을 `docs/IMAGE_SYSTEM.md`에 기록한다.

두 시안의 시각적 검토가 목적이며 다른 템플릿으로의 확장은 이번 작업에 포함하지 않는다.
