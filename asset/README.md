# Session 2: Nuclei Local Lab

이 랩은 `127.0.0.1:8010`에서만 동작하는 nuclei 실습용 서버와 로컬 템플릿 모음이다.

## 1. 서버 실행

```bash
cd nuclei-study
python3 asset/server.py
```

* 예상 결과
```bash
user@host:~/nuclei-study$ python3 asset/server.py 
[*] Nuclei lab listening on http://127.0.0.1:8010

```

* 의미
  - 로컬 실습용 웹 서버를 `127.0.0.1:8010`에 띄운다.
  - 이후 모든 `curl`과 `nuclei` 명령은 이 서버를 대상으로 요청을 보낸다.

다른 터미널에서 먼저 수동 관찰한다.

```bash
curl -i http://127.0.0.1:8010/debug
curl -i http://127.0.0.1:8010/admin
```

* 예상 결과
```text
HTTP/1.0 200 OK
Server: NucleiLab/0.2 
Date: Sat, 09 May 2026 02:41:49 GMT
Content-Type: application/json
X-Powered-By: Express
X-Lab-Target: nuclei-local-training
Set-Cookie: lab_session=guest; HttpOnly; Path=/
X-Debug-Mode: enabled
Content-Length: 137

{
  "app": "AcmeNotes",
  "version": "1.4.2-dev",
  "debug": true,
  "build": "2026.05.09-lab",
  "debug_marker": "debug-panel-enabled"
}HTTP/1.0 302 Found
Server: NucleiLab/0.2 
Date: Sat, 09 May 2026 02:41:49 GMT
Location: /login
X-Redirect-Reason: auth-required
```

* 의미
  - `/debug`는 `200 OK`와 JSON debug 정보를 반환한다.
  - `X-Debug-Mode: enabled`, `"debug": true`, `"version": "1.4.2-dev"`가 이후 nuclei matcher/extractor의 관찰 대상이다.
  - `/admin`은 직접 내용을 보여주지 않고 `302 Found`와 `Location: /login`으로 로그인 페이지 이동을 지시한다.

## 2. 템플릿 검증

```bash
nuclei -validate -t asset/templates/http -duc -ni -nc
```

* 예상 결과
```text

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

                projectdiscovery.io

[VER] Started metrics server at localhost:9092
[INF] All templates validated successfully
```

* 의미
  - `asset/templates/http` 아래 YAML 템플릿들이 nuclei 문법상 유효한지 검사한다.
  - `validate`는 템플릿 로딩/검증 단계라서 실제 취약점 탐지 요청은 수행하지 않는다.

## 3. 핵심 실행

```bash
nuclei -u http://127.0.0.1:8010 -t asset/templates/http/debug-complete-poc.yaml -duc -ni -nc
```

* 예상 결과
```text

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

                projectdiscovery.io

[ERR] Could not read nuclei-ignore file: open ~/.config/nuclei/.nuclei-ignore: no such file or directory
[INF] Current nuclei version: v3.8.0 (unknown) - remove '-duc' flag to enable update checks
[INF] Current nuclei-templates version:  (unknown) - remove '-duc' flag to enable update checks
[INF] New templates added in latest release: 0
[INF] Templates loaded for current scan: 1
[WRN] Loading 1 unsigned templates for scan. Use with caution.
[INF] Targets loaded for current scan: 1
[lab-debug-complete-poc:lab_version] [http] [low] http://127.0.0.1:8010/debug ["1.4.2-dev"]
[INF] Scan completed in 1.487719ms. 1 matches found.
```

* 의미
  - 단일 템플릿 `debug-complete-poc.yaml`만 실행한다.
  - status matcher, header matcher, body matcher가 모두 통과해서 `/debug`가 탐지된다.
  - regex extractor가 body에서 `"version": "1.4.2-dev"`를 뽑아 `lab_version`으로 출력한다.
  - `.nuclei-ignore` 경고와 unsigned template 경고는 현재 로컬 실습 환경에서는 치명적 실패가 아니다.

```bash
nuclei -l asset/inputs/targets.txt -t asset/templates/http -etags dos,dangerous -duc -ni -nc
```

* 예상 결과
```text

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

                projectdiscovery.io

[ERR] Could not read nuclei-ignore file: open ~/.config/nuclei/.nuclei-ignore: no such file or directory
[INF] Current nuclei version: v3.8.0 (unknown) - remove '-duc' flag to enable update checks
[INF] Current nuclei-templates version:  (unknown) - remove '-duc' flag to enable update checks
[INF] New templates added in latest release: 0
[INF] Templates loaded for current scan: 10
[WRN] Loading 10 unsigned templates for scan. Use with caution.
[INF] Targets loaded for current scan: 1
[INF] Templates clustered: 2 (Reduced 1 Requests)
[lab-wordpress-fingerprint] [http] [info] http://127.0.0.1:8010/wp-login.php
[lab-variable-basic-auth-helper] [http] [info] http://127.0.0.1:8010/basic-only
[lab-debug-complete-poc:lab_version] [http] [low] http://127.0.0.1:8010/debug ["1.4.2-dev"]
[lab-dsl-helper-matchers] [http] [info] http://127.0.0.1:8010/debug
[lab-express-powered-by] [http] [info] http://127.0.0.1:8010/
[lab-multi-step-login:session_token] [http] [medium] http://127.0.0.1:8010/api/login ["public-demo-session-token"]
[lab-payload-attack] [http] [info] http://127.0.0.1:8010/api/private [token="public-demo-api-token"]
[INF] Scan completed in 1.055210644s. 7 matches found.
```

* 의미
  - `-l asset/inputs/targets.txt`로 대상 URL을 파일에서 읽는다.
  - `-t asset/templates/http`로 디렉터리 안의 여러 템플릿을 한 번에 로드한다.
  - `-etags dos,dangerous`로 `dos`, `dangerous` 태그 템플릿을 제외한다.
  - `Templates clustered`는 nuclei가 중복 요청을 묶어서 요청 수를 줄였다는 뜻이다.
  - 총 10개 템플릿이 로드됐고, 그중 7개가 실제 응답 조건과 맞아 매치됐다.

## 4. 필터와 프로파일

```bash
nuclei -u http://127.0.0.1:8010 -t asset/templates/http -tags auth -duc -ni -nc
```

* 예상 결과
```text

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

                projectdiscovery.io

[ERR] Could not read nuclei-ignore file: open ~/.config/nuclei/.nuclei-ignore: no such file or directory
[INF] Current nuclei version: v3.8.0 (unknown) - remove '-duc' flag to enable update checks
[INF] Current nuclei-templates version:  (unknown) - remove '-duc' flag to enable update checks
[INF] New templates added in latest release: 0
[INF] Templates loaded for current scan: 5
[WRN] Loading 5 unsigned templates for scan. Use with caution.
[INF] Targets loaded for current scan: 1
[lab-payload-attack] [http] [info] http://127.0.0.1:8010/api/private [token="public-demo-api-token"]
[lab-variable-basic-auth-helper] [http] [info] http://127.0.0.1:8010/basic-only
[lab-multi-step-login:session_token] [http] [medium] http://127.0.0.1:8010/api/login ["public-demo-session-token"]
[INF] Scan completed in 2.744579ms. 3 matches found.
```

* 의미
  - `-tags auth`는 `info.tags`에 `auth`가 들어 있는 템플릿만 선택한다.
  - 5개 auth 템플릿이 로드됐고, 그중 3개가 매치됐다.
  - `header-auth-secret`와 `basic-auth-secret`는 각각 `-H`, `-sf` 입력이 필요한 템플릿이라 이 명령만으로는 매치되지 않는 것이 정상이다.

```bash
nuclei -u http://127.0.0.1:8010 -tp asset/profiles/lab-recommended.yaml -duc -ni -nc
```

* 예상 결과
```text

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

        projectdiscovery.io

[ERR] Could not read nuclei-ignore file: open ~/.config/nuclei/.nuclei-ignore: no such file or directory
[INF] Current nuclei version: v3.8.0 (unknown) - remove '-duc' flag to enable update checks
[INF] Current nuclei-templates version:  (unknown) - remove '-duc' flag to enable update checks
[INF] New templates added in latest release: 0
[WRN] Loading 10 unsigned templates for scan. Use with caution.
[INF] Templates loaded for current scan: 10
[INF] Targets loaded for current scan: 1
[INF] Templates clustered: 2 (Reduced 1 Requests)
[lab-debug-complete-poc:lab_version] [http] [low] http://127.0.0.1:8010/debug ["1.4.2-dev"]
[lab-dsl-helper-matchers] [http] [info] http://127.0.0.1:8010/debug
[lab-wordpress-fingerprint] [http] [info] http://127.0.0.1:8010/wp-login.php
[lab-payload-attack] [http] [info] http://127.0.0.1:8010/api/private [token="public-demo-api-token"]
[lab-express-powered-by] [http] [info] http://127.0.0.1:8010/
[lab-multi-step-login:session_token] [http] [medium] http://127.0.0.1:8010/api/login ["public-demo-session-token"]
[lab-variable-basic-auth-helper] [http] [info] http://127.0.0.1:8010/basic-only
[INF] Scan completed in 1.036671805s. 7 matches found.
```

* 의미
  - `-tp`는 profile YAML을 읽어 템플릿 경로, 포함 태그, 제외 태그를 한 번에 적용한다.
  - 이 profile은 `lab` 태그 템플릿을 실행하되 `dos`, `dangerous` 태그는 제외한다.
  - 템플릿 디렉터리 전체 실행과 비슷하지만, 선택 규칙을 명령줄이 아니라 profile 파일에 넣어 재사용한다.

## 5. 인증과 헤더

```bash
nuclei -u http://127.0.0.1:8010 -t asset/templates/http/header-auth-secret.yaml -H 'X-Lab-Auth: public-demo-api-token' -duc -ni -nc
```

* 예상 결과
```text

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

                projectdiscovery.io

[ERR] Could not read nuclei-ignore file: open ~/.config/nuclei/.nuclei-ignore: no such file or directory
[INF] Current nuclei version: v3.8.0 (unknown) - remove '-duc' flag to enable update checks
[INF] Current nuclei-templates version:  (unknown) - remove '-duc' flag to enable update checks
[INF] New templates added in latest release: 0
[INF] Templates loaded for current scan: 1
[WRN] Loading 1 unsigned templates for scan. Use with caution.
[INF] Targets loaded for current scan: 1
[lab-header-auth-secret] [http] [info] http://127.0.0.1:8010/api/private
[INF] Scan completed in 1.513747ms. 1 matches found.
```

* 의미
  - `-H 'X-Lab-Auth: public-demo-api-token'`가 모든 HTTP 요청에 custom header를 추가한다.
  - 서버의 `/api/private`는 이 헤더가 있을 때만 `200 OK`를 반환한다.
  - matcher가 보호된 API의 성공 응답을 확인해서 `lab-header-auth-secret`가 매치된다.

```bash
nuclei -u http://127.0.0.1:8010 -t asset/templates/http/basic-auth-secret.yaml -sf asset/secrets/basic-auth.yaml -duc -ni -nc
```

* 예상 결과
```text

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

                projectdiscovery.io

[ERR] Could not read nuclei-ignore file: open ~/.config/nuclei/.nuclei-ignore: no such file or directory
[INF] Current nuclei version: v3.8.0 (unknown) - remove '-duc' flag to enable update checks
[INF] Current nuclei-templates version:  (unknown) - remove '-duc' flag to enable update checks
[INF] New templates added in latest release: 0
[INF] Templates loaded for current scan: 1
[WRN] Loading 1 unsigned templates for scan. Use with caution.
[INF] Targets loaded for current scan: 1
[INF] Pre-fetching secrets from authprovider[s]
[lab-basic-auth-secret] [http] [info] http://127.0.0.1:8010/basic-only
[INF] Scan completed in 1.34332ms. 1 matches found.
```

* 의미
  - `-sf asset/secrets/basic-auth.yaml`가 nuclei secret file을 읽는다.
  - secret file의 `basicauth` 설정이 대상 도메인에 맞으면 nuclei가 Basic Authorization 헤더를 자동으로 붙인다.
  - `/basic-only`가 인증 성공 응답을 반환해서 템플릿이 매치된다.

## 6. 복잡한 요청, extractor, helper

```bash
nuclei -u http://127.0.0.1:8010 -t asset/templates/http/multi-step-login.yaml -duc -ni -nc
```

* 예상 결과
```text

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

                projectdiscovery.io

[ERR] Could not read nuclei-ignore file: open ~/.config/nuclei/.nuclei-ignore: no such file or directory
[INF] Current nuclei version: v3.8.0 (unknown) - remove '-duc' flag to enable update checks
[INF] Current nuclei-templates version:  (unknown) - remove '-duc' flag to enable update checks
[INF] New templates added in latest release: 0
[INF] Templates loaded for current scan: 1
[WRN] Loading 1 unsigned templates for scan. Use with caution.
[INF] Targets loaded for current scan: 1
[lab-multi-step-login:session_token] [http] [medium] http://127.0.0.1:8010/api/login ["public-demo-session-token"]
[INF] Scan completed in 2.256027ms. 1 matches found.
```

* 의미
  - 이 템플릿은 raw HTTP 요청 2개를 순서대로 보낸다.
  - 첫 번째 요청 `GET /login`에서 CSRF token을 regex extractor로 뽑는다.
  - `internal: true` extractor라서 중간 CSRF 값은 결과로 출력하지 않고 두 번째 요청에만 재사용한다.
  - 두 번째 요청 `POST /api/login`이 성공하면 `session_token` extractor가 `"public-demo-session-token"`을 출력한다.

```bash
nuclei -u http://127.0.0.1:8010 -t asset/templates/http/variable-basic-auth-helper.yaml -V username=lab -V password=public-demo-basic-password -duc -ni -nc
```

* 예상 결과
```text

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

                projectdiscovery.io

[ERR] Could not read nuclei-ignore file: open ~/.config/nuclei/.nuclei-ignore: no such file or directory
[INF] Current nuclei version: v3.8.0 (unknown) - remove '-duc' flag to enable update checks
[INF] Current nuclei-templates version:  (unknown) - remove '-duc' flag to enable update checks
[INF] New templates added in latest release: 0
[INF] Templates loaded for current scan: 1
[WRN] Loading 1 unsigned templates for scan. Use with caution.
[INF] Targets loaded for current scan: 1
[lab-variable-basic-auth-helper] [http] [info] http://127.0.0.1:8010/basic-only
[INF] Scan completed in 1.402879ms. 1 matches found.
```

* 의미
  - `-V username=...`, `-V password=...`로 템플릿 변수를 명령줄에서 주입한다.
  - 템플릿 내부에서 `concat(username, ":", password)`로 `lab:public-demo-basic-password` 문자열을 만들고, `base64(...)` helper로 Basic Auth 값을 생성한다.
  - nuclei가 만든 Authorization 헤더가 `/basic-only` 인증 조건을 만족해서 매치된다.

## 7. Redirect, DAST, 속도 제한

```bash
nuclei -u http://127.0.0.1:8010 -t asset/templates/http/redirect-follow.yaml -fr -duc -ni -nc
```

* 예상 결과
```text

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

                projectdiscovery.io

[ERR] Could not read nuclei-ignore file: open ~/.config/nuclei/.nuclei-ignore: no such file or directory
[INF] Current nuclei version: v3.8.0 (unknown) - remove '-duc' flag to enable update checks
[INF] Current nuclei-templates version:  (unknown) - remove '-duc' flag to enable update checks
[INF] New templates added in latest release: 0
[INF] Templates loaded for current scan: 1
[WRN] Loading 1 unsigned templates for scan. Use with caution.
[INF] Targets loaded for current scan: 1
[lab-redirect-follow] [http] [info] http://127.0.0.1:8010/login
[INF] Scan completed in 1.74548ms. 1 matches found.
```

* 의미
  - `-fr`은 HTTP redirect를 따라가도록 만든다.
  - 템플릿은 `/admin`을 요청하지만 서버가 `/login`으로 redirect하므로, 최종 매치 위치가 `http://127.0.0.1:8010/login`으로 표시된다.
  - redirect를 따라간 뒤 로그인 페이지 body 조건이 맞아 `lab-redirect-follow`가 매치된다.

```bash
nuclei -u http://127.0.0.1:8010 -as -ud asset/templates -t asset/templates/http -duc -ni -nc -vv
```

* 예상 결과
```text

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

                projectdiscovery.io

[ERR] Could not read nuclei-ignore file: open ~/.config/nuclei/.nuclei-ignore: no such file or directory
[INF] Current nuclei version: v3.8.0 (unknown) - remove '-duc' flag to enable update checks
[INF] Current nuclei-templates version:  (unknown) - remove '-duc' flag to enable update checks
[INF] New templates added in latest release: 0
[INF] Templates loaded for current scan: 11
[WRN] Loading 11 unsigned templates for scan. Use with caution.
[INF] Targets loaded for current scan: 1
[lab-express-powered-by] Lab Express Powered By Fingerprint (@local) [info]
[lab-wordpress-fingerprint] Lab WordPress Looking Fingerprint (@local) [info]
[INF] Executing Automatic scan on 1 target[s]
[lab-wordpress-fingerprint] [http] [info] http://127.0.0.1:8010/wp-login.php
[lab-express-powered-by] [http] [info] http://127.0.0.1:8010/
[INF] Found 6 tags and 2 matches on detection templates on http://127.0.0.1:8010 [wappalyzer: 5, detection: 3]
Final tags identified for http://127.0.0.1:8010: [express node.js wordpress mysql php lab]
[lab-basic-auth-secret] Lab Basic Auth Protected API (@local) [info]
[lab-debug-complete-poc] Lab Debug Endpoint Complete PoC (@local) [low]
[lab-dsl-helper-matchers] Lab DSL Helper Matchers (@local) [info]
[lab-express-powered-by] Lab Express Powered By Fingerprint (@local) [info]
[lab-header-auth-secret] Lab Header Auth Protected API (@local) [info]
[lab-multi-step-login] Lab Multi Step Login With Internal Extractor (@local) [medium]
[lab-payload-attack] Lab Payload Attack Mode (@local) [info]
[lab-redirect-follow] Lab Redirect Follow (@local) [info]
[lab-slow-dangerous-demo] Lab Slow Dangerous Demo (@local) [info]
[lab-variable-basic-auth-helper] Lab Variable Basic Auth Helper (@local) [info]
[lab-wordpress-fingerprint] Lab WordPress Looking Fingerprint (@local) [info]
[INF] Executing 11 templates on http://127.0.0.1:8010
[lab-variable-basic-auth-helper] [http] [info] http://127.0.0.1:8010/basic-only
[cluster-b84c55e96331e4364f569d92eb8fdf23e4b09a5a02cbb221aa4bb3394a2368bd:lab_version] [http] [low] http://127.0.0.1:8010/debug ["1.4.2-dev"]
[lab-wordpress-fingerprint] [http] [info] http://127.0.0.1:8010/wp-login.php
[lab-dsl-helper-matchers] [http] [info] http://127.0.0.1:8010/debug
[lab-payload-attack] [http] [info] http://127.0.0.1:8010/api/private [token="public-demo-api-token"]
[lab-express-powered-by] [http] [info] http://127.0.0.1:8010/
[lab-multi-step-login:session_token] [http] [medium] http://127.0.0.1:8010/api/login ["public-demo-session-token"]
[lab-slow-dangerous-demo] [http] [info] http://127.0.0.1:8010/slow
[INF] Scan completed in 1.208747555s. 10 matches found.
```

* 의미
  - `-as`는 automatic scan 모드다. 먼저 fingerprint/detection 템플릿으로 대상 기술 태그를 식별하고, 그 태그에 맞는 템플릿을 실행한다.
  - `-ud asset/templates`는 자동 스캔이 사용할 템플릿 루트를 로컬 실습 디렉터리로 지정한다.
  - `-vv` 때문에 실행 대상 템플릿 이름이 자세히 출력된다.
  - detection 단계에서 `express`, `node.js`, `wordpress`, `mysql`, `php`, `lab` 태그가 식별되고, 이후 11개 템플릿이 실행된다.
  - 이 명령은 `-etags dos,dangerous`를 주지 않았기 때문에 `lab-slow-dangerous-demo`도 실행되어 매치된다.

```bash
nuclei -l asset/inputs/search-urls.txt -t asset/templates/http/dast-reflection-xss.yaml -dast -duc -ni -nc
```

* 예상 결과
```text

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

                projectdiscovery.io

[ERR] Could not read nuclei-ignore file: open ~/.config/nuclei/.nuclei-ignore: no such file or directory
[INF] Current nuclei version: v3.8.0 (unknown) - remove '-duc' flag to enable update checks
[INF] Current nuclei-templates version:  (unknown) - remove '-duc' flag to enable update checks
[INF] New templates added in latest release: 0
[INF] Templates loaded for current scan: 1
[WRN] Loading 1 unsigned templates for scan. Use with caution.
[INF] Targets loaded for current scan: 1
[lab-dast-reflection-xss] [http] [low] http://127.0.0.1:8010/search?q=hello6842'"><9967&category=notes [query:q] [GET]
[INF] Scan completed in 1.590463ms. 1 matches found.
```

* 의미
  - `-dast`는 DAST/fuzz 템플릿 실행을 허용한다.
  - 입력 URL `asset/inputs/search-urls.txt`의 query parameter 중 `q` 값에 fuzz payload가 붙는다.
  - 결과 URL의 `q=hello6842'"><9967`와 `[query:q]` 표시는 `q` 파라미터가 fuzz 지점이었다는 뜻이다.
  - 서버가 해당 payload를 HTML body에 반사하므로 reflection 탐지 템플릿이 매치된다.

```bash
nuclei -u http://127.0.0.1:8010 -t asset/templates/http -rl 1 -c 1 -bs 1 -etags dos,dangerous -stats -duc -ni -nc
```

* 예상 결과
```text

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

                projectdiscovery.io

[ERR] Could not read nuclei-ignore file: open ~/.config/nuclei/.nuclei-ignore: no such file or directory
[INF] Current nuclei version: v3.8.0 (unknown) - remove '-duc' flag to enable update checks
[INF] Current nuclei-templates version:  (unknown) - remove '-duc' flag to enable update checks
[INF] New templates added in latest release: 0
[INF] Templates loaded for current scan: 10
[WRN] Loading 10 unsigned templates for scan. Use with caution.
[INF] Targets loaded for current scan: 1
[INF] Templates clustered: 2 (Reduced 1 Requests)
[lab-multi-step-login:session_token] [http] [medium] http://127.0.0.1:8010/api/login ["public-demo-session-token"]
[lab-payload-attack] [http] [info] http://127.0.0.1:8010/api/private [token="public-demo-api-token"]
[lab-variable-basic-auth-helper] [http] [info] http://127.0.0.1:8010/basic-only
[0:00:05] | Templates: 10 | Hosts: 1 | RPS: 1 | Matched: 3 | Errors: 0 | Requests: 6/11 (54%)
[lab-debug-complete-poc:lab_version] [http] [low] http://127.0.0.1:8010/debug ["1.4.2-dev"]
[lab-dsl-helper-matchers] [http] [info] http://127.0.0.1:8010/debug
[lab-express-powered-by] [http] [info] http://127.0.0.1:8010/
[lab-wordpress-fingerprint] [http] [info] http://127.0.0.1:8010/wp-login.php
[0:00:10] | Templates: 10 | Hosts: 1 | RPS: 1 | Matched: 7 | Errors: 0 | Requests: 11/11 (100%)
[INF] Scan completed in 9.994657235s. 7 matches found.
[0:00:10] | Templates: 10 | Hosts: 1 | RPS: 1 | Matched: 7 | Errors: 0 | Requests: 11/11 (100%)
```

* 의미
  - `-rl 1`은 초당 요청 수를 1 RPS로 제한한다.
  - `-c 1`은 동시에 실행할 템플릿 수를 1개로 제한한다.
  - `-bs 1`은 템플릿당 동시에 처리할 host 수를 1개로 제한한다.
  - `-stats` 때문에 중간 진행률이 `[0:00:05]`, `[0:00:10]` 형태로 출력된다.
  - 같은 템플릿 세트를 빠르게 실행했을 때보다 오래 걸리는 것이 정상이며, 최종적으로 7개가 매치된다.

## 8. 출력과 디버깅

```bash
nuclei -u http://127.0.0.1:8010 -t asset/templates/http/debug-complete-poc.yaml -jsonl -o asset/outputs/debug.jsonl -duc -ni -nc
```

* 예상 결과
```text
 
                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

                projectdiscovery.io

[ERR] Could not read nuclei-ignore file: open ~/.config/nuclei/.nuclei-ignore: no such file or directory
[INF] Current nuclei version: v3.8.0 (unknown) - remove '-duc' flag to enable update checks
[INF] Current nuclei-templates version:  (unknown) - remove '-duc' flag to enable update checks
[INF] New templates added in latest release: 0
[INF] Templates loaded for current scan: 1
[WRN] Loading 1 unsigned templates for scan. Use with caution.
[INF] Targets loaded for current scan: 1
{"template-id":"lab-debug-complete-poc","template-path":"<repo-root>/asset/templates/http/debug-complete-poc.yaml","template-encoded":"aWQ6IGxhYi1kZWJ1Zy1jb21wbGV0ZS1wb2MKCmluZm86CiAgbmFtZTogTGFiIERlYnVnIEVuZHBvaW50IENvbXBsZXRlIFBvQwogIGF1dGhvcjogbG9jYWwKICBzZXZlcml0eTogbG93CiAgZGVzY3JpcHRpb246IERldGVjdHMgdGhlIGxvY2FsIGRlYnVnIGVuZHBvaW50IHdpdGggc3RhdHVzLCBoZWFkZXIsIGFuZCBib2R5IGV2aWRlbmNlLgogIHRhZ3M6IGxhYixkZWJ1Zyxwb2MsZXhwb3N1cmUKCmh0dHA6CiAgLSBtZXRob2Q6IEdFVAogICAgcGF0aDoKICAgICAgLSAie3tCYXNlVVJMfX0vZGVidWciCgogICAgbWF0Y2hlcnMtY29uZGl0aW9uOiBhbmQKICAgIG1hdGNoZXJzOgogICAgICAtIHR5cGU6IHN0YXR1cwogICAgICAgIHN0YXR1czoKICAgICAgICAgIC0gMjAwCgogICAgICAtIHR5cGU6IHdvcmQKICAgICAgICBwYXJ0OiBoZWFkZXIKICAgICAgICB3b3JkczoKICAgICAgICAgIC0gIlgtRGVidWctTW9kZTogZW5hYmxlZCIKCiAgICAgIC0gdHlwZTogd29yZAogICAgICAgIHBhcnQ6IGJvZHkKICAgICAgICB3b3JkczoKICAgICAgICAgIC0gJyJhcHAiOiAiQWNtZU5vdGVzIicKICAgICAgICAgIC0gJyJkZWJ1ZyI6IHRydWUnCiAgICAgICAgY29uZGl0aW9uOiBhbmQKCiAgICBleHRyYWN0b3JzOgogICAgICAtIHR5cGU6IHJlZ2V4CiAgICAgICAgbmFtZTogbGFiX3ZlcnNpb24KICAgICAgICBwYXJ0OiBib2R5CiAgICAgICAgZ3JvdXA6IDEKICAgICAgICByZWdleDoKICAgICAgICAgIC0gJyJ2ZXJzaW9uIjpccyoiKFteIl0rKSInCg==","info":{"name":"Lab Debug Endpoint Complete PoC","author":["local"],"tags":["lab","debug","poc","exposure"],"description":"Detects the local debug endpoint with status, header, and body evidence.","severity":"low"},"extractor-name":"lab_version","type":"http","host":"127.0.0.1","port":"8010","scheme":"http","url":"http://127.0.0.1:8010","matched-at":"http://127.0.0.1:8010/debug","extracted-results":["1.4.2-dev"],"request":"GET /debug HTTP/1.1\r\nHost: 127.0.0.1:8010\r\nUser-Agent: Mozilla/5.0 (ZZ; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36\r\nConnection: close\r\nAccept: */*\r\nAccept-Language: en\r\nAccept-Encoding: gzip\r\n\r\n","response":"HTTP/1.0 200 OK\r\nConnection: close\r\nContent-Length: 137\r\nContent-Type: application/json\r\nDate: Sat, 09 May 2026 02:50:11 GMT\r\nServer: NucleiLab/0.2\r\nSet-Cookie: lab_session=guest; HttpOnly; Path=/\r\nX-Debug-Mode: enabled\r\nX-Lab-Target: nuclei-local-training\r\nX-Powered-By: Express\r\n\r\n{\n  \"app\": \"AcmeNotes\",\n  \"version\": \"1.4.2-dev\",\n  \"debug\": true,\n  \"build\": \"2026.05.09-lab\",\n  \"debug_marker\": \"debug-panel-enabled\"\n}","ip":"127.0.0.1","timestamp":"2026-05-09T11:50:11.792539833+09:00","curl-command":"curl -X 'GET' -d '' -H 'Accept: */*' -H 'Accept-Language: en' -H 'User-Agent: Mozilla/5.0 (ZZ; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' 'http://127.0.0.1:8010/debug'","matcher-status":true}
[INF] Scan completed in 2.129356ms. 1 matches found.
```

* 의미
  - `-jsonl`은 매치 결과를 JSON Lines 형식으로 출력한다.
  - `-o asset/outputs/debug.jsonl` 때문에 같은 JSONL 결과가 파일에도 저장된다.
  - JSON 안에는 `template-id`, `template-path`, `info`, `matched-at`, `extracted-results`, 실제 `request`, 실제 `response`, 재현용 `curl-command`가 포함된다.
  - `template-encoded`는 실행된 템플릿 내용을 base64로 인코딩해 결과에 포함한 값이다.
  - `extracted-results:["1.4.2-dev"]`는 extractor가 debug 응답에서 버전을 뽑았다는 뜻이다.

```bash
nuclei -u http://127.0.0.1:8010 -t asset/templates/http/debug-complete-poc.yaml -dreq -dresp -duc -ni -nc
```

* 예상 결과
```text

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.8.0

                projectdiscovery.io

[ERR] Could not read nuclei-ignore file: open ~/.config/nuclei/.nuclei-ignore: no such file or directory
[INF] Current nuclei version: v3.8.0 (unknown) - remove '-duc' flag to enable update checks
[INF] Current nuclei-templates version:  (unknown) - remove '-duc' flag to enable update checks
[WRN] Scan results upload to cloud is disabled.
[INF] New templates added in latest release: 0
[INF] Templates loaded for current scan: 1
[WRN] Loading 1 unsigned templates for scan. Use with caution.
[INF] Targets loaded for current scan: 1
[INF] [lab-debug-complete-poc] Dumped HTTP request for http://127.0.0.1:8010/debug

GET /debug HTTP/1.1
Host: 127.0.0.1:8010
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; WOW64; rv:41.0) Gecko/20100101 Firefox/140.0 (x64 de)
Connection: close
Accept: */*
Accept-Language: en
Accept-Encoding: gzip

[DBG] [lab-debug-complete-poc] Dumped HTTP response http://127.0.0.1:8010/debug

HTTP/1.0 200 OK
Connection: close
Content-Length: 137
Content-Type: application/json
Date: Sat, 09 May 2026 02:50:19 GMT
Server: NucleiLab/0.2
Set-Cookie: lab_session=guest; HttpOnly; Path=/
X-Debug-Mode: enabled
X-Lab-Target: nuclei-local-training
X-Powered-By: Express

{
  "app": "AcmeNotes",
  "version": "1.4.2-dev",
  "debug": true,
  "build": "2026.05.09-lab",
  "debug_marker": "debug-panel-enabled"
}
[lab-debug-complete-poc:status-1] [http] [low] http://127.0.0.1:8010/debug ["1.4.2-dev"]
[lab-debug-complete-poc:word-2] [http] [low] http://127.0.0.1:8010/debug ["1.4.2-dev"]
[lab-debug-complete-poc:word-3] [http] [low] http://127.0.0.1:8010/debug ["1.4.2-dev"]
[INF] Scan completed in 1.539163ms. 3 matches found.
```

* 의미
  - `-dreq`는 nuclei가 실제로 보낸 HTTP request를 출력한다.
  - `-dresp`는 서버에서 받은 HTTP response를 출력한다.
  - 이 옵션은 matcher가 어떤 원시 요청/응답 위에서 평가됐는지 확인할 때 유용하다.
  - 결과가 `status-1`, `word-2`, `word-3`처럼 3개로 보이는 이유는 debug 출력 모드에서 개별 matcher별 매치 상태가 드러나기 때문이다.
  - 같은 `/debug` 응답에서 status matcher 1개와 word matcher 2개가 각각 성공했다.

## 9. 현재 환경에서 주의할 점

- 이 머신의 `nuclei`의 버전은 `v3.8.0`이다.
- 이 머신의 `httpx`는 ProjectDiscovery `httpx`가 아니라 Python `httpx` CLI다.
- v3.8.0 help 기준으로 DAST 실행 플래그는 `-d`가 아니라 `-dast`다.
- `-as`는 기본적으로 설치된 templates 디렉터리를 찾으므로, 이 로컬 랩에서는 `-ud asset/templates`를 같이 준다.
- 공식 `recommended`, `bug bounty` 같은 community profile 실습은 `nuclei-templates` 설치 후 진행해야 한다.
- 공식 문서 기준 `.nuclei-ignore`는 기본 denylist로 내부 사용되며, 사용자가 직접 편집하기보다는 `-etags`, `-et`, config의 `exclude-tags`, `exclude-templates`, 그리고 필요 시 `-itags`, `-it`로 제어한다.
