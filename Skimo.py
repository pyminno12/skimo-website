import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ==========================================
# 1. 페이지 설정 및 레이아웃 규격 최적화
# ==========================================
st.set_page_config(page_title="SKIMO KOREA", page_icon="🏔️", layout="wide")

# 배경 이미지 링크 매핑 (공지사항 전용 배경 이미지 1장 추가)
BG_IMAGES = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=1800&q=80",
    "https://images.unsplash.com/photo-1518098268026-4e43a1a009de?auto=format&fit=crop&w=1800&q=80" # 공지사항용 배경  
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

# [신규] C. 콘텐츠 및 다국어 지원 도메인 - 글로벌 공지사항/뉴스 데이터
if "notice_domain" not in st.session_state:
    st.session_state.notice_domain = [
        {
            "date": "2026-06-15",
            "category": "🏆 Race Info",
            "title": {
                "KO": "2026/27 ISMF 산악스키 월드컵 개막전 일정 확정 (프랑스 알프스)",
                "EN": "2026/27 ISMF Ski Mountaineering World Cup Opening Venue Confirmed (French Alps)",
                "FR": "Ouverture de la Coupe du Monde de Ski-Alpinisme ISMF 2026/27 Confirmée (Alpes Françaises)",
                "IT": "Confermata l'Apertura della Coppa del Mondo ISMF 2026/27 (Alpi Francesi)",
                "ZH": "2026/27 ISMF 滑雪登山世界杯揭幕战日程 확정 (法国阿尔卑斯)",
                "JA": "2026/27 ISMF 山岳スキーワールド컵開幕戦日程確定 (フランス・アルプス)"
            },
            "content": {
                "KO": "국제산악스키연맹(ISMF)이 다가오는 시즌 개막전을 프랑스 알프스에서 개최한다고 밝혔습니다. 이번 대회는 올림픽 규격에 맞춘 새로운 스프린트 코스가 도입될 예정입니다.",
                "EN": "The ISMF announced that the upcoming season opener will be held in the French Alps, featuring a brand-new sprint course optimized for Olympic standards.",
                "FR": "L'ISMF a annoncé que l'ouverture de la saison prochaine aura lieu dans les Alpes françaises, avec un tout nouveau parcours de sprint optimisé pour les normes olympiques.",
                "IT": "L'ISMF ha annunciato che l'apertura della prossima stagione si terrà nelle Alpi francesi, con un percorso sprint completamente nuovo ottimizzato per gli standard olimpici.",
                "ZH": "国际滑雪登山联盟 (ISMF) 宣布, 即将到来的赛季揭幕战将在法国阿尔卑斯山举行, 并引入符合奥运标准的全新短距离赛道。",
                "JA": "国際山岳スキー連盟(ISMF)は、来シーズンの開幕戦をフランス・アルプスで開催すると発表しました。今大会ではオリンピック基準に最適化された新しいスプリントコースが導入されます。"
            }
        },
        {
            "date": "2026-06-10",
            "category": "⛷️ Athlete News",
            "title": {
                "KO": "산악스키 전설 레미 보네(Rémi Bonnet), 고산 지대 하계 훈련 돌입",
                "EN": "Skimo Legend Rémi Bonnet Starts High-Altitude Summer Training",
                "FR": "La légende du Skimo Rémi Bonnet commence son entraînement d'été en haute altitude",
                "IT": "La leggenda dello Skimo Rémi Bonnet inizia l'allenamento estivo in alta quota",
                "ZH": "滑雪登山传奇选手 雷米·博内 (Rémi Bonnet) 开启高海拔夏季 Road 训练",
                "JA": "山岳スキーのレジェンド、レミ・ボネ(Rémi Bonnet)が高地夏季トレーニングを開始"
            },
            "content": {
                "KO": "세계 랭킹 1위 레미 보네 선수가 차기 대회를 대비해 스위스 고산지대에서 체력 및 지구력 증진을 위한 본격적인 하계 크로스 트레이닝을 시작했습니다.",
                "EN": "World No. 1 Rémi Bonnet has begun intensive high-altitude cross-training in Switzerland to build endurance and strength for the upcoming winter season.",
                "FR": "Le numéro 1 mondial Rémi Bonnet a commencé un entraînement croisé intensif en haute altitude en Suisse pour renforcer son endurance en vue de la saison hivernale.",
                "IT": "Il numero 1 al mondo Rémi Bonnet ha iniziato un intenso allenamento incrociato in alta quota in Svizzera per sviluppare la resistenza in vista della stagione invernale.",
                "ZH": "世界排名第一的雷米·博内选手已在瑞士高海拔地区展开密集的交叉训练, 为即将 이르는 겨울 시즌 체력과 지구력을 보강하고 있습니다.",
                "JA": "世界ランキング1位のレミ・ボネ選手が、次기シーズンに向けスイスの高地で体力および持久力向上のための本格的な夏季クロストレーニングを開始しました。"
            }
        },
        {
            "date": "2026-06-01",
            "category": "📢 Notice",
            "title": {
                "KO": "SKIMO KOREA 플랫폼 내 실시간 심판 모바일 원격 계측 시스템 도입 안내",
                "EN": "Introduction of Real-time Mobile Remote Scoring System for Judges",
                "FR": "Introduction du système de pointage mobile à distance en temps réel pour les juges",
                "IT": "Introduzione del sistema di punteggio remoto mobile in tempo reale per i giudici",
                "ZH": "SKIMO KOREA 平台引入现场裁判移动端远程实时记分系统通知",
                "JA": "SKIMO KOREA プラットフォーム内 リアルタイム審判モバイル遠隔計測システム導入のご案内"
            },
            "content": {
                "KO": "현장 심판 패널의 모바일 인터페이스 고도화로, 거친 설산의 체크포인트(CP)에서도 딜레이 없이 리더보드로 데이터가 즉각 동기화됩니다.",
                "EN": "With the upgrade of the field judge interface, checkpoint (CP) data on rugged snow mountains synchronizes instantly with the global leaderboard without any delay.",
                "FR": "Grâce à la mise à niveau de l'interface des juges de terrain, les données des points de contrôle (CP) se synchronisent instantanément avec le classement mondial.",
                "IT": "Con l'aggiornamento dell'interfaccia dei giudici sul campo, i dati dei checkpoint (CP) si sincronizzano istantaneamente con la classifica globale.",
                "ZH": "随着现场裁判端界面的升级, 恶劣雪山中的检查点 (CP) 数据将毫无延迟地即时同步至全球排行榜。",
                "JA": "現場審判パネルのモバイルインターフェース高度化により、過酷な雪山のチェックポイント(CP)からでも遅延なくリーダーボードへデータが即座に同期されます。"
            }
        }
    ]

# 선택된 메뉴 인덱스에 기반한 배경화면 매핑
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
    
    .custom-header-bg {{
        background-color: rgba(15, 32, 39, 0.4);
        backdrop-filter: blur(5px);
        width: 100%;
        padding: 10px 0;
    }}
    
    /* 공지사항 카드 스타일 정의 */
    .notice-card {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.2s, background 0.2s;
    }}
    .notice-card:hover {{
        background: rgba(255, 255, 255, 0.09);
        transform: translateY(-2px);
    }}
    .notice-badge {{
        background-color: #00c6ff;
        color: #111;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 10px;
    }}
    .notice-date {{
        color: #cbd5e1;
        font-size: 13px;
    }}
    .notice-title {{
        font-size: 18px;
        font-weight: 600;
        color: #ffffff;
        margin-top: 8px;
        margin-bottom: 8px;
    }}
    .notice-content {{
        font-size: 14px;
        color: #e2e8f0;
        line-height: 1.6;
    }}
    
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
        "menu": ["대회 홈", "선수 참가 신청", "실시간 리더보드 (LIVE)", "🔐 심판/관리자 패널", "📢 글로벌 공지사항"],
        "desc": "본 대회는 국제산악스키연맹(ISMF) 규정을 준수하며, field 심판 시스템과 동기화되어 실시간 기록을 전 세계에 생중계합니다.",
        "video": "📺 경기 종목 안내", "intro_video": "⛷️ 산악스키 소개", "photo": "📸 올림픽 현장 갤러리", "pay": "💳 참가 신청 및 안전 결제",
        "news_title": "📰 News & Stories (최신 소식)", "search_holder": "🔍 검색어를 입력하세요...", "notice": "📢 공지사항", "auth": "👤 로그인/회원가입"
    },
    "EN": {
        "title": "SKIMO KOREA", "subtitle": "Ski Mountaineering Information Portal",
        "menu": ["Home", "Athlete Registration", "Live Leaderboard", "🔐 Judge/Admin Panel", "📢 Global Notice"],
        "desc": "This tournament complies with ISMF regulations. Scoring and penalties are aggregated in real-time globally via the field web app.",
        "video": "📺 Skimo Rules Video", "intro_video": "⛷️ What is Skimo?", "photo": "📸 Olympic Action Gallery", "pay": "💳 Register & Secure Pay",
        "news_title": "📰 News & Stories", "search_holder": "🔍 Search information...", "notice": "📢 Notice", "auth": "👤 Login/Register"
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
        "desc": "Questo torneo è conforme ai regolamenti ISMF. I punteggi e le penalità vengono aggregati in tempo reale tramite l'app web sul campo.",
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
        "desc": "본 대회는 국제산악스키연맹(ISMF)의規則에 준거하고 있으며、フィールド審判システムと同期して世界中にリアルタイムでリザルトを配信します。",
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
            if login_id in st.session_state.user_db and st.session_state.user_db[login_id]["pw"] == login_pw:
                st.session_state.logged_in_user = login_id
                st.success(f"🎉 {login_id}님, 환영합니다! ({st.session_state.user_db[login_id]['role']} 권한)")
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
                st.session_state.user_db[new_id] = {"pw": new_pw, "role": "JUDGE"}
                st.success("📝 회원가입이 완료되었습니다! 로그인 탭에서 로그인해 주세요.")

# ==========================================
# 3. 상단 레이아웃 배치 및 검색 엔진
# ==========================================
st.markdown('<div class="custom-header-bg">', unsafe_allow_html=True)
st.markdown('<div class="centered-wrapper">', unsafe_allow_html=True)

if "current_lang_code" not in st.session_state:
    st.session_state.current_lang_code = "KO"

T = LOCALIZED_TEXT[st.session_state.current_lang_code]

c_menu, c_search, c_right = st.columns([3, 4, 5])

# 검색 엔진 키워드 사전에 공지사항 인덱스(4번) 매핑
SEARCH_KEYWORDS = {
    0: ["홈", "대회", "소개", "뉴스", "소식", "경기", "갤러리", "영상", "home", "accueil", "首页", "ホーム"],
    1: ["선수", "참가", "신청", "등록", "결제", "접수", "form", "register", "inscription", "报名", "申し込み"],
    2: ["실시간", "리더", "보드", "라이브", "순위", "기록", "live", "leaderboard", "tableau", "classifica", "排行", "順位"],
    3: ["심판", "관리자", "패널", "로그", "판정", "panel", "judge", "admin", "juges", "裁判", "審判"],
    4: ["공지", "사항", "알림", "근황", "피드", "notice", "annonces", "avvisi", "公告", "お知らせ"]
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
            # [변경 기능]: '#' 링크 대신 streamlit 버튼을 배치해 클릭 시 '공지사항(인덱스 4)' 페이지로 이동하도록 바인딩
            if st.button(T["notice"], key="notice_top_nav_btn"):
                st.session_state.menu_idx = 4
                st.rerun()
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
# 5. 메인 뷰 컴포넌트 분기 관리
# ==========================================
st.markdown('<div class="content-box">', unsafe_allow_html=True)

# [콘텐츠 분기 1] 대회 홈 화면 (menu_idx == 0)
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

    # NEWS & STORIES 요약
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

# [콘텐츠 분기 2] 선수 참가 신청 (menu_idx == 1)
elif st.session_state.menu_idx == 1:
    st.markdown(f"## {T['menu'][1]}")
    
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
            next_bib = str(100 + len(st.session_state.athletes_domain) + 1)
            st.session_state.athletes_domain[next_bib] = {
                "Name": p_name, "Team": p_nation, "Category": p_event, "Status": "RACING",
                "CP1": "--:--:--", "CP2": "--:--:--", "Penalty_Sec": 0, "Final_Record": "--:--:--"
            }
            st.success(f"🎉 성공적으로 신청되었습니다! 배정된 배번호(BIB)는 [{next_bib}] 입니다.")

# [콘텐츠 분기 3] 실시간 리더보드 (menu_idx == 2)
elif st.session_state.menu_idx == 2:
    st.markdown(f"## {T['menu'][2]}")
    data_list = []
    for bib, info in st.session_state.athletes_domain.items():
        row = {"BIB": bib}
        row.update(info)
        data_list.append(row)
    df = pd.DataFrame(data_list)
    df = df[["BIB", "Name", "Team", "Category", "Status", "CP1", "CP2", "Penalty_Sec", "Final_Record"]]
    st.dataframe(df.set_index("BIB"), use_container_width=True)

# [콘텐츠 분기 4] 🔐 심판/관리자 패널 (menu_idx == 3)
elif st.session_state.menu_idx == 3:
    st.markdown(f"## {T['menu'][3]}")
    current_user = st.session_state.logged_in_user
    if current_user is None:
        st.warning("⚠️ 이 패널은 현장 심판 및 관리자 전용입니다. 먼저 로그인을 완료해 주세요.")
    else:
        user_role = st.session_state.user_db[current_user]["role"]
        st.write(f"💼 접속 계정: **{current_user}** | 🛡️ 시스템 권한: `{user_role}`")
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        st.subheader("⏱️ 경기 현장 데이터 원격 제어 (Live Telemetry Controller)")
        
        col_select, col_edit = st.columns([4, 8])
        with col_select:
            st.write("📋 현재 출전 선수 명단")
            bib_list = list(st.session_state.athletes_domain.keys())
            selected_bib = st.selectbox("수정할 선수의 배번호(BIB) 선택", bib_list)
            target_athlete = st.session_state.athletes_domain[selected_bib]
            st.info(f"선수명: {target_athlete['Name']} ({target_athlete['Team']})\n\n종목: {target_athlete['Category']}")
            
        with col_edit:
            st.write("⚙️ 실시간 선수 상태 및 계측 데이터 업데이트")
            status_options = ["RACING", "FINISHED", "DNF (기권)", "DSQ (실격)"]
            current_status_idx = status_options.index(target_athlete["Status"]) if target_athlete["Status"] in status_options else 0
            new_status = st.selectbox("레이스 상태 설정", status_options, index=current_status_idx)
            
            c1, c2 = st.columns(2)
            with c1: new_cp1 = st.text_input("Checkpoint 1 통과 시간", value=target_athlete["CP1"])
            with c2: new_cp2 = st.text_input("Checkpoint 2 통과 시간", value=target_athlete["CP2"])
            new_penalty = st.number_input("부과할 페널티 시간 (초 단위)", min_value=0, value=int(target_athlete["Penalty_Sec"]), step=5)
            
            if st.button("🚨 변경 사항 경기 데이터베이스에 동기화", use_container_width=True):
                st.session_state.athletes_domain[selected_bib]["Status"] = new_status
                st.session_state.athletes_domain[selected_bib]["CP1"] = new_cp1
                st.session_state.athletes_domain[selected_bib]["CP2"] = new_cp2
                st.session_state.athletes_domain[selected_bib]["Penalty_Sec"] = new_penalty
                st.success(f"✅ 경기 기록이 성공적으로 실시간 도메인 모델에 반영되었습니다!")
                time.sleep(1)
                st.rerun()

# -------------------------------------------------------------------------
# [신규 콘텐츠 분기 5] 📢 글로벌 공지사항 및 뉴스 피드 페이지 (menu_idx == 4)
# -------------------------------------------------------------------------
elif st.session_state.menu_idx == 4:
    lang_code = st.session_state.current_lang_code
    
    # 다국어 뷰를 위한 페이지 헤더 매핑
    page_titles = {
        "KO": "📢 글로벌 공지사항 및 세계 산악스키 뉴스",
        "EN": "📢 Global Announcements & World Skimo News",
        "FR": "📢 Annonces Globales et Nouvelles du Skimo Mondial",
        "IT": "📢 Avvisi Globali e Notizie del Mondo dello Sci Alpinismo",
        "ZH": "📢 全球公告与世界滑雪登山最新动态",
        "JA": "📢 グローバルお知らせ＆世界山岳スキーニュース"
    }
    
    st.markdown(f"## {page_titles[lang_code]}")
    st.markdown("<p style='color:#cbd5e1;'>국제산악스키연맹(ISMF)의 최신 경기 동향, 월드컵 일정, 그리고 글로벌 선수들의 생생한 훈련 근황을 다국어로 실시간 제공합니다.</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.15);'>", unsafe_allow_html=True)
    
    # 도메인 모델 데이터셋 순회하며 카드로 시각화 출력
    for item in st.session_state.notice_domain:
        # 현재 선택된 국가 언어 코드에 맞춰 알맞은 번역 텍스트를 파싱
        title_text = item["title"].get(lang_code, item["title"]["EN"])
        content_text = item["content"].get(lang_code, item["content"]["EN"])
        
        st.markdown(f"""
            <div class="notice-card">
                <div>
                    <span class="notice-badge">{item['category']}</span>
                    <span class="notice-date">📅 {item['date']}</span>
                </div>
                <div class="notice-title">{title_text}</div>
                <div class="notice-content">{content_text}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
