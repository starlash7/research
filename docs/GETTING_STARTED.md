# 처음 clone한 사람을 위한 제작 가이드

이 저장소는 자료를 정해진 JSON 형식에 넣으면 UNIT TX 디자인의 PNG를 만드는 도구다. HTML·CSS를 수정하거나 로고·폰트를 따로 설치할 필요가 없다.

처음에는 설치를 한 번 하고, 이후에는 **예제 복제 → 내용·이미지 교체 → 렌더 → PNG 확인**만 반복한다. 엑셀·PDF의 데이터를 자동으로 읽거나 리서치 내용을 작성해 주는 도구는 아니다.

## 1. 준비하고 clone하기

아래 절차는 macOS 기준이다. macOS / Python 3.9.6에서 실행을 확인했으며, Windows·Linux는 별도 실기 검증을 하지 않았다.

필요한 것은 Git, Python 3.9 이상, 일반 텍스트를 편집할 수 있는 편집기다. 터미널에서 버전을 확인한다.

```bash
git --version
python3 --version
```

명령을 찾을 수 없거나 Python이 3.9 미만이면 먼저 설치·업데이트한다. 저장소를 보관할 폴더에서 아래 명령을 실행한다.

```bash
git clone https://github.com/starlash7/research.git
cd research
```

이미 clone했다면 다시 clone하지 않고 기존 `research` 폴더로 이동한다. 이후의 모든 명령은 `render.py`와 `requirements.txt`가 있는 이 폴더에서 실행한다. JSON을 편집기에서 여는 것과 터미널의 현재 폴더를 바꾸는 것은 별개다.

## 2. 최초 설치와 샘플 확인

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
.venv/bin/python render.py --all
```

`.venv`는 이 저장소 전용 Python 환경이고, Chromium은 HTML을 PNG로 만드는 데 사용한다. 위처럼 실행 파일의 경로를 직접 쓰므로 가상환경을 따로 활성화할 필요는 없다. 최초 설치에는 인터넷 연결이 필요하고 렌더링에는 저장소의 로컬 자산을 사용한다.

새 clone에서 `[done] 8 images`가 나오면 기본 커버 2종, 프레임워크 1종, 데이터 5종이 생성된 것이다. Finder에서 결과 폴더를 연다.

```bash
open out
```

`bitcoin-use-cover.png`, `bitcoin-reserve-cover.png`, `lending-trend-example.png` 등을 열어 본다. `out/`의 PNG가 최종 이미지이며 HTML과 `manifest.json`은 업로드하지 않는다.

## 3. 만들 이미지에 맞는 예제 고르기

| 만들 내용 | 복제할 파일 | 주로 교체할 내용 |
| --- | --- | --- |
| 밝은 커버 | [cover-editorial.json](../examples/cover-editorial.json) | 분류, 제목, 부제, 프로젝트 이미지 |
| 어두운 그라데이션 커버 | [cover-object.json](../examples/cover-object.json) | 분류, 제목, 부제, 프로젝트 이미지 |
| 흐름·구조 설명 | [figure-framework.json](../examples/figure-framework.json) | `nodes` 3-5개, 선택 `summary` |
| 시간에 따른 추세 | [figure-data.json](../examples/figure-data.json) | `chart.labels`, `chart.series`, `chart.unit` |
| 항목별 순위·크기 | [figure-ranking.json](../examples/figure-ranking.json) | `items` 2-8개, `unit` |
| 100% 구성비 | [figure-composition.json](../examples/figure-composition.json) | `categories`, `groups`, `unit: "%"` |
| 핵심 지표 4개 | [figure-metrics.json](../examples/figure-metrics.json) | `metrics` 4개, 선택 `change` |
| 대상별 비교표 | [figure-comparison.json](../examples/figure-comparison.json) | `columns` 2-4개, `rows` 3-6개 |

공통으로 `slug`, `title`, `date`를 바꾸고, 본문 이미지에는 실제 `source`도 입력한다. 템플릿별 입력 제한은 [상세 명세](IMAGE_SYSTEM.md)에서 확인한다. `examples/previews/`는 비교 시안 보관용이므로 처음 제작할 때는 위 파일을 사용한다.

## 4. 내 커버 한 장 만들기

원본 예제를 보존하고 복사본을 만든다. `cp -n`은 같은 이름의 파일이 이미 있으면 덮어쓰지 않는다.

```bash
cp -n examples/cover-editorial.json examples/my-cover.json
```

편집기에서 `examples/my-cover.json`을 열고 다음 내용으로 저장한다. 코드 블록의 앞뒤에 있는 백틱은 파일에 넣지 않는다.

```json
{
  "template": "cover-editorial",
  "slug": "my-cover",
  "category": "BITCOIN RESEARCH",
  "title": "비트코인 수요는\n어떻게 변했는가",
  "subtitle": "온체인 거래와 보유 구조의 변화를 살펴본다.",
  "date": "2026.09.11",
  "hero_image": "art/bitcoin-logo.png"
}
```

이 예시는 저장소에 들어 있는 원본 BTC 이미지를 사용한다. 본인 자료로 바꿀 때 다음을 확인한다.

- `slug`는 결과 파일 이름이다. JSON 파일명만 바꾸고 `slug`를 그대로 두면 이전 PNG를 덮어쓴다. 새 이미지마다 고유한 영문 소문자·숫자·하이픈 이름을 쓴다.
- `category`는 왼쪽 위 분류이며 영문 24자 폭 이내로 쓴다.
- `title`의 `\n`은 줄바꿈 한 번이다. 최대 두 줄, 한 줄당 한글 15자 또는 영문 30자 폭 이내로 쓴다.
- `subtitle`은 필수 부제다. 짧고 구체적인 한 문장으로 쓰고 제목을 반복하지 않는다.
- `date`는 실제 기준일로 바꾼다. 왼쪽 아래 날짜에 반영된다.

저장한 뒤 렌더하고 결과를 연다.

```bash
.venv/bin/python render.py examples/my-cover.json
open out/my-cover.png
```

어두운 커버를 만들려면 복사본의 `template`을 `cover-object`로 바꾸고 `slug`도 `my-dark-cover`처럼 새 이름으로 바꾼다. 같은 렌더 명령을 실행하면 `out/my-dark-cover.png`가 생성된다.

### 프로젝트 이미지 바꾸기

Finder에서 사용할 PNG·JPG·WebP 파일을 `examples/art/`에 넣는다. 예를 들어 `project-logo.png`를 넣었다면 `hero_image` 값을 `art/project-logo.png`로 바꾼다.

경로는 저장소 루트가 아니라 **입력 JSON 파일이 있는 폴더 기준**이다. 따라서 `examples/my-cover.json`에서 `art/project-logo.png`는 `examples/art/project-logo.png`를 가리킨다. JSON을 다른 폴더로 옮기면 이미지도 그 폴더 또는 그 하위 폴더에 두고 경로를 맞춘다.

- 원격 URL, 절대 경로, `../`로 입력 폴더 밖을 가리키는 경로는 지원하지 않는다. SVG도 입력 이미지로 지원하지 않는다.
- 로고형 이미지는 투명 배경 PNG를 준비하면 사각 배경이 남지 않는다. 템플릿이 원본 이미지의 배경을 지워 주지는 않는다.
- `hero_image` 필드를 생략하면 밝은 커버에는 블루 원형, 어두운 커버에는 빈 공간이 남는다. 빈 문자열을 넣지 말고 필드 자체를 제거한다.
- 오른쪽 아래 공식 UNIT TX 로고는 자동으로 들어간다. `assets/unit-tx-logo.png`를 프로젝트 로고로 교체하지 않는다.

## 5. 내 데이터 차트 만들기

```bash
cp -n examples/figure-data.json examples/my-trend.json
```

`examples/my-trend.json`을 열고 아래의 작은 예제로 바꿔 본다. **다음 수치는 연습용 가상 데이터**다.

```json
{
  "template": "figure-data",
  "slug": "my-trend",
  "title": "월별 거래 규모 변화",
  "source": "Example data · replace before publishing",
  "date": "2026.09.11",
  "period": "2026.03 - 2026.08 · 월말 기준",
  "chart": {
    "type": "line",
    "unit": "십억 달러",
    "labels": ["26.03", "26.04", "26.05", "26.06", "26.07", "26.08"],
    "series": [
      {"name": "시장 A", "values": [11, 14, 12, 18, 22, 25]},
      {"name": "시장 B", "values": [8, 9, 11, 10, 13, 16]}
    ]
  }
}
```

```bash
.venv/bin/python render.py examples/my-trend.json
open out/my-trend.png
```

실제 자료로 바꾸는 순서는 다음과 같다.

1. `title`, `date`, 필요하면 `period`를 바꾼다. `period`는 분석 기간이고 하단 `date`와 별개다.
2. `chart.unit`에 단위를 입력하고 `labels`를 시점 순서대로 적는다. 자동으로 날짜순 정렬하지 않는다.
3. 각 `series`의 `name`과 `values`를 바꾼다. 예를 들어 시점이 6개면 모든 시리즈의 값도 6개여야 한다.
4. 실제 자료와 수치·단위를 확인한 후에만 `source`의 연습용 경고를 실제 출처로 교체한다. 실습 데이터를 그대로 발행하지 않는다.
5. 다시 렌더하고 그래프, 끝점 값, 범례를 원자료와 대조한다.

숫자는 `128400`처럼 쉼표나 따옴표 없이 입력한다. `"128,400"`은 숫자가 아니라 문자열이라 차트에서 거부된다. 비교표의 셀은 예외적으로 문자열을 사용한다. `y_min`, `y_max`는 생략하면 축 범위를 계산하며, 직접 지정한다면 모든 값을 포함해야 한다.

다른 데이터 템플릿도 같은 방식으로 복제해 편집한다. 구성비는 그룹별 합계가 100%여야 하고, 지표 카드는 정확히 4개여야 한다. 지표의 `change`는 자동 계산하지 않으므로 직접 계산한 값·단위·비교 기간을 넣거나 필드를 생략한다.

## 6. 발행 전 확인과 다음 제작

PNG를 원본 크기와 모바일에 가까운 작은 크기로 모두 확인한다.

- 제목·라벨이 잘리거나 겹치지 않는지, 제목이 두 줄을 넘지 않는지 확인한다.
- 수치, 단위, 출처, 기준일이 원자료와 맞는지 확인한다.
- 날짜가 왼쪽 아래, UNIT TX 로고가 오른쪽 아래에 한 번씩 있는지 확인한다.
- 밝은 배경의 날짜는 검정, 어두운 커버의 날짜는 흰색이며 박스·테두리가 없어야 한다.
- 커버는 1440×756, 데이터 5종은 1440×1200, 프레임워크는 1440×810인지 확인한다.

```bash
sips -g pixelWidth -g pixelHeight out/my-cover.png out/my-trend.png
```

확인한 PNG를 Substack의 커버나 본문 이미지로 사용한다. 새 자료를 만들 때는 JSON을 새 이름으로 복제하고 `slug`도 바꾼다. 같은 자료를 수정할 때는 기존 JSON을 편집하고 같은 명령을 다시 실행하면 PNG가 갱신된다. `out/`의 HTML을 직접 고치면 다음 렌더에서 덮어써진다.

색상·폰트·로고·크기·배치는 자동 적용한다. 공식 제작에서는 `accent`, `palette_preview`를 추가하지 않고 기본 UNIT TX Blue `#0064FF`를 유지한다. `templates/`와 `assets/styles.css`를 수정할 필요가 없다.

`--all`은 `examples/` 바로 아래의 모든 JSON을 렌더한다. 직접 추가한 `my-cover.json`과 `my-trend.json`도 포함되므로 파일 개수가 늘면 `[done]`의 숫자도 달라진다. 하위 `examples/previews/`는 포함하지 않는다. 한 장만 수정했다면 해당 JSON 경로로 렌더하면 된다.

템플릿을 업데이트하거나 환경을 다시 설치했다면 아래 검증도 실행한다.

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python render.py --all
```

JSON과 사용한 로컬 원본 이미지는 함께 보관한다. `out/` 생성물과 `.venv/`는 Git에서 제외된다. PNG만 전달할 때는 별도로 첨부하고, 다른 사람이 다시 생성해야 한다면 입력 JSON과 이미지도 함께 전달한다. 비공개 원자료·내부 이미지는 저장소에 올리기 전에 공유 가능 범위를 확인한다.

## 자주 막히는 부분

| 증상 | 확인할 것 |
| --- | --- |
| clone 권한 오류, `Repository not found` | 주소와 GitHub 계정의 저장소 접근 권한을 확인한다. 비공개 저장소라면 초대·인증이 필요하다. |
| `.venv/bin/python` 또는 `render.py`를 찾지 못함 | 터미널이 `research` 폴더인지 확인하고 2단계 설치를 마친다. |
| `No module named jinja2` 또는 `playwright` | `.venv/bin/pip install -r requirements.txt`를 실행하고 시스템 Python 대신 `.venv/bin/python`을 사용한다. |
| 브라우저 실행 파일이 없다는 오류 | `.venv/bin/playwright install chromium`을 실행한다. 패키지를 업데이트한 뒤에도 브라우저 재설치가 필요할 수 있다. |
| JSON 문법 오류 | 일반 텍스트·UTF-8·`.json`으로 저장한다. 큰따옴표 `"`를 사용하고 마지막 항목 뒤의 쉼표, 주석, 복사한 백틱을 제거한다. |
| `slug` 오류 또는 기존 PNG가 바뀜 | `my-cover-20260911`처럼 고유한 이름을 쓴다. 공백·한글·밑줄은 허용하지 않는다. |
| `hero_image 파일을 찾을 수 없습니다` | JSON 기준 상대 경로, 실제 파일명·대소문자·확장자를 확인한다. |
| 제목·수치가 너무 길다는 오류 | 제목을 줄이거나 허용 범위 안에서 두 줄로 나눈다. 수치는 값을 올바르게 환산하고 단위도 함께 바꾼다. CSS의 글자 크기를 줄여 우회하지 않는다. |
| 값 개수·축 범위·구성비 합계 오류 | 라벨 수와 각 값 배열의 길이, 명시한 축 범위, 그룹별 100% 합계를 확인한다. |
| 수정했는데 PNG가 그대로임 | JSON을 저장했는지, 수정한 JSON 경로로 렌더했는지, `slug`에 맞는 PNG를 열었는지 확인한다. |

해결되지 않으면 실행한 명령, 전체 오류 메시지, OS·Python 버전, 민감한 정보를 제거한 입력 JSON을 저장소 관리자에게 전달한다.

설계 규칙은 [AGENTS.md](../AGENTS.md), 전체 필드 계약은 [IMAGE_SYSTEM.md](IMAGE_SYSTEM.md), 저장소의 목표는 [goal.md](../goal.md)를 참고한다.
