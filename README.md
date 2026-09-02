# UNIT TX Research Images

UNIT TX의 Substack 리서치 커버와 본문 이미지를 JSON에서 PNG로 만드는 템플릿 저장소다. 저장소를 clone한 뒤 자료와 데이터만 바꾸면 같은 브랜드 규칙으로 이미지를 반복 제작할 수 있다. 저장소의 목표와 고정 계약은 [goal.md](goal.md)에 정리한다.

## 빠른 시작

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
.venv/bin/python render.py --all
```

결과는 `out/`에 생성된다.

```text
out/
├── onchain-adoption-cover.png       1440×756
├── stablecoin-payment-cover.png     1440×756
├── onchain-payment-framework.png    1440×810
└── token-survival-example.png       1440×1200
```

한 장만 만들려면 예제 JSON을 복제한 뒤 자료와 데이터만 바꾸고 파일 경로를 넘긴다.

```bash
cp examples/cover-editorial.json examples/my-research-cover.json
.venv/bin/python render.py examples/my-research-cover.json
```

2배 해상도 출력이 필요할 때만 `--scale 2`를 사용한다.

```bash
.venv/bin/python render.py --all --scale 2 --output-dir out-2x
```

## 템플릿

| 이름 | 크기 | 용도 |
| --- | ---: | --- |
| `cover-editorial` | 1440×756 | 밝은 에디토리얼 메인 커버 |
| `cover-object` | 1440×756 | blueprint signal map 중심의 어두운 커버 |
| `figure-framework` | 1440×810 | 구조도와 흐름도 |
| `figure-data` | 1440×1200 | 라인 또는 막대 차트와 KPI |

모든 템플릿은 날짜를 왼쪽 아래, UNIT TX 로고를 오른쪽 아래에 고정하며 가운데 푸터 문구는 사용하지 않는다. 글꼴은 SUIT Variable, 굵기는 500/600/800으로 통일한다. 밝은 계열은 흰색과 UNIT TX Blue `#0064FF`, 어두운 커버는 deep navy signal map을 사용한다.

## 저장소 구조

```text
assets/       UNIT TX 로고, SUIT Variable, 공통 CSS
examples/     복제해서 사용하는 JSON 입력
templates/    Jinja HTML 템플릿과 공통 partial
tests/        검증, 렌더링, 예제 회귀 테스트
out/          생성된 HTML, PNG, manifest
render.py     CLI와 렌더 파이프라인
```

제작 규칙은 [AGENTS.md](AGENTS.md), 저장소 목표는 [goal.md](goal.md), 필드 설명과 프리퍼블리시 체크리스트는 [docs/IMAGE_SYSTEM.md](docs/IMAGE_SYSTEM.md)에 있다. 데이터 이미지는 실제 발행 전에 `source`, `date`, 단위와 모든 수치를 반드시 검증한다.

## 검증

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python render.py --all
sips -g pixelWidth -g pixelHeight out/*.png
```
