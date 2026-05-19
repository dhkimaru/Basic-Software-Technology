# Demo Recording Guide

이 문서는 프로젝트 시연 영상을 구성할 때 사용할 순서를 정리한 가이드입니다.

## 권장 영상 길이

- 2분 ~ 4분

## 촬영 전 준비

서버에서 Streamlit 앱이 실행 중이어야 합니다.

```bash
cd ~/Basic-Software-Technology
source .venv/bin/activate
streamlit run app.py --server.address <BIND_ADDRESS> --server.port <APP_PORT>
```

Windows PowerShell에서는 SSH 터널을 열어둡니다.

```powershell
ssh -L <LOCAL_PORT>:localhost:<APP_PORT> <SSH_USER>@<SSH_HOST> -p <SSH_PORT>
```

브라우저 접속 주소:

```text
http://localhost:<LOCAL_PORT>
```

## 촬영 순서

### 1. GitHub README 소개

보여줄 내용:

- 프로젝트명: `Basic Software Technology`
- 실행 화면 캡처
- 원격 서버 실행 확인 섹션
- SheetPilot 참고 프로젝트 비교표
- Mermaid 시스템 흐름도
- AI Agent / Skill 개념 연계 섹션

### 2. 원격 서버 실행 상태 확인

서버 터미널에서 Streamlit이 실행 중인 화면을 보여줍니다.

핵심 문구:

```text
Uvicorn server started on <BIND_ADDRESS>:<APP_PORT>
```

### 3. 브라우저에서 앱 접속

브라우저 주소:

```text
http://localhost:<LOCAL_PORT>
```

설명 포인트:

- 주소는 localhost이지만 SSH 터널을 통해 원격 서버 앱을 보고 있음
- 실제 실행 위치는 회사 서버

### 4. 앱 화면 설명

보여줄 UI:

- 모델 제공자 선택
- 모델명 입력
- 엑셀 파일 업로드 영역
- 업로드 파일 목록
- 프롬프트 입력 영역

### 5. 엑셀 파일 업로드

가능하면 샘플 엑셀 2~3개를 업로드합니다.

보여줄 기능:

- 업로드 저장
- 파일 목록 확인
- 파일 미리보기
- 삭제 버튼 존재 확인

### 6. 프롬프트 처리

입력 예시:

```text
업로드된 엑셀 파일들을 합치고 동일 항목은 평균으로 계산해줘
```

보여줄 결과:

- 처리 완료 메시지
- 결과 엑셀 다운로드 버튼
- 결과 Markdown 다운로드 버튼

### 7. 마무리 설명

핵심 정리:

- SheetPilot을 참고해 Streamlit 기반 엑셀 처리 워크벤치를 구현
- 현재 MVP는 AI 생성 코드를 직접 실행하지 않고 안전한 사전 정의 함수로 처리
- 원격 서버에서 실행 확인 완료
- 향후 Ollama GPU 모델 실행과 Spark 연동으로 확장 가능

## 영상 촬영 시 주의

- 비밀번호 입력 장면은 녹화하지 않습니다.
- 회사 서버의 민감한 파일 목록은 보여주지 않습니다.
- 실제 데이터에 민감정보가 있으면 샘플 파일로 대체합니다.
- GitHub 토큰, API key, `.env` 파일 내용은 절대 보여주지 않습니다.
