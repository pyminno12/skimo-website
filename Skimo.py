import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ==========================================
# 1. 페이지 설정 및 글로벌 CSS 스타일 커스텀
# ==========================================
st.set_page_config(page_title="ISMF Korea Global Portal", page_icon="🏔️", layout="wide")

# ISMF 공식 사이트 느낌의 상단 바와 폰트 스타일을 강제로 주입하는 CSS
st.markdown("""
    <style>
    /* 기본 스트림릿 패딩 제거하여 풀 와이드 구현 */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 3rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    
    /* 상단 네비게이션 바 스타일 */
    .top-nav {
        background-color: #0f2027;
        padding: 15px 50px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .nav-logo {
        font-size: 24px;
        letter-spacing: 1px;
        color: #ffffff;
    }
    
    /* 웅장한 설산 히어로 배너 세팅 */
    .hero-section {
        background: linear-gradient(rgba(15, 32, 39, 0.5), rgba(44, 83, 100, 0.3)), 
                    url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80') no-repeat center center;
        background-size: cover;
        height: 450px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        text-align: center;
        padding: 20px;
    }
    .hero-title {
        font-size: 45px;
        font-weight: 700;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.6);
        margin-bottom: 10px;
    }
    .hero-subtitle {
        font-size: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        color: #00c6ff;
    }
    
    /* 컨텐츠가 들어갈 중앙 정렬 박스 */
    .content-box {
        max-width: 1300px;
        margin: 0 auto;
        padding: 40px 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 다국어 데이터 배열 (6개국어 대응)
# ==========================================
LANG_DICT = {
    "한국어 (KO)": "KO", "English (EN)": "EN", "Français (FR)": "FR",       
    "Italiano (IT)": "IT", "简体中文 (ZH)": "ZH", "日本語 (JA)": "JA"          
}

LOCALIZED_TEXT = {
    "KO": {
        "title": "ISMF KOREA CHAMPIONSHIP",
        "subtitle": "올림픽 정식 종목 공인 · 스키등산 세계선수권 대회",
        "menu": ["대회 홈", "선수 참가 신청", "실시간 리더보드 (LIVE)", "🔐 심판/관리자 패널"],
        "desc": "본 대회는 국제산악스키연맹(ISMF) 규정을 준수하며, 필드 심판 시스템과 동기화되어 실시간 기록을 전 세계에 생중계합니다.",
        "video": "📺 경기 룰 안내 영상", "photo": "📸 올림픽 현장 갤러리", "pay": "💳 참가 신청 및 안전 결제"
    },
    "EN": {
        "title": "ISMF KOREA CHAMPIONSHIP",
        "subtitle": "Official Olympic Sport · International Skimo Portal",
        "menu": ["Home", "Athlete Registration", "Live Leaderboard", "🔐 Judge/Admin Panel"],
        "desc": "This tournament complies with ISMF regulations. Scoring and penalties are aggregated in real-time globally via the field web app.",
        "video": "📺 Skimo Rules Video", "photo": "📸 Olympic Action Gallery", "pay": "💳 Register & Secure Pay"
    },
    "FR": {
        "title": "CHAMPIONNAT ISMF CORÉE",
        "subtitle": "Sport Olympique Officiel · Portail International de Skimo",
        "menu": ["Accueil", "Inscription Athlète", "Tableau Live", "🔐 Panneau des Juges"],
        "desc": "Ce tournoi est conforme aux règlements de l'ISMF. Les scores sont agrégés en temps réel via l'application mobile des juges.",
        "video": "📺 Vidéo des Règles", "photo": "📸 Galerie d'Action Olympique", "pay": "💳 S'inscrire et Payer"
    },
    "IT": {
        "title": "CAMPIONATO ISMF COREA",
        "subtitle": "Sport Olimpico Ufficiale · Portale Internazionale Sci Alpinismo",
        "menu": ["Home", "Iscrizione Atleta", "Classifica Live", "🔐 Pannello Giudici"],
        "desc": "Questo torneo è conforme ai regolamenti ISMF. I punteggi vengono aggregati in tempo real tramite l'app dei giudici.",
        "video": "📺 Video Regolamento", "photo": "📸 Galleria Azione Olimpiadi", "pay": "💳 Iscriviti e Paga"
    },
    "ZH": {
        "title": "ISMF 韩国锦标赛",
        "subtitle": "奥运会正式项目认证 · 登山滑雪国际门户网站",
        "menu": ["大会主页", "运动员报名", "实时排行榜", "🔐 裁判/管理员"],
        "desc": "本次比赛遵守 ISMF 规定。评分和处罚将通过现场裁判的移动网络应用实时在全球范围内汇总。",
        "video": "📺 赛事规则视频", "photo": "📸 奥运会现场画廊", "pay": "💳 安全支付并确认"
    },
    "JA": {
        "title": "ISMF 韓国選手権大会",
        "subtitle": "オリンピック正式種目公認 · 山岳スキー国際ポータル",
        "menu": ["ホーム", "選手参加申し込み", "リアルタイム順位表", "🔐 審判/管理者"],
        "desc": "本大会はISMF規定に準拠しています。スコアやペナルティは、現地審判のアプリを通じてリアルタイムで集計されます。",
        "video": "📺 競技ルール動画", "photo": "📸 オリンピック写真館", "pay": "💳 安全な決済と確定"
    }
}

# 🌐 언어 선택 및 네비게이션 제어는 사이드바 상단에서 깔끔하게 처리
selected_lang_name = st.sidebar.selectbox("🌐 Select Language", list(LANG_DICT.keys()))
current_lang = LANG_DICT[selected_lang_name]
T = LOCALIZED_TEXT[current_lang]

# --- [계획표 2단계 반영] 상단 고정형 메뉴 바 UI 아키텍처 ---
menu = st.sidebar.radio("🧭 Navigation Menu", T["menu"])

# ==========================================
# 3. 메인 상단 비주얼 영역 (ISMF 스타일 적용)
# ==========================================
# 텍스트가 배경을 가리지 않고 웅장하게 녹아들도록 HTML 컴포넌트로 결합
st.markdown(f"""
    <div class="hero-section">
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

# 모든 컨텐츠는 content-box 클래스로 감싸서 균형 잡힌 가독성 제공
st.markdown('<div class="content-box">', unsafe_allow_html=True)

# --- [모듈 1] 대회 홈 화면 (가독성 100% 보장 레이아웃) ---
if menu == T["menu"][0]:
    st.header("🏁 Upcoming Events & Overview")
    
    # 3단 분할 레이아웃으로 안내글, 유튜브, 올림픽 사진을 가로로 깔끔하게 배치!
    col_text, col_video, col_photo = st.columns([4, 4, 4])
    
    with col_text:
        st.markdown(f"### 📢 Information")
        st.write(T["desc"])
        st.markdown("""
        * **Location:** Pyeongchang / Jeongseon, Gangwon, KOREA
        * **Sanctioned by:** International Ski Mountaineering Federation (ISMF)
        * **Expected Scale:** 3,000+ Global Participants & Winter Festivals
        """)
        st.info("⚙️ **Global Sync System**\nThis platform is fully responsive and supports real-time synchronization with race control.")
        
    with col_video:
        st.markdown(f"### {T['video']}")
        st.video("https://youtu.be/KgyX5OjMTyM?si=Uu8mCwLV2X4an8Wk")
        st.caption("ISMF Official Rule Guide Video")

    with col_photo:
        st.markdown(f"### {T['photo']}")
        # 고해상도 리얼 올림픽 산악스키 주행 컷 적용
        st.image("https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=600&q=80", 
                 caption="Olympic Ski Mountaineering Athlete in Action")

    # 하단 파트너 배너 구역
    st.markdown("---")
    st.subheader("🤝 Global Partners & Sponsors")
    c_ad1, c_ad2, c_ad3 = st.columns(3)
    c_ad1.info("⛷️ **Premium Sponsor**\nGlobal Brand Ad Slot")
    c_ad2.info("🏨 **Official Lodging**\nResort & Hotel Partner")
    c_ad3.info("🥤 **Official Beverage**\nEnergy Drink Sponsor")

# --- [모듈 2] 선수 참가 신청 및 행정 결제 ---
elif menu == T["menu"][1]:
    st.header(T["reg_title"] if "reg_title" in T else T["menu"][1])
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
elif menu == T["menu"][2]:
    st.header(T["menu"][2])
    df = pd.DataFrame(st.session_state.athletes)
    st.dataframe(df.set_index("BIB"), use_container_width=True)

# --- [모듈 4] 🔐 심판 및 관리자 전용 제어 시스템 ---
elif menu == T["menu"][3]:
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
