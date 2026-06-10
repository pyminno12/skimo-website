import streamlit as st
import pandas as pd
import time

# 1. 페이지 기본 설정 (웹브라우저 탭에 표시될 내용)
st.set_page_config(page_title="ISMF KOREA", page_icon="🏔️", layout="wide")

# 2. 메인 헤더 및 대회 소개
st.title("🏔️ ISMF KOREA CHAMPIONSHIP")
st.subheader("국제산악스키연맹 공인 대한민국 산악스키 선수권 대회")
st.markdown("---")

# 3. 레이아웃 나누기 (사이드바와 메인 화면)
menu = st.sidebar.selectbox("메뉴 선택", ["대회 홈 (Home)", "실시간 리더보드 (LIVE)", "자원봉사 신청"])

if menu == "대회 홈 (Home)":
    st.header("한계를 넘어 설산을 지배하라")
    st.image("https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=800&q=80", caption="산악스키 레이스")
    
    st.markdown("""
    ### 📅 대회 개요
    * **대회명:** 2026 ISMF 대한민국 산악스키 선수권 대회
    * **규정:** ISMF(국제산악스키연맹) 국제 규격 적용
    * **주요 특징:** 본 대회는 필드 심판의 스마트폰 앱 시스템과 연동되어 실시간으로 기록이 집계됩니다.
    """)
    
    if st.button("대회 참가 신청하기 (Registration)"):
        st.success("참가 신청 페이지로 이동합니다. (추후 링크 연동)")

elif menu == "실시간 리더보드 (LIVE)":
    st.header("⏱️ 실시간 경기 현황 (LIVE)")
    st.write("각 체크포인트(CP)의 필드 심판들이 앱으로 입력한 데이터가 실시간으로 반영됩니다.")
    
    # 임시 데이터 (나중에 심판 앱 DB와 연결될 부분)
    data = {
        "순위": [1, 2, 3],
        "배번호": [104, 102, 115],
        "선수명": ["홍길동", "김철수", "이영희"],
        "소속": ["대한산악스키협회", "서울스모클럽", "한국체육대학교"],
        "최근 통과 구간": ["CP3 (정상)", "CP3 (정상)", "CP2 (업힐)"],
        "기록 (Time)": ["01:12:45", "01:14:20", "01:18:10"],
        "패널티": ["-", "-", "+1:00 (장비 규정 위반)"]
    }
    df = pd.DataFrame(data)
    
    # 웹 화면에 표 형태로 출력
    st.dataframe(df, use_container_width=True)
    
    # 실시간 새로고침 느낌을 주기 위한 버튼
    if st.button("🔄 기록 새로고침"):
        with st.spinner("최신 경기 기록을 불러오는 중..."):
            time.sleep(0.5)
        st.experimental_rerun()

elif menu == "자원봉사 신청":
    st.header("🤝 자원봉사자(서포터즈) 모집")
    st.write("대회의 원활한 운영과 디지털 심판 시스템을 지원해 줄 젊은 열정을 기다립니다.")
    
    with st.form("volunteer_form"):
        name = st.text_input("이름")
        phone = st.text_input("연락처")
        major = st.text_input("소속 / 전공 (예: 컴퓨터공학, 체육학 등)")
        submitted = st.form_submit_submit("지원하기")
        if submitted:
            st.success(f"{name}님의 지원이 정상적으로 접수되었습니다. 추후 연락드리겠습니다.")