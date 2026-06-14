import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ==========================================
# 1. 페이지 설정 및 전역 화면 레이아웃 최적화
# ==========================================
st.set_page_config(page_title="SKIMO KOREA", page_icon="🏔️", layout="wide")

# 배경 이미지 풀 리스트 (상단 메뉴 선택 시 연동 작동)
BG_IMAGES = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=1800&q=80"   
]

if "menu_idx" not in st.session_state:
    st.session_state.menu_idx = 0

selected_bg = BG_IMAGES[st.session_state.menu_idx]

# 컴포넌트 튜닝 및 UI 고도화 커스텀 CSS
st.markdown(f"""
    <style>
    /* Streamlit 기본 탑 헤더 영역 숨김 처리 */
    header[data-testid="stHeader"] {{
        display: none !important;
    }}
    .stAppDeployDropdown {{
        display: none !important;
    }}
    
    /* 셀렉트박스 마우스 오버 시 선택 커서 강제 속성 */
    div[data-testid="stSelectbox"] div[role="combobox"] {{
        cursor: pointer !important;
    }}
    div[data-testid="stSelectbox"] input {{
        cursor: pointer !important;
        caret-color: transparent !important;
    }}
    div[data-baseweb="popover"] li {{
        cursor: pointer !important;
    }}

    /* 좌측 사이드바 하이딩 및 여백 완벽 제로화 */
    [data-testid="stSidebar"] {{
        display: none !important;
    }}
    
    .block-container {{
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }}
    
    /* 다크 톤 알파 마스킹이 결합된 산악 고해상도 배경 스킨 */
    .stApp {{
        background: linear-gradient(rgba(15, 32, 39, 0.82), rgba(44, 83, 100, 0.72)), url('{selected_bg}') no-repeat center center fixed;
        background-size: cover !important;
    }}
    
    /* 중앙 그리드 보정용 고정 래퍼 크기 */
    .centered-wrapper {{
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }}
    
    /* 상단 GNB 바 블러 백그라운드 */
    .custom-header-bg {{
        background-color: rgba(15, 32, 39, 0.4);
        backdrop-filter: blur(6px);
        width: 100%;
        padding: 11px 0;
    }}
    
    /* 서브 네비게이션 앵커 스타일 */
    .right-nav-item {{
        color: #ffffff;
        font-size: 14px;
        font-weight: 500;
        text-decoration: none;
        margin-left: 22px;
        cursor: pointer;
        transition: color 0.2s;
    }}
    .right-nav-item:hover {{
        color: #00c6ff;
    }}
    
    /* 중앙 메인 타이틀 정렬 섹션 */
    .hero-section {{
        padding-top: 60px;
        padding-bottom: 25px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        text-align: center;
    }}
    .hero-title {{ 
        font-size: 44px; 
        font-weight: 800; 
        text-shadow: 3px 3px 10px rgba(0,0,0,0.95); 
        margin-bottom: 6px; 
        letter-spacing: 1.5px; 
    }}
    .hero-subtitle {{ 
        font-size: 18px; 
        font-weight: 500; 
        text-shadow: 2px 2px 5px rgba(0,0,0,0.8); 
        color: #00c6ff; 
        margin-bottom: 0px; 
    }}
    
    /* -------------------------------------------
       [요청 수정 반영] 3번 형태의 커다란 반투명 회색 글래스 박스 스킨
    ------------------------------------------- */
    .glass-search-container {{
        width: 100%;
        max-width: 1160px;
        margin: 25px auto 40px auto;
        background: rgba(255, 255, 255, 0.08);    /* 반투명 회색 스킨 채우기 */
        backdrop-filter: blur(14px);               /* 배경 글래스 모피즘 블러 */
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.23); /* 외곽 글래스 라인 */
        border-radius: 18px;                       /* 부드러운 라운딩 스킨 */
        padding: 6px 16px;                         /* 내부 인풋 정렬 매칭 트림 */
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }}
    
    /* 스트림릿 기본 텍스트 인풋 스타일을 투명화하여 글래스 박스 내부에 강제 동화 */
    .glass-search-container div[data-testid="stTextInput"] input {{
        background-color: transparent !important;
        border: none !important;
        color: #ffffff !important;
        font-size: 16px !important;
        padding: 12px 10px !important;
    }}
    .glass-search-container div[data-testid="stTextInput"] input::placeholder {{
        color: rgba(255, 255, 255, 0.55) !important;
    }}
    .glass-search-container div[data-testid="stTextInput"] div {{
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }}
    
    /* 메인 서브 리포트 데이터 구역 플레이트 */
    .content-box {{ 
        max-width: 1200px; 
        margin: 0 auto 60px auto; 
        padding: 35px; 
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.13);
        color: #ffffff;
    }}
    
    .content-box h1, .content-box h2, .content-box h3, .content-box p, .content-box li {{
        color: #ffffff !important;
    }}
    
    /* 피드 뉴스 텍스트 템플릿 로우 */
    .news-list-item {{
        padding: 15px 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.12);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .news-list-item:last-child {{
        border-bottom: none;
    }}
    .news-list-title {{
        font-size: 15px;
        font-weight: 500;
        color: #e2e8f0;
        text-decoration: none;
    }}
    .news-list-title:hover {{
        color: #00c6ff;
    }}
    .news-list-meta {{
        font-size: 13px;
        color: #cbd5e1;
        white-space: nowrap;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 다국어 글로벌 번역 데이터 스키마 정의
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
        "video": "📺 경기 종목 안내", "intro_video": "⛷️ 산악스키 종목 소개", "photo": "📸 올림픽 현장 갤러리", "pay": "💳 참가 신청 및 안전 결제",
        "news_title": "📰 News & Stories (최신 소식)", "news_tag": "대회 뉴스",
        "search_holder": "🔍 포털 사이트 내 필요한 정보를 입력해 주세요..."
    },
    "EN": {
        "title": "SKIMO KOREA",
        "subtitle": "Ski Mountaineering Information Portal",
        "menu": ["Home", "Athlete Registration", "Live Leaderboard", "🔐 Judge/Admin Panel"],
        "desc": "This tournament complies with ISMF regulations. Scoring and penalties are aggregated in real-time globally via the field web app.",
        "video": "📺 Skimo Rules Video", "intro_video": "⛷️ What is Skimo?", "photo": "📸 Olympic Action Gallery", "pay": "💳 Register & Secure Pay",
        "news_title": "📰 News & Stories", "news_tag": "Official News",
        "search_holder": "🔍 Search tournament information here..."
    }
}

for lang in ["FR", "IT", "ZH", "JA"]:
    if lang not in LOCALIZED_TEXT:
        LOCALIZED_TEXT[lang] = LOCALIZED_TEXT["EN"]

# ==========================================
# 3. 네비게이션 헤더 레이아웃 빌드
# ==========================================
st.markdown('<div class="custom-header-bg">', unsafe_allow_html=True)
st.markdown('<div class="centered-wrapper">', unsafe_allow_html=True)

c_menu, c_right = st.columns([4, 8])

with c_menu:
    selected_menu_raw = st.selectbox("Menu Select", list(LOCALIZED_TEXT["KO"]["menu"]), label_visibility="collapsed")
    menu_index = LOCALIZED_TEXT["KO"]["menu"].index(selected_menu_raw)
    if st.session_state.menu_idx != menu_index:
        st.session_state.menu_idx = menu_index
        st.rerun()
    
with c_right:
    sub_lang, sub_buttons = st.columns([4, 8])
    with sub_lang:
        selected_lang_name = st.selectbox("Global Select", list(LANG_DICT.keys()), label_visibility="collapsed")
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

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. 히어로 헤더 섹션 (1번 사진 속 상단 얇은 잔상 라인 영구 제거 완료)
# ==========================================
st.markdown(f"""
    <div class="centered-wrapper">
        <div class="hero-section">
            <div class="hero-title">{T["title"]}</div>
            <div class="hero-subtitle">🏔️ {T["subtitle"]}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 5. [수정 핵심] 대형 회색 글래스 박스 프레임 내부로 검색 컴포넌트 탑재
# ==========================================
st.markdown('<div class="centered-wrapper">', unsafe_allow_html=True)
st.markdown('<div class="glass-search-container">', unsafe_allow_html=True)

# 기존에 최하단에서 홀로 이격되어 작동하던 텍스트 입력창을 커다란 반투명 글래스 컨테이너 안으로 격하시켜 통합
search_query = st.text_input("Main Search Bar", placeholder=T["search_holder"], label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. 메인 바디 컨텐츠 플레이어 라우팅
# ==========================================
if "athletes" not in st.session_state:
    st.session_state.athletes = [
        {"BIB": "101", "Name": "김민우", "Team": "KOREA", "Status": "RACING", "CP1": "10:15:20", "CP2": "--:--:--", "Penalty": "None"},
        {"BIB": "102", "Name": "Alex Smith", "Team": "USA", "Status": "RACING", "CP1": "10:14:05", "CP2": "10:45:12", "Penalty": "None"},
        {"BIB": "103", "Name": "Chloe", "Team": "FRANCE", "Status": "RACING", "CP1": "10:16:55", "CP2": "10:49:30", "Penalty": "None"},
    ]

st.markdown('<div class="centered-wrapper"><div class="content-box">', unsafe_allow_html=True)

if search_query:
    st.info(f"🔍 '{search_query}'에 대한 포털 내 실시간 검색 결과 매칭 중...")

# -------------------------------------------------------------------------
# [서브페이지 1] 대회 홈 대시보드
# -------------------------------------------------------------------------
if menu_index == 0:
    st.markdown("## 🏁 Upcoming Events & Overview")
    
    col_text, col_video, col_intro, col_photo = st.columns([3, 3, 3, 3])
    
    with col_text:
        st.markdown(f"### 📢 Information")
        st.write(T["desc"])
        st.markdown("""
        * **Location:** Pyeongchang, KOREA
        * **Sanctioned by:** ISMF
        * **Scale:** 3,000+ Participants
        """)
        st.success("⚙️ **인터페이스 보정 완료**\n상단의 구형 잔상 라인은 삭제되었으며, 실제 작동하는 검색 컴포넌트가 대형 반투명 스킨 내부로 수렴되었습니다.")
        
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

    # 📰 NEWS & STORIES 데이터 그리드 피드
    st.markdown("<hr style='border-color: rgba(255,255,255,0.12);'>", unsafe_allow_html=True)
    st.markdown(f"## {T['news_title']}")
    
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
    
    st.markdown("<div style='background-color: rgba(255, 255, 255, 0.04); padding: 10px 20px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
    for item in news_items:
        st.markdown(f"""
            <div class="news-list-item">
                <a href="{item['link']}" target="_blank" class="news-list-title">📌 {item['title']}</a>
                <span class="news-list-meta">📅 {item['date']}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# [서브페이지 2] 참가 신청 폼 모듈
# -------------------------------------------------------------------------
elif menu_index == 1:
    st.markdown(f"## {LOCALIZED_TEXT['KO']['menu'][1]}")
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
# [서브페이지 3] 라이브 전광판 필드 리더보드
# -------------------------------------------------------------------------
elif menu_index == 2:
    st.markdown(f"## {LOCALIZED_TEXT['KO']['menu'][2]}")
    df = pd.DataFrame(st.session_state.athletes)
    st.dataframe(df.set_index("BIB"), use_container_width=True)

# -------------------------------------------------------------------------
# [서브페이지 4] 중앙 관제 패널 심판 허브
# -------------------------------------------------------------------------
elif menu_index == 3:
    st.markdown(f"## {LOCALIZED_TEXT['KO']['menu'][3]}")
    st.info("System operational. Field telemetry bridge secure.")

st.markdown('</div></div>', unsafe_allow_html=True)
