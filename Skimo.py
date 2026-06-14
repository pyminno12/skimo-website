import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ==========================================
# 1. 페이지 설정 및 풀 와이드 CSS 정의
# ==========================================
st.set_page_config(page_title="ISMF Korea Global Portal", page_icon="🏔️", layout="wide")

# 사이드바 여백 제거 및 상단 비주얼을 극대화하는 CSS 커스텀
st.markdown("""
    <style>
    /* 스트림릿 기본 사이드바를 완전히 숨김 처리 */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* 본문 상단 패딩 제거하여 배너를 천장에 밀착 */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 3rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    
    /* 글로벌 내비게이션 컨트롤 영역 스타일 */
    .nav-control-box {
        background-color: #0b1519;
        padding: 10px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #1e293b;
    }
    
    /* 웅장한 히어로 배너 세팅 */
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
        transition: background 0.6s ease-in-out;
    }
    .hero-title {
        font-size: 48px;
        font-weight: 800;
        text-shadow: 3px 3px 8px rgba(0,0,0,0.7);
        letter-spacing: 2px;
        margin-bottom: 8px;
    }
    .hero-subtitle {
        font-size: 21px;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.6);
        color: #00c6ff;
        font-weight: 500;
    }
    
    /* 컨텐츠 박스 정렬 */
    .content-box {
        max-width: 1350px;
        margin: 0 auto;
        padding: 35px 20px;
    }
    
    /* 뉴스 카드 컴포넌트 */
    .news-card {
        background-color: #0f2027;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        color: white;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    .news-img { width: 100%; height: 180px; object-fit: cover; }
    .news-body { padding: 20px; }
    .news-headline { font-size: 16px; font-weight: bold; line-height: 1.4; margin-bottom: 15px; color: #ffffff; }
    .news-meta { font-size: 12px; color: #9aa0a6; }
    .news-tag { color: #00c6ff; font-weight: bold; font-size: 11px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 다국어 데이터 모듈
# ==========================================
LANG_DICT = {
    "한국어 (KO)": "KO", "English (EN)": "EN", "Français (FR)": "FR",       
    "Italiano (IT)": "IT", "简体中文 (ZH)": "ZH", "日本語 (JA)": "JA"          
}

LOCALIZED_TEXT = {
    "KO": {
        "title": "ISMF KOREA CHAMPIONSHIP",
        "subtitle": "올림픽 정식 종목 공인 · 스키등산 세계선수권 대회",
        "menu": ["🏠 대회 홈", "📝 선수 참가 신청", "⏱️ 실시간 리더보드 (LIVE)", "🔐 심판/관리자 패널"],
        "desc": "본 대회는 국제산악스키연맹(ISMF) 규정을 준수하며, 필드 심판 시스템과 동기화되어 실시간 기록을 전 세계에 생중계합니다.",
        "video": "📺 경기 룰 안내 영상", "photo": "📸 올림픽 현장 갤러리", "pay": "💳 참가 신청 및 안전 결제",
        "news_title": "📰 News & Stories (최신 소식)", "news_tag": "대회 뉴스"
    },
    "EN": {
        "title": "ISMF KOREA CHAMPIONSHIP",
        "subtitle": "Official Olympic Sport · International Skimo Portal",
        "menu": ["🏠 Home", "📝 Registration", "⏱️ Live Leaderboard", "🔐 Judge/Admin"],
        "desc": "This tournament complies with ISMF regulations. Scoring and penalties are aggregated in real-time globally via the field web app.",
        "video": "📺 Skimo Rules Video", "photo": "📸 Olympic Action Gallery", "pay": "💳 Register & Secure Pay",
        "news_title": "📰 News & Stories", "news_tag": "Official News"
    },
    "FR": {
        "title": "CHAMPIONNAT ISMF CORÉE",
        "subtitle": "Sport Olympique Officiel · Portail International de Skimo",
        "menu": ["🏠 Accueil", "📝 Inscription", "⏱️ Tableau Live", "🔐 Panneau des Juges"],
        "desc": "Ce tournoi est conforme aux règlements de l'ISMF. Les scores sont agrégés en temps réel via l'application mobile des juges.",
        "video": "📺 Vidéo des Règles", "photo": "📸 Galerie d'Action Olympique", "pay": "💳 S'inscrire et Payer",
        "news_title": "📰 Actualités & Histoires", "news_tag": "Infos Officielles"
    },
    "IT": {
        "title": "CAMPIONATO ISMF COREA",
        "subtitle": "Sport Olimpico Ufficiale · Portale Internazionale Sci Alpinismo",
        "menu": ["🏠 Home", "📝 Iscrizione Atleta", "⏱️ Classifica Live", "🔐 Pannello Giudici"],
        "desc": "Questo torneo è conforme ai regolamenti ISMF. I punteggi vengono aggregati in tempo real tramite l'app dei giudici.",
        "video": "📺 Video Regolamento", "photo": "📸 Galleria Azione Olimpiadi", "pay": "💳 Iscriviti e Paga",
        "news_title": "📰 Notizie & Storie", "news_tag": "Notizie Ufficiali"
    },
    "ZH": {
        "title": "ISMF 韩国锦标赛",
        "subtitle": "奥运会正式项目认证 · 登山滑雪国际门户网站",
        "menu": ["🏠 大会主页", "📝 运动员报名", "⏱️ 实时排行榜", "🔐 裁判/管理员"],
        "desc": "本次比赛遵守 ISMF 规定。评分和处罚将通过现场裁判的移动网络应用实时在全球范围内汇总。",
        "video": "📺 赛事规则视频", "photo": "📸 奥运会现场画廊", "pay": "💳 安全支付并确认",
        "news_title": "📰 新闻与故事", "news_tag": "官方新闻"
    },
    "JA": {
        "title": "ISMF 韓国選手権大会",
        "subtitle": "オリンピック正式種目公認 · 山岳スキー国際ポータル",
        "menu": ["🏠 ホーム", "📝 選手参加申し込み", "⏱️ リアルタイム順位表", "🔐 審判/管理者"],
        "desc": "本大会はISMF規定に準拠しています。スコアやペナルティ는、現地審判의 アプリを通じてリアルタイムで集計されます。",
        "video": "📺 競技ルール動画", "photo": "📸 オリンピック写真館", "pay": "💳 安全な決済と確定",
        "news_title": "📰 ニュース＆ストーリー", "news_tag": "公式ニュース"
    }
}

# ==========================================
# 3. [혁신 개조] 최상단 배치 레이아웃 (언어 선택 & 메뉴 통합)
# ==========================================
# 사이드바를 쓰지 않고, 최상단 한 줄에 언어팩 선택 드롭다운 박스를 깔끔하게 배치
lang_col, space_col = st.columns([3, 9])
with lang_col:
    selected_lang_name = st.selectbox("🌐 Language Selection", list(LANG_DICT.keys()), label_visibility="collapsed")
current_lang = LANG_DICT[selected_lang_name]
T = LOCALIZED_TEXT[current_lang]

# 📢 [핵심 포인트] 가로 배치형 내비게이션 바 컴포넌트 구성!
# 화면 최상단에 4개의 버튼을 배치하여 누를 때마다 세션 상태(Session State)가 변하게 설계
if "current_menu_idx" not in st.session_state:
    st.session_state.current_menu_idx = 0

st.markdown("<p style='margin-bottom: -10px; color:#9aa0a6; font-size:12px; font-weight:bold; letter-spacing:1px;'>🏔️ ISMF NAVIGATION BAR</p>", unsafe_allow_html=True)
nav_cols = st.columns(4)
for i, menu_name in enumerate(T["menu"]):
    # 현재 선택된 메뉴 버튼은 더 굵고 직관적인 파란색 테두리(Primary) 버튼으로 강조되도록 세팅
    if st.session_state.current_menu_idx == i:
        nav_cols[i].button(menu_name, key=f"nav_{i}", use_container_width=True, type="primary")
    else:
        if nav_cols[i].button(menu_name, key=f"nav_{i}", use_container_width=True, type="secondary"):
            st.session_state.current_menu_idx = i
            st.rerun()

menu_index = st.session_state.current_menu_idx

# ==========================================
# 4. 메뉴별 동적 배경화면 매핑
# ==========================================
BG_IMAGES = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80",  # 대회 홈
    "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=1800&q=80",  # 참가 신청
    "https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=1800&q=80",  # 리더보드
    "https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=1800&q=80"   # 심판 패널
]
selected_bg = BG_IMAGES[menu_index]

# 메인 비주얼 히어로 배너 출력 (인라인 스타일로 배경 이미지 실시간 주입)
st.markdown(f"""
    <div class="hero-section" style="background: linear-gradient(rgba(11, 21, 25, 0.7), rgba(44, 83, 100, 0.45)), url('{selected_bg}') no-repeat center center; background-size: cover;">
        <div class="hero-title">{T["title"]}</div>
        <div class="hero-subtitle">🏔️ {T["subtitle"]}</div>
    </div>
""", unsafe_allow_html=True)

# 데이터 보관 세션 (Mock DB)
if "athletes" not in st.session_state:
    st.session_state.athletes = [
        {"BIB": "101", "Name": "김민우", "Team": "KOREA", "Status": "RACING", "CP1": "10:15:20", "CP2": "--:--:--", "Penalty": "None"},
        {"BIB": "102", "Name": "Alex Smith", "Team": "USA", "Status": "RACING", "CP1": "10:14:05", "CP2": "10:45:12", "Penalty": "None"},
        {"BIB": "103", "Name": "Chloe", "Team": "FRANCE", "Status": "RACING", "CP1": "10:16:55", "CP2": "10:49:30", "Penalty": "None"},
    ]

st.markdown('<div class="content-box">', unsafe_allow_html=True)

# ==========================================
# 5. 각 메뉴별 메인 콘텐츠 바디
# ==========================================

# --- [모듈 1] 대회 홈 화면 ---
if menu_index == 0:
    st.header("🏁 Upcoming Events & Overview")
    col_text, col_video, col_photo = st.columns([4, 4, 4])
    
    with col_text:
        st.markdown(f"### 📢 Information")
        st.write(T["desc"])
        st.markdown("""
        * **Location:** Pyeongchang / Jeongseon, Gangwon, KOREA
        * **Sanctioned by:** International Ski Mountaineering Federation (ISMF)
        * **Expected Scale:** 3,000+ Global Participants & Winter Festivals
        """)
        st.info("⚙️ **Global Navigation System**\nSidebar removed. Fully adapted to global top-bar standards.")
        
    with col_video:
        st.markdown(f"### {T['video']}")
        st.video("https://youtu.be/KgyX5OjMTyM?si=Uu8mCwLV2X4an8Wk")

    with col_photo:
        st.markdown(f"### {T['photo']}")
        st.image("https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=600&q=80", caption="Olympic Ski Mountaineering Athlete")

    # NEWS & STORIES 3열 격자 카드 섹션
    st.markdown("---")
    st.header(T["news_title"])
    n_col1, n_col2, n_col3 = st.columns(3)
    
    with n_col1:
        st.markdown(f"""
        <div class="news-card">
            <img class="news-img" src="https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=500&q=80">
            <div class="news-body">
                <div class="news-headline">French Alps 2030 proposal marks major milestone for ski mountaineering</div>
                <div class="news-meta">📅 June 9, 2026<br><span class="news-tag"># {T["news_tag"]} # Olympics</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with n_col2:
        st.markdown(f"""
        <div class="news-card">
            <img class="news-img" src="https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=500&q=80">
            <div class="news-body">
                <div class="news-headline">ISMF Releases Provisional 2026/27 International Calendar</div>
                <div class="news-meta">📅 June 3, 2026<br><span class="news-tag"># {T["news_tag"]} # Competitions</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with n_col3:
        st.markdown(f"""
        <div class="news-card">
            <img class="news-img" src="https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=500&q=80">
            <div class="news-body">
                <div class="news-headline">Looking Ahead: Key Olympic Qualification Moments in June</div>
                <div class="news-meta">📅 May 29, 2026<br><span class="news-tag"># {T["news_tag"]} # RoadToMilano</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🤝 Global Partners & Sponsors")
    c_ad1, c_ad2, c_ad3 = st.columns(3)
    c_ad1.info("⛷️ **Premium Sponsor**\nGlobal Brand Ad Slot")
    c_ad2.info("🏨 **Official Lodging**\nResort & Hotel Partner")
    c_ad3.info("🥤 **Official Beverage**\nEnergy Drink Sponsor")

# --- [모듈 2] 선수 참가 신청 ---
elif menu_index == 1:
    st.header(T["menu"][1])
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

# --- [모듈 3] 실시간 리더보드 ---
elif menu_index == 2:
    st.header(T["menu"][2])
    df = pd.DataFrame(st.session_state.athletes)
    st.dataframe(df.set_index("BIB"), use_container_width=True)

# --- [모듈 4] 심판 및 관리자 패널 ---
elif menu_index == 3:
    st.header(T["menu"][3])
    athlete_names = [f"#{a['BIB']} - {a['Name']}" for a in st.session_state.athletes]
    target_athlete = st.selectbox("🎯 Target Athlete", athlete_names)
    target_bib = target_athlete.split(" - ")[0].replace("#", "")
    target_cp = st.radio("📍 Select Checkpoint", ["CP1", "CP2"])
    penalty_select = st.selectbox("⚠️ Penalty Rules", ["None", "+1:00 Skin Violation", "DSQ"])
    
    if st.button("🚀 Push Data to Live Leaderboard"):
        current_time = datetime.now().strftime("%H:%M:%S")
        for athlete in st.session_state.athletes:
            if athlete["BIB"] == target_bib:
                athlete[target_cp] = current_time
                if penalty_select != "None":
                    athlete["Penalty"] = penalty_select
        st.success("Data synced successfully!")
        time.sleep(0.5)
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
