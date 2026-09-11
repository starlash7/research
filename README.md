# UNIT TX Research Images

UNIT TX의 Substack 리서치 커버와 본문 이미지를 JSON에서 PNG로 만드는 템플릿 저장소다. 저장소를 clone한 뒤 자료와 데이터만 바꾸면 같은 브랜드 규칙으로 이미지를 반복 제작할 수 있다. 저장소의 목표와 고정 계약은 [goal.md](goal.md)에 정리한다.

공식 키컬러는 **UNIT TX Blue `#0064FF`로 확정**했다 (2026.09.11). 커버·데이터·프레임워크 모두 같은 강조색을 사용한다. 공식 제작은 `examples/*.json`을 복제하고 색상 필드를 추가하지 않는다. 흑백 로고, 날짜, SUIT와 외부 프로젝트 원본 이미지의 색상은 유지한다. [이전 색상 비교 시안](docs/PALETTE_STUDIES.md)은 보관용이며 `--all`에는 포함되지 않는다.

## 빠른 시작

Python 3.9 이상과 Git이 필요하다. 아래는 macOS 기준 명령이다. 최초 설치에는 패키지와 Chromium을 내려받을 인터넷 연결이 필요하며, 이미지 렌더링에는 로컬 자산만 사용한다.

```bash
git clone https://github.com/starlash7/research.git
cd research
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
.venv/bin/python render.py --all
```

결과는 `out/`에 생성된다.

```text
out/
├── bitcoin-use-cover.png             1440×756
├── bitcoin-reserve-cover.png         1440×756
├── onchain-payment-framework.png     1440×810
├── lending-trend-example.png         1440×1200
├── lending-ranking-example.png       1440×1200
├── lending-composition-example.png   1440×1200
├── lending-metrics-example.png       1440×1200
└── lending-comparison-example.png    1440×1200
```

한 장만 만들려면 예제 JSON을 복제한 뒤 자료와 데이터만 바꾸고 파일 경로를 넘긴다. 렌더 전에 `slug`를 새 이름으로 바꾸고 제목·분류·날짜를 수정한다. 커버 이미지는 JSON 파일이 있는 폴더 또는 그 하위 폴더에 저장하고 `hero_image`에 상대 경로를 입력한다.

```bash
cp examples/cover-editorial.json examples/my-research-cover.json
# my-research-cover.json의 slug와 내용을 수정한 뒤 실행
.venv/bin/python render.py examples/my-research-cover.json
```

입력 형식은 예제와 같은 JSON이다. 엑셀·PDF·임의 이미지를 넣으면 자동으로 데이터를 추출하거나 템플릿을 선택하는 도구는 아니다.

2배 해상도 출력이 필요할 때만 `--scale 2`를 사용한다.

```bash
.venv/bin/python render.py --all --scale 2 --output-dir out-2x
```

## 템플릿

| 이름 | 크기 | 용도 |
| --- | ---: | --- |
| `cover-editorial` | 1440×756 | 밝은 에디토리얼 메인 커버 |
| `cover-object` | 1440×756 | 차콜, 스모크, 딥블루 그라데이션 커버, 선택 이미지 |
| `figure-framework` | 1440×810 | 구조도와 흐름도 |
| [`figure-data`](examples/figure-data.json) | 1440×1200 | 시계열 추세, 최대 366개 관측치 |
| [`figure-ranking`](examples/figure-ranking.json) | 1440×1200 | 2-8개 항목의 가로 막대 비교 |
| [`figure-composition`](examples/figure-composition.json) | 1440×1200 | 2-4개 범주의 100% 누적 구성비 |
| [`figure-metrics`](examples/figure-metrics.json) | 1440×1200 | 핵심 지표 4개와 선택 증감률 |
| [`figure-comparison`](examples/figure-comparison.json) | 1440×1200 | 2-4개 대상, 3-6개 항목 비교표 |

모든 템플릿은 날짜를 왼쪽 아래, UNIT TX 로고를 오른쪽 아래에 고정하며 가운데 푸터는 사용하지 않는다. 두 커버는 JSON의 `category`를 왼쪽 위에 표시한다. 글꼴은 SUIT Variable, 굵기는 500/600/800, 정보 카드 반경은 28px로 통일한다. 밝은 계열은 흰색과 UNIT TX Blue `#0064FF`, 어두운 커버는 차콜, 스모크, 딥블루의 저채도 그라데이션을 사용한다.

데이터 5종은 제목, 분석 기간·단위, 출처, 하단 푸터 위치를 공유한다. 데이터 이미지의 날짜는 실제 검정 `#000000`이고 배경 박스나 테두리는 없다. 어두운 커버 날짜는 흰색이다. 지표·해설은 자동으로 추가하지 않는다.

예를 들어 순위 차트를 만들 때는 아래 파일만 복제해 `items`, `unit`, 제목, 날짜, 출처를 교체한다. `slug`도 새 이름으로 바꾸면 기존 출력이 덮어써지지 않는다.

```bash
cp examples/figure-ranking.json examples/my-ranking.json
.venv/bin/python render.py examples/my-ranking.json
```

예제 수치와 프로토콜 A/B/C는 가상 데이터다. `source`의 `Example data · replace before publishing` 경고는 실제 자료와 출처로 교체한 뒤에만 삭제한다. 필드별 입력 계약은 [데이터 템플릿 가이드](docs/IMAGE_SYSTEM.md#데이터-템플릿-5종)를 참고한다.

## 새 디자인 비교 시안

추세·핵심 지표의 새 디자인은 선택형 시안으로 분리했다. 기존 예제와 동일한 데이터를 사용하며 기본 출력은 변경하지 않는다.

```bash
.venv/bin/python render.py examples/previews/figure-data-editorial.json
.venv/bin/python render.py examples/previews/figure-metrics-editorial.json
```

`variant: "editorial"`과 선택 `focus_index`로 적용한다. `focus_index: 0`은 첫 대상을 강조하며 생략하면 자동 선택하지 않는다. 시안 입력은 `--all`에서 제외한다.

## 저장소 구조

```text
assets/       UNIT TX 로고, SUIT Variable, 공통 CSS
examples/     복제해서 사용하는 JSON 입력
templates/    Jinja HTML 템플릿과 공통 partial
tests/        검증, 렌더링, 예제 회귀 테스트
out/          생성된 HTML, PNG, manifest
render.py     CLI와 렌더 파이프라인
figure_models.py  추가 데이터 템플릿의 검증과 차트 좌표 계산
```

제작 규칙은 [AGENTS.md](AGENTS.md), 저장소 목표는 [goal.md](goal.md), 필드 설명과 프리퍼블리시 체크리스트는 [docs/IMAGE_SYSTEM.md](docs/IMAGE_SYSTEM.md)에 있다. 데이터 이미지는 실제 발행 전에 `source`, `date`, 단위와 모든 수치를 반드시 검증한다.

## 검증

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python render.py --all
sips -g pixelWidth -g pixelHeight out/*.png
```
