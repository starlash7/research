# UNIT TX Research Image System

UNIT TX의 Substack 커버와 본문용 리서치 이미지를 JSON에서 재현 가능한 PNG로 만드는 시스템이다. 사람이 매번 좌표를 조정하는 대신, 내용과 데이터만 입력하고 동일한 디자인 규칙으로 렌더한다.

## 출력 형식

| 템플릿 | 크기 | 용도 |
| --- | ---: | --- |
| `cover-editorial` | 1440×756 | 기본 리서치 커버, 밝은 배경 |
| `cover-object` | 1440×756 | 프로젝트 또는 프로토콜 중심 커버, 어두운 그라데이션 |
| `figure-framework` | 1440×810 | 구조도, 단계, 트랜잭션 흐름 |
| `figure-data` | 1440×1200 | 시계열 추세 |
| `figure-ranking` | 1440×1200 | 가로 막대 순위·크기 비교 |
| `figure-composition` | 1440×1200 | 100% 누적 구성비 |
| `figure-metrics` | 1440×1200 | 핵심 지표 4개 |
| `figure-comparison` | 1440×1200 | 대상별 비교표 |

커버는 Substack 소셜 프리뷰의 1200×630 비율과 같다. 1440px 폭은 본문과 이메일에서 축소될 때 한글과 얇은 선이 선명하게 남도록 선택했다.

## 디자인 원칙

- Design variance 6: 커버는 좌우 비대칭 구성을 쓰고 데이터 카드는 정렬을 우선한다.
- Motion intensity 1: 결과물이 정적 PNG이므로 애니메이션을 사용하지 않는다.
- Visual density 5: 한 장에 하나의 주장만 두고 근거와 출처는 생략하지 않는다.
- 테마는 이미지 한 장 안에서 바꾸지 않는다.
- 모서리 반경은 정보 카드와 이미지 프레임에 28px로 통일한다. 커버의 독립 장식 요소는 원형만 쓴다.
- 밝은 계열은 흰색 `#FFFFFF` 배경과 토스 공식 브랜드의 Toss Blue를 참고한 UNIT TX Blue `#0064FF`를 기본으로 한다. 토스 로고나 기타 브랜드 자산은 사용하지 않는다. 데이터 시리즈는 `#123B7A`, `#0C78B7`로 구분하고, 구성비의 네 번째 범주에만 연한 블루 `#9DC3FF`를 추가한다. 색상 참고: <https://brand.toss.im/>
- 어두운 계열은 차콜 `#111318`, 스모크, 딥블루를 겹친 저채도 그라데이션을 사용한다. 단색 검정, 그리드, 임의 그래프, 생성 심볼은 넣지 않는다. `hero_image`가 입력된 경우에만 실제 이미지를 오른쪽에 표시한다.
- 전경은 `#0C1B33` 또는 어두운 배경의 `#F4F7FF`를 사용한다.

## 고정 하단 푸터

모든 템플릿은 `templates/partials/fixed-footer.html`을 include해 하단 푸터를 같은 2열 구조로 사용한다.

- 왼쪽: 기준 날짜 `date`
- 오른쪽: `assets/unit-tx-logo.png`와 `UNIT TX` 워드마크

푸터 가운데에는 주제, 템플릿 종류, 예시 경고를 넣지 않는다. 예시 데이터 경고는 정량 이미지의 `source`에 표시한다. 공식 로고는 이미지의 다른 위치에 반복해서 넣지 않는다. 날짜 글자는 밝은 배경에서 검정 `#000000`, 어두운 배경에서 흰색 `#FFFFFF`으로 표시하고, 배경 박스나 테두리는 넣지 않는다. 밝은 배경에서는 검정 로고와 `#0C1B33` 워드마크, 어두운 배경에서는 흰색 로고와 `#FFFFFF` 워드마크를 사용한다. 날짜를 제목 옆의 칩이나 상단 메타 영역에 별도로 반복하지 않는다.

## 설치

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
```

SUIT Variable은 SIL Open Font License 1.1로 배포되는 오픈 소스 글꼴이다. 저장소에는 렌더 재현성을 위한 `assets/SUIT-Variable.woff2`와 `assets/SUIT-LICENSE.txt`를 함께 포함한다. 원 프로젝트는 <https://github.com/sun-typeface/SUIT>에서 확인할 수 있다.

## 실행

한 장만 렌더한다.

```bash
.venv/bin/python render.py examples/cover-editorial.json
```

모든 예제를 렌더한다.

```bash
.venv/bin/python render.py --all
```

2배 해상도 마스터가 필요할 때만 별도 출력 디렉터리를 사용한다.

```bash
.venv/bin/python render.py --all --scale 2 --output-dir out-2x
```

기본 결과는 `out/<slug>.html`, `out/<slug>.png`, `out/manifest.json`이다.

## 공통 JSON 필드

| 필드 | 의미 | 규칙 |
| --- | --- | --- |
| `template` | 템플릿 이름 | 위 여덟 이름 중 하나 |
| `slug` | 결과 파일명 | 영문 소문자, 숫자, 하이픈 |
| `title` | 핵심 주장 또는 구체적인 분석 대상 | 커버와 데이터 이미지는 최대 두 줄 |
| `date` | 기준일 | `YYYY.MM.DD` 권장 |
| `accent` | 이전 입력 호환용 강조색 | 공식 제작은 생략하여 확정 블루 `#0064FF`를 사용한다. 다른 `#RRGGBB` 값은 과거 시안 재현용으로만 지원한다. |

두 커버는 왼쪽 위에 표시할 `category`와 본문 `subtitle`이 필수다. `category`는 영문 24자 폭 이내의 짧고 구체적인 분류명을 사용한다. 두 커버 모두 JSON과 같은 폴더 아래의 로컬 파일을 `hero_image`로 지정할 수 있다. 밝은 커버에 경로가 없으면 UNIT TX Blue 에디토리얼 원형을 표시하고, 어두운 커버에 경로가 없으면 어떤 대체 그래픽도 생성하지 않고 그라데이션과 빈 공간만 표시한다.

### 밝은 에디토리얼 커버

```json
{
  "template": "cover-editorial",
  "slug": "bitcoin-use-cover",
  "category": "BITCOIN RESEARCH",
  "title": "비트코인은\n어디에서 쓰이는가",
  "subtitle": "보유 자산을 넘어 결제와 준비자산으로 확장되는 흐름을 추적한다.",
  "date": "2026.09.03",
  "hero_image": "art/bitcoin-logo.png"
}
```

### 어두운 그라데이션 커버

```json
{
  "template": "cover-object",
  "slug": "bitcoin-reserve-cover",
  "category": "BITCOIN OUTLOOK",
  "title": "비트코인은\n준비자산이 되는가",
  "subtitle": "수요 구조와 유동성 변화를 통해 장기 채택 조건을 살펴본다.",
  "date": "2026.09.03",
  "hero_image": "art/bitcoin-logo.png"
}
```

프로젝트 이미지가 있으면 JSON과 같은 폴더 또는 그 하위 폴더에 넣고 `"hero_image": "art/project.png"`를 추가한다. 이미지는 비율을 유지한 채 잘림 없이 표시되며 템플릿이 색상이나 효과를 덧씌우지 않는다. 절대 경로, 상위 폴더로 나가는 경로, 원격 URL은 허용하지 않는다.

## 데이터 템플릿 5종

모두 1440×1200의 흰색 배경을 사용하며 `templates/data-base.html`을 공유한다. 제목, 메타데이터, 본문, 출처, 날짜·로고의 위치를 템플릿마다 바꾸지 않는다. 커버에는 영향을 주지 않는다.

- 필수 공통 필드: `template`, `slug`, `title`, `source`, `date`.
- 선택 `period`: 분석 기간이나 집계 기준. 예: `2024.09 - 2026.08 · 월말 기준`. 입력하지 않으면 대체 문구를 표시하지 않고, 하단 `date`를 기준일로 사용한다.
- 제목은 최대 두 줄, 한 줄당 영문 44자 폭 이내다. `\n`으로 한 번 줄바꿈할 수 있다. 영문 폭 계산에서 한글은 2자로 센다. 실제 렌더 후 줄바꿈을 확인한다.
- `source`는 영문 150자 폭까지, `period`는 66자 폭까지 허용한다. 출처는 차트 아래, 날짜·로고 푸터 위에 한 번만 표시한다.
- 예시 데이터는 `source`에 반드시 `Example data · replace before publishing`을 사용한다. 예제의 프로토콜 A/B/C와 모든 수치는 가상이며 투자 판단용 자료가 아니다.
- KPI, 부제, 장식 문구, 중복 결론을 자동으로 추가하지 않는다. 기존 `highlight`도 이 5종의 제목에 붙이지 않는다.
- 숫자가 너무 길면 글자 크기를 임의로 줄이지 말고 데이터 단위를 조정한다. 순위·구성비·지표 수치는 소수점 둘째 자리까지 표시하고 불필요한 끝자리 0을 제거한다.

### 1. 추세 차트 `figure-data`

복제 파일: [`examples/figure-data.json`](../examples/figure-data.json)

`chart`에 `type: "line"`, `unit`, `labels`, `series`를 넣는다. `labels`는 입력 순서를 유지하는 2-366개 관측 시점이다. `series`는 1-3개이며 각 항목에 `name`, `values`가 필요하다. 모든 시리즈의 값 개수는 `labels`와 같아야 하고 숫자는 유한해야 한다. 시점 라벨은 영문 16자 폭, 시리즈명은 22자 폭 이내다. 축과 수치 라벨은 쉼표 포함 7자를 넘지 않도록 단위를 조정한다.

축 라벨은 최대 6개만 표시하지만 그래프에는 모든 관측치를 사용한다. 첫 시점과 마지막 시점은 항상 표시한다. 마지막 값만 직접 표기하고, 가까운 값은 라벨 위치를 분리한다. 시리즈는 실선, 긴 점선, 짧은 점선으로도 구분한다. `y_min`, `y_max`를 지정할 때는 모든 데이터를 포함해야 한다.

이전 입력 호환을 위해 `type: "bar"`와 0-3개의 선택 `takeaways`도 지원한다. 막대의 항목 수는 2-12개이며 모든 항목명을 표시한다. 7개 이상이면 항목명을 영문 8자 폭 이내로 제한하고 기울여 표시한다. 직접 수치 라벨은 단일 시리즈·6개 이하일 때만 표시한다. `takeaways`는 `{ "label": "표본", "value": "1,539" }` 구조이고 입력한 경우에만 표시한다. 새 항목별 크기 비교는 아래 `figure-ranking`을 권장한다.

### 2. 순위 차트 `figure-ranking`

복제 파일: [`examples/figure-ranking.json`](../examples/figure-ranking.json)

필수: `unit`, `items`. 항목 2-8개를 `{ "label": "프로토콜 A", "value": 14.2 }` 형태로 넣는다. `label`은 영문 18자 폭 이내, 표시 숫자는 쉼표 포함 10자 이내다. 값이 큰 순서로 자동 정렬하며 입력 JSON 자체는 변경하지 않는다. 0 기준선을 포함하고, 음수 막대는 왼쪽으로 그린다. 0 값을 가짜 길이의 막대로 표시하지 않는다. 각 행에 이름과 수치가 있으므로 별도 범례 문구는 추가하지 않는다.

### 3. 구성비 차트 `figure-composition`

복제 파일: [`examples/figure-composition.json`](../examples/figure-composition.json)

필수: `unit: "%"`, `categories`, `groups`. 범주명 2-4개와 비교 그룹 1-3개를 입력한다. 각 그룹은 `{ "label": "2026", "values": [51, 21, 20, 8] }` 형태이며 값 순서는 `categories`와 같다. 범주명은 영문 18자 폭, 그룹명은 40자 폭 이내다.

각 비율은 0-100 범위이고 그룹별 합계는 100이어야 한다. 소수점 입력의 반올림 오차만 ±0.01%p 허용하며 임의로 정규화하지 않는다. 0%나 아주 작은 조각도 막대 아래 이름과 비율이 남는다. 범례는 모든 그룹에서 동일한 순서로 배치해 색상만으로 구분하지 않는다.

### 4. 지표 카드 `figure-metrics`

복제 파일: [`examples/figure-metrics.json`](../examples/figure-metrics.json)

필수: 정확히 4개의 `metrics`. 각 지표는 `label`, 숫자 `value`, `unit`을 가진다. 입력 순서대로 왼쪽 위, 오른쪽 위, 왼쪽 아래, 오른쪽 아래에 배치한다. 표시 수치는 쉼표 포함 9자 이내이며 단위는 각 카드에 표시한다.

증감을 표시할 때만 `"change": { "value": 3.9, "unit": "%", "period": "전월 대비" }`를 추가한다. 증감의 단위와 비교 기간은 필수이며, 양수·음수 기호를 함께 표시한다. 증감은 입력값 그대로 표시하며 자동 계산하지 않는다. 빠진 증감값을 0 또는 임의 설명으로 대체하지 않는다.

### 5. 비교표 `figure-comparison`

복제 파일: [`examples/figure-comparison.json`](../examples/figure-comparison.json)

필수: 비교 대상명 `columns` 2-4개, 비교 항목 `rows` 3-6개. 각 행은 `{ "label": "대출 금리", "values": ["변동 금리", "변동 금리", "고정 금리"] }` 형태다. `values`는 열 수와 같은 개수의 문자열이어야 한다. 입력 순서를 유지한다.

대상명은 영문 18자 폭, 행 이름과 셀 내용은 24자 폭 이내다. 숫자 셀도 `"14.2"`처럼 문자열로 입력하고, 해당 행 이름에 `예치금 (십억 달러)`처럼 단위를 명시한다. 4개 대상을 비교할 때만 정해진 조밀한 타이포 규격을 적용한다. 긴 문단을 넣지 않는다.

### 선택형 에디토리얼 비교 시안

`examples/previews/`에는 추세·핵심 지표 두 장의 비교용 입력이 있다. 기본 템플릿과 커버 디자인은 그대로이며, 이 시안은 `--all`에 포함하지 않는다.

```bash
.venv/bin/python render.py examples/previews/figure-data-editorial.json
.venv/bin/python render.py examples/previews/figure-metrics-editorial.json
```

시안 JSON의 `variant: "editorial"`은 공통 블루 구분선과 편집형 여백을 적용한다. 선택 `focus_index`는 0부터 시작하는 대상 번호다. 추세의 `0`은 첫 시리즈, 지표의 `0`은 왼쪽 위 카드다. 생략하면 아무 대상도 자동으로 강조하지 않는다. 음수, 범위를 벗어난 번호, 문자열·불리언 번호는 오류다.

선택 시리즈만 블루와 굵은 선·끝점·큰 숫자로 강조하고 비교 시리즈는 회색과 선 패턴으로 구분한다. 지표는 선택 카드 하나에만 블루 바탕과 흰색 텍스트를 적용한다. 원본 수치, 단위, 날짜, 출처를 변경하거나 다른 위치에 반복하지 않는다. 두 시안은 기존 예제와 같은 데이터를 사용하므로 디자인만 비교할 수 있다.

현재 지원 범위는 `figure-data`의 `line`과 `figure-metrics`다. 다른 템플릿에는 `variant`를 지정하지 않는다.

### 확정 키컬러와 이전 비교 시안

2026.09.11 공식 키컬러를 **UNIT TX Blue `#0064FF`로 확정**했다. 밝은 10색 비교판의 10번 블루이며, 공식 커버·데이터·프레임워크의 강조색을 이 색으로 통일한다.

공식 제작은 `examples/*.json`을 복제하고 `accent`와 `palette_preview`를 생략한다. 기본 렌더러와 공식 예제는 이미 같은 블루를 사용한다. 데이터 시리즈 구분용 보조 블루·중립색, 흑백 심볼·워드마크·날짜, 어두운 커버의 차콜 그라데이션과 외부 프로젝트 원본 이미지는 기존 규칙을 유지한다.

선택한 블루의 커버·추세 비교 샘플은 아래 명령으로 확인할 수 있다.

```bash
.venv/bin/python render.py examples/previews/palettes/blue-cover.json
.venv/bin/python render.py examples/previews/palettes/blue-trend.json
```

다른 19색과 10색·20색 비교판은 [이전 색상 비교 기록](PALETTE_STUDIES.md)으로 분리했다. `examples/previews/palettes/`는 기존 출력 재현을 위한 보관용이며 `--all`에는 포함하지 않는다. 색상 비교 옵션은 과거 입력 호환을 위해 남아 있지만 다른 색상은 공식 발행에 사용하지 않는다.

## 프레임워크 필드

`figure-framework`는 3-5개의 `nodes`를 순서대로 배치한다. 각 노드는 짧은 `title`과 한 문장 `body`를 가진다. 마지막 결론은 선택 필드 `summary`에 쓴다.

```json
{
  "template": "figure-framework",
  "slug": "onchain-payment-framework",
  "title": "온체인 결제는 세 개의 연결된 레이어로 완성된다",
  "source": "UNIT TX Research · conceptual framework",
  "date": "2026.09.01",
  "nodes": [
    {"key": "INTENT", "title": "결제 의도", "body": "사용자가 거래를 시작한다."},
    {"key": "SETTLEMENT", "title": "온체인 정산", "body": "네트워크가 거래를 확정한다."},
    {"key": "OFFRAMP", "title": "수취와 환전", "body": "수취인이 자산을 보유하거나 환전한다."}
  ],
  "summary": "라우팅과 환전 마찰을 줄일수록 일반 결제 경험에 가까워진다."
}
```

## 차트 선택

- 시간에 따른 추세는 `figure-data`의 `line`을 쓴다.
- 항목별 크기 비교에는 `figure-ranking`을 쓴다.
- 전체에서 차지하는 비중은 `figure-composition`, 수치 요약은 `figure-metrics`, 구조와 조건 비교는 `figure-comparison`을 쓴다.
- 파이, 도넛, 3D 차트는 지원하지 않는다. 작은 화면에서 비교가 어렵고 장식적 왜곡이 크기 때문이다.
- 추세 차트는 마지막 값만 직접 표시한다. 나머지 데이터는 축과 선으로 읽는다.
- 시리즈가 두 개 이상이면 블루 계열 색상뿐 아니라 실선과 점선도 함께 사용한다.

## 글자와 안전 여백

- 글꼴: SUIT Variable 한 종류
- 본문과 설명: 500
- 라벨, 메타데이터, 날짜: 600
- 제목과 UNIT TX 워드마크: 800
- 커버 제목: 67-68px, 최대 두 줄, 한 줄당 한글 15자 또는 영문 30자 폭 이내
- 커버 부제: 28-29px
- 데이터 5종 제목: 56px
- 데이터 축, 범례, 출처, 날짜: 26px
- 데이터 지표 값: 78px, 비교표 본문: 28px (4개 대상은 26px)
- 프레임워크 노드 제목: 35px
- 데이터 5종 외곽 여백: 가로 88px, 제목 상단 80px, 하단 푸터는 6% 고정

템플릿이 자동으로 글자를 계속 줄이지 않도록 제목 길이를 검증한다. 긴 제목은 중요한 말을 앞으로 옮겨 직접 두 줄로 나눈다.

## 제작 순서

1. 가장 가까운 `examples/*.json`을 복제한다.
2. `slug`, `category`, 제목, 본문, 날짜, 출처와 데이터를 바꾼다.
3. 로컬 이미지가 필요하면 JSON 파일 하위 경로에 저장하고 `hero_image`를 지정한다.
4. 한 장을 렌더해 제목 줄바꿈과 데이터 라벨을 확인한다.
5. 테스트와 전체 렌더를 실행한다.
6. Substack 업로드 전 실제 출처와 기준일을 다시 확인한다.

## 프리퍼블리시 체크리스트

- 제목이 한 장에서 하나의 주장만 전달하는가?
- 커버 제목이 두 줄을 넘지 않는가?
- 수치와 단위가 원문 데이터와 일치하는가?
- 출처와 기준일이 보이는가?
- 범례 없이도 시리즈를 구분할 수 있는가?
- 모바일 폭으로 축소해도 핵심 수치가 읽히는가?
- 로고에 흰색 또는 검정 사각형이 보이지 않는가?
- 외곽 6% 안으로 핵심 텍스트가 들어오지 않았는가?
- 날짜가 왼쪽 아래, 공식 로고가 오른쪽 아래에 한 번씩만 있는가?
