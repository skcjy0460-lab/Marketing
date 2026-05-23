"""
병원 블로그·키워드 광고 분석 시스템
Hospital Blog & Keyword Ad Analysis System
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime
from collections import Counter
import io
import hashlib

# ── 페이지 설정 ────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediBlog AI 분석 시스템",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS 스타일 ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Space+Mono:wght@400;700&display=swap');

:root {
    --primary: #0A5C7F;
    --accent:  #00C6AE;
    --warn:    #FF6B6B;
    --gold:    #F4C542;
    --bg:      #F0F4F8;
    --card:    #FFFFFF;
    --text:    #1A2B3C;
    --muted:   #6B8CAE;
}

html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; color: var(--text); }

/* 헤더 배너 */
.hero-banner {
    background: linear-gradient(135deg, #0A5C7F 0%, #0D7A9E 50%, #00C6AE 100%);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    color: white;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '🏥';
    position: absolute;
    right: 2rem; top: 50%;
    transform: translateY(-50%);
    font-size: 5rem;
    opacity: .15;
}
.hero-banner h1 { font-size: 2rem; font-weight: 900; margin: 0 0 .4rem; }
.hero-banner p  { font-size: 1rem; opacity: .85; margin: 0; }

/* 등급 배지 */
.badge {
    display: inline-block;
    padding: .25rem .75rem;
    border-radius: 20px;
    font-size: .75rem;
    font-weight: 700;
    letter-spacing: .04em;
}
.badge-gold   { background:#FFF3CD; color:#856404; border:1px solid #F4C542; }
.badge-silver { background:#E2E8F0; color:#475569; border:1px solid #CBD5E1; }
.badge-blue   { background:#DBEAFE; color:#1E40AF; border:1px solid #93C5FD; }
.badge-green  { background:#D1FAE5; color:#065F46; border:1px solid #6EE7B7; }
.badge-red    { background:#FEE2E2; color:#991B1B; border:1px solid #FCA5A5; }

/* 점수 카드 */
.score-card {
    background: var(--card);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(10,92,127,.10);
    border-top: 4px solid var(--primary);
}
.score-card .score-val  { font-size: 2.5rem; font-weight: 900; color: var(--primary); font-family:'Space Mono',monospace; }
.score-card .score-label{ font-size: .78rem; color: var(--muted); margin-top: .3rem; }

/* 섹션 타이틀 */
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--primary);
    border-left: 4px solid var(--accent);
    padding-left: .75rem;
    margin: 1.5rem 0 1rem;
}

/* 프리미엄 잠금 박스 */
.lock-box {
    background: linear-gradient(135deg,#0A5C7F,#00C6AE);
    border-radius: 16px;
    padding: 3rem 2rem;
    text-align: center;
    color: white;
}
.lock-box h3 { font-size:1.4rem; font-weight:800; margin:.5rem 0; }
.lock-box p  { opacity:.85; font-size:.95rem; }

/* 사이드바 */
[data-testid="stSidebar"] {
    background: #F0F6FA;
    border-right: 2px solid #D0E8F5;
}

/* 사이드바 일반 텍스트 */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p {
    color: #1A2B3C !important;
}

/* 사이드바 입력 필드 라벨 */
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stCheckbox label {
    color: #0A5C7F !important;
    font-weight: 600 !important;
    font-size: .85rem !important;
}

/* 사이드바 입력창 텍스트 */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] select {
    color: #1A2B3C !important;
    background: #FFFFFF !important;
    border: 1px solid #B0CEDE !important;
}

/* 사이드바 구분선 */
[data-testid="stSidebar"] hr {
    border-color: #C0D8E8 !important;
}

/* 사이드바 코드블록 */
[data-testid="stSidebar"] code,
[data-testid="stSidebar"] pre {
    background: #E2EEF5 !important;
    color: #1A2B3C !important;
    font-size: .78rem !important;
}

/* 사이드바 버튼 */
[data-testid="stSidebar"] .stButton > button {
    background: #0A5C7F !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #0D7A9E !important;
}

/* 사이드바 타이틀 강조 */
[data-testid="stSidebar"] strong {
    color: #0A5C7F !important;
    font-weight: 700 !important;
}

/* 정보 칩 */
.info-chip {
    display: inline-flex; align-items: center; gap:.35rem;
    background:#EBF4FF; border:1px solid #BFD9F0;
    border-radius:20px; padding:.3rem .8rem;
    font-size:.8rem; color:#1E5799; margin:.2rem;
}

/* 알림 박스 */
.alert-box {
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: .8rem 0;
    font-size: .88rem;
}
.alert-info  { background:#EBF8FF; border-left:4px solid #63B3ED; color:#2B6CB0; }
.alert-warn  { background:#FFFBEB; border-left:4px solid #F6E05E; color:#744210; }
.alert-good  { background:#F0FFF4; border-left:4px solid #68D391; color:#22543D; }
.alert-bad   { background:#FFF5F5; border-left:4px solid #FC8181; color:#822727; }

/* 비교 테이블 */
.compare-table { width:100%; border-collapse:collapse; font-size:.88rem; }
.compare-table th { background:#0A5C7F; color:white; padding:.6rem .9rem; }
.compare-table td { padding:.55rem .9rem; border-bottom:1px solid #E2E8F0; }
.compare-table tr:hover td { background:#F7FAFC; }

/* 프로그레스 바 */
.prog-bar-wrap { background:#E2E8F0; border-radius:99px; height:10px; overflow:hidden; margin:.3rem 0; }
.prog-bar      { height:100%; border-radius:99px; transition:width .6s ease; }

/* 숨김 */
.stDeployButton { display: none; }
footer { display: none; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  유틸 함수
# ══════════════════════════════════════════════════════════════════

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

DEMO_USERS = {
    "demo@hospital.com": {"pw": hash_password("demo1234"), "plan": "free",    "name": "데모 사용자"},
    "pro@hospital.com":  {"pw": hash_password("pro12345"), "plan": "premium", "name": "프리미엄 원장님"},
}

def login_user(email, pw):
    if email in DEMO_USERS and DEMO_USERS[email]["pw"] == hash_password(pw):
        return DEMO_USERS[email]
    return None

def is_premium() -> bool:
    return st.session_state.get("plan") == "premium"

def score_color(s):
    if s >= 80: return "#00C6AE"
    if s >= 60: return "#F4C542"
    if s >= 40: return "#FF9F43"
    return "#FF6B6B"

def grade_label(s):
    if s >= 85: return ("S", "badge-gold")
    if s >= 70: return ("A", "badge-blue")
    if s >= 55: return ("B", "badge-green")
    if s >= 40: return ("C", "badge-silver")
    return ("D", "badge-red")

def prog_bar(val, color="#0A5C7F"):
    return f"""
    <div class="prog-bar-wrap">
        <div class="prog-bar" style="width:{min(val,100)}%;background:{color};"></div>
    </div>"""

# ── 블로그 URL 크롤러 ──────────────────────────────────────────────
def crawl_blog(url: str) -> dict:
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    result = {
        "url": url, "title": "", "content": "", "images": 0,
        "word_count": 0, "links": 0, "tags": [], "error": None,
        "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 네이버 블로그 iframe 처리
        if "blog.naver.com" in url:
            # 포스트 ID 추출
            m = re.search(r"blog\.naver\.com/([^/]+)/(\d+)", url)
            if m:
                blog_id, post_no = m.group(1), m.group(2)
                frame_url = f"https://blog.naver.com/PostView.nhn?blogId={blog_id}&logNo={post_no}"
                resp2 = requests.get(frame_url, headers=headers, timeout=12)
                soup = BeautifulSoup(resp2.text, "html.parser")

        title_tag = soup.find("title") or soup.find("h3")
        result["title"] = title_tag.get_text(strip=True)[:120] if title_tag else "제목 없음"

        # 본문 텍스트
        for tag in soup(["script","style","header","footer","nav"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        result["content"] = text[:5000]
        result["word_count"] = len(text.replace(" ",""))
        result["images"] = len(soup.find_all("img"))
        result["links"]  = len(soup.find_all("a"))

        # 해시태그
        tags = re.findall(r"#([가-힣a-zA-Z0-9]+)", text)
        result["tags"] = tags[:20]

    except Exception as e:
        result["error"] = str(e)
    return result

# ── 점수 계산 엔진 ─────────────────────────────────────────────────
def calc_scores(data: dict) -> dict:
    wc  = data.get("word_count", 0)
    img = data.get("images", 0)
    lnk = data.get("links", 0)
    tags= len(data.get("tags", []))

    # 콘텐츠 풍부도 (글자수 기준)
    content_score = min(100, int(wc / 20))          # 2000자 = 100점

    # 이미지 활용도
    img_score = min(100, img * 12)                  # 8장 = 100점

    # 내부링크 / 태그 활용
    link_score = min(100, lnk * 8 + tags * 5)

    # 전체 블로그지수 (가중평균)
    total = int(content_score * 0.45 + img_score * 0.35 + link_score * 0.20)

    return {
        "total":   total,
        "content": content_score,
        "image":   img_score,
        "link":    link_score,
    }

# ── 키워드 분석 ────────────────────────────────────────────────────
def analyze_keywords(text: str, top_n=20) -> pd.DataFrame:
    stop = set("이 그 저 것 수 등 및 에 을 를 이 가 은 는 의 도 에서 로 으로 와 과 하다 있다 없다 되다 하는 그리고 또한 하지만 그러나 때문 위해 통해 대한 관련 우리 제가 제 저는 저도 했다 합니다 있습니다 없습니다 됩니다 드립니다 드려요 했어요".split())
    words = re.findall(r"[가-힣]{2,}", text)
    filtered = [w for w in words if w not in stop]
    freq = Counter(filtered).most_common(top_n)
    df = pd.DataFrame(freq, columns=["키워드","빈도"])
    df["비율(%)"] = (df["빈도"] / max(df["빈도"].sum(),1) * 100).round(1)
    return df

# ── 감성 분석 (규칙 기반, 무료) ────────────────────────────────────
POS_WORDS = "좋다 훌륭 최고 완벽 추천 만족 친절 빠르다 정확 깔끔 전문 감사 행복 괜찮 도움 효과 개선 치료 쾌적 상세".split()
NEG_WORDS = "나쁘다 최악 불만 불친절 느리다 오래 불편 아쉽 실망 비싸다 부족 문제 힘들 어렵 고통 부작용 불안 걱정 거부".split()

def rule_sentiment(text: str) -> dict:
    pos = sum(text.count(w) for w in POS_WORDS)
    neg = sum(text.count(w) for w in NEG_WORDS)
    total = pos + neg or 1
    score = int(pos / total * 100)
    label = "긍정" if score >= 60 else ("중립" if score >= 40 else "부정")
    return {"pos": pos, "neg": neg, "score": score, "label": label}

# ── Claude API 호출 ────────────────────────────────────────────────
def call_claude(prompt: str, api_key: str, max_tokens=2000) -> str:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": "claude-opus-4-5",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", json=body, headers=headers, timeout=60)
        r.raise_for_status()
        return r.json()["content"][0]["text"]
    except requests.exceptions.HTTPError as e:
        if r.status_code == 401:
            return "❌ API 키가 유효하지 않습니다. 설정을 확인해주세요."
        return f"❌ API 오류: {e}"
    except Exception as e:
        return f"❌ 오류: {e}"

def ai_deep_analysis(data_list: list, api_key: str) -> str:
    summaries = []
    for d in data_list[:5]:
        sc = calc_scores(d)
        sent = rule_sentiment(d.get("content",""))
        summaries.append(
            f"- 제목: {d['title'][:60]}\n"
            f"  글자수:{d['word_count']} 이미지:{d['images']} 태그:{len(d['tags'])}개\n"
            f"  블로그지수:{sc['total']} 감성:{sent['label']}({sent['score']}점)"
        )

    prompt = f"""당신은 병원 마케팅 전문 컨설턴트입니다.
아래는 병원 네이버 블로그 포스팅 분석 데이터입니다.

{chr(10).join(summaries)}

다음 항목을 한국어로 상세히 분석해주세요:
1. 전체 블로그 마케팅 현황 종합 평가 (강점/약점)
2. 검색 노출(SEO) 개선을 위한 구체적 실행 방안 3가지
3. 콘텐츠 품질 향상 전략 (의료기관 특성 반영)
4. 경쟁 병원 대비 차별화 포인트 제안
5. 월간 블로그 운영 로드맵 (4주 계획)

응답은 마크다운 형식으로 명확하게 작성해주세요.
"""
    return call_claude(prompt, api_key, max_tokens=2500)

def ai_keyword_strategy(keywords: list, specialty: str, api_key: str) -> str:
    kw_str = ", ".join([k for k,_ in keywords[:15]])
    prompt = f"""병원 마케팅 전문가로서 아래 정보를 바탕으로 키워드 광고 전략을 수립해주세요.

진료과목: {specialty}
현재 주요 키워드: {kw_str}

1. 현재 키워드의 강도 평가 (고/중/저 경쟁 분류)
2. 추천 추가 키워드 10개 (롱테일 포함)
3. 네이버 키워드 광고 입찰 전략
4. 시즌별 키워드 운영 전략 (계절성 고려)
5. 블로그 vs 키워드광고 예산 배분 추천

한국어로 실용적으로 작성해주세요.
"""
    return call_claude(prompt, api_key, max_tokens=2000)


# ══════════════════════════════════════════════════════════════════
#  사이드바 – 로그인 / 설정
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🏥 MediBlog AI")
    st.markdown("---")

    # ── 로그인 상태 ──────────────────────────────────────────────
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.markdown("**로그인**")
        email = st.text_input("이메일", placeholder="demo@hospital.com")
        pw    = st.text_input("비밀번호", type="password", placeholder="demo1234")
        if st.button("로그인", use_container_width=True):
            user = login_user(email, pw)
            if user:
                st.session_state.logged_in = True
                st.session_state.plan = user["plan"]
                st.session_state.user_name = user["name"]
                st.success(f"환영합니다, {user['name']}님!")
                st.rerun()
            else:
                st.error("이메일 또는 비밀번호가 틀렸습니다.")
        st.markdown("---")
        st.markdown("**테스트 계정**")
        st.code("무료: demo@hospital.com\n비밀번호: demo1234\n\n유료: pro@hospital.com\n비밀번호: pro12345")
    else:
        plan_badge = "⭐ 프리미엄" if is_premium() else "🆓 무료"
        st.markdown(f"**{st.session_state.user_name}** {plan_badge}")
        if st.button("로그아웃", use_container_width=True):
            for k in ["logged_in","plan","user_name"]:
                st.session_state.pop(k, None)
            st.rerun()

        if not is_premium():
            st.markdown("---")
            st.markdown("### 💎 프리미엄 업그레이드")
            st.markdown("AI 심층 분석, 경쟁사 비교, 전문 보고서를 이용하세요.")
            if st.button("업그레이드 (₩49,000/월)", use_container_width=True):
                st.info("결제 페이지 연동 필요 (Toss/카카오페이)")

    st.markdown("---")

    # ── Claude API 키 ────────────────────────────────────────────
    st.markdown("**🤖 Claude API 키** *(프리미엄 기능)*")
    api_key = st.text_input("API Key", type="password",
                            placeholder="sk-ant-...",
                            help="Anthropic Console에서 발급",
                            disabled=not is_premium())
    st.session_state["api_key"] = api_key

    st.markdown("---")
    st.markdown("**병원 정보**")
    specialty = st.selectbox("진료과목",
        ["내과","피부과","성형외과","치과","한의원","정형외과","안과","산부인과","소아과","비뇨기과","신경과","정신건강의학과","이비인후과","기타"])
    region = st.text_input("지역", placeholder="예: 강남구")
    st.session_state["specialty"] = specialty
    st.session_state["region"] = region


# ══════════════════════════════════════════════════════════════════
#  메인 헤더
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-banner">
  <h1>MediBlog AI 분석 시스템</h1>
  <p>병원 블로그 광고 효과 측정 · 키워드 전략 · AI 심층 보고서</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get("logged_in"):
    st.markdown("""
    <div class="alert-box alert-info">
        ℹ️ 로그인 후 이용 가능합니다. 왼쪽 사이드바에서 테스트 계정으로 로그인해보세요.
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════
#  탭 구성
# ══════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📊 블로그 분석",
    "📁 엑셀 일괄 분석",
    "🔍 키워드 분석",
    "📈 경쟁사 비교" + (" 🔒" if not is_premium() else ""),
    "🤖 AI 심층 보고서" + (" 🔒" if not is_premium() else ""),
])

tab_blog, tab_excel, tab_kw, tab_comp, tab_ai = tabs


# ──────────────────────────────────────────────────────────────────
#  TAB 1 : 블로그 분석
# ──────────────────────────────────────────────────────────────────
with tab_blog:
    st.markdown('<div class="section-title">블로그 URL 분석</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        urls_input = st.text_area(
            "네이버 블로그 URL 입력 (한 줄에 하나씩)",
            height=120,
            placeholder="https://blog.naver.com/your_hospital/123456789\nhttps://blog.naver.com/your_hospital/987654321"
        )
    with col2:
        st.markdown("#### 분석 옵션")
        show_keywords = st.checkbox("키워드 분석", value=True)
        show_sentiment= st.checkbox("감성 분석",   value=True)
        analyze_btn   = st.button("🔍 분석 시작", use_container_width=True, type="primary")

    if analyze_btn and urls_input.strip():
        urls = [u.strip() for u in urls_input.strip().split("\n") if u.strip()]
        results = []

        prog = st.progress(0, text="크롤링 중...")
        for i, url in enumerate(urls):
            prog.progress((i+1)/len(urls), text=f"분석 중... ({i+1}/{len(urls)})")
            data = crawl_blog(url)
            data["scores"] = calc_scores(data)
            if show_sentiment:
                data["sentiment"] = rule_sentiment(data.get("content",""))
            results.append(data)
            time.sleep(0.5)

        prog.empty()
        st.session_state["blog_results"] = results

    if "blog_results" in st.session_state:
        results = st.session_state["blog_results"]
        st.markdown(f"**총 {len(results)}개 포스팅 분석 완료**")
        st.markdown("---")

        for idx, d in enumerate(results):
            sc   = d.get("scores", {})
            sent = d.get("sentiment", {})
            g, gc= grade_label(sc.get("total",0))

            with st.expander(f"📄 {idx+1}. {d.get('title','제목 없음')[:60]}",
                             expanded=(idx==0)):
                if d.get("error"):
                    st.markdown(f'<div class="alert-box alert-bad">⚠️ 크롤링 오류: {d["error"]}</div>',
                                unsafe_allow_html=True)

                # 점수 카드
                c1,c2,c3,c4 = st.columns(4)
                with c1:
                    st.markdown(f"""<div class="score-card">
                        <div class="score-val" style="color:{score_color(sc.get('total',0))}">
                            {sc.get('total',0)}
                        </div>
                        <div class="score-label">블로그 지수<br>
                            <span class="badge {gc}">{g}등급</span>
                        </div></div>""", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""<div class="score-card">
                        <div class="score-val">{sc.get('content',0)}</div>
                        <div class="score-label">콘텐츠 점수</div></div>""", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""<div class="score-card">
                        <div class="score-val">{sc.get('image',0)}</div>
                        <div class="score-label">이미지 점수</div></div>""", unsafe_allow_html=True)
                with c4:
                    st.markdown(f"""<div class="score-card">
                        <div class="score-val">{sc.get('link',0)}</div>
                        <div class="score-label">링크/태그 점수</div></div>""", unsafe_allow_html=True)

                st.markdown("")

                # 세부 정보
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**📝 기본 정보**")
                    st.markdown(f"""
                    <div class="info-chip">✍️ 글자수 {d.get('word_count',0):,}</div>
                    <div class="info-chip">🖼️ 이미지 {d.get('images',0)}장</div>
                    <div class="info-chip">🔗 링크 {d.get('links',0)}개</div>
                    <div class="info-chip">🏷️ 태그 {len(d.get('tags',[]))}개</div>
                    <div class="info-chip">📅 {d.get('crawled_at','')}</div>
                    """, unsafe_allow_html=True)

                    # 점수 게이지
                    st.markdown("<br>**세부 점수 게이지**", unsafe_allow_html=True)
                    for label, key, color in [
                        ("콘텐츠", "content", "#0A5C7F"),
                        ("이미지", "image",   "#00C6AE"),
                        ("링크/태그","link",  "#F4C542"),
                    ]:
                        val = sc.get(key, 0)
                        st.markdown(f"<small>{label} {val}점</small>{prog_bar(val,color)}",
                                    unsafe_allow_html=True)

                with col_b:
                    if sent:
                        st.markdown("**😊 감성 분석**")
                        s_color = "#00C6AE" if sent['score']>=60 else ("#F4C542" if sent['score']>=40 else "#FF6B6B")
                        st.markdown(f"""
                        <div style="background:{s_color}18;border:1px solid {s_color};
                                    border-radius:10px;padding:1rem;text-align:center;">
                            <div style="font-size:2rem;font-weight:900;color:{s_color}">{sent['score']}점</div>
                            <div style="font-weight:700;">{sent['label']} 감성</div>
                            <div style="font-size:.8rem;opacity:.7;margin-top:.4rem;">
                                긍정 키워드 {sent['pos']}개 · 부정 키워드 {sent['neg']}개
                            </div>
                        </div>""", unsafe_allow_html=True)

                # 태그
                if d.get("tags"):
                    st.markdown("**🏷️ 해시태그**")
                    tag_html = " ".join([f'<span class="info-chip">#{t}</span>' for t in d["tags"][:15]])
                    st.markdown(tag_html, unsafe_allow_html=True)

                # 키워드
                if show_keywords and d.get("content"):
                    st.markdown("**🔑 주요 키워드**")
                    kw_df = analyze_keywords(d["content"])
                    if not kw_df.empty:
                        st.dataframe(kw_df.head(10), use_container_width=True, hide_index=True)

                # 개선 제안 (규칙 기반)
                tips = []
                if d.get("word_count",0) < 500:
                    tips.append(("⚠️ 글자수 부족", "검색 노출을 위해 최소 800자 이상 작성을 권장합니다.", "alert-warn"))
                if d.get("images",0) < 3:
                    tips.append(("📷 이미지 부족", "이미지 3장 이상 삽입 시 체류시간과 지수가 향상됩니다.", "alert-warn"))
                if len(d.get("tags",[])) < 5:
                    tips.append(("🏷️ 태그 부족", "해시태그 5~10개 활용으로 검색 유입을 늘리세요.", "alert-warn"))
                if sc.get("total",0) >= 80:
                    tips.append(("✅ 우수 포스팅", "블로그 지수 80점 이상! 상위 노출 가능성이 높습니다.", "alert-good"))

                if tips:
                    st.markdown("**💡 개선 제안**")
                    for title, msg, cls in tips:
                        st.markdown(f'<div class="alert-box {cls}"><b>{title}</b> {msg}</div>',
                                    unsafe_allow_html=True)

                st.markdown(f"🔗 [원본 포스팅 보기]({d.get('url','')})")


# ──────────────────────────────────────────────────────────────────
#  TAB 2 : 엑셀 일괄 분석
# ──────────────────────────────────────────────────────────────────
with tab_excel:
    st.markdown('<div class="section-title">엑셀 파일 일괄 분석</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-box alert-info">
        ℹ️ 엑셀 파일에 <b>url</b> 컬럼이 포함되어야 합니다. 선택 컬럼: title, category, date, memo
    </div>
    """, unsafe_allow_html=True)

    # 샘플 엑셀 다운로드
    sample_df = pd.DataFrame({
        "url": [
            "https://blog.naver.com/example/1001",
            "https://blog.naver.com/example/1002",
        ],
        "category": ["이벤트","진료안내"],
        "date": ["2024-01-10","2024-01-15"],
        "memo": ["신년 이벤트","진료시간 안내"],
    })
    buf = io.BytesIO()
    sample_df.to_excel(buf, index=False)
    st.download_button("📥 샘플 엑셀 다운로드", buf.getvalue(),
                       file_name="sample_blog_list.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    uploaded = st.file_uploader("엑셀 파일 업로드 (.xlsx)", type=["xlsx","xls","csv"])

    if uploaded:
        if uploaded.name.endswith(".csv"):
            df_up = pd.read_csv(uploaded)
        else:
            df_up = pd.read_excel(uploaded)

        st.markdown(f"**{len(df_up)}개 행 감지됨**")
        st.dataframe(df_up.head(), use_container_width=True)

        if "url" not in df_up.columns:
            st.error("'url' 컬럼이 없습니다. 엑셀 형식을 확인하세요.")
        else:
            max_rows = 20 if is_premium() else 5
            if len(df_up) > max_rows:
                st.warning(f"{'프리미엄' if is_premium() else '무료'} 플랜: 최대 {max_rows}개 분석 가능")
                df_up = df_up.head(max_rows)

            if st.button("📊 일괄 분석 시작", type="primary"):
                results_xl = []
                prog2 = st.progress(0)
                for i, row in df_up.iterrows():
                    prog2.progress((results_xl.__len__()+1)/len(df_up))
                    d = crawl_blog(row["url"])
                    d["category"] = row.get("category","")
                    d["memo"]     = row.get("memo","")
                    d["scores"]   = calc_scores(d)
                    d["sentiment"]= rule_sentiment(d.get("content",""))
                    results_xl.append(d)
                    time.sleep(0.4)
                prog2.empty()
                st.session_state["excel_results"] = results_xl

    if "excel_results" in st.session_state:
        res = st.session_state["excel_results"]
        st.markdown(f"### 📋 일괄 분석 결과 ({len(res)}개)")

        # 요약 테이블
        rows = []
        for d in res:
            sc = d.get("scores",{})
            se = d.get("sentiment",{})
            g, _ = grade_label(sc.get("total",0))
            rows.append({
                "제목": d.get("title","")[:40],
                "카테고리": d.get("category",""),
                "블로그지수": sc.get("total",0),
                "등급": g,
                "글자수": d.get("word_count",0),
                "이미지": d.get("images",0),
                "감성": se.get("label",""),
                "감성점수": se.get("score",0),
            })
        result_df = pd.DataFrame(rows)
        st.dataframe(result_df, use_container_width=True, hide_index=True)

        # 엑셀 다운로드
        out_buf = io.BytesIO()
        result_df.to_excel(out_buf, index=False)
        st.download_button("📥 결과 엑셀 다운로드", out_buf.getvalue(),
                           file_name=f"blog_analysis_{datetime.now().strftime('%Y%m%d')}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # 평균 차트
        st.markdown('<div class="section-title">카테고리별 평균 지수</div>', unsafe_allow_html=True)
        if "카테고리" in result_df.columns and result_df["카테고리"].notna().any():
            cat_avg = result_df.groupby("카테고리")["블로그지수"].mean().round(1)
            st.bar_chart(cat_avg)


# ──────────────────────────────────────────────────────────────────
#  TAB 3 : 키워드 분석
# ──────────────────────────────────────────────────────────────────
with tab_kw:
    st.markdown('<div class="section-title">키워드 광고 분석</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2,1])
    with col1:
        kw_text = st.text_area("분석할 텍스트 붙여넣기 (블로그 본문 / 광고 소재 등)",
                               height=180, placeholder="블로그 포스팅 본문을 복사해서 붙여넣으세요...")
    with col2:
        st.markdown("**타겟 키워드 설정**")
        target_kws = st.text_area("핵심 키워드 (한 줄에 하나)",
                                  height=100, placeholder="강남 피부과\n여드름 치료\n피부 관리")
        top_n = st.slider("상위 키워드 수", 10, 50, 20)

    if st.button("🔍 키워드 분석", type="primary") and kw_text:
        kw_df = analyze_keywords(kw_text, top_n)
        st.session_state["kw_df"] = kw_df
        st.session_state["kw_text"] = kw_text
        st.session_state["target_kws"] = [k.strip() for k in target_kws.split("\n") if k.strip()]

    if "kw_df" in st.session_state:
        kw_df = st.session_state["kw_df"]
        target_kws = st.session_state.get("target_kws",[])

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**📊 키워드 빈도표**")
            st.dataframe(kw_df, use_container_width=True, hide_index=True)

        with c2:
            st.markdown("**📈 상위 키워드 분포**")
            if not kw_df.empty:
                chart_df = kw_df.head(15).set_index("키워드")["빈도"]
                st.bar_chart(chart_df)

        # 타겟 키워드 포함 여부
        if target_kws:
            st.markdown('<div class="section-title">타겟 키워드 포함 여부</div>', unsafe_allow_html=True)
            kw_list = kw_df["키워드"].tolist()
            text = st.session_state.get("kw_text","")
            rows2 = []
            for kw in target_kws:
                cnt = text.count(kw)
                in_top = kw in kw_list
                density = round(cnt/max(len(text),1)*100, 3)
                rows2.append({"키워드": kw, "출현횟수": cnt, "키워드밀도(%)": density,
                               "상위20포함": "✅" if in_top else "❌",
                               "평가": "👍 적절" if 0.5<=density<=3 else ("⚠️ 과다" if density>3 else "📉 부족")})
            st.dataframe(pd.DataFrame(rows2), use_container_width=True, hide_index=True)

        # AI 키워드 전략 (프리미엄)
        if is_premium():
            st.markdown('<div class="section-title">🤖 AI 키워드 광고 전략</div>', unsafe_allow_html=True)
            api_key = st.session_state.get("api_key","")
            if api_key:
                if st.button("AI 키워드 전략 생성", type="primary"):
                    with st.spinner("AI가 키워드 전략을 수립하고 있습니다..."):
                        kw_pairs = list(zip(kw_df["키워드"].tolist(), kw_df["빈도"].tolist()))
                        result = ai_keyword_strategy(kw_pairs, st.session_state.get("specialty",""), api_key)
                    st.markdown(result)
            else:
                st.markdown('<div class="alert-box alert-warn">⚠️ 사이드바에서 Claude API 키를 입력하세요.</div>',
                            unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="lock-box" style="margin-top:1rem">
                <div style="font-size:2rem">🔒</div>
                <h3>AI 키워드 전략 — 프리미엄 전용</h3>
                <p>Claude AI가 경쟁 키워드 분석, 롱테일 키워드 추천,<br>광고 예산 배분 전략을 제공합니다.</p>
            </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────
#  TAB 4 : 경쟁사 비교 (프리미엄)
# ──────────────────────────────────────────────────────────────────
with tab_comp:
    if not is_premium():
        st.markdown("""
        <div class="lock-box">
            <div style="font-size:3rem">🔒</div>
            <h3>경쟁사 비교 분석</h3>
            <p>내 병원 블로그와 경쟁 병원 블로그를 나란히 비교 분석합니다.<br>
               블로그 지수, 콘텐츠 품질, 키워드 전략을 한눈에 파악하세요.</p>
            <br>
            <p><b>프리미엄 플랜으로 업그레이드하세요 (₩49,000/월)</b></p>
        </div>""", unsafe_allow_html=True)
        st.stop()

    st.markdown('<div class="section-title">경쟁사 블로그 비교 분석</div>', unsafe_allow_html=True)

    col_my, col_comp = st.columns(2)
    with col_my:
        st.markdown("**🏥 우리 병원 URL**")
        my_urls = st.text_area("URL 입력 (최대 3개)", height=100, key="my_urls",
                               placeholder="https://blog.naver.com/my_hospital/...")
    with col_comp:
        st.markdown("**🏪 경쟁 병원 URL**")
        comp_urls = st.text_area("URL 입력 (최대 3개)", height=100, key="comp_urls",
                                 placeholder="https://blog.naver.com/competitor/...")

    if st.button("⚔️ 비교 분석 시작", type="primary"):
        my_list   = [u.strip() for u in my_urls.strip().split("\n") if u.strip()][:3]
        comp_list = [u.strip() for u in comp_urls.strip().split("\n") if u.strip()][:3]

        all_urls = my_list + comp_list
        if not all_urls:
            st.error("URL을 입력하세요.")
        else:
            prog3 = st.progress(0, "크롤링 중...")
            all_data = []
            for i, url in enumerate(all_urls):
                prog3.progress((i+1)/len(all_urls))
                d = crawl_blog(url)
                d["scores"] = calc_scores(d)
                d["sentiment"] = rule_sentiment(d.get("content",""))
                d["group"] = "우리 병원" if url in my_list else "경쟁 병원"
                all_data.append(d)
                time.sleep(0.5)
            prog3.empty()
            st.session_state["comp_data"] = all_data

    if "comp_data" in st.session_state:
        all_data = st.session_state["comp_data"]
        my_data   = [d for d in all_data if d["group"]=="우리 병원"]
        comp_data = [d for d in all_data if d["group"]=="경쟁 병원"]

        def avg_score(lst, key):
            vals = [d.get("scores",{}).get(key,0) for d in lst]
            return round(np.mean(vals),1) if vals else 0

        # 비교 테이블
        st.markdown('<div class="section-title">📊 평균 지표 비교</div>', unsafe_allow_html=True)

        compare_rows = [
            ("블로그 지수",   avg_score(my_data,"total"),   avg_score(comp_data,"total")),
            ("콘텐츠 점수",   avg_score(my_data,"content"), avg_score(comp_data,"content")),
            ("이미지 점수",   avg_score(my_data,"image"),   avg_score(comp_data,"image")),
            ("링크/태그",     avg_score(my_data,"link"),    avg_score(comp_data,"link")),
            ("평균 글자수",
             round(np.mean([d.get("word_count",0) for d in my_data]),0) if my_data else 0,
             round(np.mean([d.get("word_count",0) for d in comp_data]),0) if comp_data else 0),
            ("평균 이미지",
             round(np.mean([d.get("images",0) for d in my_data]),1) if my_data else 0,
             round(np.mean([d.get("images",0) for d in comp_data]),1) if comp_data else 0),
        ]

        table_html = """
        <table class="compare-table">
        <tr><th>항목</th><th>🏥 우리 병원</th><th>🏪 경쟁 병원</th><th>결과</th></tr>"""
        for label, my_v, cp_v in compare_rows:
            win = "🟢 우위" if my_v > cp_v else ("🟡 동등" if my_v == cp_v else "🔴 열세")
            table_html += f"<tr><td><b>{label}</b></td><td>{my_v}</td><td>{cp_v}</td><td>{win}</td></tr>"
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)

        # 차트 비교
        st.markdown('<div class="section-title">📈 지수 분포 비교</div>', unsafe_allow_html=True)
        chart_data = {
            "우리 병원": [d.get("scores",{}).get("total",0) for d in my_data],
            "경쟁 병원": [d.get("scores",{}).get("total",0) for d in comp_data],
        }
        max_len = max(len(v) for v in chart_data.values())
        for k in chart_data:
            while len(chart_data[k]) < max_len:
                chart_data[k].append(None)
        st.line_chart(pd.DataFrame(chart_data))


# ──────────────────────────────────────────────────────────────────
#  TAB 5 : AI 심층 보고서 (프리미엄)
# ──────────────────────────────────────────────────────────────────
with tab_ai:
    if not is_premium():
        st.markdown("""
        <div class="lock-box">
            <div style="font-size:3rem">🤖</div>
            <h3>AI 심층 보고서</h3>
            <p>Claude AI가 병원 블로그를 전문 마케터 시각으로 심층 분석합니다.<br>
               SEO 전략, 콘텐츠 개선안, 월간 운영 로드맵을 제공합니다.</p>
            <br>
            <p><b>프리미엄 플랜으로 업그레이드하세요 (₩49,000/월)</b></p>
        </div>""", unsafe_allow_html=True)
        st.stop()

    st.markdown('<div class="section-title">🤖 Claude AI 심층 분석 보고서</div>', unsafe_allow_html=True)

    api_key = st.session_state.get("api_key","")
    if not api_key:
        st.markdown("""
        <div class="alert-box alert-warn">
            ⚠️ 왼쪽 사이드바에서 Anthropic API 키를 입력해야 AI 기능을 사용할 수 있습니다.<br>
            <a href="https://console.anthropic.com" target="_blank">Anthropic Console에서 발급받기 →</a>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-box alert-good">✅ API 키가 설정되었습니다.</div>',
                    unsafe_allow_html=True)

    # 데이터 소스 선택
    data_source = st.radio("분석 데이터 선택",
                           ["블로그 분석 결과 사용", "엑셀 분석 결과 사용", "직접 입력"],
                           horizontal=True)

    report_data = []
    if data_source == "블로그 분석 결과 사용":
        report_data = st.session_state.get("blog_results", [])
        st.info(f"블로그 분석 탭에서 {len(report_data)}개 포스팅 데이터를 불러왔습니다.")
    elif data_source == "엑셀 분석 결과 사용":
        report_data = st.session_state.get("excel_results", [])
        st.info(f"엑셀 분석 탭에서 {len(report_data)}개 포스팅 데이터를 불러왔습니다.")
    else:
        manual_text = st.text_area("블로그 본문 텍스트 직접 입력", height=200)
        if manual_text:
            report_data = [{"title":"직접 입력","content":manual_text,
                            "word_count":len(manual_text),"images":0,"links":0,"tags":[],
                            "scores":calc_scores({"word_count":len(manual_text),"images":0,"links":0,"tags":[]}),
                            "sentiment":rule_sentiment(manual_text)}]

    # 보고서 유형
    report_type = st.selectbox("보고서 유형", [
        "종합 마케팅 분석 보고서",
        "SEO 최적화 전략 보고서",
        "콘텐츠 개선 액션플랜",
        "월간 블로그 운영 로드맵",
    ])

    if st.button("📋 AI 보고서 생성", type="primary", disabled=not(api_key and report_data)):
        with st.spinner("Claude AI가 보고서를 작성하고 있습니다... (30~60초 소요)"):
            if report_type == "종합 마케팅 분석 보고서":
                report = ai_deep_analysis(report_data, api_key)
            else:
                # 커스텀 프롬프트
                summaries = []
                for d in report_data[:5]:
                    sc = calc_scores(d)
                    summaries.append(f"- {d.get('title','')[:40]} | 지수:{sc['total']} | 글자수:{d.get('word_count',0)}")
                prompt = f"""병원 마케팅 전문가로서 아래 블로그 데이터를 바탕으로
'{report_type}'을 한국어 마크다운으로 상세히 작성해주세요.
병원 유형: {st.session_state.get('specialty','미지정')} / 지역: {st.session_state.get('region','미지정')}

데이터:
{chr(10).join(summaries)}
"""
                report = call_claude(prompt, api_key, 2500)

        st.session_state["ai_report"] = report
        st.session_state["report_title"] = report_type

    if "ai_report" in st.session_state:
        st.markdown("---")
        st.markdown(f"### 📄 {st.session_state.get('report_title','AI 분석 보고서')}")
        st.markdown(f"*생성 일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}*")
        st.markdown("---")
        st.markdown(st.session_state["ai_report"])

        # 다운로드
        report_txt = f"# {st.session_state.get('report_title','')}\n생성: {datetime.now()}\n\n"
        report_txt += st.session_state["ai_report"]
        st.download_button("📥 보고서 다운로드 (.txt)", report_txt,
                           file_name=f"ai_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                           mime="text/plain")


# ══════════════════════════════════════════════════════════════════
#  푸터
# ══════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#6B8CAE;font-size:.78rem;padding:.5rem">
    🏥 MediBlog AI 분석 시스템 | 병원 개원·경영 컨설팅 솔루션<br>
    무료 플랜: URL 5개 분석 · 프리미엄 플랜: 무제한 + AI 심층 분석
</div>
""", unsafe_allow_html=True)
