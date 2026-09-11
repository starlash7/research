# 이전 키컬러 비교 시안 (보관)

2026.09.11 공식 키컬러를 UNIT TX Blue `#0064FF`로 확정했다. 이 문서는 색상 선택 과정의 기록이며 아래의 다른 색상과 실행 예시는 이전 비교판 재현용이다. 공식 제작 규칙은 [이미지 시스템](IMAGE_SYSTEM.md)을 따른다.

마지막 비교안은 **밝고 선명한 10색**으로 좁혔다. 새 비교판의 번호는 01 버밀리언 (`vermillion`), 02 코랄 (`coral`), 03 마젠타 (`magenta`), 04 오렌지 (`orange`), 05 앰버 (`amber`), 06 옐로 (`yellow`), 07 애시드 라임 (`lime`), 08 민트 (`mint`), 09 시안 (`cyan`), 10 UNIT 블루 (`blue`)다. 커버·추세 차트를 2색씩 크게 묶어 비교한다. 이전 20색 비교판과 번호가 다르므로 색 이름과 `palette_preview`로 입력을 찾는다.

네이비·버건디·인디고·포레스트 등 짙은 톤은 당시 비교판에서 제외했다. 아래의 전체 후보와 입력 파일은 이전 시안 재현을 위해 보관하며, 기본 브랜드색과 승인된 커버는 바꾸지 않는다.

`examples/previews/palettes/`의 40개 JSON은 동일한 밝은 커버와 추세 데이터에 20색을 적용하는 비교 시안이다. 색상칩으로만 보였던 코랄·코퍼·인디고·시안도 실제 샘플을 제공한다. 이 비교는 2026.09.11 UNIT TX Blue 확정으로 종료했다. 다른 색상은 공식 제작에 사용하지 않는다. `--all`에는 이 시안들이 포함되지 않는다.

| `palette_preview` | 주요 색면 | 데이터 선 | 작은 강조 텍스트 |
| --- | --- | --- | --- |
| `vermillion` | #E4492D | #E4492D | #B93822 |
| `lime` | #C7F542 | #526B16 | #526B16 |
| `violet` | #7546E8 | #7546E8 | #7546E8 |
| `teal` | #008F86 | #008F86 | #006E67 |
| `magenta` | #D62F8A | #D62F8A | #D62F8A |
| `amber` | #F2B233 | #A86B08 | #8C5800 |
| `burgundy` | #8C2545 | #8C2545 | #8C2545 |
| `forest` | #1D684F | #1D684F | #1D684F |
| `coral` | #F47568 | #CC5045 | #B64037 |
| `copper` | #B76E3C | #B76E3C | #925327 |
| `indigo` | #4338CA | #4338CA | #4338CA |
| `cyan` | #00A6C8 | #00809B | #006E85 |
| `red` | #D7263D | #D7263D | #D7263D |
| `orange` | #F0781E | #C85C10 | #AF4B08 |
| `yellow` | #EBCB20 | #8D7900 | #796700 |
| `olive` | #718044 | #718044 | #5B6833 |
| `mint` | #21B889 | #008763 | #007354 |
| `blue` | #0064FF | #0064FF | #0064FF |
| `navy` | #183153 | #183153 | #183153 |
| `slate` | #64748B | #64748B | #64748B |

이전 20색 비교판 번호는 기존 12색을 유지한다: 01 버밀리언, 02 코랄, 03 앰버, 04 코퍼, 05 마젠타, 06 버건디, 07 바이올렛, 08 인디고, 09 애시드 라임, 10 포레스트 그린, 11 청록, 12 시안. 추가 색은 13 레드, 14 오렌지, 15 옐로, 16 올리브, 17 민트, 18 UNIT 블루, 19 네이비, 20 슬레이트다. 번호와 색 이름은 비교판에만 표시한다.

흑백 심볼, 워드마크, 날짜, SUIT와 규격은 유지한다. 밝은 색은 흰 배경 위의 작은 글자와 얇은 선에 그대로 사용하지 않으며, 같은 계열의 짙은 보조색을 쓴다. 데이터 선은 흰 배경 대비 3 이상, 작은 강조 텍스트는 4.5 이상으로 검증한다. 키컬러는 상승·하락을 의미하지 않는다. 비교용 커버는 프로젝트 이미지 없이 기존 원형 그래픽을 사용하고 모든 후보의 텍스트 왼쪽을 88px 안전 여백에 맞춘다. 색 외의 변수를 통제하기 위해 추가 후보도 기존 시안의 문구, 예시 데이터와 기준일을 그대로 사용한다. 기존 BTC 이미지와 승인된 커버 출력에는 영향을 주지 않는다.

```bash
.venv/bin/python render.py examples/previews/palettes/vermillion-cover.json
.venv/bin/python render.py examples/previews/palettes/vermillion-trend.json
.venv/bin/python render.py examples/previews/palettes/lime-cover.json
.venv/bin/python render.py examples/previews/palettes/lime-trend.json
.venv/bin/python render.py examples/previews/palettes/violet-cover.json
.venv/bin/python render.py examples/previews/palettes/violet-trend.json
.venv/bin/python render.py examples/previews/palettes/teal-cover.json
.venv/bin/python render.py examples/previews/palettes/teal-trend.json
.venv/bin/python render.py examples/previews/palettes/magenta-cover.json
.venv/bin/python render.py examples/previews/palettes/magenta-trend.json
.venv/bin/python render.py examples/previews/palettes/amber-cover.json
.venv/bin/python render.py examples/previews/palettes/amber-trend.json
.venv/bin/python render.py examples/previews/palettes/burgundy-cover.json
.venv/bin/python render.py examples/previews/palettes/burgundy-trend.json
.venv/bin/python render.py examples/previews/palettes/forest-cover.json
.venv/bin/python render.py examples/previews/palettes/forest-trend.json
```

다른 후보도 같은 파일명 규칙을 사용한다. 예를 들어 `mint-cover.json`과 `mint-trend.json`을 각각 렌더하면 된다. 40개 샘플 전체를 렌더하려면 다음을 실행한다.

```bash
for input in examples/previews/palettes/*.json; do
  .venv/bin/python render.py "$input" || break
done
```

`palette_preview`는 `cover-editorial` 또는 `variant: "editorial"`인 `figure-data`에서만 사용하며 `accent`와 동시에 지정할 수 없다. 선택 시리즈는 기존 `focus_index`로 지정한다. 다크 커버 및 나머지 데이터 템플릿으로의 적용은 이번 시안 범위 밖이다.
