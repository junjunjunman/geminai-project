# 1. 프로젝트 환경 구축 
터미널에 입력해야 한다.

> 1. cd 프로젝트파일경로
> 2. python3 -m venv venv (가상환경을 생성해야한다.)
> 3. source ven/bin/activate

# 2. 필수 라이브러리 설치

가상환경 활성화된 상태에서 Flask, Google GenAI SDK, PDF 처리 라이브러리를 설치한다.
> pip install flask google-genai pypdf

# 3. API 키 및 인코딩 환경 설정

발급받은 Gemini API 키를 환경 변수에 저장합니다.
> export GEMINI_API_KEY="발급받은_당신의_API_키를_여기에_정확히_입력하세요"

또는 app.py코드에
> API_KEY = os.getenv('GEMINI_API_KEY')

대신

> API_KEY = '발급받은_당신의_API_키를_여기에_정확히_입력하세요'

코드로 써도 된다.

---
만약 인코딩 오류가 발생한다면
>export LANG=en_US.UTF-8

>export LC_ALL=en_US.UTF-8

# 4. 서비스 실행
> python app.py

터미널에 Running on http://127.0.0.1:5000/ 메시지가 뜨면, 웹 브라우저로 접속하여 서비스를 사용할 수 있습니다.
---
파일 내부구조

project-summarizer/

  * venv/

  * app.py
  * templates/
    * index.html
  *  static/

     * css/

         *  style.css
  *  uploads/
