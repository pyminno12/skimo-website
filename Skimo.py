import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ==========================================
# 1. 페이지 설정 및 풀 와이드 CSS 레이아웃 구조 정의
# ==========================================
st.set_page_config(page_title="SKIMO KOREA", page_icon="🏔️", layout="wide")

# 사이드바/시스템 바 제거 및 상단 커스텀 내비게이션 UI 디자인을 위한 CSS
st.markdown("""
    <style>
    /* -------------------------------------------
       [기본 바 완전 제거] 스트림릿 기본 상단 바 제거
    ------------------------------------------- */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    .stAppDeployDropdown {
        display: none !important;
    }
    
    /* -------------------------------------------
       마우스 커서 텍스트 입력창 변환 방지 규칙
    ------------------------------------------- */
    div[data-testid="stSelectbox"] div[role="combobox"] {
        cursor: pointer !important;
    }
    div[data-testid="stSelectbox"] input {
        cursor: pointer !important;
        caret-color: transparent !important;
    }
    div[data-baseweb="popover"] li {
        cursor: pointer !important;
    }

    /* 스트림릿 기본 사이드바 숨기기 및 본문 패딩 제로화 */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    .block-container {
        padding-top: 0rem;
        padding-bottom: 3rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    
    /* 우측 상단 메뉴 텍스트 스타일 */
    .right-nav-item {
        color: #ffffff;
        font-size: 15px;
        font-weight: 500;
        text-decoration: none;
        margin-left: 25px;
        cursor: pointer;
        transition: color 0.2s;
    }
    .right-nav-item:hover {
        color: #00c6ff;
    }
    
    /* 웅장한 히어로 배너 영역 스타일 */
    .hero-section {
        background-size: cover;
        height: 380px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        text-align: center;
        padding: 20px;
    }
    .hero-title { font-size: 46px; font-weight: 800; text-shadow: 3px 3px 6px rgba(0,0,0,0.8); margin-bottom: 12px; letter-spacing: 2px; }
    .hero-subtitle { font-size: 20px; font-weight: 500; text-shadow: 2px 2px 4px rgba(0,0,0,0.6); color: #00c6ff; }
    
    /* 콘텐츠 컨테이너 크기 제한 */
    .content-box { max-width: 1400px; margin: 0 auto; padding: 30px 20px; }
    
    /* 리스트형 뉴스 레이아웃 스타일 */
    .news-list-item {
        padding: 18px 15px;
        border-bottom: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .news-list-item:last-child {
        border-bottom: none;
    }
    .news-list-title {
        font-size: 16px;
        font-weight: 500;
        color: #1e293b;
        text-decoration: none;
    }
    .news-list-title:hover {
        color: #00c6ff;
    }
    .news-list-meta {
        font-size: 14px;
        color: #64748b;
        white-space: nowrap;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 다국어 데이터 배열 및 텍스트 셋업
# ==========================================
LANG_DICT = {
    "한국어 (KO)": "KO", "English (EN)": "EN", "Français (FR)": "FR",       
    "Italiano (IT)": "IT", "简体中文 (ZH)": "ZH", "日本語 (JA)": "JA"          
}

LOCALIZED_TEXT = {
    "KO": {
        "title": "SKIMO KOREA",
        "subtitle": "스키등산 정보 포털",
        "menu": ["대회 홈", "선수 참가 신청", "실시간 리더보드 (LIVE)", "🔐 심판/관리자 패널"],
        "desc": "본 대회는 국제산악스키연맹(ISMF) 규정을 준수하며, field 심판 시스템과 동기화되어 실시간 기록을 전 세계에 생중계합니다.",
        "video": "📺 경기 종목 안내 영상", "intro_video": "⛷️ 산악스키 종목 소개", "photo": "📸 올림픽 현장 갤러리", "pay": "💳 참가 신청 및 안전 결제",
        "news_title": "📰 News & Stories (최신 소식)", "news_tag": "대회 뉴스",
        "search_holder": "🔍 검색어를 입력하고 엔터를 누르세요..."
    },
    "EN": {
        "title": "SKIMO KOREA",
        "subtitle": "Ski Mountaineering Information Portal",
        "menu": ["Home", "Athlete Registration", "Live Leaderboard", "🔐 Judge/Admin Panel"],
        "desc": "This tournament complies with ISMF regulations. Scoring and penalties are aggregated in real-time globally via the field web app.",
        "video": "📺 Skimo Rules Video", "intro_video": "⛷️ What is Skimo?", "photo": "📸 Olympic Action Gallery", "pay": "💳 Register & Secure Pay",
        "news_title": "📰 News & Stories", "news_tag": "Official News",
        "search_holder": "🔍 Search information here..."
    }
}

# 다국어 기본 안전장치
for lang in ["FR", "IT", "ZH", "JA"]:
    if lang not in LOCALIZED_TEXT:
        LOCALIZED_TEXT[lang] = LOCALIZED_TEXT["EN"]

# ==========================================
# 3. [구조 고도화] 상단 레이아웃 배치 (좌측 메뉴 / 중앙 검색창 / 우측 링크)
# ==========================================
top_nav_container = st.container()

with top_nav_container:
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    # 균형감 있는 3분할 윈도우 레이아웃 설정
    c_menu, c_search, c_right = st.columns([3, 4, 4])
    
    with c_menu:
        # [왼쪽 상단] 메뉴 선택창
        selected_menu_raw = st.selectbox("Menu Select", list(LOCALIZED_TEXT["KO"]["menu"]), label_visibility="collapsed")
        menu_index = LOCALIZED_TEXT["KO"]["menu"].index(selected_menu_raw)
        
    with c_search:
        # [중앙 상단] 🔍 정보 탐색용 검색창 추가 완료!
        # 임시 기본 다국어 세팅 분할
        search_lang = LANG_DICT[st.session_state.get('prev_lang', '한국어 (KO)')] if 'prev_lang' in st.session_state else "KO"
        search_query = st.text_input("Search", placeholder=LOCALIZED_TEXT["KO"]["search_holder"], label_visibility="collapsed")
        
    with c_right:
        # [우측 상단] 다국어 선택 및 텍스트 퀵 버튼 링크
        sub_lang, sub_buttons = st.columns([4, 6])
        with sub_lang:
            selected_lang_name = st.selectbox("Global Select", list(LANG_DICT.keys()), label_visibility="collapsed")
            st.session_state['prev_lang'] = selected_lang_name
            current_lang = LANG_DICT[selected_lang_name]
            T = LOCALIZED_TEXT[current_lang]
            
        with sub_buttons:
            st.markdown(
                "<div style='text-align: right; padding-top: 6px; white-space: nowrap;'>"
                "<a class='right-nav-item' href='#'>📢 공지사항</a>"
                "<a class='right-nav-item' href='#'>👤 로그인/회원가입</a>"
                "</div>", 
                unsafe_allow_html=True
            )

# ==========================================
# 4. 히어로 배너 영역 동적 시각화 출력
# ==========================================
BG_IMAGES = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=1800&q=80"   
]
selected_bg = BG_IMAGES[menu_index]

st.markdown(f"""
    <div class="hero-section" style="background: linear-gradient(rgba(15, 32, 39, 0.75), rgba(44, 83, 100, 0.5)), url('{selected_bg}') no-repeat center center; background-size: cover;">
        <div class="hero-title">{T["title"]}</div>
        <div class="hero-subtitle">🏔️ {T["subtitle"]}</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 5. 세션 데이터 및 메인 스페이스 바인딩
# ==========================================
if "athletes" not in st.session_state:
    st.session_state.athletes = [
        {"BIB": "101", "Name": "김민우", "Team": "KOREA", "Status": "RACING", "CP1": "10:15:20", "CP2": "--:--:--", "Penalty": "None"},
        {"BIB": "102", "Name": "Alex Smith", "Team": "USA", "Status": "RACING", "CP1": "10:14:05", "CP2": "10:45:12", "Penalty": "None"},
        {"BIB": "103", "Name": "Chloe", "Team": "FRANCE", "Status": "RACING", "CP1": "10:16:55", "CP2": "10:49:30", "Penalty": "None"},
    ]

st.markdown('<div class="content-box">', unsafe_allow_html=True)

# 검색어가 입력되었을 때 필터링하는 간단한 피드백 메커니즘 추가
if search_query:
    st.info(f"🔍 '{search_query}'에 대한 포털 내 실시간 검색 결과 매칭 중...")

# -------------------------------------------------------------------------
# [콘텐츠 분기 1] 대회 홈 화면
# -------------------------------------------------------------------------
if menu_index == 0:
    st.header("🏁 Upcoming Events & Overview")
    
    col_text, col_video, col_intro, col_photo = st.columns([3, 3, 3, 3])
    
    with col_text:
        st.markdown(f"### 📢 Information")
        st.write(T["desc"])
        st.markdown("""
        * **Location:** Pyeongchang, KOREA
        * **Sanctioned by:** ISMF
        * **Scale:** 3,000+ Participants
        """)
        st.success("🔍 **Center Search System Active**\n이제 상단 중앙 포털 검색 단추를 통해 간편한 정보 서칭을 진행할 수 있습니다.")
        
    with col_video:
        st.markdown(f"### {T['video']}")
        st.video("https://youtu.be/KgyX5OjMTyM?si=Uu8mCwLV2X4an8Wk")

    with col_intro:
        st.markdown(f"### {T['intro_video']}")
        st.video("https://youtu.be/nLjES8kuFRg?si=xu3P1kuKedFOdjRl")

    with col_photo:
        st.markdown(f"### {T['photo']}")
        
        gallery_images = [
            {"path": "skimo_race_1.jpg", "caption": "❄️ 눈보라를 뚫고 올라가는 한계 극복의 업힐 레이스"},
            {"path": "skimo_race_2.jpg", "caption": "🏅 오륜기 마크 앞에서 펼쳐지는 치열한 선두권 경쟁"},
            {"path": "skimo_race_3.jpg", "caption": "🎉 꿈의 무대, 올림픽 포디움에 선 영광의 메달리스트들"}
        ]
        
        photo_idx = st.radio("📸 사진 선택", [1, 2, 3], horizontal=True, label_visibility="collapsed")
        selected_photo = gallery_images[photo_idx - 1]
        
        try:
            st.image(selected_photo["path"], use_container_width=True)
            st.caption(f"<div style='text-align:center; color:#00c6ff; font-weight:bold; margin-top:5px;'>{selected_photo['caption']}</div>", unsafe_allow_html=True)
        except Exception as e:
            import urllib.parse
            encoded_filename = urllib.parse.quote(selected_photo["path"])
            github_raw_url = f"https://raw.githubusercontent.com/pyminno12/skimo-website/main/{encoded_filename}"
            try:
                st.image(github_raw_url, use_container_width=True)
                st.caption(f"<div style='text-align:center; color:#00c6ff; font-weight:bold; margin-top:5px;'>{selected_photo['caption']}</div>", unsafe_allow_html=True)
            except:
                st.error("⚠️ 이미지를 불러오지 못했습니다.")

    # 📰 NEWS & STORIES 세로 리스트 구조
    st.markdown("---")
    st.header(T["news_title"])
    
    news_items = [
        {
            "title": "French Alps 2030 proposal marks major milestone for ski mountaineering",
            "date": "2026-06-09",
            "link": "https://www.ismf-ski.org/"
        },
        {
            "title": "ISMF Releases Provisional 2026/27 International Calendar",
            "date": "2026-06-03",
            "link": "https://www.ismf-ski.org/"
        },
        {
            "title": "Looking Ahead: Key Olympic Qualification Moments in June",
            "date": "2026-05-29",
            "link": "https://www.ismf-ski.org/"
        }
    ]
    
    st.markdown("<div style='background-color: #f8fafc; padding: 10px 20px; border-radius: 8px; border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
    for item in news_items:
        st.markdown(f"""
            <div class="news-list-item">
                <a href="{item['link']}" target="_blank" class="news-list-title">📌 {item['title']}</a>
                <span class="news-list-meta">📅 {item['date']}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# [콘텐츠 분기 2] 선수 참가 신청
# -------------------------------------------------------------------------
elif menu_index == 1:
    st.header(LOCALIZED_TEXT["KO"]["menu"][1])
    with st.form("global_reg_form"):
        p_name = st.text_input("Name")
        p_nation = st.text_input("Nationality")
        p_event = st.selectbox("Event Category", ["Sprint", "Individual", "Vertical"])
        st.metric("Registration Fee", "30,000 KRW")
        submit_btn = st.form_submit_button(T["pay"])
        if submit_btn and p_name:
            new_member = {"BIB": str(100 + len(st.session_state.athletes)+1), "Name": p_name, "Team": p_nation, "Status": "RACING", "CP1": "--:--:--", "CP2": "--:--:--", "Penalty": "None"}
            st.session_state.athletes.append(new_member)
            st.success("Registration Successful!")

# -------------------------------------------------------------------------
# [콘텐츠 분기 3] 실시간 리더보드
# -------------------------------------------------------------------------
elif menu_index == 2:
    st.header(LOCALIZED_TEXT["KO"]["menu"][2])
    df = pd.DataFrame(st.session_state.athletes)
    st.dataframe(df.set_index("BIB"), use_container_width=True)

# -------------------------------------------------------------------------
# [콘텐츠 분기 4] 심판 패널
# -------------------------------------------------------------------------
elif menu_index == 3:
    st.header(LOCALIZED_TEXT["KO"]["menu"][3])
    st.info("System operational. Field telemetry bridge secure.")

st.markdown('</div>', unsafe_allow_html=True)
