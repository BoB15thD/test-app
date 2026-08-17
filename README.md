# BoB 15기 — GitHub 보안 통제 실습

> **제한시간 30분 · 4인 1조**
> 이 리포지토리에는 의도적으로 심어둔 보안 취약점이 있습니다.

---

## 시나리오

여러분은 A사의 보안팀입니다. 개발팀 리포에서 보안 스캔 결과 취약점이 발견됐습니다.

**아무나 코드를 고쳐서 바로 넣을 수 없도록 통제를 세운 뒤**, 그 절차를 지켜서 취약점을 수정하세요.

---

## 미션 체크리스트

아래 7개를 **모두 완료**한 조는 손을 드세요.

| # | 계층 | 미션 |
|---|---|---|
| 1 | 개인 | 조원 **전원**이 개인 계정에 2FA 활성화 |
| 2 | Enterprise | Enterprise 설정에서 **2FA 전사 강제** 활성화 |
| 3 | Organization | Org 생성 → 조원 **전원 초대 및 수락** |
| 4 | Organization | **Security Configuration** 생성 (Secret Scanning + Push Protection) → **신규 리포 자동 적용** ON |
| 5 | Organization | **Org Ruleset** 생성 — `test-*` 패턴 리포에 **PR 필수 + 승인 1명** |
| 6 | Repository | 이 리포를 **`test-app`** 이름으로 fork → **코드 스캔 활성화** → 알림 확인 → 취약점 **2개 이상** 수정 |
| 7 | 통합 | 수정을 **PR로 올려 다른 조원의 승인**을 받아 머지 |

### 진행 순서 주의

- **1번을 전원이 끝낸 뒤에 2번**을 하세요. 순서가 바뀌면 2FA 미설정자는 접근이 차단됩니다.
- **4번과 5번은 서로 다른 사람이 동시에** 진행하세요. 둘 다 Org 설정이지만 메뉴가 다릅니다.
- **6번의 리포 이름은 반드시 `test-app`** 으로 하세요.

---

## 먼저 — fork한 리포에서 코드 스캔을 켜세요

**fork에는 스캔 설정이 따라오지 않습니다.** 코드는 복사되지만 스캔은 리포 설정이라 각자 켜야 합니다.

> **내 `test-app` 리포 → Security 탭 → Code scanning → Set up → Default → Enable CodeQL**

3번 클릭이면 끝나고, 켜는 즉시 스캔이 시작됩니다. 완료까지 보통 2~4분 걸리며 Actions 탭에서 진행 상황을 볼 수 있습니다.

스캔이 끝나면 **Security 탭 → Code scanning alerts** 에 알림이 뜹니다. 아무것도 안 보이면 아직 도는 중입니다.

---

## 취약점 수정 방법

`app/main.py` 에 5개의 취약점이 있습니다. 어디에 있는지는 알려주지 않습니다 — **스캔 결과로 찾으세요.**

### 수정 힌트

**SQL 인젝션** — 문자열을 이어 붙이지 말고, 파라미터 바인딩을 사용하세요.

```python
# 취약한 코드
query = "SELECT * FROM users WHERE id = '" + user_id + "'"
cursor.execute(query)

# 안전한 코드
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

**커맨드 인젝션** — `shell=True` 를 쓰지 말고, 인자를 리스트로 전달하세요.

```python
# 취약한 코드
subprocess.run("ping -c 1 " + host, shell=True)

# 안전한 코드
subprocess.run(["ping", "-c", "1", host], shell=False)
```

**경로 조작** — 사용자 입력이 상위 디렉터리로 벗어나지 못하도록 검증하세요.

```python
# 안전한 접근 예시
import os
base = "/var/app/logs"
path = os.path.realpath(os.path.join(base, filename))
if not path.startswith(base + os.sep):
    raise ValueError("잘못된 경로입니다")
```

---

## 수정 후 확인

1. 수정 내용을 새 브랜치에 커밋하고 PR을 생성합니다.
2. **다른 조원**이 PR을 승인합니다. (본인 PR은 본인이 승인할 수 없습니다)
3. 머지 후 Security 탭에서 해당 알림이 **자동으로 닫히는지** 확인합니다.

> 머지 버튼이 눌리지 않는다면, 5번 미션이 제대로 적용되었다는 뜻입니다. 조원의 승인을 받으세요.

---

## 마무리 질문

미션을 마쳤다면, 조원끼리 아래 질문에 답해 보세요.

- 왜 승인 없이는 머지가 되지 않았는가?
- 2FA를 Organization이 아니라 Enterprise에 건 이유는?
- 4번과 5번은 둘 다 Org 설정인데, 왜 서로 다른 메뉴에 있는가?

---

## 참고

- 실습이 끝나면 생성한 리포지토리와 Organization은 삭제하세요.
- 이 코드는 교육 목적으로만 사용하며, 실제 서비스에 배포하지 마세요.


- 0817_test
