# Remote Run Log

이 문서는 `Basic Software Technology` 프로젝트를 회사 원격 서버에서 실제 실행한 기록입니다.

## 실행 일자

- 2026-05-18

## 서버 접속 정보

| 항목 | 값 |
|---|---|
| SSH Host | 보안상 비공개 |
| SSH Port | 보안상 비공개 |
| User | 보안상 비공개 |
| Server OS | Ubuntu 22.04.5 LTS |
| Project Path | `<REMOTE_PROJECT_PATH>` |

## 수행한 작업

### 1. SSH 접속

```powershell
ssh <SSH_USER>@<SSH_HOST> -p <SSH_PORT>
```

접속 후 서버 프롬프트:

```text
<SSH_USER>@<REMOTE_SERVER>:~$
```

### 2. 서버 기본 환경 확인

```bash
pwd
pip3 --version
git --version
```

확인 결과:

```text
<REMOTE_HOME>
pip 22.0.2 from /usr/lib/python3/dist-packages/pip (python 3.10)
git version 2.34.1
```

### 3. GitHub 저장소 clone

```bash
git clone https://github.com/dhkimaru/Basic-Software-Technology.git
cd Basic-Software-Technology
```

### 4. Python 가상환경 생성

```bash
python3 -m venv .venv
source .venv/bin/activate
```

활성화 후 프롬프트:

```text
(.venv) <SSH_USER>@<REMOTE_SERVER>:~/Basic-Software-Technology$
```

### 5. 의존성 설치

```bash
pip install -r requirements.txt
```

설치 완료 주요 패키지:

- streamlit
- pandas
- openpyxl
- xlrd
- ollama
- openai
- google-genai

### 6. Streamlit 실행

```bash
streamlit run app.py --server.address <BIND_ADDRESS> --server.port <APP_PORT>
```

실행 결과:

```text
Uvicorn server started on <BIND_ADDRESS>:<APP_PORT>

You can now view your Streamlit app in your browser.

Local URL: http://localhost:<APP_PORT>
Network URL: http://<PRIVATE_NETWORK_IP>:<APP_PORT>
External URL: http://<PUBLIC_SERVER_IP>:<APP_PORT>
```

### 7. SSH 터널을 통한 브라우저 확인

외부에서 앱 포트 직접 접근이 제한될 수 있으므로, Windows PowerShell에서 SSH 터널을 사용했습니다.

```powershell
ssh -L <LOCAL_PORT>:localhost:<APP_PORT> <SSH_USER>@<SSH_HOST> -p <SSH_PORT>
```

이후 노트북 브라우저에서 아래 주소로 접속해 서버에서 실행 중인 Streamlit 앱을 확인했습니다.

```text
http://localhost:<LOCAL_PORT>
```

## 로컬 localhost와 서버 실행의 차이

SSH 터널을 사용하면 브라우저 주소는 로컬 주소처럼 보이지만, 앱은 노트북이 아니라 원격 서버에서 실행됩니다.

```text
Windows Browser
http://localhost:<LOCAL_PORT>
        |
        v
SSH Tunnel
        |
        v
Remote Server
Streamlit app on localhost:<APP_PORT>
```

## 수행 완료 범위

- 원격 서버 SSH 접속 완료
- GitHub 저장소 clone 완료
- Python 가상환경 생성 완료
- requirements 설치 완료
- Streamlit 앱 원격 실행 완료
- SSH 터널 기반 브라우저 접속 확인 완료

## 추가 확인이 필요한 범위

- RTX 5090 GPU 드라이버/CUDA 상태 확인
- Ollama 서버 설치 및 모델 다운로드
- GPU 기반 Ollama 모델 호출 확인
- Spark 설치 및 대용량 엑셀/CSV 처리 확장
