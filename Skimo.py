import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ==========================================
# [설계 3단계] 다국어 데이터 확장 모듈 (Global Language Pack)
# ==========================================
st.set_page_config(page_title="ISMF Korea Global System", page_icon="🏔️", layout="wide")

# 전 세계 사람들이 쉽게 선택할 수 있도록 언어 사전 정의
LANG_DICT = {
    "한국어 (KO)": "KO",
    "English (EN)": "EN",
    "Français (FR)": "FR",       # ISMF 본부가 있는 유럽 필수 언어
    "Italiano (IT)": "IT",       # 2026 동계올림픽 개최국 언어
    "简体中文 (ZH)": "ZH",       # 아시아권 거대 참가국 언어
    "日本語 (JA)": "JA"          # 인접 참가국 언어
}

# 텍스트 데이터 베이스 모듈화 (번역 데이터 배열)
LOCALIZED_TEXT = {
    "KO": {
        "title": "🏔️ 스키등산(산악스키) 대회 통합 글로벌 포털",
        "subtitle": "올림픽 정식 종목 공인 - 전 세계인을 위한 시스템",
        "menu": ["대회 홈", "선수 참가 신청", "실시간 리더보드 (LIVE)", "🔐 심판/관리자 전용 패널"],
        "notice": "🏁 경기 요강 및 문화행사 안내",
        "desc": "본 대회는 ISMF 규정을 준수하며, 필드 심판의 모바일 웹앱을 통해 전 세계에 실시간으로 판정 및 페널티가 집계됩니다.",
        "reg_title": "📝 선수 참가 신청 및 패키지 결제",
        "name": "선수명", "nation": "국적/소속", "event": "참가 종목", "pay": "💳 안전 결제 및 참가 확정",
        "live_title": "⏱️ 실시간 경기 리더보드 (전 세계 생중계)",
        "judge_title": "🔐 필드 심판 전용 실시간 제어 패널"
    },
    "EN": {
        "title": "🏔️ Ski Mountaineering Integrated Global Portal",
        "subtitle": "Official Olympic Sport - Global Information System",
        "menu": ["Home", "Athlete Registration", "Live Leaderboard", "🔐 Judge/Admin Panel"],
        "notice": "🏁 Tournament & Cultural Events Info",
        "desc": "This tournament complies with ISMF regulations. Scoring and penalties are aggregated in real-time globally via the field judges' mobile web app.",
        "reg_title": "📝 Athlete Registration & Package Payment",
        "name": "Full Name", "nation": "Nationality/Team", "event": "Event Category", "pay": "💳 Secure Payment & Confirm",
        "live_title": "⏱️ Real-Time Race Leaderboard (Global Live)",
        "judge_title": "🔐 Field Judge Real-Time Control Panel"
    },
    "FR": { # 프랑스어 (ISMF 공식 언어 중 하나)
        "title": "🏔️ Portail Global Intégré de Ski de Randonnée",
        "subtitle": "Sport Olympique Officiel - Système d'Information Mondial",
        "menu": ["Accueil", "Inscription Athlète", "Tableau de Bord Live", "🔐 Panneau des Juges"],
        "notice": "🏁 Infos sur Tournoi & Événements Culturels",
        "desc": "Ce tournoi est conforme aux règlements de l'ISMF. Les scores et pénalités sont agrégés en temps réel via l'application mobile des juges.",
        "reg_title": "📝 Inscription de l'Athlète & Paiement",
        "name": "Nom Complet", "nation": "Nationalité/Équipe", "event": "Catégorie d'Événement", "pay": "💳 Paiement Sécurisé & Confirmer",
        "live_title": "⏱️ Classement En Direct (Live Mondial)",
        "judge_title": "🔐 Panneau de Contrôle des Juges de Terrain"
    },
    "IT": { # 이탈리아어 (밀라노 동계올림픽 개최국)
        "title": "🏔️ Portale Globale Integrato dello Sci Alpinismo",
        "subtitle": "Sport Olimpico Ufficiale - Sistema Informativo Mondiale",
        "menu": ["Home", "Iscrizione Atleta", "Classifica Live", "🔐 Pannello Giudici"],
        "notice": "🏁 Info su Torneo ed Eventi Culturali",
        "desc": "Questo torneo è conforme ai regolamenti ISMF. I punteggi e le penalità vengono aggregati in tempo reale tramite l'app dei giudici.",
        "reg_title": "📝 Iscrizione Atleta e Pagamento Pacchetto",
        "name": "Nome Completo", "nation": "Nazionalità/Squadra", "event": "Categoria Gara", "pay": "💳 Pagamento Sicuro e Conferma",
        "live_title": "⏱️ Classifica di Gara in Tempo Reale",
        "judge_title": "🔐 Pannello di Controllo in Tempo Reale dei Giudici"
    },
    "ZH": { # 중국어 간체
        "title": "🏔️ 登山滑雪综合全球门户网站",
        "subtitle": "奥运会正式项目认证 - 全球信息系统",
        "menu": ["大会主页", "运动员报名", "实时排行榜 (LIVE)", "🔐 裁判/管理员面板"],
        "notice": "🏁 赛事大纲及文化活动指南",
        "desc": "本次比赛遵守 ISMF 规定。评分和处罚将通过现场裁判的移动网络应用实时在全球范围内汇总。",
        "reg_title": "📝 运动员注册与套餐支付",
        "name": "姓名", "nation": "国籍/车队", "event": "参赛项目", "pay": "💳 安全支付并确认",
        "live_title": "⏱️ 实时比赛排行榜（全球直播）",
        "judge_title": "🔐 现场裁判实时控制面板"
    },
    "JA": { # 일본어
        "title": "🏔️ 山岳スキー総合グローバルポータル",
        "subtitle": "オリンピック正式種目公認 - 全世界向けシステム",
        "menu": ["ホーム", "選手参加申し込み", "リアルタイム順位表 (LIVE)", "🔐 審판/管理者パネル"],
        "notice": "🏁 大会要項および文化イベント案内",
        "desc": "本大会はISMF規定に準拠しています。スコアやペナルティは、現地審判のモバイルアプリを通じてリアルタイムで全世界に集計されます。",
        "reg_title": "📝 選手登録およびパッケージ決済",
        "name": "選手名", "nation": "国籍/所属", "event": "参加種目", "pay": "💳 安全な決済と参加確定",
        "live_title": "⏱️ リアルタイムレース順位表（世界生中継）",
        "judge_title": "🔐 現地審判専用リアルタイム制御パネル"
    }
}

# 사이드바 상단에 지구본 모양과 함께 언어 선택 박스 배치
selected_lang_name = st.sidebar.selectbox("🌐 Select Language / 언어 선택", list(LANG_DICT.keys()))
current_lang = LANG_DICT[selected_lang_name]

# 현재 선택된 언어팩 지정
T = LOCALIZED_TEXT[current_lang]

# 메인 타이틀 화면 출력
st.title(T["title"])
st.caption(T["subtitle"])
st.markdown("---")

# ==========================================
# 데이터 저장 시스템 (Mock DB)
# ==========================================
if "athletes" not in st.session_state:
    st.session_state.athletes = [
        {"BIB": "101", "Name": "김민우", "Team": "KOREA", "Status": "RACING", "CP1": "10:15:20", "CP2": "--:--:--", "CP3": "--:--:--", "Penalty": "None"},
        {"BIB": "102", "Name": "Alex Smith", "Team": "USA", "Status": "RACING", "CP1": "10:14:05", "CP2": "10:45:12", "CP3": "--:--:--", "Penalty": "None"},
        {"BIB": "103", "Name": "Chloe", "Team": "FRANCE", "Status": "RACING", "CP1": "10:16:55", "CP2": "10:49:30", "CP3": "--:--:--", "Penalty": "None"},
    ]

# 6개국 언어로 동적 변경되는 메뉴 트리
menu = st.sidebar.radio("🧭 Navigation", T["menu"])

# --- [모듈 1] 대회 홈 ---
if menu == T["menu"][0]:
    st.header(T["notice"])
    col1, col2 = st.columns([7, 3])
    with col1:
        st.write(T["desc"])
        st.info("💡 **Olympic Standard System Architecture**\n* Fully modular language components optimized for global traffic scale.\n* Real-time sync protocol prepared for international ISMF events.")
    with col2:
        st.subheader("Sponsors")
        st.success("🤝 Premium Sponsor Slot")

# --- [모듈 2] 참가 신청 ---
elif menu == T["menu"][1]:
    st.header(T["reg_title"])
    with st.form("global_reg_form"):
        p_name = st.text_input(T["name"])
        p_nation = st.text_input(T["nation"])
        p_event = st.selectbox(T["event"], ["Sprint", "Individual", "Vertical"])
        
        st.metric("Registration Fee", "30,000 KRW")
        submit_btn = st.form_submit_button(T["pay"])
        
        if submit_btn and p_name:
            new_member = {"BIB": str(100 + len(st.session_state.athletes)+1), "Name": p_name, "Team": p_nation, "Status": "RACING", "CP1": "--:--:--", "CP2": "--:--:--", "CP3": "--:--:--", "Penalty": "None"}
            st.session_state.athletes.append(new_member)
            st.success("Success! / Enregistrement réussi! / 登録完了!")

# --- [모듈 3] 리더보드 ---
elif menu == T["menu"][2]:
    st.header(T["live_title"])
    df = pd.DataFrame(st.session_state.athletes)
    st.dataframe(df.set_index("BIB"), use_container_width=True)

# --- [모듈 4] 심판 전용 시스템 ---
elif menu == T["menu"][3]:
    st.header(T["judge_title"])
    athlete_names = [f"#{a['BIB']} - {a['Name']}" for a in st.session_state.athletes]
    
    target_athlete = st.selectbox("🎯 Select Athlete", athlete_names)
    target_bib = target_athlete.split(" - ")[0].replace("#", "")
    target_cp = st.radio("📍 Checkpoint", ["CP1", "CP2", "CP3"])
    penalty_select = st.selectbox("⚠️ Penalty Rules (ISMF)", ["None", "+1:00 Skin Regulation", "+3:00 Missing Gear", "DSQ (Disqualified)"])
    
    if st.button("🚀 Push Data to Global Server"):
        current_time = datetime.now().strftime("%H:%M:%S")
        for athlete in st.session_state.athletes:
            if athlete["BIB"] == target_bib:
                athlete[target_cp] = current_time
                if penalty_select != "None":
                    athlete["Penalty"] = penalty_select
        st.success("Data synchronized successfully across all languages!")
        time.sleep(0.5)
        st.rerun()
