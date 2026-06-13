import streamlit as st
import pandas as pd
import time

# 1. 페이지 설정
st.set_page_config(page_title="ISMF KOREA Official", page_icon="🏔️", layout="wide")

# 2. 메인 타이틀
st.title("🏔️ ISMF KOREA CHAMPIONSHIP")
st.subheader("국제산악스키연맹 공인 대한민국 산악스키 선수권 대회 및 참가 관리 시스템")
st.markdown("---")

# 3. 사이드바 메뉴 확장
menu = st.sidebar.selectbox(
    "메뉴 선택 (Menu)", 
    ["대회 홈 & 공식 요강", "대회 참가 신청 (Registration)", "실시간 리더보드 (LIVE)", "자원봉사 지원"]
)

# --- 1. 대회 홈 & 공식 요강 섹션 ---
if menu == "대회 홈 & 공식 요강":
    st.header("📢 대회 공식 안내 (Notice)")
    
    # 가상의 공식 안내서 (PDF 다운로드 기능 모사)
    st.markdown("""
    ### 📅 2026 대회 세부 일정 및 내용
    * **대회 일시:** 2026년 2월 13일(금) ~ 2월 15일(일) [3일간]
    * **대회 장소:** 대한민국 강원도 평창 설산 일대 (ISMF 공인 코스)
    * **경기 종목:** * **1일차:** 스프린트 (Sprint) - 폭발적인 스피드와 기술 요구
        * **2일차:** 인디비주얼 (Individual) - 설산을 개척하는 전통 종목
        * **3일차:** 버티컬 (Vertical) - 오직 업힐로만 승부하는 기록 경기
    * **참가 자격:** ISMF 등록 선수 및 동호인 (부문별 시상 분리)
    """)
    
    # 실제 운영 시 아버님이 작성하신 PDF 파일을 연결할 수 있는 다운로드 버튼
    mock_pdf = b"ISMF Korea Championship Official Regulation Guide PDF"
    st.download_button(
        label="📄 대회 공식 요강 가이드북 다운로드 (English/Korean)",
        data=mock_pdf,
        file_name="ISMF_Korea_2026_Guide.pdf",
        mime="application/pdf"
    )
    
    st.image("https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=800&q=80", caption="ISMF 규격 코스를 질주하는 선수들")

# --- 2. 대회 참가 신청 & 결제 섹션 (신규 추가!) ---
elif menu == "대회 참가 신청 (Registration)":
    st.header("📝 선수 참가 신청 및 패키지 예약")
    st.write("국제 규정에 따른 선수 등록 및 대회 기간 중 숙박·식사 패키지를 한 번에 선택할 수 있습니다.")
    
    with st.form("registration_form"):
        st.subheader("1. 개인 인적 사항")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("선수명 (Full Name)", placeholder="홍길동 / Hong Gil Dong")
            birth = st.date_input("생년월일 (Birth Date)")
            gender = st.radio("성별 (Gender)", ["남성 (Male)", "여성 (Female)"])
        with col2:
            phone = st.text_input("연락처 (Phone)", placeholder="010-XXXX-XXXX")
            email = st.text_input("이메일 (Email)")
            team = st.text_input("소속 팀/국가 (Team / Nation)", placeholder="예: 대한산악스키협회 / KOREA")
            
        st.markdown("---")
        st.subheader("2. 경기 종목 선택")
        category = st.selectbox("참가 부문", ["엘리트 성인부 (Elite)", "주니어부 (Junior)", "마스터즈 동호인부 (Masters)"])
        events = st.multiselect("참가 종목 (중복 선택 가능)", ["스프린트 (Sprint)", "인디비주얼 (Individual)", "버티컬 (Vertical)"])
        
        st.markdown("---")
        st.subheader("3. 숙박 및 식사 패키지 선택 (선택 사항)")
        accommodation = st.selectbox(
            "대회 공식 지정 숙소 예약",
            ["선택 안 함 (개인 해결)", "공식 콘도 2인 1실 (1박당 80,000원)", "공식 콘도 4인 1실 (1박당 40,000원)"]
        )
        stay_days = st.number_input("숙박 일수 (Nights)", min_value=0, max_value=4, value=0)
        meal_ticket = st.checkbox("대회 공식 만찬 및 식권 패키지 신청 (3일간 전 일정 식사 - 50,000원)")
        
        st.markdown("---")
        st.subheader("4. ISMF 규정에 따른 서류 제출 및 면책 동의")
        st.warning("⚠️ 산악스키는 익스트림 스포츠로서 위험 요소를 내포하고 있으므로 공식 면책동의서 제출 및 선수 안전 보험 가입 증서 업로드가 필수입니다.")
        
        insurance_file = st.file_defect = st.file_uploader("스포츠 상해 보험 가입 증서 업로드 (PDF/JPG)")
        agree = st.checkbox("본인은 대회 참가 중 발생하는 부상 및 사고에 대해 주최 측에 책임을 묻지 않으며, ISMF 반도핑 규정을 준수할 것을 동의합니다.")
        
        st.markdown("---")
        st.subheader("5. 참가비 및 결제 금액 확인")
        
        # 가상 참가비 계산 시스템
        entry_fee = len(events) * 30000  # 종목당 3만원
        room_fee = 80000 if "2인" in accommodation else (40000 if "4인" in accommodation else 0)
        total_accommodation_fee = room_fee * stay_days
        meal_fee = 50000 if meal_ticket else 0
        total_fee = entry_fee + total_accommodation_fee + meal_fee
        
        st.metric(label="총 결제 금액 (Total Amount)", value=f"{total_fee:,} 원")
        
        # 결제 수단 선택
        pay_method = st.radio("결제 수단 선택", ["신용카드 (Credit Card)", "가상계좌 무통장 입금", "해외 선수 전용 페이팔 (PayPal)"])
        
        # 제출 버튼
        submitted = st.form_submit_button("참가 신청 및 결제하기 (Submit & Pay)")
        
        if submitted:
            if not name or not email:
                st.error("❌ 필수 인적 사항(이름, 이메일)을 입력해 주세요.")
            elif not events:
                st.error("❌ 최소 하나 이상의 경기 종목을 선택해 주세요.")
            elif not agree:
                st.error("❌ 면책 동의서에 동의하셔야 참가 신청이 가능합니다.")
            else:
                with st.spinner("결제 요청 및 참가 승인 처리 중..."):
                    time.sleep(2)
                st.success(f"🎉 {name} 선수님, 참가 신청과 결제가 완료되었습니다!")
                st.balloons()
                st.info(f"등록 확인 메일이 {email}로 발송되었습니다. 배번호는 추후 심판진 배정 후 공지됩니다.")

# --- 3. 실시간 리더보드 섹션 ---
elif menu == "실시간 리더보드 (LIVE)":
    st.header("⏱️ 실시간 경기 현황 (LIVE)")
    st.write("각 체크포인트(CP)의 필드 심판들이 앱으로 입력한 데이터가 실시간으로 반영됩니다.")
    
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
    st.dataframe(df, use_container_width=True)
    
    if st.button("🔄 기록 새로고침"):
        with st.spinner("최신 경기 기록을 불러오는 중..."):
            time.sleep(0.5)
        st.rerun()

# --- 4. 자원봉사 신청 섹션 ---
elif menu == "자원봉사 지원":
    st.header("🤝 자원봉사자(서포터즈) 모집")
    st.write("대회의 원활한 운영과 디지털 심판 시스템을 지원해 줄 젊은 열정을 기다립니다.")
    
    with st.form("volunteer_form"):
        v_name = st.text_input("이름")
        v_phone = st.text_input("연락처")
        v_major = st.text_input("소속 / 전공")
        v_submitted = st.form_submit_button("지원하기")
        if v_submitted:
            st.success(f"{v_name}님의 지원이 정상적으로 접수되었습니다. 대회를 빛내주셔서 감사합니다!")
