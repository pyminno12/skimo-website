import streamlit as st
import pandas as pd
from datetime import datetime
import time
import json

# ==========================================
# 1. 페이지 설정 및 글로벌 상태 정의
# ==========================================
st.set_page_config(page_title="SKIMO KOREA", page_icon="🏔️", layout="wide")

# 배경 이미지 풀 (메뉴 전환 시 동적 배경 변경용)
BG_IMAGES = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=1800&q=80",
    "https://images.unsplash.com/photo-1518098268026-4e43a1a009de?auto=format&fit=crop&w=1800&q=80"   
]

if "menu_idx" not in st.session_state:
    st.session_state.menu_idx = 0
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# ------------------------------------------
# [🚨 중요: 브라우저 쿠키/로컬 스토리지 대용 구조 구현]
# ------------------------------------------
# Streamlit의 실험적 기능인 컴포넌트나 파일 영구 저장을 사용해 새로고침을 견디도록 설계합니다.
# 배포 환경에서도 데이터가 유지될 수 있도록 서버 로컬 json 파일을 영구 데이터베이스 허브로 활용합니다.
DB_FILE = "user_database.json"

def load_user_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # 최초 기본 계정 구조 정의
        initial_db = {
            "admin": {"pw": "1234", "role": "ADMIN"},
            "skimo": {"pw": "skimo123", "role": "JUDGE"}
        }
        save_user_db(initial_db)
        return initial_db

def save_user_db(db_data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=4)

# 실시간 유저 DB 로드 및 세션 동기화
st.session_state.user_db = load_user_db()

# B. 실시간 계측/타이밍 데이터 (Telemetry 데이터 모델)
if "athletes_domain" not in st.session_state:
    st.session_state.athletes_domain = {
        "101": {"Name": "김민우", "Team": "KOREA", "Category": "Sprint", "Status": "RACING", "CP1": "10:15:20", "CP2": "--:--:--", "Penalty_Sec": 0, "Final_Record": "--:--:--"},
        "102": {"Name": "Alex Smith", "Team": "USA", "Category": "Individual", "Status": "RACING", "CP1": "10:14:05", "CP2": "10:45:12", "Penalty_Sec": 0, "Final_Record": "--:--:--"},
        "103": {"Name": "Chloe", "Team": "FRANCE", "Category": "Vertical", "Status": "RACING", "CP1": "10:16:55", "CP2": "10:49:30", "Penalty_Sec": 10, "Final_Record": "--:--:--"},
    }

# C. 다국어 공지사항 아카이브 데이터
if "notice_domain" not in st.session_state:
    st.session_state.notice_domain = [
        {
            "date": "2026-06-15", "category": "🏆 Race Info",
            "title": {
                "KO": "2026/27 ISMF 산악스키 월드컵 개막전 일정 확정 (프랑스 알프스)",
                "EN": "2026/27 ISMF Ski Mountaineering World Cup Opening Venue Confirmed (French Alps)"
            },
            "content": {
                "KO": "국제산악스키연맹(ISMF)이 다가오는 시즌 개막전을 프랑스 알프스에서 개최한다고 밝혔습니다.",
                "EN": "The ISMF announced that the upcoming season opener will be held in the French Alps."
            }
        }
    ]

# D. 글로벌 실시간 다국어 뉴스 및 AI 요약 아카이브
if "home_news_domain" not in st.session_state:
    st.session_state.home_news_domain = [
        {
            "id": "news_01",
            "date": "2026-06-18",
            "link": "https://www.ismf-ski.org/",
            "title": {
                "KO": "🚀 2030 프랑스 알프스 동계 올림픽, 산악스키 세부 종목 규정 발표 예정",
                "EN": "🚀 2030 French Alps Winter Olympics: Detailed Skimo Regulations to be Announced",
                "FR": "🚀 Jeux Olympiques d'hiver des Alpes Françaises 2030 : Les règlements détaillés du Skimo seront annoncés",
                "IT": "🚀 Olimpiadi Invernali delle Alpi Francesi 2030: Saranno annunciati i regolamenti dettagliati dello Skimo",
                "ZH": "🚀 2030年法国阿尔卑斯冬季奥运会：滑雪登山详细项目规则即将公布",
                "JA": "🚀 2030年フランス・アルプス冬季オリンピック、山岳スキー詳細種目規定がまもなく発表予定"
            },
            "ai_summary": {
                "KO": "🤖 **AI 요약:** 2030 프랑스 동계 올림픽 조직위와 ISMF가 산악스키 정식 종목 채택에 따른 세부 중계 및 페널티 규정을 내달 확정합니다. 이번 규정은 가파른 업힐 전환 구간의 공정성 확보에 초점을 맞추고 있습니다.\n\n💡 **핵심 키워드:** `#2030동계올림픽` `#ISMF규정` `#산악스키정식종목`",
                "EN": "🤖 **AI Summary:** The 2030 French Winter Olympics Committee and ISMF will finalize detailed broadcasting and penalty regulations next month. This update focuses heavily on ensuring fairness during steep uphill transition zones.\n\n💡 **Keywords:** `#WinterOlympics2030` `#ISMF_Rules` `#SkimoOfficial`"
            }
        },
        {
            "id": "news_02",
            "date": "2026-06-12",
            "link": "https://www.ismf-ski.org/",
            "title": {
                "KO": "❄️ 아시아 산악스키 연맹, 청소년 선수 육성을 위한 동계 캠프 평창 개최 확정",
                "EN": "❄️ Asian Skimo Federation Confirms Winter Youth Development Camp in Pyeongchang",
                "FR": "❄️ La Fédération Asiatique de Skimo confirme un camp de développement pour les jeunes à Pyeongchang",
                "IT": "❄️ La Federazione Asiatica Skimo conferma il campo di sviluppo giovanile invernale a Pyeongchang",
                "ZH": "❄️ 亚洲滑雪登山联盟确认将在平昌举办冬季青少年选手培育训练营",
                "JA": "❄️ アジア山岳スキー連盟、青少年選手育成のための冬季キャンプを平昌で開催確定"
            },
            "ai_summary": {
                "KO": "🤖 **AI 요약:** 아시아 청소년 산악스키 유망주들을 위한 집중 트레이닝 캠프가 대한민국 평창 알펜시아에서 개최됩니다. 국제 기술 위원들이 직접 패트롤 및 장비 전환 기술을 지도할 예정입니다.\n\n💡 **핵심 키워드:** `#평창동계캠프` `#청소년육성` `#아시아산악스키`",
                "EN": "🤖 **AI Summary:** An intensive training camp for promising Asian youth Skimo athletes will be held in Pyeongchang Alpensia, South Korea. International technical delegates will directly mentor patrol and gear transition techniques.\n\n💡 **Keywords:** `#PyeongchangCamp` `#YouthDevelopment` `#AsianSkimo`"
            }
        },
        {
            "id": "news_03",
            "date": "2026-06-05",
            "link": "https://www.ismf-ski.org/",
            "title": {
                "KO": "🏅 대한민국 산악스키 국가대표팀, 뉴질랜드 전지훈련 위해 출국",
                "EN": "🏅 National Skimo Team Departs for Off-Season Training in New Zealand",
                "FR": "🏅 L'équipe nationale de Skimo part pour un entraînement hors saison en Nouvelle-Zélande",
                "IT": "🏅 La squadra nazionale di Skimo parte per l'allenamento fuori stagione in Nuova Zelanda",
                "ZH": "🏅 韩国滑雪登山国家队启程前往新西兰展开新赛季海外集训",
                "JA": "🏅 山岳スキー大韓民국国家대표팀, 뉴질랜드 해외원정 트레이닝을 위해 출국의 투へ"
            },
            "ai_summary": {
                "KO": "🤖 **AI 요약:** 대한민국 산악스키 국가대표 선수단이 설질 조건이 우수한 뉴질랜드 남섬 인터내셔널 스키 필드로 비시즌 전지훈련을 떠납니다. 해발 고도 2,000m 이상에서의 산소 적응 훈련에 집중합니다.\n\n💡 **핵심 키워드:** `#국가대표팀` `#뉴질랜드전지훈련` `#고산적응`",
                "EN": "🤖 **AI Summary:** The South Korean National Skimo Team departs for off-season training at the International Ski Field in the South Island of New Zealand, focusing on high-altitude oxygen adaptation over 2,000m.\n\n💡 **Keywords:** `#NationalTeam` `#NewZealandTraining` `#AltitudeAdaptation`"
            }
        }
    ]

# 동적 스타일링에 쓰일 배경 이미지 바인딩
selected_bg = BG_IMAGES[st.session_state.menu_idx] if st.session_state.menu_idx < len(BG_IMAGES) else BG_IMAGES[0]

# UI 오버레이 디자인 CSS
st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{ display: none !important; }}
    .stAppDeployDropdown {{ display: none !important; }}
    [data-testid="stSidebar"] {{ display: none !important; }}
    .block-container {{ padding-top: 0rem; padding-bottom: 0rem; padding-left: 0rem; padding-right: 0rem; }}
    
    .stApp {{
        background: linear-gradient(rgba(15, 32, 39, 0.85), rgba(44, 83, 100, 0.75)), url('{selected_bg}') no-repeat center center fixed;
        background-size: cover !important;
    }}
    
    .centered-wrapper {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
    .custom-header-bg {{ background-color: rgba(15, 32, 39, 0.4); backdrop-filter: blur(5px); width: 100%; padding: 10px 0; }}
    
    .hero-section {{ height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; text-align: center; }}
    .hero-title {{ font-size: 42px; font-weight: 800; text-shadow: 3px 3px 8px rgba(0,0,0,0.9); margin-bottom: 5px; }}
    .hero-subtitle {{ font-size: 18px; font-weight: 500; color: #00c6ff; text-shadow: 2px 2px 4px rgba(0,0,0,0.7); }}
    
    .content-box {{ 
        max-width: 1200px; margin: 0 auto 50px auto; padding: 30px; background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(10px); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.15); color: #ffffff;
    }}
    
    div.stButton > button {{
        background: transparent !important; color: white !important; border: none !important;
        font-size: 14px !important; font-weight: 500 !important;
    }}
    div.stButton > button:hover {{ color: #00c6ff !important; }}
    
    .news-flex-container {{ display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 5px 0; }}
    .news-title-link {{ font-size: 15px; font-weight: 500; color: #e2e8f0; text-decoration: none; }}
    .news-title-link:hover {{ color: #00c6ff; cursor: pointer; }}
    .news-date-span {{ font-size: 13px; color: #cbd5e1; white-space: nowrap; }}
    
    .notice-card {{ background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; margin-bottom: 15px; }}
    .notice-badge {{ background-color: #00c6ff; color: #111; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-right: 10px; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 6개국 로컬라이제이션 매핑 아키텍처
# ==========================================
LANG_DICT = {
    "한국어 (KO)": "KO", "English (EN)": "EN", "Français (FR)": "FR",       
    "Italiano (IT)": "IT", "简体中文 (ZH)": "ZH", "日本語 (JA)": "JA"          
}

LOCALIZED_TEXT = {
    "KO": {
        "title": "SKIMO KOREA", "subtitle": "스키등산 정보 포털",
        "menu": ["대회 홈", "선수 참가 신청", "실시간 리더보드 (LIVE)", "🔐 심판/관리자 패널", "📢 글로벌 공지사항"],
        "desc": "본 대회는 국제산악스키연맹(ISMF) 규정을 준수하며, field 심판 시스템과 동기화되어 실시간 기록을 전 세계에 생중계합니다.",
        "video": "📺 경기 종목 안내", "intro_video": "⛷️ 산악스키 소개", "photo": "📸 올림픽 현장 갤러리", "pay": "💳 참가 신청 및 안전 결제",
        "news_title": "📰 News & Stories (글로벌 최신 소식)", "search_holder": "🔍 검색어를 입력하세요...", "notice": "📢 공지사항", "auth": "👤 로그인/회원가입",
        "ai_btn": "🤖 AI 요약보기", "ai_modal_title": "⚡ Generative AI 실시간 요약 브리핑"
    },
    "EN": {
        "title": "SKIMO KOREA", "subtitle": "Ski Mountaineering Information Portal",
        "menu": ["Home", "Athlete Registration", "Live Leaderboard", "🔐 Judge/Admin Panel", "📢 Global Notice"],
        "desc": "This tournament complies with ISMF regulations. Scoring and penalties are aggregated in real-time globally via the field web app.",
        "video": "📺 Skimo Rules Video", "intro_video": "⛷️ What is Skimo?", "photo": "📸 Olympic Action Gallery", "pay": "💳 Register & Secure Pay",
        "news_title": "📰 News & Stories (Global Latest News)", "search_holder": "🔍 Search information...", "notice": "📢 Notice", "auth": "👤 Login/Register",
        "ai_btn": "🤖 View AI Summary", "ai_modal_title": "⚡ Generative AI Real-time Briefing"
    }
}

# 다국어 기본 안전장치
if "current_lang_code" not in st.session_state:
    st.session_state.current_lang_code = "KO"
if st.session_state.current_lang_code not in LOCALIZED_TEXT:
    st.session_state.current_lang_code = "KO"

T = LOCALIZED_TEXT[st.session_state.current_lang_code]

# ------------------------------------------
# [🚨 고도화: 영구 저장 방식의 로그인/회원가입 모달]
# ------------------------------------------
@st.dialog("🔐 SKIMO KOREA 계정 관리")
def auth_dialog():
    tab1, tab2 = st.tabs(["👤 로그인", "📝 회원가입"])
    
    with tab1:
        login_id = st.text_input("아이디", key="login_id").strip()
        login_pw = st.text_input("비밀번호", type="password", key="login_pw").strip()
        if st.button("로그인 완료", use_container_width=True):
            # 파일에서 실시간으로 다시 읽어와 검증
            current_db = load_user_db()
            if login_id in current_db and current_db[login_id]["pw"] == login_pw:
                st.session_state.logged_in_user = login_id
                st.success(f"🎉 반갑습니다, {login_id}님! 로그인 성공.")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("❌ 아이디 또는 비밀번호가 일치하지 않습니다.")
                
    with tab2:
        reg_id = st.text_input("새로운 아이디 생성", key="reg_id").strip()
        reg_pw = st.text_input("새로운 비밀번호 설정", type="password", key="reg_pw").strip()
        reg_pw_confirm = st.text_input("비밀번호 확인", type="password", key="reg_pw_confirm").strip()
        
        if st.button("회원가입 신청", use_container_width=True):
            current_db = load_user_db()
            if not reg_id or not reg_pw:
                st.warning("⚠️ 아이디와 비밀번호를 모두 입력해주세요.")
            elif reg_id in current_db:
                st.error("❌ 이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요.")
            elif reg_pw != reg_pw_confirm:
                st.error("❌ 비밀번호 확인이 일치하지 않습니다.")
            else:
                # 새로운 유저 정보를 로컬 파일 데이터베이스에 저장
                current_db[reg_id] = {"pw": reg_pw, "role": "USER"}
                save_user_db(current_db)
                st.session_state.user_db = current_db  # 상태 동기화
                st.success("🚀 회원가입 성공! 이제 로그인 탭에서 로그인해 주세요.")

# 생성형 AI 기반 뉴스 요약 모달 창 정의
@st.dialog("🎯 AI 요약 브리핑")
def ai_summary_dialog(news_item, lang_code):
    st.markdown(f"### {T['ai_modal_title']}")
    st.write("---")
    current_title = news_item["title"].get(lang_code, news_item["title"]["EN"])
    st.markdown(f"**📌 대상 뉴스:** {current_title}")
    with st.spinner("LLM 인퍼런스 엔진 가동 중..."):
        time.sleep(0.7)
    summary_content = news_item["ai_summary"].get(lang_code, news_item["ai_summary"]["EN"])
    st.markdown(summary_content)
    st.write("---")
    st.link_button("🔗 원문 뉴스 링크 열기 (ISMF)", news_item["link"], use_container_width=True)

# ==========================================
# 3. 글로벌 상단 동적 라우터 바
# ==========================================
st.markdown('<div class="custom-header-bg">', unsafe_allow_html=True)
st.markdown('<div class="centered-wrapper">', unsafe_allow_html=True)

c_menu, c_search, c_right = st.columns([3, 4, 5])

SEARCH_KEYWORDS = {
    0: ["홈", "대회", "소개", "뉴스", "home", "news"],
    1: ["선수", "참가", "신청", "등록", "접수"],
    2: ["실시간", "리더", "라이브", "순위", "live"],
    3: ["심판", "관리자", "패널", "judge"],
    4: ["공지", "사항", "알림", "notice"]
}

with c_search:
    search_query = st.text_input("Search", placeholder=T["search_holder"], label_visibility="collapsed")
    if search_query:
        query_clean = search_query.strip().lower()
        for idx, keywords in SEARCH_KEYWORDS.items():
            if any(kw in query_clean for kw in keywords):
                if st.session_state.menu_idx != idx:
                    st.session_state.menu_idx = idx
                    st.rerun()

with c_menu:
    menu_list = list(T["menu"])
    selected_menu_raw = st.selectbox("Menu", menu_list, index=st.session_state.menu_idx if st.session_state.menu_idx < len(menu_list) else 0, label_visibility="collapsed")
    menu_index = menu_list.index(selected_menu_raw)
    if st.session_state.menu_idx != menu_index:
        st.session_state.menu_idx = menu_index
        st.rerun()

with c_right:
    sub_lang, sub_buttons = st.columns([4, 6])
    with sub_lang:
        selected_lang_name = st.selectbox("Language", list(LANG_DICT.keys()), index=0, label_visibility="collapsed")
        new_lang_code = LANG_DICT[selected_lang_name]
        if st.session_state.current_lang_code != new_lang_code:
            st.session_state.current_lang_code = new_lang_code
            st.rerun()
    with sub_buttons:
        if st.session_state.logged_in_user is None:
            if st.button(T["auth"]): auth_dialog()
        else:
            if st.button(f"🔓 로그아웃 ({st.session_state.logged_in_user})"):
                st.session_state.logged_in_user = None
                st.rerun()

st.markdown('</div></div>', unsafe_allow_html=True)

# 메인 뷰포트 레이아웃 상자 구동
st.markdown(f'<div class="centered-wrapper"><div class="hero-section"><div class="hero-title">{T["title"]}</div><div class="hero-subtitle">🏔️ {T["subtitle"]}</div></div></div>', unsafe_allow_html=True)
st.markdown('<div class="content-box">', unsafe_allow_html=True)

# -------------------------------------------------------------------------
# [라우터 메뉴 분기 제어 체계]
# -------------------------------------------------------------------------
if st.session_state.menu_idx == 0:
    st.markdown("## 🏁 Upcoming Events & Overview")
    col_text, col_video, col_intro, col_photo = st.columns([3, 3, 3, 3])
    
    with col_text:
        st.markdown("### 📢 Information")
        st.write(T["desc"])
        st.markdown("* **Location:** Pyeongchang, KOREA\n* **Sanctioned by:** ISMF\n* **Scale:** 3,000+ Participants")
        
    with col_video:
        st.markdown(f"### {T['video']}")
        st.video("https://youtu.be/KgyX5OjMTyM")

    with col_intro:
        st.markdown(f"### {T['intro_video']}")
        st.video("https://youtu.be/nLjES8kuFRg")

    with col_photo:
        st.markdown(f"### {T['photo']}")
        gallery_images = [
            {"path": "skimo_race_1.jpg", "caption": "❄️ 눈보라를 뚫고 올라가는 레이스"},
            {"path": "skimo_race_2.jpg", "caption": "🏅 영광의 시상대 현장"},
            {"path": "skimo_race_3.jpg", "caption": "🎉 박진감 넘치는 다운힐 피니시"}
        ]
        photo_idx = st.radio("Photo Select", [1, 2, 3], horizontal=True, label_visibility="collapsed")
        selected_photo = gallery_images[photo_idx - 1]
        
        try:
            st.image(selected_photo["path"], caption=selected_photo["caption"], use_container_width=True)
        except:
            import urllib.parse
            encoded_filename = urllib.parse.quote(selected_photo["path"])
            github_url = f"https://raw.githubusercontent.com/pyminno12/skimo-website/main/{encoded_filename}"
            st.image(github_url, caption=selected_photo["caption"], use_container_width=True)

    st.markdown("<hr style='border-color: rgba(255,255,255,0.15);'>", unsafe_allow_html=True)
    st.markdown(f"## {T['news_title']}")
    
    lang_code = st.session_state.current_lang_code
    for item in st.session_state.home_news_domain:
        localized_news_title = item["title"].get(lang_code, item["title"]["EN"])
        c_news_title, c_news_btn = st.columns([8, 2])
        with c_news_title:
            st.markdown(f"""
                <div class="news-flex-container">
                    <span class="news-title-link">📌 {localized_news_title}</span>
                    <span class="news-date-span">📅 {item['date']}</span>
                </div>
            """, unsafe_allow_html=True)
        with c_news_btn:
            if st.button(T["ai_btn"], key=f"btn_ai_{item['id']}", use_container_width=True):
                ai_summary_dialog(item, lang_code)

elif st.session_state.menu_idx == 1:
    st.markdown(f"## {T['menu'][1]}")
    with st.form("reg_form"):
        p_name = st.text_input("Athlete Name")
        p_nation = st.text_input("Country/Team")
        p_event = st.selectbox("Category", ["Sprint", "Individual", "Vertical"])
        if st.form_submit_button(T["pay"]) and p_name:
            next_bib = str(100 + len(st.session_state.athletes_domain) + 1)
            st.session_state.athletes_domain[next_bib] = {"Name": p_name, "Team": p_nation, "Category": p_event, "Status": "RACING", "CP1": "--:--:--", "CP2": "--:--:--", "Penalty_Sec": 0, "Final_Record": "--:--:--"}
            st.success(f"선수 등록 완료! 배정 배번호: [{next_bib}]")

elif st.session_state.menu_idx == 2:
    st.markdown(f"## {T['menu'][2]}")
    data_list = [{"BIB": b, **i} for b, i in st.session_state.athletes_domain.items()]
    df = pd.DataFrame(data_list)[["BIB", "Name", "Team", "Category", "Status", "CP1", "CP2", "Penalty_Sec", "Final_Record"]]
    st.dataframe(df.set_index("BIB"), use_container_width=True)

elif st.session_state.menu_idx == 3:
    st.markdown(f"## {T['menu'][3]}")
    if st.session_state.logged_in_user is None:
        st.warning("⚠️ 권한 경고: 심판 계정으로 로그인이 필요합니다.")
    else:
        # 현재 로그인된 유저의 권한 파악
        current_db = load_user_db()
        user_role = current_db.get(st.session_state.logged_in_user, {}).get("role", "USER")
        
        if user_role not in ["ADMIN", "JUDGE"]:
            st.error("🚫 접근 거부: 귀하는 일반 사용자로, 심판/관리자 패널을 조작할 권한이 없습니다.")
        else:
            bib_list = list(st.session_state.athletes_domain.keys())
            selected_bib = st.selectbox("업데이트할 BIB 선택", bib_list)
            new_status = st.selectbox("상태 값 변경", ["RACING", "FINISHED", "DNF", "DSQ"])
            if st.button("🚨 데이터 필드 실시간 동기화"):
                st.session_state.athletes_domain[selected_bib]["Status"] = new_status
                st.success(f"배번호 {selected_bib}번 선수의 경기 상태가 {new_status}로 변경 및 동기화되었습니다.")
                time.sleep(0.5)
                st.rerun()

elif st.session_state.menu_idx == 4:
    st.markdown(f"## {T['menu'][4]}")
    lang_code = st.session_state.current_lang_code
    for item in st.session_state.notice_domain:
        title_text = item["title"].get(lang_code, item["title"]["EN"])
        content_text = item["content"].get(lang_code, item["content"]["EN"])
        st.markdown(f'<div class="notice-card"><div><span class="notice-badge">{item["category"]}</span><span>📅 {item["date"]}</span></div><div style="font-size:18px; font-weight:600; margin:10px 0;">{title_text}</div><div>{content_text}</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
