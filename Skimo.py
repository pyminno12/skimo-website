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
    "https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=1800&q=80",
    "https://images.unsplash.com/photo-1518098268026-4e43a1a009de?auto=format&fit=crop&w=1800&q=80"   
]

# 시스템 구동 상태 상태 정의
if "menu_idx" not in st.session_state:
    st.session_state.menu_idx = 0
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# ------------------------------------------
# [도메인 모델 구조화]: 세션 내 데이터 설계
# ------------------------------------------

# A. 사용자 및 권한 도메인 (Judge & Auth Domain)
if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "admin": {"pw": "1234", "role": "ADMIN"},
        "skimo": {"pw": "skimo123", "role": "JUDGE"}
    }

# B. 선수 및 경기/기록 데이터 통합 도메인 (Athlete & Telemetry Domain)
if "athletes_domain" not in st.session_state:
    st.session_state.athletes_domain = {
        "101": {"Name": "김민우", "Team": "KOREA", "Category": "Sprint", "Status": "RACING", "CP1": "10:15:20", "CP2": "--:--:--", "Penalty_Sec": 0, "Final_Record": "--:--:--"},
        "102": {"Name": "Alex Smith", "Team": "USA", "Category": "Individual", "Status": "RACING", "CP1": "10:14:05", "CP2": "10:45:12", "Penalty_Sec": 0, "Final_Record": "--:--:--"},
        "103": {"Name": "Chloe", "Team": "FRANCE", "Category": "Vertical", "Status": "RACING", "CP1": "10:16:55", "CP2": "10:49:30", "Penalty_Sec": 10, "Final_Record": "--:--:--"},
    }

# C-1. 글로벌 공지사항 데이터 (Notice Domain)
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

# [신규 추가] C-2. 홈 화면용 글로벌 최신 뉴스 데이터 (Home News Domain)
if "home_news_domain" not in st.session_state:
    st.session_state.home_news_domain = [
        {
            "date": "2026-06-18",
            "link": "https://www.ismf-ski.org/",
            "title": {
                "KO": "🚀 2030 프랑스 알프스 동계 올림픽, 산악스키 세부 종목 규정 발표 예정",
                "EN": "🚀 2030 French Alps Winter Olympics: Detailed Skimo Regulations to be Announced",
                "FR": "🚀 Jeux Olympiques d'hiver des Alpes Françaises 2030 : Les règlements détaillés du Skimo seront annoncés",
                "IT": "🚀 Olimpiadi Invernali delle Alpi Francesi 2030: Saranno annunciati i regolamenti dettagliati dello Skimo",
                "ZH": "🚀 2030年法国阿尔卑斯冬季奥运会：滑雪登山详细项目规则即将公布",
                "JA": "🚀 2030年フランス・アルプス冬季オリンピック、山岳スキー詳細種目規定がまもなく発表予定"
            }
        },
        {
            "date": "2026-06-12",
            "link": "https://www.ismf-ski.org/",
            "title": {
                "KO": "❄️ 아시아 산악스키 연맹, 청소년 선수 육성을 위한 동계 캠프 평창 개최 확정",
                "EN": "❄️ Asian Skimo Federation Confirms Winter Youth Development Camp in Pyeongchang",
                "FR": "❄️ La Fédération Asiatique de Skimo confirme un camp de développement pour les jeunes à Pyeongchang",
                "IT": "❄️ La Federazione Asiatica Skimo conferma il campo di sviluppo giovanile invernale a Pyeongchang",
                "ZH": "❄️ 亚洲滑雪登山联盟确认将在平昌举办冬季青少年选手培育训练营",
                "JA": "❄️ アジア山岳スキー連盟、青少年選手育成のための冬季キャンプを平昌で開催確定"
            }
        },
        {
            "date": "2026-06-05",
            "link": "https://www.ismf-ski.org/",
            "title": {
                "KO": "🏅 대한민국 산악스키 국가대표팀, 뉴질랜드 전지훈련 위해 출국",
                "EN": "🏅 National Skimo Team Departs for Off-Season Training in New Zealand",
                "FR": "🏅 L'équipe nationale de Skimo part pour un entraînement hors saison en Nouvelle-Zélande",
                "IT": "🏅 La squadra nazionale di Skimo parte per l'allenamento fuori stagione in Nuova Zelanda",
                "ZH": "🏅 韩国滑雪登山国家队启程前往新西兰展开新赛季海外集训",
                "JA": "🏅 山岳スキー大韓民国国家代表チーム、ニュージーランド海外遠征トレーニングのため 출국"
            }
        }
    ]

selected_bg = BG_IMAGES[st.session_state.menu_idx] if st.session_state.menu_idx < len(BG_IMAGES) else BG_IMAGES[0]

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
    .custom-header-bg {{ background-color: rgba(15, 32, 39, 0.4); backdrop-filter: blur(5px); width: 100%; padding: 10px 0; }}
    
    .notice-card {{
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px; padding: 20px; margin-bottom: 15px; transition: transform 0.2s, background 0.2s;
    }}
    .notice-card:hover {{ background: rgba(255, 255, 255, 0.09); transform: translateY(-2px); }}
    .notice-badge {{ background-color: #00c6ff; color: #111; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-right: 10px; }}
    .notice-date {{ color: #cbd5e1; font-size: 13px; }}
    .notice-title {{ font-size: 18px; font-weight: 600; color: #ffffff; margin-top: 8px; margin-bottom: 8px; }}
    .notice-content {{ font-size: 14px; color: #e2e8f0; line-height: 1.6; }}
    
    div.stButton > button {{
        background: transparent !important; color: white !important; border: none !important; padding: 0px !important;
        margin-left: 20px !important; font-size: 14px !important; font-weight: 500 !important; transition: color 0.2s !important;
    }}
    div.stButton > button:hover {{ color: #00c6ff !important; background: transparent !important; }}
    div.stButton > button:focus {{ color: #00c6ff !important; box-shadow: none !important; }}
    
    .hero-section {{ height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; text-align: center; }}
    .hero-title {{ font-size: 42px; font-weight: 800; text-shadow: 3px 3px 8px rgba(0,0,0,0.9); margin-bottom: 5px; letter-spacing: 1px; }}
    .hero-subtitle {{ font-size: 18px; font-weight: 500; text-shadow: 2px 2px 4px rgba(0,0,0,0.7); color: #00c6ff; }}
    
    .content-box {{ 
        max-width: 1200px; margin: 0 auto 50px auto; padding: 30px; background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.15); color: #ffffff;
    }}
    
    .news-list-item {{ padding: 14px 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.15); display: flex; justify-content: space-between; align-items: center; }}
    .news-list-item:last-child {{ border-bottom: none; }}
    .news-list-title {{ font-size: 15px; font-weight: 500; color: #e2e8f0; text-decoration: none; transition: color 0.2s; }}
    .news-list-title:hover {{ color: #00c6ff; }}
    .news-list-meta {{ font-size: 13px; color: #cbd5e1; white-space: nowrap; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 6개국 다국어 번역 사전
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
        "news_title": "📰 News & Stories (글로벌 최신 소식)", "search_holder": "🔍 검색어를 입력하세요...", "notice": "📢 공지사항", "auth": "👤 로그인/회원가입"
    },
    "EN": {
        "title": "SKIMO KOREA", "subtitle": "Ski Mountaineering Information Portal",
        "menu": ["Home", "Athlete Registration", "Live Leaderboard", "🔐 Judge/Admin Panel", "📢 Global Notice"],
        "desc": "This tournament complies with ISMF regulations. Scoring and penalties are aggregated in real-time globally via the field web app.",
        "video": "📺 Skimo Rules Video", "intro_video": "⛷️ What is Skimo?", "photo": "📸 Olympic Action Gallery", "pay": "💳 Register & Secure Pay",
        "news_title": "📰 News & Stories (Global Latest News)", "search_holder": "🔍 Search information...", "notice": "📢 Notice", "auth": "👤 Login/Register"
    },
    "FR": {
        "title": "SKIMO CORÉE", "subtitle": "Portail d'information sur le ski-alpinisme",
        "menu": ["Accueil", "Inscription des athlètes", "Tableau croisé en direct", "🔐 Panel des juges/admin", "📢 Annonces Globales"],
        "desc": "Ce tournoi est conforme aux règlements de l'ISMF. Les scores et les pénalités sont agrégés en temps réel via l'application web de terrain.",
        "video": "📺 Vidéo des règles", "intro_video": "⛷️ Qu'est-ce que le Skimo?", "photo": "📸 Galerie Olympique", "pay": "💳 S'inscrire et payer",
        "news_title": "📰 Nouvelles et histoires", "search_holder": "🔍 Rechercher des informations...", "notice": "📢 Annonces", "auth": "👤 Connexion/S'inscrire"
    },
    "IT": {
        "title": "SKIMO COREA", "subtitle": "Portale di informazioni sullo sci alpinismo",
        "menu": ["Home", "Iscrizione Atleti", "Classifica in Tempo Reale", "🔐 Pannello Giudici/Admin", "📢 Avvisi Globali"],
        "desc": "Questo torneo é conforme ai regolamenti ISMF. I punteggi e le penalità vengono aggregati in tempo reale tramite l'app web sul campo.",
        "video": "📺 Video del regolamento", "intro_video": "⛷️ Cos'è lo Skimo?", "photo": "📸 Galleria d'azione olimpica", "pay": "💳 Iscriviti e paga",
        "news_title": "📰 Notizie e storie", "search_holder": "🔍 Cerca informazioni...", "notice": "📢 Avvisi", "auth": "👤 Accedi/Registrati"
    },
    "ZH": {
        "title": "SKIMO 韩国", "subtitle": "滑雪登山信息门户网站",
        "menu": ["首页", "运动员报名", "实时排行榜", "🔐 裁判/管理员面板", "📢 全球公告"],
        "desc": "本次比赛遵守国际滑雪登山联盟(ISMF)规定。得分和处罚通过现场网络应用全球实时汇总。",
        "video": "📺 比赛规则视频", "intro_video": "⛷️ 什么是滑雪登山?", "photo": "📸 奥运现场画廊", "pay": "💳 立即报名与安全支付",
        "news_title": "📰 新闻与故事", "search_holder": "🔍 输入搜索内容...", "notice": "📢 官方公告", "auth": "👤 登录/注册"
    },
    "JA": {
        "title": "SKIMO KOREA", "subtitle": "山岳スキー情報ポータル",
        "menu": ["大会ホーム", "選手参加申し込み", "リアルタイム順位表", "🔐 審判/管理者パネル", "📢 グローバルお知らせ"],
        "desc": "本大会は国際山岳スキー連盟(ISMF)の規則に準拠しており、フィールド審判システムと同期して世界中にリアルタイムでリザルトを配信します。",
        "video": "📺 競技種目のご案内", "intro_video": "⛷️ 山岳スキーとは？", "photo": "📸 オリンピックギャラリー", "pay": "💳 参加申し込みと安全決済",
        "news_title": "📰 ニュース&ストーリー", "search_holder": "🔍 検索キーワードを入力...", "notice": "📢 お知らせ", "auth": "👤 ログイン/会員登録"
    }
}

# 계정 관리 대화상자
@st.dialog("🔐 SKIMO KOREA 계정 관리")
def auth_dialog():
    tab1, tab2 = st.tabs(["👤 로그인", "📝 회원가입"])
    with tab1:
        st.write("포털 서비스를 위해 로그인해 주세요.")
        login_id = st.text_input("아이디", key="login_id")
        login_pw = st.text_input("비밀번호", type="password", key="login_pw")
        if st.button("로그인 완료", use_container_width=True):
            if login_id in st.session_state.user_db and st.session_state.user_db[login_id]["pw"] == login_pw:
                st.session_state.logged_in_user = login_id
                st.success(f"🎉 {login_id}님, 환영합니다!")
                time.sleep(1)
                st.rerun()
            else: st.error("❌ 비밀번호가 일치하지 않습니다.")

# ==========================================
# 3. 상단 네비게이션 및 라우터 제어
# ==========================================
st.markdown('<div class="custom-header-bg">', unsafe_allow_html=True)
st.markdown('<div class="centered-wrapper">', unsafe_allow_html=True)

if "current_lang_code" not in st.session_state:
    st.session_state.current_lang_code = "KO"

T = LOCALIZED_TEXT[st.session_state.current_lang_code]
c_menu, c_search, c_right = st.columns([3, 4, 5])

SEARCH_KEYWORDS = {
    0: ["홈", "대회", "소개", "뉴스", "소식", "경기", "갤러리", "영상", "home", "news"],
    1: ["선수", "참가", "신청", "등록", "접수"],
    2: ["실시간", "리더", "보드", "라이브", "순위"],
    3: ["심판", "관리자", "패널"],
    4: ["공지", "사항", "알림"]
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
    selected_menu_raw = st.selectbox("Menu Select", menu_list, index=st.session_state.menu_idx if st.session_state.menu_idx < len(menu_list) else 0, label_visibility="collapsed")
    menu_index = menu_list.index(selected_menu_raw)
    if st.session_state.menu_idx != menu_index:
        st.session_state.menu_idx = menu_index
        st.rerun()
    
with c_right:
    sub_lang, sub_buttons = st.columns([4, 6])
    with sub_lang:
        selected_lang_name = st.selectbox("Global Select", list(LANG_DICT.keys()), index=list(LANG_DICT.values()).index(st.session_state.current_lang_code), label_visibility="collapsed")
        new_lang_code = LANG_DICT[selected_lang_name]
        if st.session_state.current_lang_code != new_lang_code:
            st.session_state.current_lang_code = new_lang_code
            st.rerun()
        
    with sub_buttons:
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            if st.button(T["notice"], key="notice_top_nav_btn"):
                st.session_state.menu_idx = 4
                st.rerun()
        with btn_col2:
            if st.session_state.logged_in_user is None:
                if st.button(T["auth"], key="auth_btn"): auth_dialog()
            else:
                if st.button(f"🔓 로그아웃 ({st.session_state.logged_in_user})", key="logout_btn"):
                    st.session_state.logged_in_user = None
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 히어로 헤더
st.markdown(f'<div class="centered-wrapper"><div class="hero-section"><div class="hero-title">{T["title"]}</div><div class="hero-subtitle">🏔️ {T["subtitle"]}</div></div></div>', unsafe_allow_html=True)
st.markdown('<div class="content-box">', unsafe_allow_html=True)

# -------------------------------------------------------------------------
# [콘텐츠 분기 1] 대회 홈 화면 (menu_idx == 0) - 업데이트 집중 영역!
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
        try: st.image("https://raw.githubusercontent.com/pyminno12/skimo-website/main/skimo_race_1.jpg", use_container_width=True)
        except: st.error("⚠️ Image Load Error")

    # [💡 업데이트]: 메인 홈 화면 하단의 NEWS & STORIES 섹션을 글로벌 세션 객체와 바인딩
    st.markdown("<hr style='border-color: rgba(255,255,255,0.15);'>", unsafe_allow_html=True)
    st.markdown(f"## {T['news_title']}")
    
    st.markdown("<div style='background-color: rgba(255, 255, 255, 0.04); padding: 10px 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    lang_code = st.session_state.current_lang_code
    for item in st.session_state.home_news_domain:
        # 사용자가 선택한 언어 코드를 파싱하고, 없을 경우 영어(EN)를 디폴트로 매핑
        localized_news_title = item["title"].get(lang_code, item["title"]["EN"])
        
        st.markdown(f"""
            <div class="news-list-item">
                <a href="{item['link']}" target="_blank" class="news-list-title">📌 {localized_news_title}</a>
                <span class="news-list-meta">📅 {item['date']}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# [콘텐츠 분기 2] 선수 참가 신청 (menu_idx == 1)
elif st.session_state.menu_idx == 1:
    st.markdown(f"## {T['menu'][1]}")
    with st.form("global_reg_form"):
        p_name = st.text_input("Name")
        p_nation = st.text_input("Nationality")
        p_event = st.selectbox("Event Category", ["Sprint", "Individual", "Vertical"])
        submit_btn = st.form_submit_button(T["pay"])
        if submit_btn and p_name:
            next_bib = str(100 + len(st.session_state.athletes_domain) + 1)
            st.session_state.athletes_domain[next_bib] = {"Name": p_name, "Team": p_nation, "Category": p_event, "Status": "RACING", "CP1": "--:--:--", "CP2": "--:--:--", "Penalty_Sec": 0, "Final_Record": "--:--:--"}
            st.success(f"🎉 배정된 배번호는 [{next_bib}] 입니다.")

# [콘텐츠 분기 3] 실시간 리더보드 (menu_idx == 2)
elif st.session_state.menu_idx == 2:
    st.markdown(f"## {T['menu'][2]}")
    data_list = [{"BIB": b, **i} for b, i in st.session_state.athletes_domain.items()]
    df = pd.DataFrame(data_list)[["BIB", "Name", "Team", "Category", "Status", "CP1", "CP2", "Penalty_Sec", "Final_Record"]]
    st.dataframe(df.set_index("BIB"), use_container_width=True)

# [콘텐츠 분기 4] 🔐 심판/관리자 패널 (menu_idx == 3)
elif st.session_state.menu_idx == 3:
    st.markdown(f"## {T['menu'][3]}")
    if st.session_state.logged_in_user is None: st.warning("⚠️ 심판 전용 패널입니다. 로그인을 완료해 주세요.")
    else:
        bib_list = list(st.session_state.athletes_domain.keys())
        selected_bib = st.selectbox("BIB 선택", bib_list)
        target = st.session_state.athletes_domain[selected_bib]
        new_status = st.selectbox("상태 변경", ["RACING", "FINISHED", "DNF", "DSQ"])
        if st.button("🚨 동기화"):
            st.session_state.athletes_domain[selected_bib]["Status"] = new_status
            st.success("반영되었습니다.")
            st.rerun()

# [콘텐츠 분기 5] 📢 글로벌 공지사항 및 뉴스 피드 페이지 (menu_idx == 4)
elif st.session_state.menu_idx == 4:
    lang_code = st.session_state.current_lang_code
    st.markdown(f"## {T['menu'][4]}")
    for item in st.session_state.notice_domain:
        title_text = item["title"].get(lang_code, item["title"]["EN"])
        content_text = item["content"].get(lang_code, item["content"]["EN"])
        st.markdown(f'<div class="notice-card"><div><span class="notice-badge">{item["category"]}</span><span class="notice-date">📅 {item["date"]}</span></div><div class="notice-title">{title_text}</div><div class="notice-content">{content_text}</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
