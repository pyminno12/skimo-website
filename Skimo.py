import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import json
import re
import secrets
import string
from sqlalchemy import text

# ==========================================
# 1. 페이지 설정 및 글로벌 상태 정의
# ==========================================
st.set_page_config(page_title="SKIMO KOREA", page_icon="🏔️", layout="wide")

# 배경 이미지 풀
BG_IMAGES = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1614531341773-3bef8ca0da3b?auto=format&fit=crop&w=1800&q=80",  
    "https://images.unsplash.com/photo-1482867996988-2faec3cbb4f9?auto=format&fit=crop&w=1800&q=80",
    "https://images.unsplash.com/photo-1502680390469-be75c86b636f?auto=format&fit=crop&w=1800&q=80",
    "https://images.unsplash.com/photo-1518098268026-4e43a1a009de?auto=format&fit=crop&w=1800&q=80"   
]

if "menu_idx" not in st.session_state:
    st.session_state.menu_idx = 0
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# [브라우저 쿠키/로컬 스토리지 대용 구조]
DB_FILE = "user_database.json"
DB_TABLE_NAME = "skimo_users"

# ==========================================
# [신규 추가] 영구 데이터베이스 연결 (회원 정보 유실 방지)
# ------------------------------------------
# 문제: Streamlit Cloud 등 대부분의 무료 클라우드 호스팅은 로컬 디스크가
#       "임시(ephemeral)" 저장소라서, 앱이 재시작/재배포되면 로컬 파일이
#       초기화되어 user_database.json에 저장된 회원 정보가 사라집니다.
# 해결: secrets.toml에 [connections.skimo_db] 설정(Postgres 등 외부 DB 접속 정보)이
#       있으면 그 DB에 영구 저장하고, 설정이 없으면 기존처럼 로컬 JSON 파일을
#       사용합니다(로컬 개발용 폴백 - 이 경우 여전히 배포 환경에서는 유실될 수 있음).
# ==========================================
@st.cache_resource
def get_db_connection():
    """
    secrets.toml에 [connections.skimo_db] 설정이 있으면 SQL(Postgres 등) 연결을 반환하고,
    설정이 없거나 연결에 실패하면 (None, 실패사유)를 반환합니다(로컬 JSON 폴백 모드로 전환).
    결과 전체가 캐싱되므로 재실행 없이도(캐시 히트 시에도) 실패 사유가 유지됩니다.
    """
    try:
        if "connections" not in st.secrets or "skimo_db" not in st.secrets["connections"]:
            return None, "secrets.toml(또는 Streamlit Cloud Secrets)에 [connections.skimo_db] 설정 자체가 없습니다."

        conn = st.connection("skimo_db", type="sql")
        with conn.session as s:
            s.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {DB_TABLE_NAME} (
                    user_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL
                )
            """))
            s.commit()
        return conn, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

DB_CONN, DB_CONNECTION_ERROR_MSG = get_db_connection()
USING_PERSISTENT_DB = DB_CONN is not None

def ensure_user_meta_fields(db_data: dict) -> dict:
    """
    레거시 계정 데이터(이전 버전에서 생성된 계정)에 신규 필드를 보정합니다.
    - status: ACTIVE / SUSPENDED
    - pw_last_changed: 마지막 비밀번호 변경 시각 (ISO 포맷)
    - pw_history: 비밀번호 변경 이력 로그
    - email: 본인 인증용 이메일 (없으면 None)
    - phone: 본인 인증용 휴대폰 번호 (없으면 None)
    """
    changed = False
    now_iso = datetime.now().isoformat(timespec="seconds")
    for uid, info in db_data.items():
        if "status" not in info:
            info["status"] = "ACTIVE"
            changed = True
        if "pw_last_changed" not in info:
            info["pw_last_changed"] = now_iso
            changed = True
        if "pw_history" not in info:
            info["pw_history"] = [{"timestamp": now_iso, "changed_by": "시스템(자동 보정)"}]
            changed = True
        if "email" not in info:
            info["email"] = None
            changed = True
        if "phone" not in info:
            info["phone"] = None
            changed = True
    if changed:
        save_user_db(db_data)
    return db_data

def _build_initial_db() -> dict:
    now_iso = datetime.now().isoformat(timespec="seconds")
    return {
        "admin": {
            "pw": "1234", "role": "ADMIN", "status": "ACTIVE",
            "pw_last_changed": now_iso,
            "pw_history": [{"timestamp": now_iso, "changed_by": "시스템(초기 생성)"}],
            "email": None, "phone": None
        },
        "skimo": {
            "pw": "skimo123", "role": "JUDGE", "status": "ACTIVE",
            "pw_last_changed": now_iso,
            "pw_history": [{"timestamp": now_iso, "changed_by": "시스템(초기 생성)"}],
            "email": None, "phone": None
        }
    }

def load_user_db():
    # ---------- 1) 영구 DB가 연결되어 있는 경우 ----------
    if DB_CONN is not None:
        try:
            with DB_CONN.session as s:
                rows = s.execute(text(f"SELECT user_id, data FROM {DB_TABLE_NAME}")).fetchall()
            if rows:
                db_data = {}
                for row in rows:
                    try:
                        db_data[row[0]] = json.loads(row[1])
                    except (json.JSONDecodeError, TypeError):
                        # 개별 계정 데이터가 손상된 경우 해당 계정만 건너뜁니다.
                        continue
                if not db_data:
                    initial_db = _build_initial_db()
                    save_user_db(initial_db)
                    return initial_db
                return ensure_user_meta_fields(db_data)
            else:
                # DB가 비어있으면(최초 실행) 기본 계정을 생성해 DB에 저장
                initial_db = _build_initial_db()
                save_user_db(initial_db)
                return initial_db
        except Exception as e:
            st.error(f"❌ DB 조회 중 오류가 발생했습니다: {e}")
            return _build_initial_db()

    # ---------- 2) 영구 DB 미설정 → 로컬 JSON 파일 폴백 ----------
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            raw_content = f.read().strip()
        if not raw_content:
            # 파일은 존재하지만 내용이 비어있는 경우 (손상된 파일)
            raise json.JSONDecodeError("empty file", raw_content, 0)
        db_data = json.loads(raw_content)
        return ensure_user_meta_fields(db_data)
    except (FileNotFoundError, json.JSONDecodeError):
        # 파일이 없거나(FileNotFoundError), 있어도 비어있거나 손상된 경우(JSONDecodeError)
        # 모두 기본 계정으로 새로 초기화합니다.
        initial_db = _build_initial_db()
        save_user_db(initial_db)
        return initial_db

def save_user_db(db_data):
    # ---------- 1) 영구 DB가 연결되어 있는 경우: DB에 저장 ----------
    if DB_CONN is not None:
        try:
            with DB_CONN.session as s:
                s.execute(text(f"DELETE FROM {DB_TABLE_NAME}"))
                for uid, info in db_data.items():
                    s.execute(
                        text(f"INSERT INTO {DB_TABLE_NAME} (user_id, data) VALUES (:uid, :data)"),
                        {"uid": uid, "data": json.dumps(info, ensure_ascii=False)}
                    )
                s.commit()
            return
        except Exception as e:
            st.error(f"❌ DB 저장 중 오류가 발생했습니다: {e}")
            # DB 저장 실패 시에도 최소한 로컬 파일에는 백업 저장 시도
    # ---------- 2) 영구 DB 미설정(또는 저장 실패) → 로컬 JSON 파일에 저장 ----------
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=4)

# ==========================================
# [신규 추가] 비밀번호 보안 정책
# ==========================================
PASSWORD_POLICY_HINT = "🔐 비밀번호는 최소 8자 이상이며, 영문/숫자/특수문자를 각각 1개 이상 포함해야 합니다."

def validate_password_policy(pw: str):
    """
    비밀번호 정책 검증
    - 최소 8자 이상
    - 영문자 최소 1개
    - 숫자 최소 1개
    - 특수문자 최소 1개
    반환값: (통과여부: bool, 실패 사유 메시지: str)
    """
    if len(pw) < 8:
        return False, "비밀번호는 최소 8자리 이상이어야 합니다."
    if not re.search(r'[A-Za-z]', pw):
        return False, "비밀번호에 영문자가 최소 1개 포함되어야 합니다."
    if not re.search(r'[0-9]', pw):
        return False, "비밀번호에 숫자가 최소 1개 포함되어야 합니다."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=~`\[\];\'/\\]', pw):
        return False, "비밀번호에 특수문자가 최소 1개 포함되어야 합니다. (예: ! @ # $ % 등)"
    return True, ""

def generate_temp_password(length: int = 10) -> str:
    """정책을 만족하는 임시 비밀번호를 자동 생성합니다."""
    letters = string.ascii_letters
    digits = string.digits
    specials = "!@#$%^&*"
    # 각 카테고리 최소 1개씩 보장 후 나머지는 랜덤으로 채움
    base = [secrets.choice(letters), secrets.choice(digits), secrets.choice(specials)]
    remaining_pool = letters + digits + specials
    base += [secrets.choice(remaining_pool) for _ in range(max(length - 3, 0))]
    secrets.SystemRandom().shuffle(base)
    return "".join(base)

# ==========================================
# [신규 추가] 비밀번호 만료 정책 & 변경 이력 로깅
# ==========================================
PASSWORD_EXPIRY_DAYS = 90  # 비밀번호 만료 주기 (일)

def is_password_expired(user_record: dict) -> bool:
    """마지막 비밀번호 변경일로부터 PASSWORD_EXPIRY_DAYS가 지났는지 확인합니다."""
    last_changed_str = user_record.get("pw_last_changed")
    if not last_changed_str:
        return False
    try:
        last_changed = datetime.fromisoformat(last_changed_str)
    except ValueError:
        return False
    return (datetime.now() - last_changed).days >= PASSWORD_EXPIRY_DAYS

def log_password_change(db_data: dict, user_id: str, changed_by: str):
    """비밀번호 변경 이력을 기록하고 마지막 변경일을 갱신합니다."""
    now_iso = datetime.now().isoformat(timespec="seconds")
    db_data[user_id]["pw_last_changed"] = now_iso
    db_data[user_id].setdefault("pw_history", []).append({"timestamp": now_iso, "changed_by": changed_by})
    # 이력은 최근 20건까지만 보관 (파일 비대화 방지)
    db_data[user_id]["pw_history"] = db_data[user_id]["pw_history"][-20:]

# ==========================================
# [신규 추가] 이메일/SMS 본인 인증(OTP) 시스템
# ==========================================
OTP_EXPIRY_SECONDS = 300  # 인증번호 유효시간: 5분

def generate_otp_code() -> str:
    """6자리 숫자 인증번호를 안전하게 생성합니다."""
    return f"{secrets.randbelow(1000000):06d}"

def mask_email(email: str) -> str:
    """이메일 주소를 부분적으로 마스킹합니다. 예: ab****@gmail.com"""
    if not email or "@" not in email:
        return "*****"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "*" * max(len(local) - 1, 1)
    else:
        masked_local = local[:2] + "*" * (len(local) - 2)
    return f"{masked_local}@{domain}"

def mask_phone(phone: str) -> str:
    """휴대폰 번호를 부분적으로 마스킹합니다. 예: *******1234"""
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) < 4:
        return "*" * len(digits)
    return "*" * (len(digits) - 4) + digits[-4:]

def send_email_otp(to_email: str, otp_code: str):
    """
    st.secrets['smtp']에 SMTP 설정(host, port, user, password, sender)이 있으면
    실제 이메일을 발송합니다. 설정이 없거나 발송에 실패하면
    (False, 안내메시지)를 반환해 호출부에서 데모 모드로 처리하도록 합니다.
    """
    try:
        smtp_conf = st.secrets.get("smtp", None)
    except Exception:
        smtp_conf = None

    if not smtp_conf:
        return False, "SMTP 설정이 등록되어 있지 않아 실제 이메일이 발송되지 않았습니다."

    try:
        import smtplib
        from email.mime.text import MIMEText

        sender = smtp_conf.get("sender", smtp_conf.get("user", ""))
        msg = MIMEText(
            f"[SKIMO KOREA] 비밀번호 재설정 인증번호는 {otp_code} 입니다.\n"
            f"인증번호는 {OTP_EXPIRY_SECONDS // 60}분간 유효합니다.\n"
            f"본인이 요청하지 않았다면 이 메일을 무시해주세요."
        )
        msg["Subject"] = "[SKIMO KOREA] 비밀번호 재설정 인증번호"
        msg["From"] = sender
        msg["To"] = to_email

        with smtplib.SMTP(smtp_conf["host"], int(smtp_conf.get("port", 587))) as server:
            server.starttls()
            server.login(smtp_conf["user"], smtp_conf["password"])
            server.sendmail(sender, [to_email], msg.as_string())
        return True, f"{mask_email(to_email)} 주소로 인증번호를 발송했습니다."
    except Exception as e:
        return False, f"이메일 발송 중 오류가 발생했습니다: {e}"

def send_sms_otp(phone_number: str, otp_code: str):
    """
    st.secrets['twilio']에 Twilio 설정(account_sid, auth_token, from_number)이 있으면
    실제 SMS를 발송합니다. 설정이 없거나 발송에 실패하면
    (False, 안내메시지)를 반환해 호출부에서 데모 모드로 처리하도록 합니다.
    """
    try:
        twilio_conf = st.secrets.get("twilio", None)
    except Exception:
        twilio_conf = None

    if not twilio_conf:
        return False, "SMS 발송 설정(Twilio 등)이 등록되어 있지 않아 실제 문자가 발송되지 않았습니다."

    try:
        from twilio.rest import Client
        client = Client(twilio_conf["account_sid"], twilio_conf["auth_token"])
        client.messages.create(
            body=f"[SKIMO KOREA] 비밀번호 재설정 인증번호: {otp_code} (5분간 유효)",
            from_=twilio_conf["from_number"],
            to=phone_number
        )
        return True, f"{mask_phone(phone_number)} 번호로 인증번호를 발송했습니다."
    except Exception as e:
        return False, f"SMS 발송 중 오류가 발생했습니다: {e}"

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
                "KO": "🤖 **AI 요약:** 2030 프랑스 동계 올림픽 조직위 및 ISMF가 산악스키 정식 종목 채택에 따른 세부 중계 및 페널티 규정을 내달 확정합니다.\n\n💡 **핵심 키워드:** `#2030동계올림픽` `#ISMF규정`",
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
        padding: 15px; border-radius: 12px; margin-bottom: 15px; min-height: 170px;
    }}
    .equip-title {{ font-size: 18px; font-weight: bold; color: #00c6ff; margin-bottom: 8px; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 6개국 로컬라이제이션 매핑 아키텍처
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
        "equip_main_title": "🎿 ISMF 공인 산악스키 필수 5대 장비 안내",
        "equip_sub": "산악스키(Skimo) 대회는 경량화와 안전성이 승패를 가르는 핵심 요소입니다. 국제연맹(ISMF) 규정에 따른 필수 장비들의 가이드입니다.",
        "e1_t": "1. 초경량 산악스키 (Skimo Skis)", "e1_d": "오르막길을 빠르게 뛰어 올라가야 하므로 일반 알파인 스키에 비해 상상할 수 없을 정도로 가볍습니다. 남성용 기준 최소 780g, 여성용 700g 선으로 제한되며 탄소 섬유(Carbon)로 제작됩니다.",
        "e2_t": "2. 투어링 바인딩 (Tech Bindings)", "e2_d": "산악스키 바인딩은 업힐 모드 시 뒷굽이 떨어져 걸어 올라갈 수 있게 설계되었습니다. 다운힐 모드 시에는 뒷굽을 고정합니다. 핀(Pin) 테크 방식을 채택해 무게가 겨우 100g 안팎입니다.",
        "e3_t": "3. 등반용 클라이밍 스킨 (Climbing Skins)", "e3_d": "스키 플레이트 바닥에 붙이는 모헤어(Mohair) 소재의 전용 스킨입니다. 앞방향으로는 미끄러지지만, 뒷방향으로는 털이 서서 눈을 움켜쥐기 때문에 미끄러지지 않고 수직 오르막을 오를 수 있습니다.",
        "e4_t": "4. 워크 모드 지원 부츠 (Skimo Boots)", "e4_d": "레버 하나로 발목 관절 구동 범위를 60도 이상 확보하는 '워크 모드'와 활강을 위해 고정하는 '스키 모드'를 전환할 수 있습니다. 카본 재질로 발목 피로도를 최소화합니다.",
        "e5_t": "5. 탄소섬유 카본 폴 (Carbon Poles)", "e5_d": "상체 반동과 팔 근육을 이용해 업힐 추진력을 내는 도구입니다. 일반 스키 폴보다 길며, 샤프트 전체가 100% High-Modulus 카본으로 되어 있어 매우 가볍고 단단한 강성을 유지합니다.",
        "change_pw_btn": "🔒 비밀번호 변경",
        "forgot_pw_btn": "🔑 비밀번호 재설정"
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
        "equip_main_title": "🎿 ISMF Official Ski Mountaineering Mandatory Equipment",
        "equip_sub": "In Skimo racing, lightweight tech and safety are key. Here is the mandatory gear guide under ISMF rules.",
        "e1_t": "1. Ultra-Lightweight Skis", "e1_d": "Extremely light for fast uphill climbing. Minimum weight is restricted to 780g for men and 700g for women, made primarily of carbon fiber.",
        "e2_t": "2. Tech Tour Bindings", "e2_d": "Designed with a free-heel system for walking uphill, and locks down for alpine descents. Tech pin system keeps weight around 100g.",
        "e3_t": "3. Climbing Skins", "e3_d": "Mohair-based skins attached to ski bases. They glide forward smoothly but grip the snow firmly when moving backwards to allow vertical climbing.",
        "e4_t": "4. Walk-Mode Boots", "e4_d": "Features a swift lever switching between a 60° ankle rotation 'Walk Mode' and a rigid 'Ski Mode' for high-speed alpine descents.",
        "e5_t": "5. Carbon Racing Poles", "e5_d": "Provides essential upper-body propulsion during climbs. Slightly longer than alpine poles, built with 100% high-modulus carbon fiber.",
        "change_pw_btn": "🔒 Change Password",
        "forgot_pw_btn": "🔑 Reset Password"
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
        "equip_main_title": "🎿 Équipement obligatoire officiel de ski-alpinisme de l'ISMF",
        "equip_sub": "En ski-alpinisme, la légèreté et la sécurité sont cruciales. Voici le guide du matériel obligatoire selon l'ISMF.",
        "e1_t": "1. Skis ultra-légers", "e1_d": "Extrêmement légers pour les montées rapides. Limité à un minimum de 780g pour les hommes et 700g pour les femmes, fabriqués en fibre de carbone.",
        "e2_t": "2. Fixations Tech", "e2_d": "Conçues avec un système de talon libre pour la montée et verrouillables pour la descente. Le système à broches limite le poids à environ 100g.",
        "e3_t": "3. Peaux de phoque", "e3_d": "Peaux en mohair fixées sous les skis. Elles glissent vers l'avant mais agrippent la neige vers l'arrière pour permettre les ascensions verticales.",
        "e4_t": "4. Chaussures avec mode marche", "e4_d": "Dotées d'un levier basculant entre un 'Mode Marche' à 60° de rotation et un 'Mode Ski' rigide pour les descentes alpines rapides.",
        "e5_t": "5. Bâtons de course en carbone", "e5_d": "Fournissent la propulsion du haut du corps en montée. Plus longs que les bâtons alpins, 100% en fibre de carbone haute rigidité.",
        "change_pw_btn": "🔒 Changer le mot de passe",
        "forgot_pw_btn": "🔑 Réinitialiser le mot de passe"
    },
    "IT": {
        "title": "SKIMO KOREA", "subtitle": "Portale informativo sullo sci alpinismo",
        "menu": ["Home", "Iscrizione Atleti", "Classifica in Tempo Reale", "🎿 Guida all'attrezzatura", "🔐 Pannello Giudici/Admin", "📢 Avviso Globale"],
        "desc": "Questo torneo è conforme ai regolamenti ISMF. I punteggi e le penalità vengono aggregati in tempo reale tramite l'app web sul campo.",
        "video": "📺 Video delle regole dello Skimo", "intro_video": "⛷️ Cos'è lo Skimo?", "photo": "📸 Galleria d'azione olimpica", "pay": "💳 Registrati e pagamento sicuro",
        "news_title": "📰 News & Stories (Ultime notizie globali)", "search_holder": "🔍 Cerca informazioni...", "notice": "📢 Avviso", "auth": "👤 Accedi/Registrati",
        "ai_btn": "🤖 Visualizza il riepilogo dell'IA", "ai_modal_title": "⚡ Briefing in tempo reale dell'IA generativa",
        "stats_title": "📊 Analisi telemetrica in tempo reale", "total_athletes": "Atleti totali", "racing_athletes": "In gara ora", "finished_athletes": "Finito",
        "chart_country": "Atleti per paese", "chart_category": "Partecipazione per categoria", "toast_update": "📢 [Sincronizzazione live] Lo stato dell'atleta #{bib} è stato aggiornato a {status}!", 
        "equip_main_title": "🎿 Attrezzatura obbligatoria ufficiale di sci alpinismo ISMF",
        "equip_sub": "Nello sci alpinismo, la leggerezza e la sicurezza sono fondamentali. Ecco la guida ai materiali secondo le regole ISMF.",
        "e1_t": "1. Sci ultraleggeri", "e1_d": "Estremamente leggeri per salite veloci. Peso minimo limitato a 780g per gli uomini e 700g per le donne, realizzati in fibra di carbonio.",
        "e2_t": "2. Attacchi da alpinismo (Tech)", "e2_d": "Progettati con tallone libero per la camminata in salita e bloccabili per la discesa. Il sistema a perni mantiene il peso intorno ai 100g.",
        "e3_t": "3. Pelli di foca (Skins)", "e3_d": "Pelli in mohair applicate sotto la soletta. Scivolano in avanti ma fanno presa sulla neve all'indietro per consentire la salita verticale.",
        "e4_t": "4. Scarponi modalità Walk", "e4_d": "Dotati di una leva rapida che passa dalla modalità 'Walk' (rotazione caviglia >60°) alla modalità 'Ski' rigida per la discesa.",
        "e5_t": "5. Bastoncini in carbonio", "e5_d": "Forniscono la propulsione essenziale della parte superiore del corpo. Più lunghi dei bastoncini alpini, 100% in carbonio ad alto modulo.",
        "change_pw_btn": "🔒 Cambia password",
        "forgot_pw_btn": "🔑 Reimposta password"
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
        "equip_main_title": "🎿 ISMF 官方滑雪登山强制性装备指南",
        "equip_sub": "在滑雪登山比赛中，极致轻量化与安全性是取胜关键。以下是符合ISMF规定的必备装备要求。",
        "e1_t": "1. 超轻量滑雪板", "e1_d": "极轻的重量设计便于快速攀登。男子雪板最低限重780克，女子最低700克，主要采用碳纤维材质打造。",
        "e2_t": "2. 科技巡航固定器", "e2_d": "专为攀登时后跟分离设计，便于行走；滑降时可锁定后跟。采用插销技术，重量仅在100克左右。",
        "e3_t": "3. 防滑攀登雪皮", "e3_d": "贴在雪板底部的马海毛材质专用雪皮。向前可平滑向前滑行，向后时绒毛抓雪倒伏防滑，实现垂直攀登。",
        "e4_t": "4. 步行模式滑雪鞋", "e4_d": "具备快速换挡杆，可在提供60度以上踝关节活动度的“步行模式”与高强度滑降的“滑雪模式”之间自由切换。",
        "e5_t": "5. 碳纤维竞赛雪杖", "e5_d": "用于在攀登过程中提供上肢推进力。长度略长于普通高山雪杖，由100%高模量碳纤维制成，极轻且坚硬。",
        "change_pw_btn": "🔒 修改密码",
        "forgot_pw_btn": "🔑 重置密码"
    },
    "JA": {
        "title": "SKIMO KOREA", "subtitle": "山岳スキー情報ポータル",
        "menu": ["大会ホーム", "選手参加申込", "リアルタイムリーダーボード", "🎿 必須ギアガイド", "🔐 審判/管理者パネル", "📢 グローバルお知らせ"],
        "desc": "本大会은 国際山岳スキー連盟（ISMF）の規定に準拠しています。スコアやペナルティは、フィールドのウェブアプリを通じてリアルタイムで集計されます。",
        "video": "📺 山岳スキー規則動画", "intro_video": "⛷️ 山岳スキーとは？", "photo": "📸 オリンピックギャラリー", "pay": "💳 参加申込と安全な決済",
        "news_title": "📰 News & Stories (最新のグローバルニュース)", "search_holder": "🔍 情報を検索...", "notice": "📢 お知らせ", "auth": "👤 ログイン/会員登録",
        "ai_btn": "🤖 AI要約を見る", "ai_modal_title": "⚡ 生成AIリアルタイムブリーフィング",
        "stats_title": "📊 リアルタイム競技テレメトリ分析 (Telemetry Analytics)", "total_athletes": "総参加選手数", "racing_athletes": "現在レース中", "finished_athletes": "完走者数",
        "chart_country": "国別選手分布", "chart_category": "種目別参加比率", "toast_update": "📢 [ライブ同期] ゼッケン {bib} 番の 選手ステータスが {status} に更新されました！",
        "equip_main_title": "🎿 ISMF 公認 山岳スキー必須5大ギアガイド",
        "equip_sub": "山岳スキーレースでは、軽量化と安全性が勝敗を分けます。ISMF規定に基づく必須ギアの解説です。",
        "e1_t": "1. 超軽量山岳スキー板", "e1_d": "登高で素早く駆け上がるため非常に軽いです。男子は最低780g、女子は700gに制限され、カーボンファイバーで製造されます。",
        "e2_t": "2. テックビンディング", "e2_d": "登りではヒール가上がり歩行可能で、滑走時はヒールを固定します。ピンテック方式を採用し、重量はわずか100g前後です。",
        "e3_t": "3. クライミングスキン", "e3_d": "滑走面に貼り付けるモヘア素材의 専用スキンです。前方には滑りますが、後方には毛が立ち雪を掴むため、斜面を垂直に登れます。",
        "e4_t": "4. ウォークモード対応ブーツ", "e4_d": "レバー一つで足首の可動域を60度以上確保する「ウォークモード」と、滑走用に固定する「スキーモード」を切り替えられる軽量カーボンブーツです。",
        "e5_t": "5. カーボンレーシングポール", "e5_d": "上半身の推進力を得るための道具です。通常のアルペンポールより長めで、100%高弾性カーボン製のため非常に軽く頑丈です。",
        "change_pw_btn": "🔒 パスワード変更",
        "forgot_pw_btn": "🔑 パスワード再設定"
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
        with st.form("login_form", clear_on_submit=False):
            login_id = st.text_input("아이디", key="login_id").strip()
            login_pw = st.text_input("비밀번호", type="password", key="login_pw").strip()
            login_submitted = st.form_submit_button("로그인 완료", use_container_width=True)

        if login_submitted:
            current_db = load_user_db()
            if login_id in current_db and current_db[login_id]["pw"] == login_pw:
                if current_db[login_id].get("status", "ACTIVE") == "SUSPENDED":
                    st.error("🚫 이 계정은 관리자에 의해 정지된 상태입니다. 관리자에게 문의해주세요.")
                else:
                    st.session_state.logged_in_user = login_id
                    st.session_state.force_pw_change = is_password_expired(current_db[login_id])
                    st.success(f"🎉 반갑습니다, {login_id}님! 로그인 성공.")
                    time.sleep(0.5)
                    st.rerun()
            else:
                st.error("❌ 아이디 또는 비밀번호가 일치하지 않습니다.")
    with tab2:
        with st.form("signup_form", clear_on_submit=False):
            reg_id = st.text_input("새로운 아이디 생성", key="reg_id").strip()
            reg_pw = st.text_input("새로운 비밀번호 설정", type="password", key="reg_pw").strip()
            reg_pw_confirm = st.text_input("비밀번호 확인", type="password", key="reg_pw_confirm").strip()
            st.caption(PASSWORD_POLICY_HINT)
            st.write("---")
            reg_email = st.text_input("이메일 (비밀번호 재설정용, 필수)", key="reg_email").strip()
            reg_phone = st.text_input("휴대폰 번호 (선택, 예: 010-1234-5678)", key="reg_phone").strip()
            st.caption("📧 이메일은 비밀번호를 잊었을 때 본인 인증(인증번호 발송)을 위해 사용됩니다.")
            signup_submitted = st.form_submit_button("회원가입 신청", use_container_width=True)

        if signup_submitted:
            current_db = load_user_db()
            EMAIL_REGEX = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
            if not reg_id or not reg_pw:
                st.warning("⚠️ 아이디와 비밀번호를 모두 입력해주세요.")
            elif reg_id in current_db:
                st.error("❌ 이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요.")
            elif reg_pw != reg_pw_confirm:
                st.error("❌ 비밀번호 확인이 일치하지 않습니다.")
            elif not reg_email:
                st.warning("⚠️ 비밀번호 재설정을 위해 이메일은 필수로 입력해주세요.")
            elif not re.match(EMAIL_REGEX, reg_email):
                st.error("❌ 올바른 이메일 형식이 아닙니다. (예: name@example.com)")
            else:
                is_valid, policy_msg = validate_password_policy(reg_pw)
                if not is_valid:
                    st.error(f"❌ {policy_msg}")
                else:
                    now_iso = datetime.now().isoformat(timespec="seconds")
                    current_db[reg_id] = {
                        "pw": reg_pw,
                        "role": "USER",
                        "status": "ACTIVE",
                        "pw_last_changed": now_iso,
                        "pw_history": [{"timestamp": now_iso, "changed_by": "본인(회원가입)"}],
                        "email": reg_email,
                        "phone": reg_phone if reg_phone else None
                    }
                    save_user_db(current_db)
                    st.session_state.user_db = current_db
                    st.success("🚀 회원가입 성공! 이제 로그인 탭에서 로그인해 주세요.")

# ==========================================
# [신규 추가] 비밀번호 변경 모달
# ==========================================
@st.dialog("🔒 비밀번호 변경")
def change_password_dialog():
    current_user = st.session_state.logged_in_user
    st.write(f"현재 로그인 계정: **{current_user}**")
    st.write("---")

    tab_pw, tab_contact = st.tabs(["🔒 비밀번호 변경", "📧 연락처 정보"])

    with tab_pw:
        with st.form("change_pw_form", clear_on_submit=False):
            cur_pw = st.text_input("현재 비밀번호", type="password", key="pw_change_current").strip()
            new_pw = st.text_input("새 비밀번호", type="password", key="pw_change_new").strip()
            new_pw_confirm = st.text_input("새 비밀번호 확인", type="password", key="pw_change_confirm").strip()
            st.caption(PASSWORD_POLICY_HINT)
            pw_submitted = st.form_submit_button("💾 비밀번호 변경하기", use_container_width=True)

        if pw_submitted:
            current_db = load_user_db()

            if current_user not in current_db:
                st.error("❌ 계정 정보를 찾을 수 없습니다. 다시 로그인해주세요.")
            elif current_db[current_user]["pw"] != cur_pw:
                st.error("❌ 현재 비밀번호가 일치하지 않습니다.")
            elif not new_pw:
                st.warning("⚠️ 새 비밀번호를 입력해주세요.")
            elif new_pw == cur_pw:
                st.warning("⚠️ 새 비밀번호는 현재 비밀번호와 달라야 합니다.")
            elif new_pw != new_pw_confirm:
                st.error("❌ 새 비밀번호 확인이 일치하지 않습니다.")
            else:
                is_valid, policy_msg = validate_password_policy(new_pw)
                if not is_valid:
                    st.error(f"❌ {policy_msg}")
                else:
                    current_db[current_user]["pw"] = new_pw
                    log_password_change(current_db, current_user, "본인")
                    save_user_db(current_db)
                    st.session_state.user_db = current_db
                    st.session_state.force_pw_change = False
                    st.success("✅ 비밀번호가 성공적으로 변경되었습니다! 잠시 후 창이 닫힙니다.")
                    time.sleep(1.2)
                    st.rerun()

    with tab_contact:
        st.caption("여기서 등록한 이메일/휴대폰 번호는 '비밀번호 재설정(OTP 인증)' 기능에 사용됩니다.")
        contact_db = load_user_db()
        my_info = contact_db.get(current_user, {})
        my_email = my_info.get("email") or ""
        my_phone = my_info.get("phone") or ""

        with st.form("change_contact_form", clear_on_submit=False):
            new_email = st.text_input("이메일", value=my_email, key="my_contact_email").strip()
            new_phone = st.text_input("휴대폰 번호", value=my_phone, key="my_contact_phone").strip()
            contact_submitted = st.form_submit_button("💾 연락처 정보 저장", use_container_width=True)

        if contact_submitted:
            EMAIL_REGEX = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
            if new_email and not re.match(EMAIL_REGEX, new_email):
                st.error("❌ 올바른 이메일 형식이 아닙니다. (예: name@example.com)")
            else:
                fresh_db = load_user_db()
                fresh_db[current_user]["email"] = new_email if new_email else None
                fresh_db[current_user]["phone"] = new_phone if new_phone else None
                save_user_db(fresh_db)
                st.session_state.user_db = fresh_db
                st.success("✅ 연락처 정보가 저장되었습니다.")
                time.sleep(1)
                st.rerun()

# ==========================================
# [신규 추가] 이메일/SMS 본인 인증(OTP) 기반 비밀번호 재설정 모달
# 1단계: 아이디 입력 + 인증 채널 선택 → 인증번호 발송
# 2단계: 인증번호 확인
# 3단계: 인증 완료 후 새 비밀번호 설정
# ==========================================
def _reset_pw_flow_state():
    """비밀번호 재설정 플로우 상태를 처음으로 초기화합니다."""
    st.session_state.pw_reset_step = "id_input"
    st.session_state.pw_reset_target_id = ""
    st.session_state.pw_reset_otp_code = None
    st.session_state.pw_reset_otp_expiry = None
    st.session_state.pw_reset_channel = None
    st.session_state.pw_reset_verified = False
    st.session_state.pw_reset_send_result = None
    st.session_state.pw_reset_verified_message = None

@st.dialog("🔑 비밀번호 재설정")
def forgot_password_dialog():
    # 세션 상태 초기화 (최초 진입 시에만)
    if "pw_reset_step" not in st.session_state:
        _reset_pw_flow_state()

    step = st.session_state.pw_reset_step

    # -------------------------------------------------------------
    # STEP 1: 아이디 입력 + 인증 채널(이메일/SMS) 선택 후 인증번호 발송
    # -------------------------------------------------------------
    if step == "id_input":
        st.write("가입된 아이디를 입력하고 본인 인증을 진행해주세요.")
        st.caption("🔐 등록된 이메일 또는 휴대폰 번호로 인증번호(OTP)를 발송하여 본인 확인 후 비밀번호를 재설정합니다.")
        st.write("---")

        input_id = st.text_input("아이디", key="forgot_pw_id_input").strip()

        target_info = None
        channel_choice = None
        if input_id:
            db = load_user_db()
            target_info = db.get(input_id)
            if target_info is None:
                st.error("❌ 존재하지 않는 아이디입니다.")
            elif target_info.get("status", "ACTIVE") == "SUSPENDED":
                st.error("🚫 정지된 계정입니다. 관리자에게 문의해주세요.")
            else:
                has_email = bool(target_info.get("email"))
                has_phone = bool(target_info.get("phone"))
                if not has_email and not has_phone:
                    st.error("❌ 이 계정에는 등록된 이메일/휴대폰 번호가 없습니다. 관리자에게 문의해주세요.")
                else:
                    options = []
                    if has_email:
                        options.append(f"📧 이메일 ({mask_email(target_info['email'])})")
                    if has_phone:
                        options.append(f"📱 SMS ({mask_phone(target_info['phone'])})")
                    channel_choice = st.radio("인증 방법 선택", options, key="forgot_pw_channel_radio")

        can_send = bool(input_id and target_info and target_info.get("status", "ACTIVE") != "SUSPENDED" and channel_choice)

        if st.button("📨 인증번호 발송", use_container_width=True, disabled=not can_send):
            otp = generate_otp_code()
            st.session_state.pw_reset_target_id = input_id
            st.session_state.pw_reset_otp_code = otp
            st.session_state.pw_reset_otp_expiry = time.time() + OTP_EXPIRY_SECONDS

            if channel_choice.startswith("📧"):
                st.session_state.pw_reset_channel = "EMAIL"
                sent, msg = send_email_otp(target_info["email"], otp)
            else:
                st.session_state.pw_reset_channel = "SMS"
                sent, msg = send_sms_otp(target_info["phone"], otp)

            # 발송 결과는 여기서 바로 표시하지 않고 세션에 저장합니다.
            # (바로 다음 줄에서 화면을 전환(rerun)하기 때문에, 여기서 표시하면
            #  전환 직전 아주 짧은 순간만 보이고 사라져버립니다.)
            st.session_state.pw_reset_send_result = {"sent": sent, "msg": msg, "otp": otp}

            st.session_state.pw_reset_step = "otp_verify"
            st.rerun()

    # -------------------------------------------------------------
    # STEP 2: 인증번호 확인
    # -------------------------------------------------------------
    elif step == "otp_verify":
        channel_label = "이메일" if st.session_state.pw_reset_channel == "EMAIL" else "SMS"
        st.write(f"아이디 **{st.session_state.pw_reset_target_id}** 로 {channel_label} 인증번호를 발송했습니다.")

        # 발송/재발송 직후 저장해둔 결과를 여기서 지속적으로 표시합니다.
        # (STEP 1에서 바로 표시하면 화면 전환과 함께 순식간에 사라지는 문제가 있어
        #  결과를 세션에 저장해뒀다가 이 화면에서 계속 보여주는 방식으로 변경했습니다.)
        send_result = st.session_state.get("pw_reset_send_result")
        if send_result:
            if send_result["sent"]:
                st.success(f"✅ {send_result['msg']}")
            else:
                st.warning(f"⚠️ {send_result['msg']}")
                st.info(
                    f"🔧 [데모 모드] 실제 발송 채널이 설정되지 않아 인증번호를 화면에 표시합니다: "
                    f"**{send_result['otp']}**\n\n"
                    f"(실제 운영 환경에서는 이 안내가 표시되지 않고 이메일/SMS로만 전달됩니다. "
                    f"아래 '인증번호 6자리 입력'란에 이 번호를 그대로 입력해주세요.)"
                )

        remaining = int(st.session_state.pw_reset_otp_expiry - time.time())
        if remaining > 0:
            st.caption(f"⏱️ 인증번호 유효시간: 약 {remaining // 60}분 {remaining % 60}초 남음")
        else:
            st.error("⏰ 인증번호가 만료되었습니다. 재발송 버튼을 눌러 다시 받아주세요.")

        otp_input = st.text_input("인증번호 6자리 입력", key="forgot_pw_otp_input", max_chars=6).strip()

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ 인증번호 확인", use_container_width=True):
                if not st.session_state.pw_reset_otp_expiry or time.time() > st.session_state.pw_reset_otp_expiry:
                    st.error("⏰ 인증번호가 만료되었습니다. 다시 발송해주세요.")
                elif not otp_input:
                    st.warning("⚠️ 인증번호를 입력해주세요.")
                elif otp_input != st.session_state.pw_reset_otp_code:
                    st.error("❌ 인증번호가 일치하지 않습니다.")
                else:
                    st.session_state.pw_reset_verified = True
                    st.session_state.pw_reset_verified_message = "✅ 본인 인증이 완료되었습니다."
                    st.session_state.pw_reset_step = "set_new_pw"
                    st.rerun()
        with c2:
            if st.button("🔄 인증번호 재발송", use_container_width=True):
                db = load_user_db()
                target_info = db.get(st.session_state.pw_reset_target_id, {})
                otp = generate_otp_code()
                st.session_state.pw_reset_otp_code = otp
                st.session_state.pw_reset_otp_expiry = time.time() + OTP_EXPIRY_SECONDS

                if st.session_state.pw_reset_channel == "EMAIL":
                    sent, msg = send_email_otp(target_info.get("email", ""), otp)
                else:
                    sent, msg = send_sms_otp(target_info.get("phone", ""), otp)

                # 재발송 결과도 동일하게 세션에 저장 후 rerun 시 위쪽 안내 영역에서 표시됩니다.
                st.session_state.pw_reset_send_result = {"sent": sent, "msg": msg, "otp": otp}
                st.rerun()

        st.write("")
        if st.button("⬅️ 처음으로 돌아가기", key="forgot_pw_back_to_id"):
            _reset_pw_flow_state()
            st.rerun()

    # -------------------------------------------------------------
    # STEP 3: 본인 인증 완료 후 새 비밀번호 설정
    # -------------------------------------------------------------
    elif step == "set_new_pw":
        if not st.session_state.pw_reset_verified:
            st.error("❌ 본인 인증이 완료되지 않았습니다. 처음부터 다시 진행해주세요.")
            if st.button("⬅️ 처음으로 돌아가기"):
                _reset_pw_flow_state()
                st.rerun()
        else:
            st.success(f"✅ 본인 인증 완료 (아이디: **{st.session_state.pw_reset_target_id}**)")
            st.write("---")

            with st.form("forgot_pw_final_form", clear_on_submit=False):
                final_new_pw = st.text_input("새 비밀번호", type="password", key="forgot_pw_final_new").strip()
                final_new_pw_confirm = st.text_input("새 비밀번호 확인", type="password", key="forgot_pw_final_confirm").strip()
                st.caption(PASSWORD_POLICY_HINT)
                final_submitted = st.form_submit_button("💾 비밀번호 재설정 완료", use_container_width=True)

            if final_submitted:
                if not final_new_pw:
                    st.warning("⚠️ 새 비밀번호를 입력해주세요.")
                elif final_new_pw != final_new_pw_confirm:
                    st.error("❌ 새 비밀번호 확인이 일치하지 않습니다.")
                else:
                    is_valid, policy_msg = validate_password_policy(final_new_pw)
                    if not is_valid:
                        st.error(f"❌ {policy_msg}")
                    else:
                        db = load_user_db()
                        uid = st.session_state.pw_reset_target_id
                        if uid not in db:
                            st.error("❌ 계정 정보를 찾을 수 없습니다.")
                        else:
                            db[uid]["pw"] = final_new_pw
                            channel_label = "이메일" if st.session_state.pw_reset_channel == "EMAIL" else "SMS"
                            log_password_change(db, uid, f"본인({channel_label} 인증 재설정)")
                            save_user_db(db)
                            st.session_state.user_db = db
                            st.success(f"✅ [{uid}] 계정의 비밀번호가 재설정되었습니다! 이제 새 비밀번호로 로그인해주세요.")
                            _reset_pw_flow_state()
                            time.sleep(1.5)
                            st.rerun()

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
            # [수정] 비로그인 상태에서도 "로그인/회원가입" 버튼 옆에 "비밀번호 재설정" 버튼을 함께 표시
            b_auth, b_forgot = st.columns(2)
            with b_auth:
                if st.button(T["auth"]):
                    auth_dialog()
            with b_forgot:
                if st.button(T["forgot_pw_btn"]):
                    forgot_password_dialog()
        else:
            # 로그인 상태일 때 비밀번호 변경 버튼과 로그아웃 버튼을 함께 표시
            b_pw, b_logout = st.columns(2)
            with b_pw:
                if st.button(T["change_pw_btn"]):
                    change_password_dialog()
            with b_logout:
                if st.button(f"🔓 로그아웃 ({st.session_state.logged_in_user})"):
                    st.session_state.logged_in_user = None
                    st.rerun()

st.markdown('</div></div>', unsafe_allow_html=True)

# 메인 뷰포트 레이아웃
st.markdown(f'<div class="centered-wrapper"><div class="hero-section"><div class="hero-title">{T["title"]}</div><div class="hero-subtitle">🏔️ {T["subtitle"]}</div></div></div>', unsafe_allow_html=True)
st.markdown('<div class="content-box">', unsafe_allow_html=True)

# ==========================================
# [신규 추가] 비밀번호 만료 시 강제 변경 게이트
# 로그인 상태에서 비밀번호가 만료된 경우, 변경 전까지 다른 메뉴 접근을 차단합니다.
# ==========================================
if st.session_state.logged_in_user and st.session_state.get("force_pw_change", False):
    st.warning(f"🔔 보안 정책에 따라 비밀번호가 {PASSWORD_EXPIRY_DAYS}일 이상 경과하여 만료되었습니다. 계속 이용하시려면 먼저 비밀번호를 변경해주세요.")
    st.markdown("### 🔒 비밀번호 만료 - 변경 필수")

    force_cur_pw = st.text_input("현재 비밀번호", type="password", key="force_pw_current").strip()
    force_new_pw = st.text_input("새 비밀번호", type="password", key="force_pw_new").strip()
    force_new_pw_confirm = st.text_input("새 비밀번호 확인", type="password", key="force_pw_confirm").strip()
    st.caption(PASSWORD_POLICY_HINT)

    if st.button("💾 비밀번호 변경하고 계속하기", use_container_width=True, key="force_pw_submit_btn"):
        force_db = load_user_db()
        uid = st.session_state.logged_in_user
        if uid not in force_db:
            st.error("❌ 계정 정보를 찾을 수 없습니다. 다시 로그인해주세요.")
        elif force_db[uid]["pw"] != force_cur_pw:
            st.error("❌ 현재 비밀번호가 일치하지 않습니다.")
        elif not force_new_pw:
            st.warning("⚠️ 새 비밀번호를 입력해주세요.")
        elif force_new_pw == force_cur_pw:
            st.warning("⚠️ 새 비밀번호는 현재 비밀번호와 달라야 합니다.")
        elif force_new_pw != force_new_pw_confirm:
            st.error("❌ 새 비밀번호 확인이 일치하지 않습니다.")
        else:
            is_valid, policy_msg = validate_password_policy(force_new_pw)
            if not is_valid:
                st.error(f"❌ {policy_msg}")
            else:
                force_db[uid]["pw"] = force_new_pw
                log_password_change(force_db, uid, "본인(만료 강제 변경)")
                save_user_db(force_db)
                st.session_state.user_db = force_db
                st.session_state.force_pw_change = False
                st.success("✅ 비밀번호가 변경되었습니다. 계속 이용하실 수 있습니다.")
                time.sleep(1)
                st.rerun()

    st.stop()

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
# [🎿 필수 장비 가이드 - 정확한 장비 전용 고화질 사진 반영 완료]
# -------------------------------------------------------------------------
elif st.session_state.menu_idx == 3:
    st.markdown(f"## {T['equip_main_title']}")
    st.write(T['equip_sub'])
    st.write("---")
    
    row1_c1, row1_c2, row1_c3 = st.columns(3)
    row2_c1, row2_c2 = st.columns(2)
    
    with row1_c1:
        st.markdown(f"""
        <div class="equip-card">
            <div class="equip-title">{T['e1_t']}</div>
            <p style='font-size:14px; color:#cbd5e1;'>{T['e1_d']}</p>
        </div>
        """, unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1551698618-1dfe5d97d256?auto=format&fit=crop&w=600&q=80", caption="Skimo Lightweight Skis", use_container_width=True)
        
    with row1_c2:
        st.markdown(f"""
        <div class="equip-card">
            <div class="equip-title">{T['e2_t']}</div>
            <p style='font-size:14px; color:#cbd5e1;'>{T['e2_d']}</p>
        </div>
        """, unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1565992441121-4367c2967103?auto=format&fit=crop&w=600&q=80", caption="Tech Binding System", use_container_width=True)
        
    with row1_c3:
        st.markdown(f"""
        <div class="equip-card">
            <div class="equip-title">{T['e3_t']}</div>
            <p style='font-size:14px; color:#cbd5e1;'>{T['e3_d']}</p>
        </div>
        """, unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=600&q=80", caption="Climbing Skins Setup", use_container_width=True)

    with row2_c1:
        st.markdown(f"""
        <div class="equip-card">
            <div class="equip-title">{T['e4_t']}</div>
            <p style='font-size:14px; color:#cbd5e1;'>{T['e4_d']}</p>
        </div>
        """, unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1548777123-e216912df7d8?auto=format&fit=crop&w=600&q=80", caption="Walk-Mode Skimo Boots", use_container_width=True)

    with row2_c2:
        st.markdown(f"""
        <div class="equip-card">
            <div class="equip-title">{T['e5_t']}</div>
            <p style='font-size:14px; color:#cbd5e1;'>{T['e5_d']}</p>
        </div>
        """, unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1518098268026-4e43a1a009de?auto=format&fit=crop&w=600&q=80", caption="Carbon Racing Poles", use_container_width=True)

# -------------------------------------------------------------------------
# [🔐 심판 / 관리자 패널]
# -------------------------------------------------------------------------
elif st.session_state.menu_idx == 4:
    st.markdown(f"## {T['menu'][4]}")
    
    current_user = st.session_state.logged_in_user
    current_db = load_user_db()
    
    if not current_user or current_db.get(current_user, {}).get("role") not in ["ADMIN", "JUDGE"]:
        st.warning("⚠️ 이 메뉴는 심판(JUDGE) 및 관리자(ADMIN) 권한이 있는 계정만 접근할 수 있습니다.")
        st.info("테스트용 심판 계정: `skimo` / `skimo123`  |  관리자 계정: `admin` / `1234`로 상단에서 로그인하세요.")
    else:
        st.success(f"🔑 현장 심판/관리자 전용 제어판에 접속하셨습니다. (접속자: **{current_user}**)")

        if USING_PERSISTENT_DB:
            st.info("💾 회원 데이터 저장 방식: **영구 DB 연결됨** — 앱이 재시작/재배포되어도 회원 정보가 유지됩니다.")
        else:
            st.warning("⚠️ 회원 데이터 저장 방식: **로컬 파일 모드** — 배포 환경에 따라 앱 재시작 시 회원 정보가 유실될 수 있습니다. `secrets.toml`에 `[connections.skimo_db]`를 설정해 영구 DB를 연결하는 것을 권장합니다.")
            if DB_CONNECTION_ERROR_MSG:
                st.error(f"🔍 연결 실패 원인: `{DB_CONNECTION_ERROR_MSG}`")
                if st.button("🔄 DB 연결 다시 시도", key="retry_db_conn_btn"):
                    get_db_connection.clear()
                    st.rerun()

        st.markdown("---")
        
        target_bib = st.selectbox("선수 선택 (배번호)", list(st.session_state.athletes_domain.keys()))
        athlete_data = st.session_state.athletes_domain[target_bib]
        
        with st.form("judge_control_form"):
            c_j1, c_j2 = st.columns(2)
            with c_j1:
                new_status = st.selectbox("경기 상태 (Status)", ["RACING", "FINISHED", "DNF", "DSQ"], index=["RACING", "FINISHED", "DNF", "DSQ"].index(athlete_data["Status"]))
                new_cp1 = st.text_input("체크포인트 1 (CP1)", value=athlete_data["CP1"])
                new_cp2 = st.text_input("체크포인트 2 (CP2)", value=athlete_data["CP2"])
            with c_j2:
                new_penalty = st.number_input("추가 페널티(초)", value=int(athlete_data["Penalty_Sec"]), min_value=0, step=5)
                new_final = st.text_input("최종 기록 (Final Record)", value=athlete_data["Final_Record"])
                
            if st.form_submit_button("💾 기록 반영 및 전 세계 실시간 동기화"):
                st.session_state.athletes_domain[target_bib].update({
                    "Status": new_status,
                    "CP1": new_cp1,
                    "CP2": new_cp2,
                    "Penalty_Sec": new_penalty,
                    "Final_Record": new_final
                })
                toast_msg = T["toast_update"].format(bib=target_bib, status=new_status)
                st.toast(toast_msg)
                st.success(f"✅ 배번호 [{target_bib}] {athlete_data['Name']} 선수의 기록이 업데이트되었습니다.")

        # -------------------------------------------------------------
        # [신규 추가] 관리자(ADMIN) 전용 - 사용자 비밀번호 초기화 패널
        # JUDGE 권한은 접근 불가, ADMIN 권한만 접근 가능
        # -------------------------------------------------------------
        if current_db.get(current_user, {}).get("role") == "ADMIN":
            st.markdown("---")
            st.markdown("### 🛡️ 관리자 전용 - 계정 비밀번호 초기화")
            st.caption("본인 계정이 아닌 다른 사용자의 비밀번호를 초기화하거나 직접 지정할 수 있습니다. (ADMIN 권한 전용)")

            with st.expander("👥 사용자 계정 비밀번호 관리 열기", expanded=False):
                admin_db = load_user_db()
                user_list = list(admin_db.keys())
                target_user_id = st.selectbox("대상 계정 선택 (아이디)", user_list, key="admin_target_user_select")
                st.write(f"선택된 계정 권한: **{admin_db.get(target_user_id, {}).get('role', '알수없음')}**")

                reset_mode = st.radio(
                    "초기화 방식 선택",
                    ["🎲 임시 비밀번호 자동 발급", "✍️ 새 비밀번호 직접 지정"],
                    horizontal=True,
                    key="admin_reset_mode"
                )

                if reset_mode == "🎲 임시 비밀번호 자동 발급":
                    st.caption("정책(8자 이상, 영문+숫자+특수문자)을 만족하는 임시 비밀번호를 자동 생성합니다.")
                    if st.button("🔄 임시 비밀번호 발급하기", key="admin_temp_reset_btn"):
                        admin_db_fresh = load_user_db()
                        if target_user_id not in admin_db_fresh:
                            st.error("❌ 대상 계정을 찾을 수 없습니다.")
                        else:
                            temp_pw = generate_temp_password()
                            admin_db_fresh[target_user_id]["pw"] = temp_pw
                            log_password_change(admin_db_fresh, target_user_id, f"관리자({current_user})")
                            save_user_db(admin_db_fresh)
                            st.session_state.user_db = admin_db_fresh
                            st.success(f"✅ [{target_user_id}] 계정의 비밀번호가 초기화되었습니다.")
                            st.code(temp_pw, language=None)
                            st.warning("⚠️ 이 임시 비밀번호를 해당 사용자에게 안전한 채널로 전달하고, 로그인 후 즉시 변경하도록 안내하세요. 이 화면을 벗어나면 다시 확인할 수 없습니다.")
                else:
                    with st.form("admin_direct_reset_form", clear_on_submit=False):
                        admin_new_pw = st.text_input("새 비밀번호 지정", type="password", key="admin_new_pw_input").strip()
                        admin_new_pw_confirm = st.text_input("새 비밀번호 확인", type="password", key="admin_new_pw_confirm_input").strip()
                        st.caption(PASSWORD_POLICY_HINT)
                        admin_direct_submitted = st.form_submit_button("💾 비밀번호 직접 변경하기")

                    if admin_direct_submitted:
                        admin_db_fresh = load_user_db()
                        if target_user_id not in admin_db_fresh:
                            st.error("❌ 대상 계정을 찾을 수 없습니다.")
                        elif not admin_new_pw:
                            st.warning("⚠️ 새 비밀번호를 입력해주세요.")
                        elif admin_new_pw != admin_new_pw_confirm:
                            st.error("❌ 비밀번호 확인이 일치하지 않습니다.")
                        else:
                            is_valid, policy_msg = validate_password_policy(admin_new_pw)
                            if not is_valid:
                                st.error(f"❌ {policy_msg}")
                            else:
                                admin_db_fresh[target_user_id]["pw"] = admin_new_pw
                                log_password_change(admin_db_fresh, target_user_id, f"관리자({current_user})")
                                save_user_db(admin_db_fresh)
                                st.session_state.user_db = admin_db_fresh
                                st.success(f"✅ [{target_user_id}] 계정의 비밀번호가 변경되었습니다.")

            # -------------------------------------------------------------
            # [신규 추가] 관리자 전용 - 계정 상태 관리 (정지/정지해제/삭제)
            # -------------------------------------------------------------
            st.markdown("---")
            st.markdown("### 🚫 관리자 전용 - 계정 상태 관리 (정지 / 삭제)")
            st.caption("문제가 있는 계정을 정지시키거나 영구 삭제할 수 있습니다. 본인 계정은 이 패널에서 정지/삭제할 수 없습니다.")

            with st.expander("🗂️ 계정 상태 관리 열기", expanded=False):
                admin_db_status = load_user_db()
                status_user_list = list(admin_db_status.keys())
                status_target_id = st.selectbox("대상 계정 선택 (아이디)", status_user_list, key="admin_status_target_select")
                target_info = admin_db_status.get(status_target_id, {})

                st.write(f"권한: **{target_info.get('role', '알수없음')}**")
                current_email = target_info.get("email") or ""
                current_phone = target_info.get("phone") or ""
                st.write(f"등록된 이메일: **{current_email if current_email else '없음 (본인 인증 재설정 불가)'}**")
                st.write(f"등록된 휴대폰: **{current_phone if current_phone else '없음'}**")

                # ---- 이메일/휴대폰 등록·수정 (본인 인증 재설정에 사용됨) ----
                with st.expander("✏️ 이메일 / 휴대폰 번호 등록·수정", expanded=(not current_email)):
                    st.caption("여기서 등록한 이메일/휴대폰 번호는 '비밀번호 재설정(OTP 인증)' 기능에 사용됩니다.")
                    with st.form(f"admin_contact_form_{status_target_id}", clear_on_submit=False):
                        new_email_input = st.text_input("이메일", value=current_email, key=f"admin_edit_email_{status_target_id}").strip()
                        new_phone_input = st.text_input("휴대폰 번호", value=current_phone, key=f"admin_edit_phone_{status_target_id}").strip()
                        admin_contact_submitted = st.form_submit_button("💾 연락처 정보 저장")

                    if admin_contact_submitted:
                        EMAIL_REGEX = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
                        if new_email_input and not re.match(EMAIL_REGEX, new_email_input):
                            st.error("❌ 올바른 이메일 형식이 아닙니다. (예: name@example.com)")
                        else:
                            fresh_db = load_user_db()
                            fresh_db[status_target_id]["email"] = new_email_input if new_email_input else None
                            fresh_db[status_target_id]["phone"] = new_phone_input if new_phone_input else None
                            save_user_db(fresh_db)
                            st.session_state.user_db = fresh_db
                            st.success(f"✅ [{status_target_id}] 계정의 연락처 정보가 저장되었습니다.")
                            st.rerun()

                st.write("---")

                if status_target_id == current_user:
                    st.info("ℹ️ 본인 계정은 이 패널에서 정지하거나 삭제할 수 없습니다. 다른 관리자에게 요청해주세요.")
                else:
                    current_status = target_info.get("status", "ACTIVE")
                    status_label = "🟢 활성 (ACTIVE)" if current_status == "ACTIVE" else "🔴 정지 (SUSPENDED)"
                    st.write(f"현재 상태: **{status_label}**")
                    st.write(f"마지막 비밀번호 변경: **{target_info.get('pw_last_changed', '기록 없음')}**")

                    # 비밀번호 변경 이력 표시
                    history = target_info.get("pw_history", [])
                    if history:
                        with st.popover("🕒 비밀번호 변경 이력 보기"):
                            st.caption(f"최근 {min(len(history), 10)}건 표시")
                            for h in reversed(history[-10:]):
                                st.write(f"- `{h.get('timestamp', '알수없음')}` · 변경자: **{h.get('changed_by', '알수없음')}**")

                    c_status1, c_status2 = st.columns(2)
                    with c_status1:
                        toggle_label = "🔴 계정 정지하기" if current_status == "ACTIVE" else "🟢 계정 정지 해제하기"
                        if st.button(toggle_label, key="admin_toggle_status_btn", use_container_width=True):
                            fresh_db = load_user_db()
                            fresh_db[status_target_id]["status"] = "SUSPENDED" if current_status == "ACTIVE" else "ACTIVE"
                            save_user_db(fresh_db)
                            st.session_state.user_db = fresh_db
                            st.success(f"✅ [{status_target_id}] 계정 상태가 변경되었습니다.")
                            st.rerun()
                    with c_status2:
                        confirm_delete = st.checkbox("삭제를 확인합니다 (되돌릴 수 없음)", key="admin_delete_confirm_checkbox")
                        if st.button("🗑️ 계정 영구 삭제", key="admin_delete_account_btn", use_container_width=True, disabled=not confirm_delete):
                            fresh_db = load_user_db()
                            if status_target_id in fresh_db:
                                del fresh_db[status_target_id]
                                save_user_db(fresh_db)
                                st.session_state.user_db = fresh_db
                                st.success(f"✅ [{status_target_id}] 계정이 영구 삭제되었습니다.")
                                st.rerun()

# -------------------------------------------------------------------------
# [📢 글로벌 공지사항 - notice_data.json 자동 로드]
# -------------------------------------------------------------------------
elif st.session_state.menu_idx == 5:
    st.markdown(f"## {T['menu'][5]}")
    st.markdown("---")
    
    # notice_data.json 파일 읽기
    try:
        with open("notice_data.json", "r", encoding="utf-8") as f:
            notices = json.load(f)
    except FileNotFoundError:
        notices = st.session_state.notice_domain

    lang_code = st.session_state.current_lang_code
    for notice in notices:
        n_title = notice["title"].get(lang_code, notice["title"]["EN"])
        n_content = notice["content"].get(lang_code, notice["content"]["EN"])
        
        st.markdown(f"""
        <div class="notice-card">
            <span class="notice-badge">{notice['category']}</span>
            <span style="font-size:13px; color:#cbd5e1;">📅 {notice['date']}</span>
            <h3 style="margin-top:10px; margin-bottom:10px; color:#00c6ff;">{n_title}</h3>
            <p style="font-size:15px; color:#e2e8f0; line-height:1.6;">{n_content}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
