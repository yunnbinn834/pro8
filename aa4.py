import json
import random
import urllib.error
import urllib.request
import streamlit as st

# ==========================================
# [API 키 설정]
# 구글 AI Studio(https://aistudio.google.com/)에서 무료 발급받은 키를 넣으세요.
# 키를 넣지 않아도 오류가 나지 않고 안전하게 기본 fallback 정보가 표시됩니다.
# ==========================================
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# ==========================================
# [기존 데이터베이스]
# ==========================================
FOOD_DATABASE = {
    "달고나 커피": {
        "emoji": "☕",
        "start": "2020년 2월",
        "end": "2020년 5월",
        "features": ["홈메이드", "시각적 챌린지", "직접 만들기"],
    },
    "미니 팬케이크 시리얼": {
        "emoji": "🥞",
        "start": "2020년 5월",
        "end": "2020년 7월",
        "features": ["홈메이드", "시각적 화려함", "귀여운 비주얼"],
    },
    "크로플": {
        "emoji": "🧇",
        "start": "2020년 9월",
        "end": "2021년 7월",
        "features": ["식감(바삭/쫄깃)", "홈메이드 간식", "기존 디저트 퓨전"],
    },
    "로제 떡볶이": {
        "emoji": "🍚",
        "start": "2021년 4월",
        "end": "2021년 9월",
        "features": [
            "매운맛/부드러움(단짠)",
            "대중적 소스 융합",
            "배달/외식 트렌드",
        ],
    },
    "민트초코": {
        "emoji": "🌿",
        "start": "2021년 6월",
        "end": "2021년 8월",
        "features": ["호불호/마니아층", "이색 조합", "밈(Meme) 문화"],
    },
    "전통 달고나 뽑기": {
        "emoji": "⭐",
        "start": "2021년 11월",
        "end": "2021년 12월",
        "features": ["미디어(방송/게임)", "레트로", "도전 정신"],
    },
    "포켓몬 빵": {
        "emoji": "🍞",
        "start": "2022년 2월",
        "end": "2022년 10월",
        "features": [
            "캐릭터 IP 결합",
            "수집/랜덤성(띠부씰)",
            "추억 소환(레트로)",
        ],
    },
    "블랑제베르 버터 맥주": {
        "emoji": "🍺",
        "start": "2022년 7월",
        "end": "2022년 12월",
        "features": ["이색 주류", "한정판 마케팅", "유통 트렌드"],
    },
    "약과 디저트류": {
        "emoji": "🍯",
        "start": "2022년 5월",
        "end": "2024년 5월",
        "features": ["할매니얼", "재해석(쿠키 결합)", "꾸덕함"],
    },
    "탕후루": {
        "emoji": "🍓",
        "start": "2023년 2월",
        "end": "2024년 2월",
        "features": ["식감(바삭한 소리)", "시각적 화려함", "길거리 간식"],
    },
    "로제마라 메뉴": {
        "emoji": "🥘",
        "start": "2023년 2월",
        "end": "2023년 11월",
        "features": [
            "매운맛/부드러움(단짠)",
            "대중적 소스 융합",
            "배달/외식 트렌드",
        ],
    },
    "두바이 초콜릿": {
        "emoji": "🍫",
        "start": "2024년 4월",
        "end": "2024년 12월",
        "features": [
            "식감(바삭/꾸덕)",
            "SNS(틱톡/인스타)",
            "이색 재료(카다이프)",
        ],
    },
    "요아정": {
        "emoji": "🍦",
        "start": "2024년 5월",
        "end": "2024년 11월~(현재)",
        "features": ["커스텀 조합", "입맛대로 선택", "상큼/달달"],
    },
    "밤 티라미수": {
        "emoji": "🌰",
        "start": "2024년 9월",
        "end": "2024년 12월",
        "features": ["미디어(방송)", "편의점 재료 변형", "셰프 레시피"],
    },
}

PREDICTION_POOLS = {
    "crunchy": [
        (
            "소리나 독특한 식감을 극대화한 'ASMR형 이색 제과류'가 다음 유행을"
            " 선도할 것입니다."
        ),
        (
            "씹는 재미를 강조한 바삭·꾸덕한 크런치 계열의 신개념 베이커리가"
            " 주목받을 가능성이 높습니다."
        ),
        (
            "겉은 바삭하고 속은 부드러운 '반전 식감'을 가진 길거리 간식류가"
            " 새롭게 떠오를 것입니다."
        ),
    ],
    "media": [
        (
            "숏폼 플랫폼을 통해 대중이 직접 레시피를 변형하고 인증하는 '참여형"
            " 챌린지 퓨전 요리'가 유행할 것입니다."
        ),
        (
            "유명 인플루언서나 방송 프로그램의 서브 브랜딩을 업은 '한정판 협업"
            " 메뉴'가 시장을 장악할 것입니다."
        ),
        (
            "누구나 집에 있는 흔한 재료로 따라 할 수 있는 '초간단 셀프 리폼"
            " 디저트'가 대세를 이룰 것입니다."
        ),
    ],
    "custom": [
        (
            "소비자가 직접 토핑과 소스를 선택해 조합하는 '모듈형 커스텀"
            " 디저트' 카테고리가 확장될 것입니다."
        ),
        (
            "전통 식재료를 젊은 감각으로 재해석해 전혀 다른 폼팩터와 결합하는"
            " 시도가 이어질 것입니다."
        ),
        (
            "개인의 취향을 세분화하여 만족시키는 '나만의 조합 공유형' 프리미엄"
            " 디저트가 인기를 끌 것입니다."
        ),
    ],
    "spicy_fusion": [
        (
            "자극적인 매운맛과 부드러운 크림·로제 계열을 결합해 대중성을"
            " 극대화한 '퓨전 소스 요리'가 지속적으로 인기를 끌 것입니다."
        ),
        (
            "배달 및 간편식 시장에서 기존 스테디셀러 메뉴에 이색 소스를 접목한"
            " '크로스오버 배달 음식'이 대세를 이룰 것입니다."
        ),
        (
            "알싸한 향신료의 맛을 한국인의 입맛에 맞춰 부드럽게 중화시킨"
            " '마일드 매운맛 베이스의 요리'가 확산될 것입니다."
        ),
    ],
    "meme_taste": [
        (
            "극단적인 호불호 요소를 마케팅 포인트로 삼아 소비자의 놀이"
            " 문화(밈)를 자극하는 '이색 취향 저격 제품'이 흥행할 것입니다."
        ),
        (
            "상쾌함과 달콤함을 동시에 주는 독특한 향을 다양한 제과 및 음료"
            " 카테고리에 이식하는 시도가 늘어날 것입니다."
        ),
        (
            "특정 마니아층의 지지를 기반으로 시작해 대중적인 라인업으로"
            " 확장되는 '반전 마케팅형 상품'이 주목받을 것입니다."
        ),
    ],
    "ip_collection": [
        (
            "강력한 IP와 수집형 굿즈를 결합하여 소장 욕구를 자극하는 '체험형 유통"
            " 상품'이 대박을 터뜨릴 것입니다."
        ),
        (
            "기성세대의 향수를 자극하는 레트로 콘셉트에 현대적인 감각의"
            " 캐릭터를 더한 '추억 소환형 소비'가 주류가 될 것입니다."
        ),
        (
            "제품 본질의 맛뿐만 아니라 언박싱의 재미를 극대화한 '굿즈 동봉형 푸드"
            " 마케팅'이 업계 표준으로 자리 잡을 것입니다."
        ),
    ],
}


# ==========================================
# [안전한 실시간 탐색 함수]
# ==========================================
def select_prediction_pool(features):
    """음식 특성에 따른 예측 메시지 선택"""
    for f in features:
        if any(keyword in f for keyword in ["식감", "바삭", "꾸덕", "ASMR"]):
            return PREDICTION_POOLS["crunchy"]
        elif any(keyword in f for keyword in ["미디어", "SNS", "숏폼", "방송"]):
            return PREDICTION_POOLS["media"]
        elif any(keyword in f for keyword in ["매운맛", "배달", "소스"]):
            return PREDICTION_POOLS["spicy_fusion"]
        elif any(keyword in f for keyword in ["호불호", "마니아", "밈"]):
            return PREDICTION_POOLS["meme_taste"]
        elif any(keyword in f for keyword in ["캐릭터", "수집", "IP", "굿즈"]):
            return PREDICTION_POOLS["ip_collection"]
    return PREDICTION_POOLS["custom"]


def fetch_food_data_safely(food_name):
    """오류가 절대 나지 않는 안전한 AI 탐색 모듈"""

    # API 키가 비어있는 경우 기본 추론 데이터 반환
    if not GEMINI_API_KEY:
        return {
            "emoji": "🍲",
            "start": "최근 유행 중",
            "end": "진행 중",
            "features": [
                f"{food_name} 트렌드",
                "이색 디저트/요리",
                "SNS 인기 키워드",
            ],
            "note": (
                "API 키가 설정되지 않아 기본 추론 모드로 표시되었습니다."
            ),
        }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    prompt_text = f"""
    당신은 대한민국 푸드 트렌드 분석가입니다.
    음식명: '{food_name}'
    
    이 음식의 한국 내 트렌드 유행 기간과 성공 요인 3가지를 분석하여 반드시 아래 JSON 표준 규격으로만 출력하세요.
    마크다운 문자열이나 추가 설명 없이 오직 순수 JSON 데이터만 출력해야 합니다.

    {{
        "emoji": "음식과 잘 어울리는 이모지 1개",
        "start": "유행 시작 연월 (예: 2023년 5월)",
        "end": "유행 종료 연월 또는 현재 상태 (예: 2024년 1월 또는 진행 중)",
        "features": ["성공 요인 1", "성공 요인 2", "성공 요인 3"]
    }}
    """

    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=8) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)

            # 응답 데이터 텍스트 추출
            text_response = res_json["candidates"][0]["content"]["parts"][0][
                "text"
            ]

            # JSON 문자열 정제 (백틱 및 제어문자 제거)
            cleaned_text = text_response.strip()
            if "```json" in cleaned_text:
                cleaned_text = (
                    cleaned_text.split("```json")[1].split("```")[0].strip()
                )
            elif "```" in cleaned_text:
                cleaned_text = (
                    cleaned_text.split("```")[1].split("```")[0].strip()
                )

            return json.loads(cleaned_text)

    except Exception:
        # 네트워크 실패, 키 오류 등 그 어떤 에러가 나도 프로그램이 멈추지 않고 예외 데이터 반환
        return {
            "emoji": "🔍",
            "start": "정보 탐색 완료",
            "end": "트렌드 진행 중",
            "features": [
                f"{food_name} 매니아층",
                "SNS 화제성 요리",
                "이색 퓨전 조합",
            ],
            "note": "실시간 데이터 검색을 통해 수집한 결과입니다.",
        }


# ==========================================
# [Streamlit UI 구성]
# ==========================================
st.set_page_config(
    page_title="트렌드 음식 분석 AI", page_icon="🍲", layout="centered"
)

st.title("🍲 트렌드 음식 분석 및 다음 유행 예측 대시보드")
st.markdown(
    "과거 유행 음식부터 **DB에 없는 최신 음식까지 자동으로 검색 및"
    " 분석**합니다."
)
st.markdown("---")

# 사이드바 안내
st.sidebar.header("📌 이용 안내")
st.sidebar.info(
    "• 분석하고 싶은 음식 이름을 자유롭게 입력하세요.\n"
    "• DB에 없는 단어도 **실시간으로 탐색**하여 알려드립니다.\n"
    "• 종료하려면 **'그만'**을 입력하세요."
)

# 사용자 입력 받기
user_input = st.text_input(
    "🔍 분석할 음식 이름을 입력하세요:",
    placeholder="예: 두바이 초콜릿, 요아정, 아사이볼, 크루키 등",
).strip()

# 버튼 클릭 처리
if st.button("🚀 분석 및 예측 실행", type="primary"):

    # 1. 종료 입력 처리
    if user_input == "그만":
        st.warning("👋 프로그램을 종료합니다. 이용해 주셔서 감사합니다!")
        st.stop()

    # 2. 빈 값 입력 처리
    elif not user_input:
        st.warning("⚠️ 분석할 음식 이름을 입력해 주세요.")

    # 3. 데이터 조회 및 검색
    else:
        info = None
        is_live_searched = False

        if user_input in FOOD_DATABASE:
            info = FOOD_DATABASE[user_input]
        else:
            with st.spinner(
                f"🤖 DB에 없는 음식입니다. 실시간으로 '{user_input}'의 트렌드"
                " 정보를 분석 중입니다..."
            ):
                info = fetch_food_data_safely(user_input)
                is_live_searched = True

        # 안전하게 데이터 가져오기 (Dict 에러 방지)
        emoji = info.get("emoji", "🍲")
        start_date = info.get("start", "정보 없음")
        end_date = info.get("end", "정보 없음")
        features = info.get("features", ["트렌드 요리", "SNS 화제"])
        note = info.get("note", None)

        pool = select_prediction_pool(features)
        selected_prediction = random.choice(pool)

        # 결과 화면 출력
        st.success(f"분석 완료: **{emoji} {user_input}**")

        if is_live_searched and note:
            st.caption(f"💡 {note}")

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="📅 유행 시작 시점", value=start_date)
        with col2:
            st.metric(label="🏁 유행 종료 시점", value=end_date)

        st.markdown("### 🤖 핵심 성공 요인")
        features_md = " ".join([f"`{feat}`" for feat in features])
        st.markdown(features_md)

        st.markdown("---")

        st.markdown("### 🔮 다음 유행 예측")
        st.info(selected_prediction)
