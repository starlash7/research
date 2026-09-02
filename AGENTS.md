# UNIT TX Research Image Rules

이 저장소는 UNIT TX가 Substack 리서치에 사용하는 이미지 템플릿과 렌더러를 관리한다. 모든 변경은 아래 규칙과 [`docs/IMAGE_SYSTEM.md`](docs/IMAGE_SYSTEM.md)를 따른다.

## 고정 규격

- 메인 커버 `cover-*`: 1440×756px
- 본문 와이드 `figure-framework`: 1440×810px
- 본문 데이터 `figure-data`: 1440×1200px
- 템플릿 안에서 캔버스 크기를 임의로 바꾸지 않는다.
- 핵심 텍스트와 로고는 사방 6% 안전 여백 안쪽에 둔다.

## 브랜드

- `assets/unit-tx-logo.png`가 유일한 공식 심볼이다.
- 로고를 다시 그리거나 비율, 간격, 형태를 바꾸지 않는다.
- 밝은 배경에는 검정, 어두운 배경에는 흰색으로만 표시한다.
- 기본 글꼴은 저장소에 포함한 Pretendard Variable이다.
- 밝은 계열의 기본 강조색은 UNIT TX blue `#2F6BFF` 하나다. 다른 블루 계열은 데이터 시리즈를 구분할 때만 쓴다.
- 어두운 계열은 deep navy 바탕의 blueprint grid와 signal map을 사용한다. 메탈 구체나 장식용 3D 오브젝트를 기본 요소로 사용하지 않는다.

## 카피와 데이터

- 커버 제목은 최대 두 줄이며 강제 줄바꿈은 한 번만 허용한다. 한 줄은 한글 15자 또는 영문 30자 폭 이내로 쓴다.
- 장식용 문구보다 구체적인 주장과 대상이 드러나는 제목을 쓴다.
- 수치가 들어간 이미지는 `source`와 `date`를 반드시 표시한다.
- 단위, 범례, 기준 시점 없이 차트를 만들지 않는다.
- 예시 수치는 반드시 `Example data · replace before publishing`으로 표시한다.
- 색상만으로 상승, 하락, 시리즈 차이를 전달하지 않는다. 텍스트나 기호를 함께 쓴다.
- 이미지 안의 가시적 카피에는 em dash와 en dash를 사용하지 않는다. 범위와 구분에는 일반 하이픈을 쓴다.

## 자산과 출력

- 모든 이미지와 폰트는 로컬 자산으로 저장한다. 렌더 중 원격 URL을 요청하지 않는다.
- 반복 제작 시 HTML을 직접 수정하지 말고 `examples/*.json`과 같은 입력 JSON을 복제해 편집한다.
- slug는 영문 소문자, 숫자, 하이픈만 사용한다.
- 생성물은 `out/`에 두며 템플릿, JSON 입력, 테스트만 커밋한다.
- 실행 명령은 `.venv/bin/python render.py <input.json>` 또는 `.venv/bin/python render.py --all`이다.

## 완료 기준

- `python -m unittest discover -s tests -v`가 통과해야 한다.
- 실제 PNG를 렌더하고 `sips`로 픽셀 크기를 확인한다.
- 원본 크기로 열어 잘림, 겹침, 의도하지 않은 줄바꿈, 로고 사각 배경을 확인한다.
- 데이터 카드에서는 출처, 날짜, 단위, 범례가 모바일 축소 상태에서도 식별 가능해야 한다.
