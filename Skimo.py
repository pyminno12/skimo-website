import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# [설계 3단계] 부품(API) 및 데이터 모듈화 정의
# ==========================================
st.set_page_config(page_title="ISMF Korea Central System", page_icon="🏔️", layout="wide")

# 1. 시스템 전역 상태 관리 (Mock 데이터베이스)
if "athletes" not in st.session_state:
    st.session_state.athletes = [
        {"BIB": "101", "Name": "김민우", "Team": "강원스모클럽", "Status": "경쟁중", "CP1": "10:15:20", "CP2": "--:--:--", "CP3": "--:--:--", "Penalty": "없음"},
        {"BIB": "102", "Name": "John Doe", "Team": "USA National", "Status": "경쟁중", "CP1": "10:14:05", "CP2": "10:45:12", "CP3": "--:--:--", "Penalty": "없음"},
        {"BIB": "103", "Name": "이서연", "Team": "한국체육대학교", "Status": "경쟁중", "CP1": "10:16:55", "CP2": "10:49:30", "CP3": "--:--:--", "Penalty": "없음"},
    ]

if "logs" not in st.session_state:
    st.session_state.logs = []

# 다국어 모듈
lang = st.sidebar.radio("🌐 Language", ["KO", "EN"])
T = {
    "KO": {"home": "대회 홈/문화행사", "reg": "선수 참가 신청 (결제)", "live": "실시간 리더보드 (LIVE)", "judge": "🔐 심판/관리자 전용 패널"},
    "EN": {"home": "Home/Events", "reg": "Registration & Pay", "live": "Live Leaderboard", "judge": "🔐 Judge/Admin Panel"}
}[lang]

st.title("🏔️ ISMF KOREA SEMI-CENTRAL SYSTEM")
st.caption("계획표 기반의 권한 분리 및 실시간 경기 제어 통합 솔루션")
st.markdown("---")

# ==========================================
# [설계 1단계] 사용자 그룹 권한 분류 (메뉴 트리)
# ==========================================
menu = st.sidebar.radio("🧭 메뉴 트리 (Menu Tree)", [T["home"], T["reg"], T["live"], T["judge"]])

# --- 1. 일반 안내 및 연계 문화행사 모듈 ---
if menu == T["home"]:
    st.header("📢 대회 및 문화행사 통합 포털")
    col_info, col_ad = st.columns([7, 3])
    
    with col_info:
        st.subheader("🏁 경기 요강 및 룰 가이드")
        st.write("본 대회는 ISMF 규정을 준수하며, 필드 심판의 모바일 앱을 통해 실시간으로 판정 및 페널티가 집계됩니다.")
        
        # 실제 외부 API(구글맵 등) 연동을 위한 명세 확장 구역
        st.info("⚙️ **[기술 명세] External API 연동 인터페이스**\n* 위치 서비스: Google Maps API 기반 코스 매핑 예정\n* 인증 서비스: 자원봉사자 및 심판용 OAuth 2.0 보안 토큰 적용 가능 구조")
        
        st.markdown("### 🎭 대회 연계 문화/레저 프로그램")
        st.markdown("* **설산 아웃도어 스포츠 박람회:** 베이스캠프 내 주요 스폰서 장비 전시 및 부스 운영\n* **정선/평창 겨울 문화 페스티벌:** 참가 선수 및 관람객 5,000명 대상 야간 미디어 파사드 공연")

    with col_ad:
        st.subheader("🤝 후원사 및 광고 수익화 영역")
        st.image("https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=400&q=80", caption="공식 타이틀 스폰서십 광고 노출")
        st.success("📈 **광고 슬롯 B**\n\n대규모 트래픽 발생 시 구글 애드센스 및 지역 리조트 배너 연동 컴포넌트")

# --- 2. 선수 참가 신청 및 패키지 결제 모듈 ---
elif menu == T["reg"]:
    st.header("📝 선수 참가 신청 및 행정 결제 모듈")
    st.write("선수 등록부터 숙박, 식사 예약, 결제 모듈 연동을 위한 프론트 동선 스케치 화면입니다.")
    
    with st.form("checkout_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("선수명 (Name)")
            bib_wish = st.text_input("희망 배번호 (Desired BIB)")
        with c2:
            event_type = st.selectbox("참가 종목", ["스프린트 (Sprint)", "인디비주얼 (Individual)", "버티컬 (Vertical)"])
            package = st.selectbox("숙박/식사 패키지 선택", ["선택 안함", "공식 콘도 2인실 + 전일정 식권 (+100,000원)", "공식 콘도 4인실 (+50,000원)"])
        
        st.markdown("##### 📄 안전 보장 및 면책 동의")
        agree = st.checkbox("ISMF 반도핑 규정 동의 및 경기 중 상해에 대한 주최측 면책에 동의합니다.")
        
        # [설계 3단계] 결제 모듈(PG) 연동 가상 인터페이스
        fee = 30000 + (100000 if "2인" in package else (50000 if "4인" in package else 0))
        st.metric("최종 결제 금액 (PG 연동 예정)", f"{fee:,} 원")
        
        pay_btn = st.form_submit_button("💳 안전 결제 및 참가 확정")
        if pay_btn:
            if name and agree:
                new_athlete = {"BIB": bib_wish if bib_wish else str(100 + len(st.session_state.athletes)+1), "Name": name, "Team": "개인등록", "Status": "경쟁중", "CP1": "--:--:--", "CP2": "--:--:--", "CP3": "--:--:--", "Penalty": "없음"}
                st.session_state.athletes.append(new_athlete)
                st.success(f"🎉 결제 승인 완료! {name} 선수가 데이터베이스에 성공적으로 등록되었습니다.")
            else:
                st.error("❌ 필수 입력 사항을 확인하고 면책 동의서에 체크해 주세요.")

# --- 3. 일반 관람객용 실시간 리더보드 모듈 ---
elif menu == T["live"]:
    st.header("⏱️ 일반 관람객용 실시간 경기 리더보드")
    st.write("현장에 오지 못한 관람객과 미디어가 실시간으로 순위와 패널티를 추적하는 대시보드입니다.")
    
    # 데이터 출력의 직관성 및 시각화 확보
    df = pd.DataFrame(st.session_state.athletes)
    st.dataframe(df.set_index("BIB"), use_container_width=True)
    
    if st.button("🔄 즉시 새로고침 (Manual Refresh)"):
        st.rerun()

# --- 4. [설계 1, 2단계] 🔐 심판 및 관리자 전용 실시간 제어 패널 ---
elif menu == T["judge"]:
    st.header("🔐 필드 심판 및 관리자 전용 제어 시스템")
    st.write("현장 고령 자원봉사자/심판들의 특성을 고려하여 **최소한의 스마트폰 터치(동선 최소화)**로 설계된 입력기입니다.")
    
    # 선수 리스트업 생성
    athlete_names = [f"#{a['BIB']} - {a['Name']}" for a in st.session_state.athletes]
    
    col_input, col_view = st.columns([4, 6])
    
    with col_input:
        st.subheader("📱 모바일 현장 기록 입력기")
        target_athlete = st.selectbox("🎯 대상 선수 선택", athlete_names)
        target_bib = target_athlete.split(" - ")[0].replace("#", "")
        
        target_cp = st.radio("📍 현재 통과 체크포인트 (CP)", ["CP1", "CP2", "CP3"])
        
        st.markdown("---")
        st.subheader("⚠️ ISMF 규정 페널티 부여")
        penalty_type = st.selectbox("페널티 사유 선택", ["없음", "+1:00 (스킨 탈착 규정 위반)", "+3:00 (의무 장비 누락)", "실격 (DSQ)"])
        
        # [설계 2단계 반영] 터치 최소화 '동시 입력' 버튼
        if st.button("🚀 기록 및 페널티 실시간 전송"):
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # 메인 DB 업데이트 세션 (모듈간 데이터 동기화)
            for athlete in st.session_state.athletes:
                if athlete["BIB"] == target_bib:
                    athlete[target_cp] = current_time
                    if penalty_type != "없음":
                        athlete["Penalty"] = penalty_type
                        if "실격" in penalty_type:
                            athlete["Status"] = "실격(DSQ)"
            
            st.success(f"데이터 송신 성공! {target_athlete} 선수의 {target_cp} 통과 시간({current_time}) 및 페널티가 중앙 시스템으로 즉시 반영되었습니다.")
            time.sleep(1)
            st.rerun()
            
    with col_view:
        st.subheader("📊 주주총회 및 운영진 실시간 재정/인력 관제 현황")
        
        # 총계 연산 자동화 모듈
        total_a = len(st.session_state.athletes)
        dsq_count = sum(1 for a in st.session_state.athletes if "실격" in a["Status"])
        
        m1, m2 = st.columns(2)
        m1.metric("현재 레이스 중인 총 선수", f"{total_a} 명")
        m2.metric("실격(DSQ) 및 패널티 발생", f"{dsq_count} 건", delta="- 실시간 반영중", delta_color="inverse")
        
        st.markdown("##### 📝 심판실 원격 모니터링 테이블")
        st.dataframe(pd.DataFrame(st.session_state.athletes)[["BIB", "Name", "Status", "Penalty"]], use_container_width=True)
