---
target: <대상 이름과 판: 예) 채널 이름 최근 23편 (2024-01~2026-10) / 앱 이름 7.37.1>
kind: product | youtube | paper | business
question: <사용자가 물은 것, 한 줄>
date: YYYY-MM-DD
snapshot: <대상을 고정한 방법: sha256, URL + 수집일, 영상 ID 목록 파일, arXiv 판>
status: open | closed
---

# <제목>

## 질문 체크리스트

| id | 질문 | 필요한 증거 | 상태 |
|---|---|---|---|
| Q1 | | | unresolved |

상태: `answered` / `partial` / `unresolved`.

## 발견

| id | 주장 | 상태 | 권위 | 증거 | 범위 | 한계 |
|---|---|---|---|---|---|---|
| F1 | | observed | artifact | evidence/<file> | | |

- 상태: `observed` / `derived` / `inferred` / `unknown`.
- 권위: `artifact` / `replay` / `history` / `external` / `statement` / `inference`.
- 증거: 케이스 폴더 기준 상대 경로, 수집일이 붙은 URL, 영상 ID + 시각, 쪽·식 번호.
- 범위: 무엇을 어디까지 봤는가. "없다·0개·안 쓴다" 같은 부정 주장은 반드시 범위에 숫자(편 수, 날짜, 파일 수, 판)를 쓴다.

## 미해결

| id | 질문 | 필요한 권위 | 다음 탐침 |
|---|---|---|---|

질문 칸은 체크리스트 ID 로 시작한다: `(Q3) ...`. 닫힌 장부(`status: closed`)에서는 `unresolved` 인 질문마다 이 표에 한 줄이 있어야 한다.

## 재구성 의무

만들 것이 없으면 이 절을 지운다.

| id | 성질 | 합격 조건 | 검증기 | 권위 | 상태 |
|---|---|---|---|---|---|

상태: `open` / `pass` / `fail`. `pass` 는 권위가 `replay` 일 때만 쓴다.

## 결론

체크리스트 순서대로, 각 답이 어느 발견(F#)에 기대는지 적는다.
