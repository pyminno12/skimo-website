import streamlit as st
import pandas as pd
import time

# 1. 페이지 설정 및 기본 테마 정의
st.set_page_config(page_title="Ski Mountaineering Portal", page_icon="🏔️", layout="wide")

# 2. 다국어 지원 (외국인 방문자 고려)
if "lang" not in st.session_state:
    st.session_state.lang = "KO"

col_title, col_lang = st.columns([8, 2])
with col_lang:
    lang_choice = st.selectbox("🌐 Language", ["한국어 (KO)", "English (EN)"])
    st.session_state.lang = "KO" if "한국어" in lang_choice else "EN"

# 언어 팩 정의
texts = {
    "KO": {
        "title": "🏔️ 스키등산(산악스키) 대회정보 통합 포털",
        "subtitle": "행사 기획, 참가자, 봉사자, 관리자를 위한 통합 솔루션 시스템",
        "menu": ["대회 홈 & 문화행사 정보", "선수 참가 신청", "자원봉사 지원", "실시간 리더보드 (LIVE)", "🔐 관리자 모드"],
        "home_title": "📢 대회 및 연계 행사 안내",
        "ad_title": "🤝 공식 후원사 및 광고 파트너",
        "stats_title": "📊 대회 총괄 관리 대시보드 (기획자/관리자용)",
        "v_total": "총 지원 봉사자", "a_total": "총 등록 선수", "fee_total": "누적 참가비 매출"
    },
    "EN": {
        "title": "🏔️ Ski Mountaineering Tournament Portal",
        "subtitle": "Integrated Solution for Organizers, Athletes, Volunteers, and Admins",
        "menu": ["Home & Cultural Events", "Athlete Registration", "Volunteer Application", "Live Leaderboard", "🔐 Admin Mode"],
        "home_title": "📢 Tournament & Event Information",
        "ad_title": "🤝 Official Sponsors & Advertisers",
        "stats_title": "📊 Tournament Management Dashboard (For Organizers)",
        "v_total": "Total Volunteers", "a_total": "Total Athletes", "fee_total": "Total Revenue"
    }
}

T = texts[st.session_state.lang]

# 헤더 출력
with col_title:
    st.title(T["title"])
    st.caption(T["subtitle"])
st.markdown("---")

# 3. 통합 포털 메뉴 구조 구성
menu = st.sidebar.radio("🧭 Portal Menu", T["menu"])

# 가상 데이터베이스 (대규모 접속 및 유지보수성을 고려한 데이터 모델 모사)
if "athletes_db" not in st.session_state:
    st.session_state.athletes_db = [
        {"ID": 1, "Name": "홍길동", "Nation": "KOREA", "Event": "Sprint", "Fee": 30000},
        {"ID": 2, "Name": "Alex Smith", "Nation": "USA", "Event": "Individual", "Fee": 110000},
        {"ID": 3, "Name": "김철수", "Nation": "KOREA", "Event": "Vertical", "Fee": 80000},
    ]
if "volunteers_db" not in st.session_state:
    st.session_state.volunteers_db = [
        {"이름": "박영민", "연락처": "010-1234-5678", "전공": "컴퓨터공학"}
    ]

# --- [메뉴 1] 대회 홈 & 연계 문화행사 정보 ---
if menu in ["대회 홈 & 문화행사 정보", "Home & Cultural Events"]:
    st.header(T["home_title"])
    
    col_info, col_poster = st.columns([6, 4])
    with col_info:
        st.markdown(f"""
        ### 📅 2026 ISMF 대한민국 산악스키 선수권 대회
        * **개최지:** 강원도 평창 설산 일대 (ISMF 국제 공인 코스)
        * **규모:** 국내외 선수 및 동호인 **3,000명 ~ 5,000명 참여 예상** 
        
        ### 🎭 연계 문화/레저 행사 (통합 솔루션)
        * **산악 아웃도어 박람회:** 대회 기간 내 베이스캠프 전시장 운영 (장비 시연 및 체험)
        * **설산 문화 공연:** 개막식 당일 동계 스포츠 성공 기원 미디어아트 및 문화 공연 개최
        * **외국인 참가자 케어 서비스:** 인천공항-정선/평창 간 공식 셔틀버스 및 영문 가이드 지원
        """)
    with col_poster:
        st.image("https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=800&q=80", caption="ISMF Skimo World Cup Event")

    # [수정 요구 반영] 수천 명이 모였을 때 붙이는 광고/스폰서 구역 구체화
    st.markdown("---")
    st.subheader(T["ad_title"])
    col_ad1, col_ad2, col_ad3 = st.columns(3)
    with col_ad1:
        st.info("⛷️ **Premium Sponsor A**\n\n글로벌 아웃도어 브랜드 광고 구역")
    with col_ad2:
        st.info("🏨 **Official Lodging B**\n\n대회 공식 지정 리조트 및 숙박 연계 광고")
    with col_ad3:
        st.info("🥤 **Energy Drink C**\n\n스포츠 음료 공식 후원사 브랜드 배너")

# --- [메뉴 2] 선수 참가 신청 ---
elif menu in ["선수 참가 신청", "Athlete Registration"]:
    st.header("📝 Athlete Registration / 선수 참가 신청")
    with st.form("reg_form"):
        u_name = st.text_input("Name / 이름")
        u_nation = st.text_input("Nationality / 국적", value="KOREA")
        u_event = st.selectbox("Event / 종목", ["Sprint", "Individual", "Vertical"])
        u_package = st.checkbox("Apply for Accommodation + Meal Package (숙박 및 식사 패키지 포함 - 80,000원 추가)")
        
        calc_fee = 30000 + (80000 if u_package else 0)
        st.metric("Total Fee / 결제 예정 금액", f"{calc_fee:,} KRW")
        
        submit = st.form_submit_button("Submit & Pay / 참가 신청 및 결제")
        if submit and u_name:
            st.session_state.athletes_db.append({"ID": len(st.session_state.athletes_db)+1, "Name": u_name, "Nation": u_nation, "Event": u_event, "Fee": calc_fee})
            st.success(f"🎉 Registration Complete! Welcome, {u_name}!")
            st.balloons()

# --- [메뉴 3] 자원봉사 지원 ---
elif menu in ["자원봉사 지원", "Volunteer Application"]:
    st.header("🤝 Volunteer Application / 자원봉사 서포터즈 지원")
    with st.form("vol_form"):
        v_name = st.text_input("이름 (Name)")
        v_phone = st.text_input("연락처 (Phone)")
        v_spec = st.text_input("특기 및 전공 (예: 영어 통역 가능, 컴퓨터공학 등)")
        v_submit = st.form_submit_button("Apply / 지원하기")
        if v_submit and v_name:
            st.session_state.volunteers_db.append({"이름": v_name, "연락처": v_phone, "전공": v_spec})
            st.success(f"❤️ {v_name}님, 대회 자원봉사 지원이 완료되었습니다!")

# --- [메뉴 4] 실시간 리더보드 (LIVE) ---
elif menu in ["실시간 리더보드 (LIVE)", "Live Leaderboard"]:
    st.header("⏱️ Live Race Leaderboard")
    st.caption("필드 심판용 앱과 연동되어 실시간으로 업데이트되는 경기 순위입니다.")
    
    live_data = pd.DataFrame(st.session_state.athletes_db)
    st.dataframe(live_data, use_container_width=True)

# --- [메뉴 5] 🔐 관리자 모드 (신규 추가!) ---
elif menu in ["🔐 관리자 모드", "🔐 Admin Mode"]:
    st.header(T["stats_title"])
    st.write("주최측(아버님 및 사무국)이 대회의 전반적인 규모와 재정, 인력을 한눈에 파악하는 화면입니다.")
    
    # 총계 연산 및 시각화 (직관성/편리성 확보)
    total_athletes = len(st.session_state.athletes_db)
    total_vols = len(st.session_state.volunteers_db)
    total_revenue = sum([item["Fee"] for item in st.session_state.athletes_db])
    
    m1, m2, m3 = st.columns(3)
    m1.metric(T["a_total"], f"{total_athletes} 명")
    m2.metric(T["v_total"], f"{total_vols} 명")
    m3.metric(T["fee_total"], f"{total_revenue:,} 원")
    
    st.subheader("📋 실시간 등록 선수 명단 관리")
    st.dataframe(pd.DataFrame(st.session_state.athletes_db), use_container_width=True)
    
    st.subheader("📋 현장 자원봉사자 배치 명단")
    st.dataframe(pd.DataFrame(st.session_state.volunteers_db), use_container_width=True)
