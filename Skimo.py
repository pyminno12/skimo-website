import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import json

# ==========================================
# 1. 페이지 설정 및 글로벌 상태 정의
# ==========================================
st.set_page_config(page_title="SKIMO KOREA", page_icon="🏔️", layout="wide")

# 배경 이미지 풀 (장비 가이드용 배경 이미지 추가 포함)
BG_IMAGES = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=1800&q=80",
    "https://images.unsplash.com/photo-1502680390469-be75c86b636f?auto=format&fit=crop&w=1800&q=80", # 장비 가이드용 배경
    "https://images.unsplash.com/photo-1518098268026-4e43a1a009de?auto=format&fit=crop&w=1800&q=80"   
]

if "menu_idx" not in st.session_state:
    st.session_state.menu_idx = 0
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# [브라우저 쿠키/로컬 스토리지 대용 구조]
DB_FILE = "user_database.json"

def load_user_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        initial_db = {
            "admin": {"pw": "1234", "role": "ADMIN"},
            "skimo": {"pw": "skimo123", "role": "JUDGE"}
        }
        save_user_db(initial_db)
        return initial_db

def save_user_db(db_data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=4)

st.session_state.user_db = load_user_db()

# 실시간 계측/타이밍 데이터
if "athletes_domain" not in st.session_state:
    st.session_state.athletes_domain = {
        "101": {"Name": "김민우", "Team": "KOREA", "Category": "Sprint", "Status": "RACING", "CP1": "10:15:20", "CP2": "--:--:--", "Penalty_Sec": 0, "Final_Record": "--:--:--"},
        "102": {"Name": "Alex Smith", "Team": "USA", "Category": "Individual", "Status": "RACING", "CP1": "10:14:05", "CP2": "10:45:12", "Penalty_Sec": 0, "Final_Record": "--:--:--"},
        "103": {"Name": "Chloe", "Team": "FRANCE", "Category": "Vertical", "Status": "FINISHED", "CP1": "10:16:55", "CP2": "10:49:30", "Penalty_Sec": 10, "Final_Record": "11:05:14"},
        "104": {"Name": "Takahashi", "Team": "JAPAN", "Category": "Sprint", "Status": "RACING", "CP1": "10:20:11", "CP2": "--:--:--", "Penalty_Sec": 0, "Final_Record": "--:--:--"},
        "105": {"Name": "Li Wei", "Team": "CHINA", "Category": "Individual", "Status": "DNF", "CP1": "10:11:00", "CP2": "--:--:--", "Penalty_Sec": 0, "Final_Record": "--:--:--"},
    }

# 공지사항 데이터
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

# 뉴스 및 AI 요약 데이터
if "home_news_domain" not in st.session_state:
    st.session_state.home_news_domain = [
        {
            "id": "news_01", "date": "2026-06-18", "link": "https://www.ismf-ski.org/",
            "title": {
                "KO": "🚀 2030 프랑스 알프스 동계 올림픽, 산악스키 세부 종목 규정 발표 예정",
                "EN": "🚀 2030 French Alps Winter Olympics: Detailed Skimo Regulations to be Announced",
                "FR": "🚀 Jeux Olympiques d'hiver des Alpes Françaises 2030 : Les règlements détaillés du Skimo seront annoncés",
                "IT": "🚀 Olimpiadi Invernali delle Alpi Francesi 2030: Saranno annunciati i regolamenti dettagliati dello Skimo",
                "ZH": "🚀 2030年法国阿尔卑斯冬季奥运会：滑雪登山详细项目规则即将公布",
                "JA": "🚀 2030年フランス・アルプス冬季オリンピック、山岳スキー詳細種目規定がまもなく発表予定"
            },
            "ai_summary": {
                "KO": "🤖 **AI 요약:** 2030 프랑스 동계 올림픽 조직위 and ISMF가 산악스키 정식 종목 채택에 따른 세부 중계 및 페널티 규정을 내달 확정합니다.\n\n💡 **핵심 키워드:** `#2030동계올림픽` `#ISMF규정`",
                "EN": "🤖 **AI Summary:** The 2030 French Winter Olympics Committee and ISMF will finalize detailed regulations next month.\n\n💡 **Keywords:** `#WinterOlympics2030` `#ISMF_Rules`"
            }
        }
    ]

selected_bg = BG_IMAGES[st.session_state.menu_idx] if st.session_state.menu_idx < len(BG_IMAGES) else BG_IMAGES[0]

st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{ display: none !important; }}
    .stAppDeployDropdown {{ display: none !important; }}
    [data-testid="stSidebar"] {{ display: none !important; }}
    .block-container {{ padding-top: 0rem; padding-bottom: 0rem; padding-left: 0rem; padding-right: 0rem; }}
    
    .stApp {{
        background: linear-gradient(rgba(15, 32, 39, 0.85), rgba(44, 83, 100, 0.75)), url('{selected_bg}') no-repeat center center fixed;
        background-size: cover !important;
    }}
    
    .centered-wrapper {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
    .custom-header-bg {{ background-color: rgba(15, 32, 39, 0.4); backdrop-filter: blur(5px); width: 100%; padding: 10px 0; }}
    
    .hero-section {{ height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; text-align: center; }}
    .hero-title {{ font-size: 42px; font-weight: 800; text-shadow: 3px 3px 8px rgba(0,0,0,0.9); margin-bottom: 5px; }}
    .hero-subtitle {{ font-size: 18px; font-weight: 500; color: #00c6ff; text-shadow: 2px 2px 4px rgba(0,0,0,0.7); }}
    
    .content-box {{ 
        max-width: 1200px; margin: 0 auto 50px auto; padding: 30px; background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(10px); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.15); color: #ffffff;
    }}
    
    div.stButton > button {{
        background: transparent !important; color: white !important; border: none !important;
        font-size: 14px !important; font-weight: 500 !important;
    }}
    div.stButton > button:hover {{ color: #00c6ff !important; }}
    
    .news-flex-container {{ display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 5px 0; }}
    .news-title-link {{ font-size: 15px; font-weight: 500; color: #e2e8f0; text-decoration: none; }}
    .news-title-link:hover {{ color: #00c6ff; cursor: pointer; }}
    .news-date-span {{ font-size: 13px; color: #cbd5e1; white-space: nowrap; }}
    
    .notice-card {{ background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; margin-bottom: 15px; }}
    .notice-badge {{ background-color: #00c6ff; color: #111; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-right: 10px; }}
    
    div[data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 10px; border-radius: 8px;
    }}
    
    /* 장비 가이드 카드 디자인 */
    .equip-card {{
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px; border-radius: 12px; margin-bottom: 20px;
    }}
    .equip-title {{ font-size: 18px; font-weight: bold; color: #00c6ff; margin-bottom: 8px; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 6개국 로컬라이제이션 매핑 아키텍처 (장비 가이드 키 추가)
# ==========================================
LANG_DICT = {
    "한국어 (KO)": "KO", "English (EN)": "EN", "Français (FR)": "FR",       
    "Italiano (IT)": "IT", "简体中文 (ZH)": "ZH", "日本語 (JA)": "JA"          
}

LOCALIZED_TEXT = {
    "KO": {
        "title": "SKIMO KOREA", "subtitle": "스키등산 정보 포털",
        "menu": ["대회 홈", "선수 참가 신청", "실시간 리더보드 (LIVE)", "🎿 필수 장비 가이드", "🔐 심판/관리자 패널", "📢 글로벌 공지사항"],
        "desc": "본 대회는 국제산악스키연맹(ISMF) 규정을 준수하며, field 심판 시스템과 동기화되어 실시간 기록을 전 세계에 생중계합니다.",
        "video": "📺 경기 종목 안내", "intro_video": "⛷️ 산악스키 소개", "photo": "📸 올림픽 현장 갤러리", "pay": "💳 참가 신청 및 안전 결제",
        "news_title": "📰 News & Stories (글로벌 최신 소식)", "search_holder": "🔍 검색어를 입력하세요...", "notice": "📢 공지사항", "auth": "👤 로그인/회원가입",
        "ai_btn": "🤖 AI 요약보기", "ai_modal_title": "⚡ Generative AI 실시간 요약 브리핑",
        "stats_title": "📊 실시간 경기 텔레메트리 분석 (Telemetry Analytics)", "total_athletes": "총 참가 선수", "racing_athletes": "현재 레이싱 중", "finished_athletes": "완주 성공",
        "chart_country": "국가별 선수 분포", "chart_category": "세부 종목별 참가 비중", "toast_update": "📢 [실시간 동기화] 배번호 {bib}번 선수의 상태가 {status}로 업데이트되었습니다!",
        "equip_main_title": "🎿 ISMF 공인 산악스키 필수 5대 장비 안내"
    },
    "EN": {
        "title": "SKIMO KOREA", "subtitle": "Ski Mountaineering Information Portal",
        "menu": ["Home", "Athlete Registration", "Live Leaderboard", "🎿 Equipment Guide", "🔐 Judge/Admin Panel", "📢 Global Notice"],
        "desc": "This tournament complies with ISMF regulations. Scoring and penalties are aggregated in real-time globally via the field web app.",
        "video": "📺 Skimo Rules Video", "intro_video": "⛷️ What is Skimo?", "photo": "📸 Olympic Action Gallery", "pay": "💳 Register & Secure Pay",
        "news_title": "📰 News & Stories (Global Latest News)", "search_holder": "🔍 Search information...", "notice": "📢 Notice", "auth": "👤 Login/Register",
        "ai_btn": "🤖 View AI Summary", "ai_modal_title": "⚡ Generative AI Real-time Briefing",
        "stats_title": "📊 Live Telemetry Analytics", "total_athletes": "Total Athletes", "racing_athletes": "Racing Now", "finished_athletes": "Finished",
        "chart_country": "Athletes by Country", "chart_category": "Participation by Category", "toast_update": "📢 [Live Sync] Athlete #{bib} status updated to {status}!",
        "equip_main_title": "🎿 ISMF Official Ski Mountaineering Mandatory Equipment"
    },
    "FR": {
        "title": "SKIMO KOREA", "subtitle": "Portail d'information sur le ski-alpinisme",
        "menu": ["Accueil", "Inscription des athlètes", "Classement en direct", "🎿 Guide de l'équipement", "🔐 Panneau des juges/admin", "📢 Avis mondial"],
        "desc": "Ce tournoi est conforme aux règlements de l'ISMF. Les scores et les pénalités sont agrégés en temps réel via l'application web de terrain.",
        "video": "📺 Vidéo des règlements du Skimo", "intro_video": "⛷️ Qu'est-ce que le Skimo?", "photo": "📸 Galerie d'action olympique", "pay": "💳 S'inscrire et paiement sécurisé",
        "news_title": "📰 News & Stories (Dernières nouvelles mondiales)", "search_holder": "🔍 Rechercher des informations...", "notice": "📢 Avis", "auth": "👤 Connexion/S'inscrire",
        "ai_btn": "🤖 Voir le résumé de l'AI", "ai_modal_title": "⚡ Briefing en temps réel de l'IA générative",
        "stats_title": "📊 Analyse télémétrique en direct", "total_athletes": "Total des athlètes", "racing_athletes": "En course", "finished_athletes": "Terminé",
        "chart_country": "Athlètes par pays", "chart_category": "Participation par catégorie", "toast_update": "📢 [Sync en direct] Le statut de l'athlète #{bib} a été mis à jour en {status}!",
        "equip_main_title": "🎿 Équipement obligatoire officiel de ski-alpinisme de l'ISMF"
    },
    "IT": {
        "title": "SKIMO KOREA", "subtitle": "Portale informativo sullo sci alpinismo",
        "menu": ["Home", "Iscrizione Atleti", "Classifica in Tempo Reale", "🎿 Guida all'attrezzatura", "🔐 Pannello Giudici/Admin", "📢 Avviso Globale"],
        "desc": "Questo torneo è conforme ai regolamenti ISMF. I punteggi e le penalità vengono aggregati in tempo reale tramite l'app web sul campo.",
        "video": "📺 Video delle regole dello Skimo", "intro_video": "⛷️ Cos'è lo Skimo?", "photo": "📸 Galleria d'azione olimpica", "pay": "💳 Registrati e pagamento sicuro",
        "news_title": "📰 News & Stories (Ultime notizie globali)", "search_holder": "🔍 Cerca informazioni...", "notice": "📢 Avviso", "auth": "👤 Accedi/Registrati",
        "ai_btn": "🤖 Visualizza il riepilogo dell'IA", "ai_modal_title": "⚡ Briefing in tempo reale dell'IA generativa",
        "stats_title": "📊 Analisi telemetrica in tempo reale", "total_athletes": "Atleti totali", "racing_athletes": "In gara ora", "finished_athletes": "Finito",
        "chart_country": "Atleti per paese", "chart_category": "Partecipazione per categoria", "toast_update": "📢 [Sincronizzazione live] Lo stato dell'atleta #{bib} è stato aggiornato a {status}!" ,
        "equip_main_title": "🎿 Attrezzatura obbligatoria ufficiale di sci alpinismo ISMF"
    },
    "ZH": {
        "title": "SKIMO KOREA", "subtitle": "滑雪登山信息门户网站",
        "menu": ["赛事首页", "运动员报名", "实时排行榜 (LIVE)", "🎿 必备装备指南", "🔐 裁判/管理员控制台", "📢 全球公告"],
        "desc": "本次赛事遵守国际滑雪登山联盟 (ISMF) 的规定。得分和处罚通过实地网页应用程序在全球范围内实时汇总。",
        "video": "📺 滑雪登山规则视频", "intro_video": "⛷️ 什么是滑雪登山？", "photo": "📸 奥运现场画廊", "pay": "💳 立即报名与安全支付",
        "news_title": "📰 News & Stories (全球最新动态)", "search_holder": "🔍 输入搜索内容...", "notice": "📢 公告", "auth": "👤 登录/注册",
        "ai_btn": "🤖 查看 AI 摘要", "ai_modal_title": "⚡ 生成式 AI 实时简报",
        "stats_title": "📊 实时比赛遥测数据分析 (Telemetry Analytics)", "total_athletes": "总参赛人数", "racing_athletes": "正在比赛中", "finished_athletes": "成功完赛",
        "chart_country": "各国选手分布", "chart_category": "各项目报名比例", "toast_update": "📢 [实时同步] 号码牌 {bib} 选手状态已更新为 {status}!",
        "equip_main_title": "🎿 ISMF 官方滑雪登山强制性装备指南"
    },
    "JA": {
        "title": "SKIMO KOREA", "subtitle": "山岳スキー情報ポータル",
        "menu": ["大会ホーム", "選手参加申込", "リアルタイムリーダーボード", "🎿 必須ギアガイド", "🔐 審判/管理者パネル", "📢 グローバルお知らせ"],
        "desc": "本大会は国際山岳スキー連盟（ISMF）の規定に準拠しています。スコ아やペナルティは、フィールドのウェブアプリを通じてリアルタイムで集計されます。",
        "video": "📺 山岳スキー規則動画", "intro_video": "⛷️ 山岳スキーとは？", "photo": "📸 オリンピックギャラリー", "pay": "💳 参加申込と安全な決済",
        "news_title": "📰 News & Stories (最新のグローバルニュース)", "search_holder": "🔍 情報を検索...", "notice": "📢 お知らせ", "auth": "👤 ログイン/会員登録",
        "ai_btn": "🤖 AI要約を見る", "ai_modal_title": "⚡ 生成AIリアルタイムブリーフィング",
        "stats_title": "📊 リアルタイム競技テレメトリ分析 (Telemetry Analytics)", "total_athletes": "総参加選手数", "racing_athletes": "現在レース中", "finished_athletes": "完走者数",
        "chart_country": "国別選手分布", "chart_category": "種目別参加比率", "toast_update": "📢 [ライブ同期] ゼッケン {bib} 番의 選手ステータスが {status} に更新されました！",
        "equip_main_title": "🎿 ISMF 公認 山岳スキー必須5大ギアガイド"
    }
}

if "current_lang_code" not in st.session_state:
    st.session_state.current_lang_code = "KO"

T = LOCALIZED_TEXT.get(st.session_state.current_lang_code, LOCALIZED_TEXT["EN"])

# 로그인/회원가입 모달
@st.dialog("🔐 SKIMO KOREA 계정 관리")
def auth_dialog():
    tab1, tab2 = st.tabs(["👤 로그인", "📝 회원가입"])
    with tab1:
        login_id = st.text_input("아이디", key="login_id").strip()
        login_pw = st.text_input("비밀번호", type="password", key="login_pw").strip()
        if st.button("로그인 완료", use_container_width=True):
            current_db = load_user_db()
            if login_id in current_db and current_db[login_id]["pw"] == login_pw:
                st.session_state.logged_in_user = login_id
                st.success(f"🎉 반갑습니다, {login_id}님! 로그인 성공.")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("❌ 아이디 또는 비밀번호가 일치하지 않습니다.")
    with tab2:
        reg_id = st.text_input("새로운 아이디 생성", key="reg_id").strip()
        reg_pw = st.text_input("새로운 비밀번호 설정", type="password", key="reg_pw").strip()
        reg_pw_confirm = st.text_input("비밀번호 확인", type="password", key="reg_pw_confirm").strip()
        if st.button("회원가입 신청", use_container_width=True):
            current_db = load_user_db()
            if not reg_id or not reg_pw:
                st.warning("⚠️ 아이디와 비밀번호를 모두 입력해주세요.")
            elif reg_id in current_db:
                st.error("❌ 이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요.")
            elif reg_pw != reg_pw_confirm:
                st.error("❌ 비밀번호 확인이 일치하지 않습니다.")
            else:
                current_db[reg_id] = {"pw": reg_pw, "role": "USER"}
                save_user_db(current_db)
                st.session_state.user_db = current_db  
                st.success("🚀 회원가입 성공! 이제 로그인 탭에서 로그인해 주세요.")

# AI 뉴스 요약 모달 창
@st.dialog("🎯 AI 요약 브리핑")
def ai_summary_dialog(news_item, lang_code):
    st.markdown(f"### {T['ai_modal_title']}")
    st.write("---")
    current_title = news_item["title"].get(lang_code, news_item["title"]["EN"])
    st.markdown(f"**📌 대상 뉴스:** {current_title}")
    with st.spinner("LLM 인퍼런스 엔진 가동 중..."):
        time.sleep(0.7)
    summary_content = news_item["ai_summary"].get(lang_code, news_item["ai_summary"]["EN"])
    st.markdown(summary_content)
    st.write("---")
    st.link_button("🔗 원문 뉴스 링크 열기 (ISMF)", news_item["link"], use_container_width=True)

# ==========================================
# 3. 글로벌 상단 동적 라우터 바
# ==========================================
st.markdown('<div class="custom-header-bg">', unsafe_allow_html=True)
st.markdown('<div class="centered-wrapper">', unsafe_allow_html=True)

c_menu, c_search, c_right = st.columns([3, 4, 5])

SEARCH_KEYWORDS = {
    0: ["홈", "대회", "소개", "뉴스", "home", "news"],
    1: ["선수", "참가", "신청", "등록", "접수"],
    2: ["실시간", "리더", "라이브", "순위", "live", "대시보드"],
    3: ["장비", "가이드", "스키", "부츠", "폴", "스킨", "바인딩", "equipment"],
    4: ["심판", "관리자", "패널", "judge"],
    5: ["공지", "사항", "알림", "notice"]
}

with c_search:
    search_query = st.text_input("Search", placeholder=T["search_holder"], label_visibility="collapsed")
    if search_query:
        query_clean = search_query.strip().lower()
        for idx, keywords in SEARCH_KEYWORDS.items():
            if any(kw in query_clean for kw in keywords):
                if st.session_state.menu_idx != idx:
                    st.session_state.menu_idx = idx
                    st.rerun()

with c_menu:
    menu_list = list(T["menu"])
    selected_menu_raw = st.selectbox("Menu", menu_list, index=st.session_state.menu_idx if st.session_state.menu_idx < len(menu_list) else 0, label_visibility="collapsed")
    menu_index = menu_list.index(selected_menu_raw)
    if st.session_state.menu_idx != menu_index:
        st.session_state.menu_idx = menu_index
        st.rerun()

with c_right:
    sub_lang, sub_buttons = st.columns([4, 6])
    with sub_lang:
        lang_keys = list(LANG_DICT.keys())
        current_lang_name = [k for k, v in LANG_DICT.items() if v == st.session_state.current_lang_code]
        default_lang_idx = lang_keys.index(current_lang_name[0]) if current_lang_name else 0
        
        selected_lang_name = st.selectbox("Language", lang_keys, index=default_lang_idx, label_visibility="collapsed")
        new_lang_code = LANG_DICT[selected_lang_name]
        if st.session_state.current_lang_code != new_lang_code:
            st.session_state.current_lang_code = new_lang_code
            st.rerun()
            
    with sub_buttons:
        if st.session_state.logged_in_user is None:
            if st.button(T["auth"]): auth_dialog()
        else:
            if st.button(f"🔓 로그아웃 ({st.session_state.logged_in_user})"):
                st.session_state.logged_in_user = None
                st.rerun()

st.markdown('</div></div>', unsafe_allow_html=True)

# 메인 뷰포트 레이아웃
st.markdown(f'<div class="centered-wrapper"><div class="hero-section"><div class="hero-title">{T["title"]}</div><div class="hero-subtitle">🏔️ {T["subtitle"]}</div></div></div>', unsafe_allow_html=True)
st.markdown('<div class="content-box">', unsafe_allow_html=True)

# -------------------------------------------------------------------------
# [라우터 메뉴 분기 제어 체계]
# -------------------------------------------------------------------------
if st.session_state.menu_idx == 0:
    st.markdown("## 🏁 Upcoming Events & Overview")
    col_text, col_video, col_intro, col_photo = st.columns([3, 3, 3, 3])
    
    with col_text:
        st.markdown("### 📢 Information")
        st.write(T["desc"])
        st.markdown("* **Location:** Pyeongchang, KOREA\n* **Sanctioned by:** ISMF\n* **Scale:** 3,000+ Participants")
        
    with col_video:
        st.markdown(f"### {T['video']}")
        st.video("https://youtu.be/KgyX5OjMTyM")

    with col_intro:
        st.markdown(f"### {T['intro_video']}")
        st.video("https://youtu.be/nLjES8kuFRg")

    with col_photo:
        st.markdown(f"### {T['photo']}")
        gallery_images = [
            {"path": "skimo_race_1.jpg", "caption": "❄️ 눈보라를 뚫고 올라가는 레이스"},
            {"path": "skimo_race_2.jpg", "caption": "🏅 영광의 시상대 현장"},
            {"path": "skimo_race_3.jpg", "caption": "🎉 박진감 넘치는 다운힐 피니시"}
        ]
        photo_idx = st.radio("Photo Select", [1, 2, 3], horizontal=True, label_visibility="collapsed")
        selected_photo = gallery_images[photo_idx - 1]
        
        try:
            st.image(selected_photo["path"], caption=selected_photo["caption"], use_container_width=True)
        except:
            import urllib.parse
            encoded_filename = urllib.parse.quote(selected_photo["path"])
            github_url = f"https://raw.githubusercontent.com/pyminno12/skimo-website/main/{encoded_filename}"
            st.image(github_url, caption=selected_photo["caption"], use_container_width=True)

    st.markdown("<hr style='border-color: rgba(255,255,255,0.15);'>", unsafe_allow_html=True)
    st.markdown(f"## {T['news_title']}")
    
    lang_code = st.session_state.current_lang_code
    for item in st.session_state.home_news_domain:
        localized_news_title = item["title"].get(lang_code, item["title"]["EN"])
        c_news_title, c_news_btn = st.columns([8, 2])
        with c_news_title:
            st.markdown(f"""
                <div class="news-flex-container">
                    <span class="news-title-link">📌 {localized_news_title}</span>
                    <span class="news-date-span">📅 {item['date']}</span>
                </div>
            """, unsafe_allow_html=True)
        with c_news_btn:
            if st.button(T["ai_btn"], key=f"btn_ai_{item['id']}", use_container_width=True):
                ai_summary_dialog(item, lang_code)

elif st.session_state.menu_idx == 1:
    st.markdown(f"## {T['menu'][1]}")
    with st.form("reg_form"):
        p_name = st.text_input("Athlete Name")
        p_nation = st.text_input("Country/Team").upper()
        p_event = st.selectbox("Category", ["Sprint", "Individual", "Vertical"])
        if st.form_submit_button(T["pay"]) and p_name:
            next_bib = str(100 + len(st.session_state.athletes_domain) + 1)
            st.session_state.athletes_domain[next_bib] = {"Name": p_name, "Team": p_nation, "Category": p_event, "Status": "RACING", "CP1": "--:--:--", "CP2": "--:--:--", "Penalty_Sec": 0, "Final_Record": "--:--:--"}
            st.success(f"선수 등록 완료! 배정 배번호: [{next_bib}]")

elif st.session_state.menu_idx == 2:
    st.markdown(f"## {T['menu'][2]}")
    data_list = [{"BIB": b, **i} for b, i in st.session_state.athletes_domain.items()]
    df = pd.DataFrame(data_list)
    
    st.markdown(f"### {T['stats_title']}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(T["total_athletes"], f"{len(df)}명")
    m2.metric(T["racing_athletes"], f"{len(df[df['Status'] == 'RACING'])}명", delta=f"+{len(df[df['Status'] == 'RACING'])} LIVE")
    m3.metric(T["finished_athletes"], f"{len(df[df['Status'] == 'FINISHED'])}명")
    m4.metric("DNF / DSQ", f"{len(df[df['Status'] == 'DNF'])}명")
    
    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
        country_counts = df["Team"].value_counts().reset_index()
        country_counts.columns = ["Country", "Count"]
        fig_country = px.bar(country_counts, x="Country", y="Count", title=T["chart_country"], color="Count", color_continuous_scale="Blugrn")
        fig_country.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_country, use_container_width=True)
    with c_chart2:
        cat_counts = df["Category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig_cat = px.pie(cat_counts, values="Count", names="Category", title=T["chart_category"], hole=0.4)
        fig_cat.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_cat, use_container_width=True)
        
    st.markdown("---")
    df_display = df[["BIB", "Name", "Team", "Category", "Status", "CP1", "CP2", "Penalty_Sec", "Final_Record"]]
    st.dataframe(df_display.set_index("BIB"), use_container_width=True)

# -------------------------------------------------------------------------
# [🆕 추가 메뉴: 🎿 필수 장비 가이드 가로 그리드 레이아웃]
# -------------------------------------------------------------------------
elif st.session_state.menu_idx == 3:
    st.markdown(f"## {T['equip_main_title']}")
    st.write("산악스키(Skimo) 대회는 경량화와 안전성이 승패를 가르는 핵심 요소입니다. 국제연맹(ISMF) 규정에 따른 필수 장비들의 가이드입니다.")
    st.write("---")
    
    # 5대 장비를 깔끔하게 3열 / 2열 그리드로 나누어 시각화
    row1_c1, row1_c2, row1_c3 = st.columns(3)
    row2_c1, row2_c2 = st.columns(2)
    
    with row1_c1:
        st.markdown("""
        <div class="equip-card">
            <div class="equip-title">1. 초경량 산악스키 (Skimo Skis)</div>
            <p style='font-size:14px; color:#cbd5e1;'>오르막길을 빠르게 뛰어 올라가야 하므로 일반 알파인 스키에 비해 상상할 수 없을 정도로 가볍습니다. 남성용 기준 최소 780g, 여성용 700g 선으로 제한되며 탄소 섬유(Carbon)로 제작됩니다.</p>
        </div>
        """, unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1605548230624-8d2d0419c517?auto=format&fit=crop&w=500&q=80", caption="Carbon Light Skis", use_container_width=True)
        
    with row1_c2:
        st.markdown("""
        <div class="equip-card">
            <div class="equip-title">2. 투어링 바인딩 (Tech Bindings)</div>
            <p style='font-size:14px; color:#cbd5e1;'>산악스키 바인딩은 업힐 모드 시 뒷굽이 떨어져 걸어 올라갈 수 있게 설계되었습니다. 다운힐 모드 시에는 뒷굽을 고정합니다. 핀(Pin) 테크 방식을 채택해 무게가 겨우 100g 안팎입니다.</p>
        </div>
        """, unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=500&q=80", caption="Tech Binding System", use_container_width=True)
        
    with row1_c3:
        st.markdown("""
        <div class="equip-card">
            <div class="equip-title">3. 등반용 클라이밍 스킨 (Climbing Skins)</div>
            <p style='font-size:14px; color:#cbd5e1;'>스키 플레이트 바닥에 붙이는 모헤어(Mohair) 소재의 전용 스킨입니다. 앞방향으로는 미끄러지지만, 뒷방향으로는 털이 서서 눈을 움켜쥐기 때문에 미끄러지지 않고 수직 오르막을 오를 수 있습니다.</p>
        </div>
        """, unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=500&q=80", caption="Climbing Skins Setup", use_container_width=True)

    with row2_c1:
        st.markdown("""
        <div class="equip-card">
            <div class="equip-title">4. 워크 모드 지원 부츠 (Skimo Boots)</div>
            <p style='font-size:14px; color:#cbd5e1;'>레버 하나로 발목 관절 구동 범위를 60도 이상 확보하는 '워크 모드'와 활강을 위해 고정하는 '스키 모드'를 전환할 수 있습니다. 카본 재질로 발목 피로도를 최소화합니다.</p>
        </div>
        """, unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1518098268026-4e43a1a009de?auto=format&fit=crop&w=500&q=80", caption="Lightweight Boots", use_container_width=True)
        
    with row2_c2:
        st.markdown("""
        <div class="equip-card">
            <div class="equip-title">5. 탄소섬유 카본 폴 (Carbon Poles)</div>
            <p style='font-size:14px; color:#cbd5e1;'>상체 반동과 팔 근육을 이용해 업힐 추진력을 내는 도구입니다. 일반 스키 폴보다 길며, 샤프트 전체가 100% High-Modulus 카본으로 되어 있어 매우 가볍고 단단한 강성을 유지합니다.</p>
        </div>
        """, unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=500&q=80", caption="Racing Carbon Poles", use_container_width=True)

elif st.session_state.menu_idx == 4:
    st.markdown(f"## {T['menu'][4]}")
    if st.session_state.logged_in_user is None:
        st.warning("⚠️ 권한 경고: 심판 계정으로 로그인이 필요합니다.")
    else:
        current_db = load_user_db()
        user_role = current_db.get(st.session_state.logged_in_user, {}).get("role", "USER")
        if user_role not in ["ADMIN", "JUDGE"]:
            st.error("🚫 접근 거부: 심판/관리자 패널을 조작할 권한이 없습니다.")
        else:
            bib_list = list(st.session_state.athletes_domain.keys())
            selected_bib = st.selectbox("업데이트할 BIB 선택", bib_list)
            new_status = st.selectbox("상태 값 변경", ["RACING", "FINISHED", "DNF", "DSQ"])
            if st.button("🚨 데이터 필드 실시간 동기화"):
                st.session_state.athletes_domain[selected_bib]["Status"] = new_status
                toast_msg = T["toast_update"].format(bib=selected_bib, status=new_status)
                st.toast(toast_msg, icon="🏂")
                st.success(f"배번호 {selected_bib}번 선수의 경기 상태가 {new_status}로 변경되었습니다.")
                time.sleep(1.0)
                st.rerun()

elif st.session_state.menu_idx == 5:
    st.markdown(f"## {T['menu'][5]}")
    lang_code = st.session_state.current_lang_code
    for item in st.session_state.notice_domain:
        title_text = item["title"].get(lang_code, item["title"]["EN"])
        content_text = item["content"].get(lang_code, item["content"]["EN"])
        st.markdown(f'<div class="notice-card"><div><span class="notice-badge">{item["category"]}</span><span>📅 {item["date"]}</span></div><div style="font-size:18px; font-weight:600; margin:10px 0;">{title_text}</div><div>{content_text}</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
