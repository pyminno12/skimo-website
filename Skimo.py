import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ==========================================
# 1. 페이지 설정 및 레이아웃 규격 최적화
# ==========================================
st.set_page_config(page_title="SKIMO KOREA", page_icon="🏔️", layout="wide")

# 배경 이미지 링크 매핑 (선택된 메뉴에 따라 유동적으로 변화)
BG_IMAGES = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=1800&q=80"   
]

# 시스템 구동에 필요한 세션 구조 초기화
if "menu_idx" not in st.session_state:
    st.session_state.menu_idx = 0
if "user_db" not in st.session_state:
    # 데모용 기본 회원 데이터베이스 (아이디: 비밀번호)
    st.session_state.user_db = {"admin": "1234", "skimo": "skimo123"}
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

selected_bg = BG_IMAGES[st.session_state.menu_idx]

# 전체 화면 배경 스타일 및 컴포넌트 커스텀 CSS 적용
st.markdown(f"""
    <style>
    /* -------------------------------------------
       [기본 바 완전 제거] 스트림릿 기본 상단 바 제거
    ------------------------------------------- */
    header[data-testid="stHeader"] {{
        display: none !important;
    }}
    .stAppDeployDropdown {{
        display: none !important;
    }}
    
    /* -------------------------------------------
       마우스 커서 텍스트 입력창 변환 방지 규칙
    ------------------------------------------- */
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

    /* 스트림릿 기본 사이드바 숨기기 및 본문 패딩 제로화 */
    [data-testid="stSidebar"] {{
        display: none !important;
    }}
    
    .block-container {{
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }}
    
    /* -------------------------------------------
       [핵심 수정] 웹사이트 전체를 감싸는 산악 배경화면 설정
    ------------------------------------------- */
    .stApp {{
        background: linear-gradient(rgba(15, 32, 39, 0.85), rgba(44, 83, 100, 0.75)), url('{selected_bg}') no-repeat center center fixed;
        background-size: cover !important;
    }}
    
    /* 중앙 정렬 컨테이너 규격 (최대 1200px 제한) */
    .centered-wrapper {{
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }}
    
    /* 상단 투명 네비게이션 바 배경 */
    .custom-header-bg {{
        background-color: rgba(15, 32, 39, 0.4);
        backdrop-filter: blur(5px);
        width: 100%;
        padding: 10px 0;
    }}
    
    /* 우측 상단 메뉴 텍스트 및 스트림릿 버튼 커스텀 내포 스타일 */
    .right-nav-item {{
        color: #ffffff;
        font-size: 14px;
        font-weight: 500;
        text-decoration: none;
        margin-left: 20px;
        cursor: pointer;
        transition: color 0.2s;
    }}
    .right-nav-item:hover {{
        color: #00c6ff;
    }}
    
    /* 스트림릿 기본 링크 버튼을 상단 GNB 내비게이션 바 테마에 맞춤 튜닝 */
    div.stButton > button {{
        background: transparent !important;
        color: white !important;
        border: none !important;
        padding: 0px !important;
        margin-left: 20px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: color 0.2s !important;
    }}
    div.stButton > button:hover {{
        color: #00c6ff !important;
        background: transparent !important;
    }}
    div.stButton > button:focus {{
        color: #00c6ff !important;
        box-shadow: none !important;
    }}
    
    /* 깔끔하고 컴팩트한 타이틀 섹션 */
    .hero-section {{
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        text-align: center;
    }}
    .hero-title {{ font-size: 42px; font-weight: 800; text-shadow: 3px 3px 8px rgba(0,0,0,0.9); margin-bottom: 5px; letter-spacing: 1px; }}
    .hero-subtitle {{ font-size: 18px; font-weight: 500; text-shadow: 2px 2px 4px rgba(0,0,0,0.7); color: #00c6ff; }}
    
    /* -------------------------------------------
       [핵심 수정] 하단 설명 레이아웃까지 배경이 투명하게 비치는 글래스모피즘 컨테이너
    ------------------------------------------- */
    .content-box {{ 
        max-width: 1200px; 
        margin: 0 auto 50px auto; 
        padding: 30px; 
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #ffffff;
    }}
    
    /* 하단 글래스 박스 안의 텍스트 및 헤더 가독성 확보 */
    .content-box h1, .content-box h2, .content-box h3, .content-box p, .content-box li {{
        color: #ffffff !important;
    }}
    
    /* 리스트형 뉴스 레이아웃 스타일 */
    .news-list-item {{
        padding: 14px 15px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.15);
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
        "video": "📺 경기 종목 안내", "intro_video": "⛷️ 산악스키 소개", "photo": "📸 올림픽 현장 갤러리", "pay": "💳 참가 신청 및 안전 결제",
        "news_title": "📰 News & Stories (최신 소식)", "news_tag": "대회 뉴스",
        "search_holder": "🔍 검색어를 입력하세요..."
    },
    "EN": {
        "title": "SKIMO KOREA",
        "subtitle": "Ski Mountaineering Information Portal",
        "menu": ["Home", "Athlete Registration", "Live Leaderboard", "🔐 Judge/Admin Panel"],
        "desc": "This tournament complies with ISMF regulations. Scoring and penalties are aggregated in real-time globally via the field web app.",
        "video": "📺 Skimo Rules Video", "intro_video": "⛷️ What is Skimo?", "photo": "📸 Olympic Action Gallery", "pay": "💳 Register & Secure Pay",
        "news_title": "📰 News & Stories", "news_tag": "Official News",
        "search_holder": "🔍 Search information..."
    }
}

for lang in ["FR", "IT", "ZH", "JA"]:
    if lang not in LOCALIZED_TEXT:
        LOCALIZED_TEXT[lang] = LOCALIZED_TEXT["EN"]

# ==========================================
# [기능 추가] 로그인 및 회원가입 모달 대화상자 함수
# ==========================================
@st.dialog("🔐 SKIMO KOREA 계정 관리")
def auth_dialog():
    tab1, tab2 = st.tabs(["👤 로그인", "📝 회원가입"])
    
    with tab1:
        st.write("포털 서비스를 위해 로그인해 주세요.")
        login_id = st.text_input("아이디", key="login_id")
        login_pw = st.text_input("비밀번호", type="password", key="login_pw")
        
        if st.button("로그인 완료", use_container_width=True):
            if login_id in st.session_state.user_db and st.session_state.user_db[login_id] == login_pw:
                st.session_state.logged_in_user = login_id
                st.success(f"🎉 {login_id}님, 환영합니다!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ 아이디 또는 비밀번호가 일치하지 않습니다.")
                
    with tab2:
        st.write("새로운 SKIMO KOREA 계정을 생성합니다.")
        new_id = st.text_input("사용할 아이디", key="new_id")
        new_pw = st.text_input("비밀번호 설정", type="password", key="new_pw")
        new_pw_confirm = st.text_input("비밀번호 확인", type="password", key="new_pw_confirm")
        
        if st.button("회원가입 신청", use_container_width=True):
            if not new_id or not new_pw:
                st.warning("⚠️ 아이디와 비밀번호를 모두 입력해 주세요.")
            elif new_id in st.session_state.user_db:
                st.error("❌ 이미 존재하는 아이디입니다.")
            elif new_pw != new_pw_confirm:
                st.error("❌ 비밀번호 확인이 일치하지 않습니다.")
            else:
                st.session_state.user_db[new_id] = new_pw
                st.success("📝 회원가입이 완료되었습니다! 로그인 탭에서 로그인해 주세요.")

# ==========================================
# 3. 상단 레이아웃 배치
# ==========================================
st.markdown('<div class="custom-header-bg">', unsafe_allow_html=True)
st.markdown('<div class="centered-wrapper">', unsafe_allow_html=True)

c_menu, c_search, c_right = st.columns([3, 4, 5])

with c_menu:
    selected_menu_raw = st.selectbox("Menu Select", list(LOCALIZED_TEXT["KO"]["menu"]), label_visibility="collapsed")
    menu_index = LOCALIZED_TEXT["KO"]["menu"].index(selected_menu_raw)
    if st.session_state.menu_idx != menu_index:
        st.session_state.menu_idx = menu_index
        st.rerun()
    
with c_search:
    search_query = st.text_input("Search", placeholder=LOCALIZED_TEXT["KO"]["search_holder"], label_visibility="collapsed")
    
with c_right:
    sub_lang, sub_buttons = st.columns([4, 6])
    with sub_lang:
        selected_lang_name = st.selectbox("Global Select", list(LANG_DICT.keys()), label_visibility="collapsed")
        current_lang = LANG_DICT[selected_lang_name]
        T = LOCALIZED_TEXT[current_lang]
        
    with sub_buttons:
        # 로그인 상태에 따른 GNB 우측 단추 분기 제어 영역
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            st.markdown("<div style='margin-top: 6px;'><a class='right-nav-item' href='#'>📢 공지사항</a></div>", unsafe_allow_html=True)
        with btn_col2:
            if st.session_state.logged_in_user is None:
                # 클릭 시 파이썬 내부 모달(auth_dialog)을 호출하도록 스트림릿 버튼 배치
                if st.button("👤 로그인/회원가입", key="auth_btn"):
                    auth_dialog()
            else:
                # 로그인 완료 시 로그아웃 단추 표시
                if st.button(f"🔓 로그아웃 ({st.session_state.logged_in_user})", key="logout_btn"):
                    st.session_state.logged_in_user = None
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. 히어로 타이틀 영역 (배경을 제거하여 전체 화면 산과 병합)
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
# 5. 세션 데이터 및 메인 스페이스 바인딩
# ==========================================
if "athletes" not in st.session_state:
    st.session_state.athletes = [
        {"BIB": "101", "Name": "김민우", "Team": "KOREA", "Status": "RACING", "CP1": "10:15:20", "CP2": "--:--:--", "Penalty": "None"},
        {"BIB": "102", "Name": "Alex Smith", "Team": "USA", "Status": "RACING", "CP1": "10:14:05", "CP2": "10:45:12", "Penalty": "None"},
        {"BIB": "103", "Name": "Chloe", "Team": "FRANCE", "Status": "RACING", "CP1": "10:16:55", "CP2": "10:49:30", "Penalty": "None"},
    ]

# 반투명 글래스 컨테이너 시작
st.markdown('<div class="content-box">', unsafe_allow_html=True)

# 로그인 성공 메시지 홈 배너 노출
if st.session_state.logged_in_user:
    st.toast(f"🔒 {st.session_state.logged_in_user}님 계정으로 보안 접속 중")

if search_query:
    st.info(f"🔍 '{search_query}'에 대한 포털 내 실시간 검색 결과 매칭 중...")

# -------------------------------------------------------------------------
# [콘텐츠 분기 1] 대회 홈 화면
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
        st.success("✨ **Skin Redesigned**\nISMF 공식 홈페이지처럼 광활한 만년설 산악 배경이 중앙과 하단 콘텐츠 영역까지 전체적으로 부드럽게 흐르도록 통합되었습니다.")
        
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

    # 📰 NEWS & STORIES
    st.markdown("<hr style='border-color: rgba(255,255,255,0.15);'>", unsafe_allow_html=True)
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
    
    st.markdown("<div style='background-color: rgba(255, 255, 255, 0.05); padding: 10px 20px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
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
# [콘텐츠 분기 3] 실시간 리더보드
# -------------------------------------------------------------------------
elif menu_index == 2:
    st.markdown(f"## {LOCALIZED_TEXT['KO']['menu'][2]}")
    df = pd.DataFrame(st.session_state.athletes)
    st.dataframe(df.set_index("BIB"), use_container_width=True)

# -------------------------------------------------------------------------
# [콘텐츠 분기 4] 심판 패널
# -------------------------------------------------------------------------
elif menu_index == 3:
    st.markdown(f"## {LOCALIZED_TEXT['KO']['menu'][3]}")
    st.info("System operational. Field telemetry bridge secure.")

st.markdown('</div>', unsafe_allow_html=True) # 반투명 글래스 컨테이너 끝
