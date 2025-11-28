# app.py
# -*- coding: utf-8 -*-
import locale
import os
import sys
import tempfile

# 인코딩 문제 해결을 위해 로케일 설정 강제 (macOS 환경 문제 해결)
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') 
os.environ['PYTHONIOENCODING'] = 'utf-8'

from flask import Flask, request, render_template, jsonify
from pypdf import PdfReader
from google import genai
from google.genai import types

# ----------------------------------------------------------------------
# 1. Gemini 클라이언트 초기화 및 API 설정
# ----------------------------------------------------------------------

# API 키를 환경 변수에서 로드합니다.
# ⚠️ 직접 키를 입력하려면 os.getenv('GEMINI_API_KEY') 대신 직접 키를 넣으세요.
API_KEY = os.getenv('GEMINI_API_KEY') 

if not API_KEY:
    print("FATAL ERROR: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
    sys.exit(1)

try:
    # API 키를 client 객체에 직접 전달
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    print(f"FATAL ERROR: Gemini 클라이언트 초기화 실패: {e}")
    sys.exit(1)


# ----------------------------------------------------------------------
# 2. PDF 처리 및 요약 로직 (기존 코드 재사용)
# ----------------------------------------------------------------------

def extract_text_from_pdf(pdf_path: str) -> str:
    """PDF 파일 경로에서 텍스트를 추출하여 반환합니다."""
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            raw_text = page.extract_text()
            # 텍스트 추출 중 인코딩 문제를 방지하기 위해 명시적으로 처리
            if raw_text:
                text += raw_text.encode('utf-8', errors='ignore').decode('utf-8')
    except Exception as e:
        print(f"PDF 텍스트 추출 중 오류 발생: {e}")
        # 오류가 발생해도 부분 텍스트를 반환할 수 있도록 빈 문자열 반환 대신 로그만 남김
        return ""
    return text

def summarize_with_gemini(text: str, model_name: str = 'gemini-2.5-flash') -> str:
    """추출된 텍스트를 Gemini 모델로 요약합니다."""
    
    if len(text) < 100:
        return "텍스트 내용이 너무 짧거나 추출에 실패했습니다."

    # 텍스트를 API로 전달하기 전, 인코딩 문제에 대비한 최종 정리
    cleaned_text = text.encode('utf-8', errors='ignore').decode('utf-8')

    prompt = (
        "당신은 전문 요약가입니다. 다음 문서 내용을 한국어로 간결하고 핵심적인 정보만을 담아 요약해 주세요. "
        "주요 주제, 결론, 핵심 데이터 포인트를 포함해야 합니다.\n\n"
        f"--- 문서 내용 ---\n{cleaned_text}" 
    )

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
            )
        )
        return response.text
    except Exception as e:
        print(f"Gemini API 호출 중 심각한 오류 발생: {e}")
        return f"Gemini API 호출 중 오류 발생: {e}"


# ----------------------------------------------------------------------
# 3. Flask 웹 서비스 라우팅
# ----------------------------------------------------------------------

app = Flask(__name__)

@app.route('/')
def index():
    """메인 페이지 로드"""
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    """PDF 파일을 받아 요약하고 결과를 JSON으로 반환"""
    
    if 'pdf_file' not in request.files:
        return jsonify({'error': '파일이 첨부되지 않았습니다.'}), 400
    
    uploaded_file = request.files['pdf_file']
    if uploaded_file.filename == '' or not uploaded_file.filename.endswith('.pdf'):
        return jsonify({'error': '유효한 PDF 파일을 첨부해 주세요.'}), 400

    # tempfile을 사용하여 파일을 임시로 저장하고 경로를 확보
    try:
        # with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        #     file_path = tmp_file.name
        #     uploaded_file.save(file_path)
        
        # ⚠️ 단순화를 위해 uploads 폴더에 저장 (실제 서비스에서는 보안을 위해 tempfile 사용 권장)
        file_path = os.path.join(os.getcwd(), 'uploads', uploaded_file.filename)
        uploaded_file.save(file_path)
        
        # 텍스트 추출 및 요약 실행
        full_text = extract_text_from_pdf(file_path)
        
        if not full_text:
             return jsonify({'error': 'PDF에서 텍스트를 추출하지 못했거나 문서가 비어 있습니다.'}), 500

        summary_text = summarize_with_gemini(full_text)
        
        # 임시 파일 삭제 (실제 서비스에서 필수)
        os.remove(file_path)

        return jsonify({'summary': summary_text})

    except Exception as e:
        return jsonify({'error': f'서버 처리 중 예기치 않은 오류 발생: {str(e)}'}), 500

if __name__ == '__main__':
    # 디버그 모드 활성화 (개발 중 편리)
    # 실제 운영 시에는 debug=False로 설정해야 합니다.
    app.run(debug=True)