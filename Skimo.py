import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ==========================================
# 다국어 데이터 확장 모듈 (Global Language Pack)
# ==========================================
st.set_page_config(page_title="ISMF Korea Global System", page_icon="🏔️", layout="wide")

LANG_DICT = {
    "한국어 (KO)": "KO",
    "English (EN)": "EN",
    "Français (FR)": "FR",       
    "Italiano (IT)": "IT",       
    "简体中文 (ZH)": "ZH",       
    "日本語 (JA)": "JA"          
}

LOCALIZED_TEXT = {
    "KO": {
        "title": "🏔️ 스키등산(산악스키) 대회 통합 글로벌 포털",
        "subtitle": "올림픽 정식 종목 공인 - 전 세계인을 위한 시스템",
        "menu": ["대회 홈", "선수 참가 신청", "실시간 리더보드 (LIVE)", "🔐 심판/관리자 전용 패널"],
        "notice": "🏁 경기 요강 및 문화행사 안내",
        "desc": "본 대회는 ISMF 규정을 준수하며, 필드 심판의 모바일 웹앱을 통해 전 세계에 실시간으로 판정 및 페널티가 집계됩니다.",
        "video_title": "📺 산악스키 경기 룰 & 소개 영상",
        "photo_title": "📸 올림픽 산악스키 경기 현장",
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
        "video_title": "📺 Skimo Rules & Introduction Video",
        "photo_title": "📸 Olympic Skimo Action Photos",
        "reg_title": "📝 Athlete Registration & Package Payment",
        "name": "Full Name", "nation": "Nationality/Team", "event": "Event Category", "pay": "💳 Secure Payment & Confirm",
        "live_title": "⏱️ Real-Time Race Leaderboard (Global Live)",
        "judge_title": "🔐 Field Judge Real-Time Control Panel"
    },
    "FR": {
        "title": "🏔️ Portail Global Intégré de Ski de Randonnée",
        "subtitle": "Sport Olympique Officiel - Système d'Information Mondial",
        "menu": ["Accueil", "Inscription Athlète", "Tableau de Bord Live", "🔐 Panneau des Juges"],
        "notice": "🏁 Infos sur Tournoi & Événements Culturels",
        "desc": "Ce tournoi est conforme aux règlements de l'ISMF. Les scores et pénalités sont agrégés en temps réel via l'application mobile des juges.",
        "video_title": "📺 Vidéo de Présentation & Règles du Skimo",
        "photo_title": "📸 Photos de Compétition Olympique",
        "reg_title": "📝 Inscription de l'Athlète & Paiement",
        "name": "Nom Complet", "nation": "Nationalité/Équipe", "event": "Catégorie d'Événement", "pay": "💳 Paiement Sécurisé & Confirmer",
        "live_title": "⏱️ Classement En Direct (Live Mondial)",
        "judge_title": "🔐 Panneau de Contrôle des Juges de Terrain"
    },
    "IT": {
        "title": "🏔️ Portale Globale Integrato dello Sci Alpinismo",
        "subtitle": "Sport Olimpico Ufficiale - Sistema Informativo Mondiale",
        "menu": ["Home", "Iscrizione Atleta", "Classifica Live", "🔐 Pannello Giudici"],
        "notice": "🏁 Info su Torneo ed Eventi Culturali",
        "desc": "Questo torneo è conforme ai regolamenti ISMF. I punteggi e le penalità vengono aggregati in tempo reale tramite l'app dei giudici.",
        "video_title": "📺 Video di Introduzione e Regolamento Skimo",
        "photo_title": "📸 Foto d'Azione delle Olimpiadi di Skimo",
        "reg_title": "📝 Iscrizione Atleta e Pagamento Pacchetto",
        "name": "Nome Completo", "nation": "Nazionalità/Squadra", "event": "Categoria Gara", "pay": "💳 Pagamento Sicuro e Conferma",
        "live_title": "⏱️ Classifica di Gara in Tempo Reale",
        "judge_title": "🔐 Pannello di Controllo in Tempo Reale dei Giudici"
    },
    "ZH": {
        "title": "🏔️ 登山滑雪综合全球门户网站",
        "subtitle": "奥运会正式项目认证 - 全球信息系统",
        "menu": ["大会主页", "运动员报名", "实时排行榜 (LIVE)", "🔐 裁判/管理员面板"],
        "notice": "🏁 赛事大纲及文化活动指南",
        "desc": "本次比赛遵守 ISMF 规定。评分和处罚将通过现场裁判的移动网络应用实时在全球范围内汇总。",
        "video_title": "📺 登山滑雪规则与介绍视频",
        "photo_title": "📸 奥运会登山滑雪比赛现场照片",
        "reg_title": "📝 运动员注册与套餐支付",
        "name": "姓名", "nation": "国籍/车队", "event": "参赛项目", "pay": "💳 安全支付并确认",
        "live_title": "⏱️ 实时比赛排行榜（全球直播）",
        "judge_title": "🔐 现场裁判实时控制面板"
    },
    "JA": {
        "title": "🏔️ 山岳スキー総合グローバルポータル",
        "subtitle": "オリンピック正式種目公認 - 全世界向けシステム",
        "menu": ["ホーム", "選手参加申し込み", "リアルタイム順位表 (LIVE)", "🔐 審판/管理者パネル"],
        "notice": "🏁 大会要項および文化イベント案内",
        "desc": "本大会はISMF規定に準拠しています。スコアやペナルティは、現地審判의 モバイルアプリを通じてリアルタイムで全世界に集計されます。",
        "video_title": "📺 山岳スキーのルール＆紹介動画",
        "photo_title": "📸 オリンピック山岳スキー競技写真",
        "reg_title": "📝 選手登録およびパッケージ決済",
        "name": "選手名", "nation": "国籍/所属", "event": "参加種目", "pay": "💳 安全な決済と参加確定",
        "live_title": "⏱️ リアルタイムレース順位表（世界生中継）",
        "judge_title": "🔐 現地審判専用リアルタイム制御パネル"
    }
}

selected_lang_name = st.sidebar.selectbox("🌐 Select Language / 언어 선택", list(LANG_DICT.keys()))
current_lang = LANG_DICT[selected_lang_name]
T = LOCALIZED_TEXT[current_lang]

st.title(T["title"])
st.caption(T["subtitle"])
st.markdown("---")

if "athletes" not in st.session_state:
    st.session_state.athletes = [
        {"BIB": "101", "Name": "김민우", "Team": "KOREA", "Status": "RACING", "CP1": "10:15:20", "CP2": "--:--:--", "CP3": "--:--:--", "Penalty": "None"},
        {"BIB": "102", "Name": "Alex Smith", "Team": "USA", "Status": "RACING", "CP1": "10:14:05", "CP2": "10:45:12", "CP3": "--:--:--", "Penalty": "None"},
        {"BIB": "103", "Name": "Chloe", "Team": "FRANCE", "Status": "RACING", "CP1": "10:16:55", "CP2": "10:49:30", "CP3": "--:--:--", "Penalty": "None"},
    ]

menu = st.sidebar.radio("🧭 Navigation", T["menu"])

# --- [모듈 1] 대회 홈 (유튜브 비디오 및 올림픽 사진 추가) ---
if menu == T["menu"][0]:
    st.header(T["notice"])
    
    # 레이아웃을 3단으로 균형 있게 분할하여 안내 설명이 가려지지 않도록 설계
    col_text, col_video, col_photo = st.columns([4, 4, 4])
    
    with col_text:
        st.markdown(f"### 🏔️ About the Race")
        st.write(T["desc"])
        st.markdown("""
        * **대회 일시:** 2026년 겨울 시즌 중 개최 예정
        * **경기 규정:** ISMF 국제 규정 전면 적용 (스프린트, 인디비주얼, 버티컬)
        * **예상 규모:** 국내외 선수, 관계자 및 관람객 3,000명~5,000명 참여 규모의 초대형 포럼 연계 행사
        """)
        st.info("💡 **Olympic System Info**\nThis website automatically translates into 6 languages and synchronizes with the judges' telemetry system.")
        
    with col_video:
        st.markdown(f"### {T['video_title']}")
        # 요청한 산악스키 안내 및 룰 설명 유튜브 영상 삽입
        st.video("https://youtu.be/KgyX5OjMTyM?si=Uu8mCwLV2X4an8Wk")
        st.caption("출처: 국제산악스키연맹(ISMF) 공식 안내 영상")

    with col_photo:
        st.markdown(f"### {T['photo_title']}")
        # 올림픽 산악스키 선수의 역동적인 주행 사진 삽입 (안내 창을 가리지 않는 독립 배치)
        st.image("https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=500&q=80", 
                 caption="올림픽 경기에서 설산을 질주하는 산악스키 국가대표 선수")
        
    # 하단 스폰서 영역 유지
    st.markdown("---")
    st.subheader("🤝 Global Partners & Sponsors")
    c_ad1, c_ad2 = st.columns(2)
    c_ad1.info("⛷️ **Premium Sponsor Slot**\nGlobal Outdoor Brand Banner Area")
    c_ad2.info("🥤 **Official Energy Drink Slot**\nOfficial Tournament Beverage Partner")

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
            st.success("Success! / Registration Complete!")

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
        st.success("Data synchronized successfully!")
        time.sleep(0.5)
        st.rerun()
