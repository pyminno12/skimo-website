import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ==========================================
# 1. 페이지 설정 및 풀 와이드 CSS 레이아웃 구조 정의
# ==========================================
st.set_page_config(page_title="ISMF Korea Global Portal", page_icon="🏔️", layout="wide")

# 사이드바/시스템 바 제거 및 마우스 커서 교정, 로고 테두리 제거를 위한 CSS
st.markdown("""
    <style>
    /* -------------------------------------------
       [치명적 문제 해결 1] 스트림릿 기본 검은색 상단 바 완전 제거
    ------------------------------------------- */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    .stAppDeployDropdown {
        display: none !important;
    }
    
    /* -------------------------------------------
       [치명적 문제 해결 2] 마우스 커서 텍스트 입력창 변환 방지
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

    /* 1. 스트림릿 기본 사이드바 숨기기 및 본문 패딩 제거 */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    .block-container {
        padding-top: 0rem;
        padding-bottom: 3rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    
    /* 2. 상단 고정형 글로벌 내비게이션 바 레이아웃 */
    .custom-top-bar {
        background-color: #0f2027;
        padding: 15px 40px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #00c6ff;
    }
    
    /* 3. 로고 마크 스타일링 */
    .brand-logo-clean {
        color: white;
        font-size: 16px;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 8px;
        white-space: nowrap;
        padding: 10px 0px;
    }
    
    /* 4. 웅장한 히어로 배너 영역 */
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
        transition: background 0.5s ease-in-out;
    }
    .hero-title { font-size: 42px; font-weight: 700; text-shadow: 3px 3px 6px rgba(0,0,0,0.7); margin-bottom: 8px; }
    .hero-subtitle { font-size: 18px; text-shadow: 2px 2px 4px rgba(0,0,0,0.6); color: #00c6ff; }
    
    /* 5. 콘텐츠 컨테이너 크기 제한 */
    .content-box { max-width: 1400px; margin: 0 auto; padding: 30px 20px; }
    
    /* 6. 뉴스 카드 컴포넌트 */
    .news-card {
        background-color: #0f2027; border-radius: 8px; padding: 0px; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15); color: white; overflow: hidden; height: 100%;
        display: flex; flex-direction: column;
    }
    .news-img { width: 100%; height: 170px; object-fit: cover; }
    .news-body { padding: 20px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
    .news-headline { font-size: 15px; font-weight: bold; line-height: 1.4; margin-bottom: 12px; color: #ffffff; }
    .news-meta { font-size: 12px; color: #9aa0a6; }
    .news-tag { color: #00c6ff; font-weight: bold; margin-top: 5px; font-size: 11px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 다국어 데이터 배열
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
        "video": "📺 대회 룰 안내 영상", "intro_video": "⛷️ 산악스키 종목 소개", "photo": "📸 올림픽 현장 갤러리", "pay": "💳 참가 신청 및 안전 결제",
        "news_title": "📰 News & Stories (최신 소식)", "news_tag": "대회 뉴스"
    },
    "EN": {
        "title": "ISMF KOREA CHAMPIONSHIP",
        "subtitle": "Official Olympic Sport · International Skimo Portal",
        "menu": ["Home", "Athlete Registration", "Live Leaderboard", "🔐 Judge/Admin Panel"],
        "desc": "This tournament complies with ISMF regulations. Scoring and penalties are aggregated in real-time globally via the field web app.",
        "video": "📺 Skimo Rules Video", "intro_video": "⛷️ What is Skimo?", "photo": "📸 Olympic Action Gallery", "pay": "💳 Register & Secure Pay",
        "news_title": "📰 News & Stories", "news_tag": "Official News"
    },
    "FR": {
        "title": "CHAMPIONNAT ISMF CORÉE",
        "subtitle": "Sport Olympique Officiel · Portail International de Skimo",
        "menu": ["Accueil", "Inscription Athlète", "Tableau Live", "🔐 Panneau des Juges"],
        "desc": "Ce tournoi est conforme aux règlements de l'ISMF. Les scores sont agrégés en temps réel via l'application mobile des juges.",
        "video": "📺 Vidéo des Règles", "intro_video": "⛷️ Qu'est-ce que le Skimo?", "photo": "📸 Galerie d'Action Olympique", "pay": "💳 S'inscrire et Payer",
        "news_title": "📰 Actualités & Histoires", "news_tag": "Infos Officielles"
    },
    "IT": {
        "title": "CAMPIONATO ISMF COREA",
        "subtitle": "Sport Olimpico Ufficiale · Portale Internazionale Sci Alpinismo",
        "menu": ["Home", "Iscrizione Atleta", "Classifica Live", "🔐 Pannello Giudici"],
        "desc": "Questo torneo è conforme ai regolamenti ISMF. I punteggi vengono aggregati in tempo real tramite l'app dei giudici.",
        "video": "📺 Video Regolamento", "intro_video": "⛷️ Cos'è lo Skimo?", "photo": "📸 Galleria Azione Olimpiadi", "pay": "💳 Iscriviti e Paga",
        "news_title": "📰 Notizie & Storie", "news_tag": "Notizie Ufficiali"
    },
    "ZH": {
        "title": "ISMF 韩国锦标赛",
        "subtitle": "奥运会正式项目认证 · 登山滑雪国际门户网站",
        "menu": ["大会主页", "运动员报名", "实时排行榜", "🔐 裁判/管理员"],
        "desc": "本次比赛遵守 ISMF 规定。评分 and 处罚将通过现场裁判의 移动网络应用实时在全球范围内汇总。",
        "video": "📺 赛事规则视频", "intro_video": "⛷️ 什么是滑雪登山?", "photo": "📸 奥运会现场画廊", "pay": "💳 安全支付并确认",
        "news_title": "📰 新闻与故事", "news_tag": "官方新闻"
    },
    "JA": {
        "title": "ISMF 韓国選手権大会",
        "subtitle": "オリンピック正式種目公認 · 山岳スキー国際ポータル",
        "menu": ["ホーム", "選手参加申し込み", "リアルタイム順位表", "🔐 審判/管理者"],
        "desc": "本大会은 ISMF規定에 준거해 있습니다. 스코어 및 페널ティ는 현지 심판의 앱을 통해 실시간으로 집계됩니다.",
        "video": "📺 競技ルール動画", "intro_video": "⛷️ 山岳スキーとは？", "photo": "📸 オリンピック写真館", "pay": "💳 安全な決済と確定",
        "news_title": "📰 ニュース＆ストーリー", "news_tag": "公式ニュース"
    }
}

# ==========================================
# 3. 최상단 통합형 내비게이션 구조 설계 (사이드바 대체)
# ==========================================
top_nav_container = st.container()

with top_nav_container:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    c_logo, c_menu, c_lang = st.columns([3, 5, 2])
    
    with c_logo:
        st.markdown("<div style='padding-top:5px;'><span class='brand-logo-clean'>🏔️ ISMF NAVIGATION BAR</span></div>", unsafe_allow_html=True)
        
    with c_menu:
        selected_menu_raw = st.selectbox("Menu Select", list(LOCALIZED_TEXT["KO"]["menu"]), label_visibility="collapsed")
        menu_index = LOCALIZED_TEXT["KO"]["menu"].index(selected_menu_raw)
        
    with c_lang:
        selected_lang_name = st.selectbox("Global Select", list(LANG_DICT.keys()), label_visibility="collapsed")
        current_lang = LANG_DICT[selected_lang_name]
        T = LOCALIZED_TEXT[current_lang]

# ==========================================
# 4. 동적 배경화면 결합 처리 및 히어로 배너 출력
# ==========================================
BG_IMAGES = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=1800&q=80"   
]
selected_bg = BG_IMAGES[menu_index]

st.markdown(f"""
    <div class="hero-section" style="background: linear-gradient(rgba(15, 32, 39, 0.7), rgba(44, 83, 100, 0.45)), url('{selected_bg}') no-repeat center center; background-size: cover;">
        <div class="hero-title">{T["title"]}</div>
        <div class="hero-subtitle">🏔️ {T["subtitle"]}</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 5. 세션 데이터 베이스 인스턴스 활성화
# ==========================================
if "athletes" not in st.session_state:
    st.session_state.athletes = [
        {"BIB": "101", "Name": "김민우", "Team": "KOREA", "Status": "RACING", "CP1": "10:15:20", "CP2": "--:--:--", "Penalty": "None"},
        {"BIB": "102", "Name": "Alex Smith", "Team": "USA", "Status": "RACING", "CP1": "10:14:05", "CP2": "10:45:12", "Penalty": "None"},
        {"BIB": "103", "Name": "Chloe", "Team": "FRANCE", "Status": "RACING", "CP1": "10:16:55", "CP2": "10:49:30", "Penalty": "None"},
    ]

st.markdown('<div class="content-box">', unsafe_allow_html=True)

# --- [콘텐츠 분기 1] 대회 홈 화면 ---
if menu_index == 0:
    st.header("🏁 Upcoming Events & Overview")
    
    # 4단 분할 레이아웃 유지 (개요, 룰 안내 영상, 종목 소개 영상, 이미지 갤러리)
    col_text, col_video, col_intro, col_photo = st.columns([3, 3, 3, 3])
    
    with col_text:
        st.markdown(f"### 📢 Information")
        st.write(T["desc"])
        st.markdown("""
        * **Location:** Pyeongchang, KOREA
        * **Sanctioned by:** ISMF
        * **Scale:** 3,000+ Participants
        """)
        st.success("🖼️ **Custom Gallery Active**\nYour uploaded Olympic Skimo race photos are now successfully linked.")
        
    with col_video:
        st.markdown(f"### {T['video']}")
        st.video("https://youtu.be/KgyX5OjMTyM?si=Uu8mCwLV2X4an8Wk")

    with col_intro:
        st.markdown(f"### {T['intro_video']}")
        st.video("https://youtu.be/nLjES8kuFRg?si=xu3P1kuKedFOdjRl")

    with col_photo:
        st.markdown(f"### {T['photo']}")
        
        # [수정된 영문 경로 설정]
gallery_images = [
    {"path": "skimo_race_1.jpg", "caption": "❄️ 눈보라를 뚫고 올라가는 한계 극복의 업힐 레이스"},
    {"path": "skimo_race_2.jpg", "caption": "🏅 오륜기 마크 앞에서 펼쳐지는 치열한 선두권 경쟁"},
    {"path": "skimo_race_3.jpg", "caption": "🎉 꿈의 무대, 올림픽 포디움에 선 영광의 메달리스트들"}
]
        
        # 유저가 조작할 수 있는 라디오 인터페이스
        photo_idx = st.radio("📸 사진 선택", [1, 2, 3], horizontal=True, label_visibility="collapsed")
        selected_photo = gallery_images[photo_idx - 1]
        
        # 로컬 파일 경로 읽어서 화면에 띄우기
        try:
            st.image(selected_photo["path"], use_container_width=True)
            st.caption(f"<div style='text-align:center; color:#00c6ff; font-weight:bold; margin-top:5px;'>{selected_photo['caption']}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error("⚠️ 이미지를 불러오지 못했습니다. 파일명이 정확한지, 스크립트와 동일한 폴더에 파일이 존재하는지 확인해주세요.")

    # NEWS & STORIES 섹션
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

# --- [콘텐츠 분기 2] 선수 참가 신청 ---
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

# --- [콘텐츠 분기 3] 실시간 리더보드 ---
elif menu_index == 2:
    st.header(LOCALIZED_TEXT["KO"]["menu"][2])
    df = pd.DataFrame(st.session_state.athletes)
    st.dataframe(df.set_index("BIB"), use_container_width=True)

# --- [콘텐츠 분기 4] 심판 패널 ---
elif menu_index == 3:
    st.header(LOCALIZED_TEXT["KO"]["menu"][3])
    st.info("System operational. Field telemetry bridge secure.")

st.markdown('</div>', unsafe_allow_html=True)
