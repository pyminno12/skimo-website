import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ==========================================
# 1. 페이지 기본 설정 및 디자인 테마 정의
# ==========================================
st.set_page_config(page_title="ISMF Korea Global Portal", page_icon="🏔️", layout="wide")

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
        "video": "📺 경기 룰 안내 영상", "photo": "📸 올림픽 현장 갤러리", "pay": "💳 참가 신청 및 안전 결제",
        "news_title": "📰 News & Stories (최신 소식)",
        "news_tag": "대회 뉴스"
    },
    "EN": {
        "title": "ISMF KOREA CHAMPIONSHIP",
        "subtitle": "Official Olympic Sport · International Skimo Portal",
        "menu": ["Home", "Athlete Registration", "Live Leaderboard", "🔐 Judge/Admin Panel"],
        "desc": "This tournament complies with ISMF regulations. Scoring and penalties are aggregated in real-time globally via the field web app.",
        "video": "📺 Skimo Rules Video", "photo": "📸 Olympic Action Gallery", "pay": "💳 Register & Secure Pay",
        "news_title": "📰 News & Stories",
        "news_tag": "Official News"
    },
    "FR": {
        "title": "CHAMPIONNAT ISMF CORÉE",
        "subtitle": "Sport Olympique Officiel · Portail International de Skimo",
        "menu": ["Accueil", "Inscription Athlète", "Tableau Live", "🔐 Panneau des Juges"],
        "desc": "Ce tournoi est conforme aux règlements de l'ISMF. Les scores sont agrégés en temps réel via l'application mobile des juges.",
        "video": "📺 Vidéo des Règles", "photo": "📸 Galerie d'Action Olympique", "pay": "💳 S'inscrire et Payer",
        "news_title": "📰 Actualités & Histoires",
        "news_tag": "Infos Officielles"
    },
    "IT": {
        "title": "CAMPIONATO ISMF COREA",
        "subtitle": "Sport Olimpico Ufficiale · Portale Internazionale Sci Alpinismo",
        "menu": ["Home", "Iscrizione Atleta", "Classifica Live", "🔐 Pannello Giudici"],
        "desc": "Questo torneo è conforme ai regolamenti ISMF. I punteggi vengono aggregati in tempo real tramite l'app dei giudici.",
        "video": "📺 Video Regolamento", "photo": "📸 Galleria Azione Olimpiadi", "pay": "💳 Iscriviti e Paga",
        "news_title": "📰 Notizie & Storie",
        "news_tag": "Notizie Ufficiali"
    },
    "ZH": {
        "title": "ISMF 韩国锦标赛",
        "subtitle": "奥运会正式项目认证 · 登山滑雪国际门户网站",
        "menu": ["大会主页", "运动员报名", "实时排行榜", "🔐 裁判/管理员"],
        "desc": "本次比赛遵守 ISMF 规定。评分和处罚将通过现场裁判的移动网络应用实时在全球范围内汇总。",
        "video": "📺 赛事规则视频", "photo": "📸 奥运会现场画廊", "pay": "💳 安全支付并确认",
        "news_title": "📰 新闻与故事",
        "news_tag": "官方新闻"
    },
    "JA": {
        "title": "ISMF 韓国選手権大会",
        "subtitle": "オリンピック正式種目公認 · 山岳スキー国際ポータル",
        "menu": ["ホーム", "選手参加申し込み", "リアルタイム順位表", "🔐 審判/管理者"],
        "desc": "本大会はISMF規定に準拠しています。スコアやペナルティは、現地審判의 アプリを通じてリアルタイムで集計されます。",
        "video": "📺 競技ルール動画", "photo": "📸 オリンピック写真館", "pay": "💳 安全な決済と確定",
        "news_title": "📰 ニュース＆ストーリー",
        "news_tag": "公式ニュース"
    }
}

selected_lang_name = st.sidebar.selectbox("🌐 Select Language", list(LANG_DICT.keys()))
current_lang = LANG_DICT[selected_lang_name]
T = LOCALIZED_TEXT[current_lang]

menu = st.sidebar.radio("🧭 Navigation Menu", T["menu"])
menu_index = T["menu"].index(menu)

# 메뉴별 동적 배경화면 설정
BG_IMAGES = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=1800&q=80"   
]
selected_bg = BG_IMAGES[menu_index]

# ==========================================
# 3. CSS 커스텀 스타일 디자인 세팅 (뉴스 카드 스타일 정의)
# ==========================================
st.markdown(f"""
    <style>
    .block-container {{
        padding-top: 0rem; padding-bottom: 3rem; padding-left: 0rem; padding-right: 0rem;
    }}
    .hero-section {{
        background: linear-gradient(rgba(15, 32, 39, 0.65), rgba(44, 83, 100, 0.45)), url('{selected_bg}') no-repeat center center;
        background-size: cover; height: 450px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; text-align: center; padding: 20px; transition: background 0.5s ease-in-out;
    }}
    .hero-title {{ font-size: 45px; font-weight: 700; text-shadow: 3px 3px 6px rgba(0,0,0,0.6); margin-bottom: 10px; }}
    .hero-subtitle {{ font-size: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); color: #00c6ff; }}
    .content-box {{ max-width: 1300px; margin: 0 auto; padding: 40px 20px; }}
    
    /* [뉴스 스타일 컴포넌트] 보낸 사진 스타일 그대로 구현 */
    .news-card {{
        background-color: #0f2027;
        border-radius: 8px;
        padding: 0px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        color: white;
        overflow: hidden;
        height: 100%;
        display: flex;
        flex-direction: column;
    }}
    .news-img {{
        width: 100%;
        height: 180px;
        object-fit: cover;
    }}
    .news-body {{
        padding: 20px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .news-headline {{
        font-size: 16px;
        font-weight: bold;
        line-height: 1.4;
        margin-bottom: 15px;
        color: #ffffff;
    }}
    .news-meta {{
        font-size: 12px;
        color: #9aa0a6;
    }}
    .news-tag {{
        color: #00c6ff;
        font-weight: bold;
        margin-top: 5px;
        font-size: 11px;
    }}
    </style>
""", unsafe_allow_html=True)

# 상단 히어로 배너 출력
st.markdown(f"""
    <div class="hero-section">
        <div class="hero-title">{T["title"]}</div>
        <div class="hero-subtitle">🏔️ {T["subtitle"]}</div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="content-box">', unsafe_allow_html=True)

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
        st.info("⚙️ **Global Sync System**\nFully responsive with instant race administration telemetry integration.")
        
    with col_video:
        st.markdown(f"### {T['video']}")
        st.video("https://youtu.be/KgyX5OjMTyM?si=Uu8mCwLV2X4an8Wk")

    with col_photo:
        st.markdown(f"### {T['photo']}")
        st.image("https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=600&q=80", caption="Olympic Ski Mountaineering Athlete")

    # ==========================================
    # 4. [신규 추가] NEWS & STORIES 섹션 (보내준 사진 양식 반영)
    # ==========================================
    st.markdown("---")
    st.header(T["news_title"])
    
    # 3열 격자(Grid) 배치로 카드 배치
    n_col1, n_col2, n_col3 = st.columns(3)
    
    with n_col1:
        st.markdown(f"""
        <div class="news-card">
            <img class="news-img" src="https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=500&q=80">
            <div class="news-body">
                <div class="news-headline">French Alps 2030 proposal marks major milestone for ski mountaineering</div>
                <div class="news-meta">
                    📅 June 9, 2026<br>
                    <span class="news-tag"># {T["news_tag"]} # Olympics</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with n_col2:
        st.markdown(f"""
        <div class="news-card">
            <img class="news-img" src="https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=500&q=80">
            <div class="news-body">
                <div class="news-headline">ISMF Releases Provisional 2026/27 International Calendar</div>
                <div class="news-meta">
                    📅 June 3, 2026<br>
                    <span class="news-tag"># {T["news_tag"]} # Competitions</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with n_col3:
        st.markdown(f"""
        <div class="news-card">
            <img class="news-img" src="https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=500&q=80">
            <div class="news-body">
                <div class="news-headline">Looking Ahead: Key Olympic Qualification Moments in June</div>
                <div class="news-meta">
                    📅 May 29, 2026<br>
                    <span class="news-tag"># {T["news_tag"]} # RoadToMilano</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 하단 파트너 배너 구역
    st.markdown("---")
    st.subheader("🤝 Global Partners & Sponsors")
    c_ad1, c_ad2, c_ad3 = st.columns(3)
    c_ad1.info("⛷️ **Premium Sponsor**\nGlobal Brand Ad Slot")
    c_ad2.info("🏨 **Official Lodging**\nResort & Hotel Partner")
    c_ad3.info("🥤 **Official Beverage**\nEnergy Drink Sponsor")

# --- [모듈 2] 선수 참가 신청 ---
elif menu_index == 1:
    if "athletes" not in st.session_state: st.session_state.athletes = []
    st.header(T["menu"][1])
    with st.form("global_reg_form"):
        p_name = st.text_input("Name")
        p_nation = st.text_input("Nationality")
        p_event = st.selectbox("Event Category", ["Sprint", "Individual", "Vertical"])
        st.metric("Registration Fee", "30,000 KRW")
        submit_btn = st.form_submit_button(T["pay"])
        if submit_btn and p_name:
            st.success("Registration Successful!")

# --- [모듈 3] 실시간 리더보드 ---
elif menu_index == 2:
    st.header(T["menu"][2])
    st.warning("No dynamic telemetry data found in session. Database ready.")

# --- [모듈 4] 🔐 심판 및 관리자 패널 ---
elif menu_index == 3:
    st.header(T["menu"][3])
    st.info("System operational. Field telemetry bridge secure.")

st.markdown('</div>', unsafe_allow_html=True)
