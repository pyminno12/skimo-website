import json
import os
from datetime import datetime
import google.generativeai as genai

# 1. API 키 설정 (GitHub Secrets에서 불러옴)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def fetch_daily_skimo_info():
    prompt = """
    산악스키(Skimo) 관람객 및 선수를 위한 오늘의 유용한 장비 팁, ISMF 규정, 뉴스 또는 훈련 정보 1건을 새로 생성해줘.
    반드시 아래 JSON 형식을 엄격히 지켜서 응답해. 설명문은 일절 포함하지 마.

    [
        {
            "date": "YYYY-MM-DD",
            "category": "🏔️ Daily Skimo",
            "title": {
                "KO": "한국어 제목",
                "EN": "영어 제목",
                "FR": "프랑스어 제목",
                "IT": "이탈리아어 제목",
                "ZH": "중국어 제목",
                "JA": "일본어 제목"
            },
            "content": {
                "KO": "한국어 내용 (2-3문장)",
                "EN": "영어 내용",
                "FR": "프랑스어 내용",
                "IT": "이탈리아어 내용",
                "ZH": "중국어 내용",
                "JA": "일본어 내용"
            }
        }
    ]
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    clean_json = response.text.replace("```json", "").replace("```", "").strip()
    new_notice = json.loads(clean_json)
    return new_notice[0]

def update_notice_file():
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    try:
        with open("notice_data.json", "r", encoding="utf-8") as f:
            notices = json.load(f)
    except FileNotFoundError:
        notices = []
        
    try:
        new_item = fetch_daily_skimo_info()
        new_item["date"] = today_str
        
        notices.insert(0, new_item)
        notices = notices[:10]
        
        with open("notice_data.json", "w", encoding="utf-8") as f:
            json.dump(notices, f, ensure_ascii=False, indent=4)
        print("Successfully updated notice_data.json")
    except Exception as e:
        print(f"Error updating notices: {e}")

if __name__ == "__main__":
    update_notice_file()
