---
target: 예시 채널 2026년 영상 6편
kind: youtube
question: 이 채널은 박스를 쓰는가
date: 2026-10-13
snapshot: <영상 ID 목록>
status: closed
---

## 질문 체크리스트

| id | 질문 | 필요한 증거 | 상태 |
|---|---|---|---|
| Q1 | 박스를 쓰는가 | 프레임 | answered |
| Q2 | 어떤 편집기를 쓰는가 | 진술 + 화면 | unresolved |
| Q2 | 중복 id | | done |

## 발견

| id | 주장 | 상태 | 권위 | 증거 | 범위 | 한계 |
|---|---|---|---|---|---|---|
| F1 | 이 채널은 박스를 안 쓴다 | observed | replay | evidence/frames.json | 전체 채널 | |
| F2 | Vrew 로 편집한다 | observed | inference | 본인 진술 | | |
| F3 | 자막은 한 줄이다 | derived | artifact | | 6편 | |
| F4 | 키워드 칩이 없는 것은 미니멀 취향 때문이다 | inferred | inference | 프레임 시트 | 6편 | |

## 재구성 의무

| id | 성질 | 합격 조건 | 검증기 | 권위 | 상태 |
|---|---|---|---|---|---|
| O1 | 자막 높이 | 81 px ± 5 | | artifact | pass |
