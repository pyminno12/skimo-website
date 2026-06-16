import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ==========================================
# 1. 페이지 설정 및 레이아웃 규격 최적화
# ==========================================
st.set_page_config(page_title="SKIMO KOREA", page_icon="🏔️", layout="wide")

# 배경 이미지 링크 매핑
BG_IMAGES = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=1800&q=80"   
]

if "menu_idx" not in st.session_state:
    st.session_state.menu_idx = 0
if "user_db" not in st.session_state:
    st.session_state.user_db = {"admin": "1234", "skimo": "skimo123"}
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

selected_bg = BG_IMAGES[st.session_state.menu_idx]

# 스타일 및 컴포넌트 커스텀 CSS 적용
st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{ display: none !important; }}
    .stAppDeployDropdown {{ display: none !important; }}
    
    div[data-testid="stSelectbox"] div[role="combobox"] {{ cursor: pointer !important; }}
    div[data-testid="stSelectbox"] input {{ cursor: pointer !important; caret-color: transparent !important; }}
    div[data-baseweb="popover"] li {{ cursor: pointer !important; }}
    [data-testid="stSidebar"] {{ display: none !important; }}
    
    .block-container {{ padding-top: 0rem; padding-bottom: 0rem; padding-left: 0rem; padding-right: 0rem; }}
    
    .stApp {{
        background: linear-gradient(rgba(15, 32, 39, 0.85), rgba(44, 83, 100, 0.75)), url('{selected_bg}') no-repeat center center fixed;
        background-size: cover !important;
    }}
    
    .centered-wrapper {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
    
    .custom-header-bg {{
        background-color: rgba(15, 32, 39, 0.4);
        backdrop-filter: blur(5px);
        width: 100%;
        padding: 10px 0;
    }}
    
    .right-nav-item {{
        color: #ffffff; font-size: 14px; font-weight: 500; text-decoration: none; margin-left: 20px; cursor: pointer; transition: color 0.2s;
    }}
    .right-nav-item:hover {{ color: #00c6ff; }}
    
    div.stButton > button {{
        background: transparent !important; color: white !important; border: none !important; padding: 0px !important;
        margin-left: 20px !important; font-size: 14px !important; font-weight: 500 !important; transition: color 0.2s !important;
    }}
    div.stButton > button:hover {{ color: #00c6ff !important; background: transparent !important; }}
    div.stButton > button:focus {{ color: #00c6ff !important; box-shadow: none !important; }}
    
    .hero-section {{
        height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; text-align: center;
    }}
    .hero-title {{ font-size: 42px; font-weight: 800; text-shadow: 3px 3px 8px rgba(0,0,0,0.9); margin-bottom: 5px; letter-spacing: 1px; }}
    .hero-subtitle {{ font-size: 18px; font-weight: 500; text-shadow: 2px 2px 4px rgba(0,0,0,0.7); color: #00c6ff; }}
    
    .content-box {{ 
        max-width: 1200px; margin: 0 auto 50px auto; padding: 30px; background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.15); color: #ffffff;
    }}
    
    .content-box h1, .content-box h2, .content-box h3, .content-box p, .content-box li {{ color: #ffffff !important; }}
    
    .news-list-item {{
        padding: 14px 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.15); display: flex; justify-content: space-between; align-items: center;
    }}
    .news-list-item:last-child {{ border-bottom: none; }}
    .news-list-title {{ font-size: 15px; font-weight: 500; color: #e2e8f0; text-decoration: none; }}
    .news-list-title:hover {{ color: #00c6ff; }}
    .news-list-meta {{ font-size: 13px; color: #cbd5e1; white-space: nowrap; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 6개국 다국어 번역 데이터
# ==========================================
LANG_DICT = {
    "한국어 (KO)": "KO", "English (EN)": "EN", "Français (FR)": "FR",       
    "Italiano (IT)": "IT", "简体中文 (ZH)": "ZH", "日本語 (JA)": "JA"          
}

LOCALIZED_TEXT = {
    "KO": {
        "title": "SKIMO KOREA", "subtitle": "스키등산 정보 포털",
        "menu": ["대회 홈", "선수 참가 신청", "실시간 리더보드 (LIVE)", "🔐 심판/관리자 패널"],
        "desc": "본 대회는 국제산악스키연맹(ISMF) 규정을 준수하며, field 심판 시스템과 동기화되어 실시간 기록을 전 세계에 생중계합니다.",
        "video": "📺 경기 종목 안내", "intro_video": "⛷️ 산악스키 소개", "photo": "📸 올림픽 현장 갤러리", "pay": "💳 참가 신청 및 안전 결제",
        "news_title": "📰 News & Stories (최신 소식)", "search_holder": "🔍 검색어를 입력하세요...", "notice": "📢 공지사항", "auth": "👤 로그인/회원가입"
    },
    "EN": {
        "title": "SKIMO KOREA", "subtitle": "Ski Mountaineering Information Portal",
        "menu": ["Home", "Athlete Registration", "Live Leaderboard", "🔐 Judge/Admin Panel"],
        "desc": "This tournament complies with ISMF regulations. Scoring and penalties are aggregated in real-time globally via the field web app.",
        "video": "📺 Skimo Rules Video", "intro_video": "⛷️ What is Skimo?", "photo": "📸 Olympic Action Gallery", "pay": "💳 Register & Secure Pay",
        "news_title": "📰 News & Stories", "search_holder": "🔍 Search information...", "notice": "📢 Notice", "auth": "👤 Login/Register"
    },
    "FR": {
        "title": "SKIMO CORÉE", "subtitle": "Portail d'information sur le ski-alpinisme",
        "menu": ["Accueil", "Inscription des athlètes", "Tableau croisé en direct", "🔐 Panel des juges/admin"],
        "desc": "Ce tournoi est conforme aux règlements de l'ISMF. Les scores et les pénalités sont agrégés en temps réel via l'application web de terrain.",
        "video": "📺 Vidéo des règles", "intro_video": "⛷️ Qu'est-ce que le Skimo?", "photo": "📸 Galerie Olympique", "pay": "💳 S'inscrire et payer",
        "news_title": "📰 Nouvelles et histoires", "search_holder": "🔍 Rechercher des informations...", "notice": "📢 Annonces", "auth": "👤 Connexion/S'inscrire"
    },
    "IT": {
        "title": "SKIMO COREA", "subtitle": "Portale di informazioni sullo sci alpinismo",
        "menu": ["Home", "Iscrizione Atleti", "Classifica in Tempo Reale", "🔐 Pannello Giudici/Admin"],
        "desc": "Questo torneo è conforme ai regolamenti ISMF. I punteggi e le penalità vengono aggregati in tempo reale tramite l'app web sul campo.",
        "video": "📺 Video del regolamento", "intro_video": "⛷️ Cos'è lo Skimo?", "photo": "📸 Galleria d'azione olimpica", "pay": "💳 Iscriviti e paga",
        "news_title": "📰 Notizie e storie", "search_holder": "🔍 Cerca informazioni...", "notice": "📢 Avvisi", "auth": "👤 Accedi/Registrati"
    },
    "ZH": {
        "title": "SKIMO 韩国", "subtitle": "滑雪登山信息门户网站",
        "menu": ["首页", "运动员报名", "实时排行榜", "🔐 裁判/管理员面板"],
        "desc": "本次比赛遵守国际滑雪登山联盟(ISMF)规定。得分和处罚通过现场网络应用全球实时汇总。",
        "video": "📺 比赛规则视频", "intro_video": "⛷️ 什么是滑雪登山?", "photo": "📸 奥运现场画廊", "pay": "💳 立即报名与安全支付",
        "news_title": "📰 新闻与故事", "search_holder": "🔍 输入搜索内容...", "notice": "📢 官方公告", "auth": "👤 登录/注册"
    },
    "JA": {
        "title": "SKIMO KOREA", "subtitle": "山岳スキー情報ポータル",
        "menu": ["大会ホーム", "選手参加申し込み", "リアルタイム順位表", "🔐 審判/管理者パネル"],
        "desc": "本大会は国際山岳スキー連盟(ISMF)の規則に準拠しており、フィールド審判システムと同期して世界中にリアルタイムでリザルトを配信します。",
        "video": "📺 競技種目のご案内", "intro_video": "⛷️ 山岳スキーとは？", "photo": "📸 オリンピックギャラリー", "pay": "💳 参加申し込みと安全決済",
        "news_title": "📰 ニュース&ストーリー", "search_holder": "🔍 検索キーワードを入力...", "notice": "📢 お知らせ", "auth": "👤 ログイン/会員登録"
    }
}

# ==========================================
# 로그인 및 회원가입 모달 대화상자 함수
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

if "current_lang_code" not in st.session_state:
    st.session_state.current_lang_code = "KO"

T = LOCALIZED_TEXT[st.session_state.current_lang_code]

c_menu, c_search, c_right = st.columns([3, 4, 5])

# 검색 키워드 사전
SEARCH_KEYWORDS = {
    0: ["홈", "대회", "소개", "뉴스", "소식", "경기", "갤러리", "영상", "home", "accueil", "首页", "ホーム"],
    1: ["선수", "참가", "신청", "등록", "결제", "접수", "form", "register", "inscription", "报名", "申し込み"],
    2: ["실시간", "리더", "보드", "라이브", "순위", "기록", "live", "leaderboard", "tableau", "classifica", "排行", "順位"],
    3: ["심판", "관리자", "패널", "로그", "판정", "panel", "judge", "admin", "juges", "裁判", "審判"]
}

with c_search:
    search_query = st.text_input("Search", placeholder=T["search_holder"], label_visibility="collapsed")
    if search_query:
        query_clean = search_query.strip().lower()
        matched_index = None
        for idx, keywords in SEARCH_KEYWORDS.items():
            if any(kw in query_clean for kw in keywords):
                matched_index = idx
                break
        if matched_index is not None and st.session_state.menu_idx != matched_index:
            st.session_state.menu_idx = matched_index
            st.rerun()

with c_menu:
    menu_list = list(T["menu"])
    selected_menu_raw = st.selectbox(
        "Menu Select", 
        menu_list, 
        index=st.session_state.menu_idx if st.session_state.menu_idx < len(menu_list) else 0, 
        label_visibility="collapsed"
    )
    menu_index = menu_list.index(selected_menu_raw)
    if st.session_state.menu_idx != menu_index:
        st.session_state.menu_idx = menu_index
        st.rerun()
    
with c_right:
    sub_lang, sub_buttons = st.columns([4, 6])
    with sub_lang:
        lang_names = list(LANG_DICT.keys())
        lang_codes = list(LANG_DICT.values())
        default_lang_idx = lang_codes.index(st.session_state.current_lang_code)
        
        selected_lang_name = st.selectbox("Global Select", lang_names, index=default_lang_idx, label_visibility="collapsed")
        new_lang_code = LANG_DICT[selected_lang_name]
        
        if st.session_state.current_lang_code != new_lang_code:
            st.session_state.current_lang_code = new_lang_code
            st.rerun()
        
    with sub_buttons:
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            st.markdown(f"<div style='margin-top: 6px;'><a class='right-nav-item' href='#'>{T['notice']}</a></div>", unsafe_allow_html=True)
        with btn_col2:
            if st.session_state.logged_in_user is None:
                if st.button(T["auth"], key="auth_btn"):
                    auth_dialog()
            else:
                logout_text = "🔓 Logout" if st.session_state.current_lang_code == "EN" else f"🔓 로그아웃 ({st.session_state.logged_in_user})"
                if st.button(logout_text, key="logout_btn"):
                    st.session_state.logged_in_user = None
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. 히어로 타이틀 영역
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

st.markdown('<div class="content-box">', unsafe_allow_html=True)

if st.session_state.logged_in_user:
    st.toast(f"🔒 {st.session_state.logged_in_user} Securing Connection")

if search_query:
    st.success(f"🔍 '{search_query}'")

# -------------------------------------------------------------------------
# [콘텐츠 분기 1] 대회 홈 화면 (menu_idx == 0)
# -------------------------------------------------------------------------
if st.session_state.menu_idx == 0:
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
        
    with col_video:
        st.markdown(f"### {T['video']}")
        st.video("https://youtu.be/KgyX5OjMTyM?si=Uu8mCwLV2X4an8Wk")

    with col_intro:
        st.markdown(f"### {T['intro_video']}")
        st.video("https://youtu.be/nLjES8kuFRg?si=xu3P1kuKedFOdjRl")

    with col_photo:
        st.markdown(f"### {T['photo']}")
        gallery_images = [
            {"path": "skimo_race_1.jpg", "caption": "❄️ 레이스 현장 1"},
            {"path": "skimo_race_2.jpg", "caption": "🏅 레이스 현장 2"},
            {"path": "skimo_race_3.jpg", "caption": "🎉 레이스 현장 3"}
        ]
        photo_idx = st.radio("📸 사진 선택", [1, 2, 3], horizontal=True, label_visibility="collapsed")
        selected_photo = gallery_images[photo_idx - 1]
        
        try:
            st.image(selected_photo["path"], use_container_width=True)
        except:
            import urllib.parse
            encoded_filename = urllib.parse.quote(selected_photo["path"])
            github_raw_url = f"https://raw.githubusercontent.com/pyminno12/skimo-website/main/{encoded_filename}"
            try:
                st.image(github_raw_url, use_container_width=True)
            except:
                st.error("⚠️ Image Error")

    # 📰 NEWS & STORIES
    st.markdown("<hr style='border-color: rgba(255,255,255,0.15);'>", unsafe_allow_html=True)
    st.markdown(f"## {T['news_title']}")
    
    news_items = [
        {"title": "French Alps 2030 proposal marks major milestone for ski mountaineering", "date": "2026-06-09", "link": "https://www.ismf-ski.org/"},
        {"title": "ISMF Releases Provisional 2026/27 International Calendar", "date": "2026-06-03", "link": "https://www.ismf-ski.org/"},
        {"title": "Looking Ahead: Key Olympic Qualification Moments in June", "date": "2026-05-29", "link": "https://www.ismf-ski.org/"}
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
# [콘텐츠 분기 2] 선수 참가 신청 (menu_idx == 1) - 이미지 변경 완료
# -------------------------------------------------------------------------
elif st.session_state.menu_idx == 1:
    st.markdown(f"## {T['menu'][1]}")
    
    # [변경 사항] 레이아웃 가독성을 위해 상단 폼 내부에 업로드해주신 레이스 서포트 이미지 배치
    try:
        st.image("skimo_race_4.avif", use_container_width=True)
    except:
        try:
            st.image("https://raw.githubusercontent.com/pyminno12/skimo-website/main/skimo_race_4.avif", use_container_width=True)
        except:
            st.info("🏔️ Milano Cortina 2026 Ski Mountaineering Race")
            
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
# [콘텐츠 분기 3] 실시간 리더보드 (menu_idx == 2)
# -------------------------------------------------------------------------
elif st.session_state.menu_idx == 2:
    st.markdown(f"## {T['menu'][2]}")
    df = pd.DataFrame(st.session_state.athletes)
    st.dataframe(df.set_index("BIB"), use_container_width=True)

# -------------------------------------------------------------------------
# [콘텐츠 분기 4] 심판 패널 (menu_idx == 3)
# -------------------------------------------------------------------------
elif st.session_state.menu_idx == 3:
    st.markdown(f"## {T['menu'][3]}")
    st.info("System operational. Field telemetry bridge secure.")

st.markdown('</div>', unsafe_allow_html=True)
