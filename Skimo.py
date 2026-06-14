import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="SKIMO KOREA", page_icon="🏔️", layout="wide")

# CSS 수정: 문제의 회색 반투명 테두리(잔상)를 강제 삭제
st.markdown("""
    <style>
    /* 1. 사이드바 숨김 */
    [data-testid="stSidebar"] { display: none !important; }
    
    /* 2. 스트림릿 기본 테두리 및 그림자 강제 제거 (핵심 수정) */
    div[data-testid="stTextInput"] > div > div {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
    }
    
    /* 3. 검색창을 포함하던 컨테이너의 잔상 테두리 제거 */
    .stApp .block-container { padding-top: 1rem; }
    
    /* 4. 전체적인 폰트 및 배경 레이아웃 */
    .stApp { background-color: #0e1117; color: white; }
    
    .hero-title { font-size: 50px; font-weight: bold; text-align: center; margin-top: 20px; }
    .hero-subtitle { font-size: 20px; text-align: center; color: #00c6ff; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown('<div class="hero-title">SKIMO KOREA</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">🏔️ 스키등산 정보 포털</div>', unsafe_allow_html=True)

# 검색창 영역 (잔상 없는 깔끔한 텍스트 입력창)
search_query = st.text_input("", placeholder="🔍 포털 사이트 내 필요한 정보를 입력해 주세요...")

# 이후 컨텐츠들...
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🏁 Upcoming Events")
    st.write("대회 일정이 곧 공개됩니다.")

with col2:
    st.subheader("📺 경기 안내")
    st.write("규정 및 영상 자료")

with col3:
    st.subheader("📸 갤러리")
    st.write("현장 사진 모음")
