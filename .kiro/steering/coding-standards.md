---
inclusion: auto
---

# 코드 생성 품질 가이드

이 프로젝트의 Python 코드 생성 시 반드시 아래 아키텍처 가이드를 준수하세요.

Code like Kent Beck. Must follow SOLID principles:
- **S**ingle Responsibility: 클래스/함수는 하나의 책임만 가진다
- **O**pen/Closed: 확장에는 열려 있고, 수정에는 닫혀 있어야 한다
- **L**iskov Substitution: 하위 타입은 상위 타입을 대체할 수 있어야 한다
- **I**nterface Segregation: 클라이언트가 사용하지 않는 인터페이스에 의존하지 않는다
- **D**ependency Inversion: 구체 구현이 아닌 추상화에 의존한다

DRY (Don't Repeat Yourself): 동일한 로직을 두 곳 이상에 작성하지 않는다. 중복 발견 시 공통 함수/모듈로 추출한다.

## AI 코드 생성 행동 원칙

- **Think Before Coding**: 가정을 명시하고, 불확실하면 질문하고, 혼란스러우면 멈춘다
- **Simplicity First**: 요청하지 않은 기능·추상화·에러 처리를 추가하지 않는다
- **Surgical Changes**: 요청된 부분만 바꾸고 나머지는 건드리지 않는다
- **Goal-Driven Execution**: "기능 추가" 대신 "테스트 통과시키기"처럼 구체적 목표로 변환한다

## 필수 참조 문서

#[[file:pyproject.toml]]

## Git Commit 규칙

### Commit 단위
- 작업한 내용을 **논리적인 작업 묶음**에 따라 분리하여 Commit

### Commit Message 형식
- **Gitmoji**로 시작
- **50자 이내** (영어/한글)
- **첫 글자는 대문자**
- 예시: `✨ Add AWS Cognito authentication support`

### 자주 사용하는 Gitmoji

| Emoji | 코드 | 용도 |
|-------|------|------|
| ✨ | `:sparkles:` | 새 기능 |
| 🐛 | `:bug:` | 버그 수정 |
| ♻️ | `:recycle:` | 리팩토링 |
| 📝 | `:memo:` | 문서 |
| 🔧 | `:wrench:` | 설정 변경 |
| ⬆️ | `:arrow_up:` | 의존성 업그레이드 |
| 🏗️ | `:building_construction:` | 아키텍처 변경 |
| ✅ | `:white_check_mark:` | 테스트 추가 |
| 🔒 | `:lock:` | 보안 관련 |

## 함수 인자 줄바꿈 (인자 2개 이상)

```python
# ✅ 올바름
async def process_audio(
    audio_data: bytes,
    sample_rate: int = 16000,
) -> AudioResult:
    ...

# ❌ 금지
async def process_audio(audio_data: bytes, sample_rate: int = 16000) -> AudioResult:
    ...
```

## Strands Tools — Annotated 사용

```python
from typing import Annotated
from strands import tool

@tool
async def find_destination(
    query: Annotated[str, "검색할 목적지"],
) -> str:
    ...
```

## 금지 사항

- 동기 I/O 호출 (async 컨텍스트 내)
- 하드코딩된 자격 증명
- 전역 상태 변수
- `print()` 디버깅
- 무한 재시도

## 인프라 규칙

- 반드시 Terraform으로 인프라 먼저 생성하고 진행
- 유닛테스트는 꼭 진행하고 넘어갈 것

## 테스트 규칙

- PBT (Property-Based Testing) with Hypothesis (Python) / fast-check (TypeScript)
- Hypothesis의 `@given`과 pytest fixture를 함께 쓸 때 fixture 대신 헬퍼 함수 사용
- 모든 비즈니스 로직에 example-based + PBT 병행
