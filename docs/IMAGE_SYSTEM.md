# UNIT TX Research Image System

UNIT TX의 Substack 커버와 본문용 리서치 이미지를 JSON에서 재현 가능한 PNG로 만드는 시스템이다. 사람이 매번 좌표를 조정하는 대신, 내용과 데이터만 입력하고 동일한 디자인 규칙으로 렌더한다.

## 출력 형식

| 템플릿 | 크기 | 용도 |
| --- | ---: | --- |
| `cover-editorial` | 1440×756 | 기본 리서치 커버, 밝은 배경 |
| `cover-object` | 1440×756 | 프로젝트 또는 프로토콜 중심 커버, 어두운 배경 |
| `figure-framework` | 1440×810 | 구조도, 단계, 트랜잭션 흐름 |
| `figure-data` | 1440×1200 | 차트와 핵심 수치 |

커버는 Substack 소셜 프리뷰의 1200×630 비율과 같다. 1440px 폭은 본문과 이메일에서 축소될 때 한글과 얇은 선이 선명하게 남도록 선택했다.

## 디자인 원칙

- Design variance 6: 커버는 좌우 비대칭 구성을 쓰고 데이터 카드는 정렬을 우선한다.
- Motion intensity 1: 결과물이 정적 PNG이므로 애니메이션을 사용하지 않는다.
- Visual density 5: 한 장에 하나의 주장만 두고 근거와 출처는 생략하지 않는다.
- 테마는 이미지 한 장 안에서 바꾸지 않는다.
- 모서리 반경은 정보 카드에만 18px로 통일한다. 커버의 장식 요소는 원형 또는 캡슐만 쓴다.
- 강조색은 `#E84B18` 하나를 기본으로 한다. 상승과 하락 색상은 차트 의미가 있을 때만 사용한다.
- 배경은 `#F4F3EF`, 전경은 `#0B0C0D`를 기본으로 하며 순백과 순흑의 강한 대비를 피한다.

## 설치

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
```

Pretendard Variable은 SIL Open Font License 1.1로 배포되는 오픈 소스 글꼴이다. 저장소에는 렌더 재현성을 위해 WOFF2 파일만 포함한다. 원 프로젝트와 라이선스는 <https://github.com/orioncactus/pretendard>에서 확인할 수 있다.

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
| `template` | 템플릿 이름 | 위 네 이름 중 하나 |
| `slug` | 결과 파일명 | 영문 소문자, 숫자, 하이픈 |
| `title` | 핵심 주장 | 커버는 최대 두 줄 |
| `date` | 기준일 | `YYYY.MM.DD` 권장 |
| `accent` | 선택 강조색 | `#RRGGBB`, 생략 시 UNIT TX orange |

커버는 `eyebrow`, `subtitle`, 선택 `author`를 추가한다. `cover-object`는 JSON과 같은 폴더 아래의 로컬 파일을 `hero_image`로 지정할 수 있다. 경로가 없으면 UNIT TX 심볼에서 파생한 CSS 오브젝트가 표시된다.

## 데이터 차트 필드

`figure-data`는 `source`, `chart`, `takeaways`가 필수다. `chart.type`은 `line` 또는 `bar`, `labels`는 2-12개, `series`는 1-3개다. 각 시리즈의 `values` 수는 `labels` 수와 같아야 한다.

```json
{
  "template": "figure-data",
  "slug": "token-survival",
  "title": "상위 토큰의 생존율은 시간이 갈수록 낮아진다",
  "source": "Example data · replace before publishing",
  "date": "2026.09.01",
  "chart": {
    "type": "line",
    "unit": "%",
    "labels": ["1Y", "2Y", "3Y"],
    "series": [
      {"name": "최초 진입 기준", "values": [92.0, 78.0, 63.0]}
    ]
  },
  "takeaways": [
    {"label": "표본", "value": "1,539 tokens"}
  ]
}
```

## 프레임워크 필드

`figure-framework`는 3-5개의 `nodes`를 순서대로 배치한다. 각 노드는 짧은 `title`과 한 문장 `body`를 가진다. 마지막 결론은 선택 필드 `summary`에 쓴다.

## 제작 순서

1. 가장 가까운 `examples/*.json`을 복제한다.
2. `slug`, 제목, 본문, 날짜, 출처와 데이터를 바꾼다.
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

