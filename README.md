# channel-kit

유튜브 영상에서 보여 드린 방법을 Claude Code 에 바로 설치해서 쓸 수 있게 묶은 플러그인 모음입니다.
에피소드마다 플러그인이 하나씩 있습니다. 가입이나 이메일 없이 무료입니다.

## 설치

Claude Code 안에서 이 한 줄을 입력하세요.

```
/plugin marketplace add juhyunchoi-mech/channel-kit
```

그다음 쓰고 싶은 플러그인을 설치합니다.

```
/plugin install rule-meter@channel-kit
/plugin install edit-teardown@channel-kit
```

터미널에서 하셔도 됩니다: `claude plugin marketplace add juhyunchoi-mech/channel-kit`, 그리고
`claude plugin install rule-meter@channel-kit`.

설치한 뒤에는 Claude 에게 그냥 말로 부탁하면 됩니다. 이름으로 직접 부르고 싶으면 `/rule-meter:rule-meter`,
`/edit-teardown:edit-teardown` 처럼 입력하세요.

## 들어 있는 것

| 에피소드 | 플러그인 | 하는 일 |
|---|---|---|
| EP01 | `rule-meter` | CLAUDE.md 에 "이건 쓰지 마"라고 적어 둔 규칙을 Claude 가 실제로 지키는지, 내 대화 기록에서 주 단위로 셉니다 |
| EP04 | `edit-teardown` | 유튜버의 편집을 뜯어보는 방법입니다. 질문 목록부터 쓰고, 발견마다 근거를 붙이고, "없다"는 말에는 어디까지 봤는지 적고, 측정 도구는 내 영상으로 먼저 검증합니다 |

### rule-meter (EP01)

이렇게 말해 보세요. "내 CLAUDE.md 규칙 중에 하나 골라서 잘 지켜지는지 재 줘."

- Claude Code 가 내 컴퓨터에 남기는 대화 기록(`~/.claude/projects/`)만 읽고, 개수만 출력합니다.
  어디로도 보내지 않습니다.
- 기본으로 세는 것은 em dash(`—`)입니다. `TODO` 처럼 금지한 다른 문자열도 셀 수 있습니다.
- Claude Code 는 기본 설정에서 30일이 지난 대화 기록을 지웁니다. 그래서 보통 최근 한 달 정도만 보입니다.
- 스크립트만 따로 쓰고 싶으면 `plugins/rule-meter/skills/rule-meter/scripts/cc_rule_meter.py` 를
  `python3 cc_rule_meter.py --marker "TODO"` 처럼 실행하면 됩니다.

### edit-teardown (EP04)

이렇게 말해 보세요. "이 유튜버가 자막 강조를 어떻게 하는지 내 영상이랑 같은 기준으로 비교해 줘."

- 앱을 뜯어보는 도구 [REA](https://github.com/morluto/rea)의 일하는 방식을 영상 편집 분석에 옮긴 것입니다.
  앱이나 웹사이트를 뜯어보려면 REA 를 직접 설치하세요.
- 장부 양식(`templates/ledger.md`)과 장부 형식 검사기(`scripts/ledger_check.py`)가 들어 있습니다.
  검사기는 형식만 봅니다. 발견이 맞는지는 근거 파일을 열어 봐야 압니다.
- **영상에서 쓴 측정 스크립트 세 개는 들어 있지 않습니다.** 자막 강조 횟수, 카드 전환 길이, 카드 안 이동
  길이를 쟀던 스크립트는 한 채널의 카드 배치와 제 편집 도구에 맞춰져 있어서, 다른 영상에 그대로 쓰면
  숫자가 틀립니다. 대신 Claude 가 여러분의 질문에 맞는 측정 스크립트를 만들고, 정답을 아는 여러분 영상에
  먼저 돌려 검증한 다음에 쓰도록 되어 있습니다.
- 필요한 도구: `python3`, `ffmpeg`, `yt-dlp`. 경우에 따라 `opencv-python`, `numpy` 도 씁니다.
  설치는 Claude 가 먼저 물어봅니다.
- 다른 사람 영상을 내려받아도 되는지는 플랫폼 약관을 보고 직접 판단하세요. 내려받은 영상, 프레임,
  자막은 분석용으로만 두고 다시 올리지 마세요. 편집 방식을 참고하는 것은 괜찮지만, 남의 대본이나
  화면, 썸네일, 목소리를 가져오면 안 됩니다.

## 업데이트와 삭제

- 업데이트: `/plugin marketplace update channel-kit`
- 삭제: `/plugin uninstall rule-meter@channel-kit`, 마켓플레이스까지 지우려면
  `/plugin marketplace remove channel-kit`

## 폴더 구조

```
.claude-plugin/marketplace.json     플러그인 목록
plugins/rule-meter/                 EP01
plugins/edit-teardown/              EP04
```

새 에피소드에서 나눠 드릴 것이 생기면 `plugins/` 아래에 하나씩 늘어납니다.
