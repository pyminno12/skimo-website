import streamlit as st
import pandas as pd
from datetime import datetime
import time
import json
import os

# ==========================================
# [신규 핵심 기능]: JSON 기반 로컬 파일 DB 시스템
# ==========================================
DB_FILE = "users_db.json"

def load_users():
    """로컬 파일에서 가입된 사용자 정보를 읽어옵니다."""
    # 파일이 없으면 초기 관리자/심판 계정 세팅 후 파일 생성
    if not os.path.exists(DB_FILE):
        initial_db = {
            "admin": {"pw": "1234", "role": "ADMIN"},
            "skimo": {"pw": "skimo123", "role": "JUDGE"}
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_db, f, ensure_ascii=False, indent=4)
        return initial_db
    
    # 파일이 있으면 읽어서 파이썬 딕셔너리로 변환
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"admin": {"pw": "1234", "role": "ADMIN"}}

def save_users(users_dict):
    """사용자 정보 변경(회원가입/탈퇴) 시 파일을 영구 저장합니다."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users_dict, f, ensure_ascii=False, indent=4)

# 페이지 설정 및 레이아웃 규격 최적화
st.set_page_config(page_title="SKIMO KOREA", page_icon="🏔️", layout="wide")

# 배경 이미지 링크 매핑
BG_IMAGES = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=1800&q=80",
    "https://images.unsplash.com/photo-1518098268026-4e43a1a009de?auto=format&fit=crop&w=1800&q=80"   
]

# 시스템 구동 상태 정의
if "menu_idx" not in st.session_state:
    st.session_state.menu_idx = 0
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# A. 사용자 및 권한 도메인 (임시 세션 대신 로컬 파일 DB 로드)
user_db = load_users()

# B. 선수 및 경기/기록 데이터 통합 도메인
if "athletes_domain" not in st.session_state:
    st.session_state.athletes_domain = {
        "101": {"Name": "김민우", "Team": "KOREA", "Category": "Sprint", "Status": "RACING", "CP1": "10:15:20", "CP2": "--:--:--", "Penalty_Sec": 0, "Final_Record": "--:--:--"},
        "102": {"Name": "Alex Smith", "Team": "USA", "Category": "Individual", "Status": "RACING", "CP1": "10:14:05", "CP2": "10:45:12", "Penalty_Sec": 0, "Final_Record": "--:--:--"},
        "103": {"Name": "Chloe", "Team": "FRANCE", "Category": "Vertical", "Status": "RACING", "CP1": "10:16:55", "CP2": "10:49:30", "Penalty_Sec": 10, "Final_Record": "--:--:--"},
    }

# C-1. 글로벌 공지사항 데이터
if "notice_domain" not in st.session_state:
    st.session_state.notice_domain = [
        {
            "date": "2026-06-15", "category": "🏆 Race Info",
            "title": {"KO": "2026/27 ISMF 산악스키 월드컵 개막전 일정 확정 (프랑스 알프스)"},
            "content": {"KO": "국제산악스키연맹(ISMF)이 다가오는 시즌 개막전을 프랑스 알프스에서 개최한다고 밝혔습니다."}
        }
    ]

# C-2. 홈 화면용 글로벌 최신 뉴스 데이터
if "home_news_domain" not in st.session_state:
    st.session_state.home_news_domain = [
        {"date": "2026-06-18", "link": "https://www.ismf-ski.org/", "title": {"KO": "🚀 2030 프랑스 알프스 동계 올림픽, 산악스키 세부 종목 규정 발표 예정", "EN": "🚀 2030 French Alps Winter Olympics: Detailed Skimo Regulations to be Announced"}},
        {"date": "2026-06-12", "link": "https://www.ismf-ski.org/", "title": {"KO": "❄️ 아시아 산악스키 연맹, 청소년 선수 육성을 위한 동계 캠프 평창 개최 확정", "EN": "❄️ Asian Skimo Federation Confirms Winter Youth Development Camp in Pyeongchang"}},
        {"date": "2026-06-05", "link": "https://www.ismf-ski.org/", "title": {"KO": "🏅 대한민국 산악스키 국가대표팀, 뉴질랜드 전지훈련 위해 출국", "EN": "🏅 National Skimo Team Departs for Off-Season Training in New Zealand"}}
    ]

selected_bg = BG_IMAGES[st.session_state.menu_idx] if st.session_state.menu_idx < len(BG_IMAGES) else BG_IMAGES[0]

# CSS 스타일 정의
st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{ display: none !important; }}
    .stAppDeployDropdown {{ display: none !important; }}
    [data-testid="stSidebar"] {{ display: none !important; }}
    .block-container {{ padding-top: 0rem; padding-bottom: 0rem; padding-left: 0rem; padding-right: 0rem; }}
    .stApp {{ background: linear-gradient(rgba(15, 32, 39, 0.85), rgba(44, 83, 100, 0.75)), url('{selected_bg}') no-repeat center center fixed; background-size: cover !important; }}
    .centered-wrapper {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
    .custom-header-bg {{ background-color: rgba(15, 32, 39, 0.4); backdrop-filter: blur(5px); width: 100%; padding: 10px 0; }}
    .notice-card {{ background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; margin-bottom: 15px; }}
    .notice-badge {{ background-color: #00c6ff; color: #111; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-right: 10px; }}
    .notice-date {{ color: #cbd5e1; font-size: 13px; }}
    .notice-title {{ font-size: 18px; font-weight: 600; color: #ffffff; margin-top: 8px; margin-bottom: 8px; }}
    .notice-content {{ font-size: 14px; color: #e2e8f0; line-height: 1.6; }}
    div.stButton > button {{ background: transparent !important; color: white !important; border: none !important; padding: 0px !important; margin-left: 20px !important; font-size: 14px !important; font-weight: 500; }}
    div.stButton > button:hover {{ color: #00c6ff !important; }}
    .hero-section {{ height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; }}
    .hero-title {{ font-size: 42px; font-weight: 800; text-shadow: 3px 3px 8px rgba(0,0,0,0.9); }}
    .hero-subtitle {{ font-size: 18px; color: #00c6ff; }}
    .content-box {{ max-width: 1200px; margin: 0 auto 50px auto; padding: 30px; background: rgba(255, 255, 255, 0.07); backdrop-filter: blur(10px); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.15); color: #ffffff; }}
    .news-list-item {{ padding: 14px 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.15); display: flex; justify-content: space-between; align-items: center; }}
    .news-list-title {{ font-size: 15px; color: #e2e8f0; text-decoration: none; }}
    .news-list-meta {{ font-size: 13px; color: #cbd5e1; }}
    </style>
""", unsafe_allow_html=True)

# 6개국 다국어 사전
LANG_DICT = {"한국어 (KO)": "KO", "English (EN)": "EN", "Français (FR)": "FR", "Italiano (IT)": "IT", "简体中文 (ZH)": "ZH", "日本語 (JA)": "JA"}
LOCALIZED_TEXT = {
    "KO": {"title": "SKIMO KOREA", "subtitle": "스키등산 정보 포털", "menu": ["대회 홈", "선수 참가 신청", "실시간 리더보드 (LIVE)", "🔐 심판/관리자 패널", "📢 글로벌 공지사항"], "desc": "본 대회는 국제산악스키연맹(ISMF) 규정을 준수하며, 실시간 기록을 생중계합니다.", "video": "📺 경기 종목 안내", "intro_video": "⛷️ 산악스키 소개", "photo": "📸 올림픽 현장 갤러리", "pay": "💳 참가 신청 및 안전 결제", "news_title": "📰 News & Stories (글로벌 최신 소식)", "search_holder": "🔍 검색어를 입력하세요...", "notice": "📢 공지사항", "auth": "👤 로그인/회원가입"},
    "EN": {"title": "SKIMO KOREA", "subtitle": "Ski Mountaineering Information Portal", "menu": ["Home", "Athlete Registration", "Live Leaderboard", "🔐 Judge/Admin Panel", "📢 Global Notice"], "desc": "This tournament complies with ISMF regulations. Scores are updated in real-time.", "video": "📺 Skimo Rules Video", "intro_video": "⛷️ What is Skimo?", "photo": "📸 Olympic Action Gallery", "pay": "💳 Register & Secure Pay", "news_title": "📰 News & Stories (Global Latest News)", "search_holder": "🔍 Search information...", "notice": "📢 Notice", "auth": "👤 Login/Register"}
}

# ==========================================
# [💡 업데이트]: 회원가입 영구 보존 및 탈퇴 모달창
# ==========================================
@st.dialog("🔐 SKIMO KOREA 계정 관리")
def auth_dialog():
    # 매번 최신 파일 DB 상태를 읽어옴
    current_users = load_users()
    
    # 1단계: 로그인이 안 되어 있을 때 (로그인 / 회원가입)
    if st.session_state.logged_in_user is None:
        tab1, tab2 = st.tabs(["👤 로그인", "📝 회원가입"])
        with tab1:
            st.write("포털 서비스를 위해 로그인해 주세요.")
            login_id = st.text_input("아이디", key="login_id")
            login_pw = st.text_input("비밀번호", type="password", key="login_pw")
            if st.button("로그인 완료", use_container_width=True):
                if login_id in current_users and current_users[login_id]["pw"] == login_pw:
                    st.session_state.logged_in_user = login_id
                    st.success(f"🎉 {login_id}님, 환영합니다! ({current_users[login_id]['role']} 권한)")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ 아이디 또는 비밀번호가 일치하지 않습니다.")
        with tab2:
            st.write("새로운 SKIMO KOREA 계정을 생성합니다. (컴퓨터에 영구 저장됩니다)")
            new_id = st.text_input("사용할 아이디", key="new_id")
            new_pw = st.text_input("비밀번호 설정", type="password", key="new_pw")
            if st.button("회원가입 신청", use_container_width=True):
                if not new_id or not new_pw:
                    st.warning("⚠️ 아이디와 비밀번호를 모두 입력해 주세요.")
                elif new_id in current_users:
                    st.error("❌ 이미 존재하는 아이디입니다.")
                else:
                    # 파일 데이터베이스에 추가 및 물리적 파일 저장
                    current_users[new_id] = {"pw": new_pw, "role": "JUDGE"}
                    save_users(current_users)
                    st.success("📝 회원가입이 완료되었습니다! 이제 로그인할 수 있습니다.")
                    time.sleep(1)
                    st.rerun()
                    
    # 2단계: 로그인이 이미 되어 있을 때 (로그아웃 / 회원탈퇴)
    else:
        user = st.session_state.logged_in_user
        st.write(f"👤 현재 접속 계정: **{user}**")
        st.write(f"🛡️ 권한 등급: `{current_users[user]['role']}`")
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        
        # 로그아웃 버튼
        if st.button("🔓 로그아웃", use_container_width=True):
            st.session_state.logged_in_user = None
            st.success("로그아웃 되었습니다.")
            time.sleep(0.5)
            st.rerun()
            
        # [신규 기능]: 회원 탈퇴 로직
        st.write("🛑 계정 영구 삭제를 원하시면 아래 단추를 누르세요.")
        if st.button("🚨 회원 탈퇴 (계정 영구 삭제)", use_container_width=True):
            if user in ["admin", "skimo"]:
                st.error("❌ 시스템 기본 관리자/심판 계정은 탈퇴할 수 없습니다.")
            else:
                # 딕셔너리에서 제거 후 파일 갱신 및 세션 해제
                del current_users[user]
                save_users(current_users)
                st.session_state.logged_in_user = None
                st.success("🗑️ 계정이 안전하게 영구 삭제되었습니다.")
                time.sleep(1)
                st.rerun()

# ==========================================
# 3. 상단 레이아웃 배치 및 검색 엔진
# ==========================================
st.markdown('<div class="custom-header-bg">', unsafe_allow_html=True)
st.markdown('<div class="centered-wrapper">', unsafe_allow_html=True)

if "current_lang_code" not in st.session_state:
    st.session_state.current_lang_code = "KO"

T = LOCALIZED_TEXT.get(st.session_state.current_lang_code, LOCALIZED_TEXT["KO"])
c_menu, c_search, c_right = st.columns([3, 4, 5])

with c_search:
    search_query = st.text_input("Search", placeholder=T["search_holder"], label_visibility="collapsed")
    # (검색 엔진 생략 가능하나 유지)

with c_menu:
    menu_list = list(T["menu"])
    selected_menu_raw = st.selectbox("Menu", menu_list, index=st.session_state.menu_idx if st.session_state.menu_idx < len(menu_list) else 0, label_visibility="collapsed")
    st.session_state.menu_idx = menu_list.index(selected_menu_raw)
    
with c_right:
    sub_lang, sub_buttons = st.columns([4, 6])
    with sub_lang:
        selected_lang_name = st.selectbox("Lang", list(LANG_DICT.keys()), index=list(LANG_DICT.values()).index(st.session_state.current_lang_code), label_visibility="collapsed")
        st.session_state.current_lang_code = LANG_DICT[selected_lang_name]
        
    with sub_buttons:
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            if st.button(T["notice"], key="notice_top_nav_btn"):
                st.session_state.menu_idx = 4
                st.rerun()
        with btn_col2:
            # 상태 표시 텍스트 다이나믹 바인딩
            auth_text = T["auth"] if st.session_state.logged_in_user is None else f"👤 {st.session_state.logged_in_user}"
            if st.button(auth_text, key="auth_management_btn"):
                auth_dialog()

st.markdown('</div></div>', unsafe_allow_html=True)

# 히어로 헤더 및 콘텐츠 박스 시작
st.markdown(f'<div class="centered-wrapper"><div class="hero-section"><div class="hero-title">{T["title"]}</div><div class="hero-subtitle">🏔️ {T["subtitle"]}</div></div></div>', unsafe_allow_html=True)
st.markdown('<div class="content-box">', unsafe_allow_html=True)

# [콘텐츠 분기 1] 대회 홈 화면
if st.session_state.menu_idx == 0:
    st.markdown("## 🏁 Upcoming Events & Overview")
    col_text, col_video, col_intro, col_photo = st.columns([3, 3, 3, 3])
    with col_text:
        st.markdown(f"### 📢 Information")
        st.write(T["desc"])
    with col_video: st.video("https://youtu.be/KgyX5OjMTyM?si=Uu8mCwLV2X4an8Wk")
    with col_intro: st.video("https://youtu.be/nLjES8kuFRg?si=xu3P1kuKedFOdjRl")
    with col_photo: st.image("https://raw.githubusercontent.com/pyminno12/skimo-website/main/skimo_race_1.jpg", use_container_width=True)

    # 뉴스 피드 섹션
    st.markdown("<hr style='border-color: rgba(255,255,255,0.15);'>", unsafe_allow_html=True)
    st.markdown(f"## {T['news_title']}")
    st.markdown("<div style='background-color: rgba(255, 255, 255, 0.04); padding: 10px 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    for item in st.session_state.home_news_domain:
        localized_news_title = item["title"].get(st.session_state.current_lang_code, item["title"]["EN"])
        st.markdown(f'<div class="news-list-item"><a href="{item["link"]}" target="_blank" class="news-list-title">📌 {localized_news_title}</a><span class="news-list-meta">📅 {item["date"]}</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# [콘텐츠 분기 2] 선수 참가 신청
elif st.session_state.menu_idx == 1:
    st.markdown(f"## {T['menu'][1]}")
    with st.form("global_reg_form"):
        p_name = st.text_input("Name")
        p_nation = st.text_input("Nationality")
        p_event = st.selectbox("Event Category", ["Sprint", "Individual", "Vertical"])
        if st.form_submit_button(T["pay"]) and p_name:
            next_bib = str(100 + len(st.session_state.athletes_domain) + 1)
            st.session_state.athletes_domain[next_bib] = {"Name": p_name, "Team": p_nation, "Category": p_event, "Status": "RACING", "CP1": "--:--:--", "CP2": "--:--:--", "Penalty_Sec": 0, "Final_Record": "--:--:--"}
            st.success(f"🎉 배정된 배번호는 [{next_bib}] 입니다.")

# [콘텐츠 분기 3] 실시간 리더보드
elif st.session_state.menu_idx == 2:
    st.markdown(f"## {T['menu'][2]}")
    data_list = [{"BIB": b, **i} for b, i in st.session_state.athletes_domain.items()]
    df = pd.DataFrame(data_list)[["BIB", "Name", "Team", "Category", "Status", "CP1", "CP2", "Penalty_Sec", "Final_Record"]]
    st.dataframe(df.set_index("BIB"), use_container_width=True)

# [콘텐츠 분기 4] 🔐 심판/관리자 패널
elif st.session_state.menu_idx == 3:
    st.markdown(f"## {T['menu'][3]}")
    if st.session_state.logged_in_user is None: st.warning("⚠️ 심판 전용 패널입니다. 로그인을 완료해 주세요.")
    else:
        st.write(f"💼 접속 계정: **{st.session_state.logged_in_user}** | 권한: `{user_db.get(st.session_state.logged_in_user, {}).get('role', 'GUEST')}`")
        bib_list = list(st.session_state.athletes_domain.keys())
        selected_bib = st.selectbox("BIB 선택", bib_list)
        new_status = st.selectbox("상태 변경", ["RACING", "FINISHED", "DNF", "DSQ"])
        if st.button("🚨 동기화"):
            st.session_state.athletes_domain[selected_bib]["Status"] = new_status
            st.success("반영되었습니다.")

# [콘텐츠 분기 5] 📢 글로벌 공지사항 및 뉴스 피드 페이지
elif st.session_state.menu_idx == 4:
    st.markdown(f"## {T['menu'][4]}")
    for item in st.session_state.notice_domain:
        title_text = item["title"].get(st.session_state.current_lang_code, "No Title")
        content_text = item["content"].get(st.session_state.current_lang_code, "No Content")
        st.markdown(f'<div class="notice-card"><div><span class="notice-badge">{item["category"]}</span><span class="notice-date">📅 {item["date"]}</span></div><div class="notice-title">{title_text}</div><div class="notice-content">{content_text}</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
