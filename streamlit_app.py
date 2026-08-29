import streamlit as st
from openai import OpenAI
from dataclasses import dataclass
from typing import List


# ============================================================
# 1. 기본 설정
# ============================================================

st.set_page_config(
    page_title="커피 원두 추천 챗봇",
    page_icon="☕",
    layout="centered"
)

st.title("☕ 나에게 맞는 원두 찾기")
st.write(
    "커피 취향을 편하게 이야기해주세요. "
    "몇 번의 대화를 통해 당신에게 잘 맞는 원두를 찾아드릴게요."
)


# ============================================================
# 2. 원두 데이터
# ============================================================

@dataclass
class Coffee:
    name: str
    origin: str
    process: str
    roast: str

    acidity: float
    sweetness: float
    body: float

    chocolate: float
    nutty: float
    caramel: float
    fruity: float
    floral: float

    description: str
    brew_methods: List[str]


COFFEES = [

    Coffee(
        name="브라질 세하도",
        origin="브라질",
        process="Natural",
        roast="Medium",

        acidity=2,
        sweetness=4,
        body=4,

        chocolate=5,
        nutty=5,
        caramel=4,
        fruity=2,
        floral=1,

        description="초콜릿, 견과류, 카라멜처럼 고소하고 달콤한 풍미",
        brew_methods=["아메리카노", "에스프레소", "핸드드립"]
    ),

    Coffee(
        name="콜롬비아 우일라",
        origin="콜롬비아",
        process="Washed",
        roast="Medium",

        acidity=3,
        sweetness=4,
        body=3,

        chocolate=4,
        nutty=3,
        caramel=4,
        fruity=3,
        floral=2,

        description="카라멜과 초콜릿을 중심으로 은은한 과일 향",
        brew_methods=["아메리카노", "에스프레소", "핸드드립"]
    ),

    Coffee(
        name="과테말라 안티구아",
        origin="과테말라",
        process="Washed",
        roast="Medium",

        acidity=3,
        sweetness=4,
        body=4,

        chocolate=5,
        nutty=3,
        caramel=4,
        fruity=3,
        floral=2,

        description="다크 초콜릿과 카라멜, 은은한 과일 느낌",
        brew_methods=["아메리카노", "에스프레소", "핸드드립"]
    ),

    Coffee(
        name="에티오피아 예가체프",
        origin="에티오피아",
        process="Washed",
        roast="Light",

        acidity=5,
        sweetness=4,
        body=2,

        chocolate=1,
        nutty=1,
        caramel=2,
        fruity=5,
        floral=5,

        description="베리, 시트러스, 꽃 향이 선명한 화사한 커피",
        brew_methods=["핸드드립"]
    ),

    Coffee(
        name="케냐 AA",
        origin="케냐",
        process="Washed",
        roast="Light",

        acidity=5,
        sweetness=4,
        body=3,

        chocolate=2,
        nutty=1,
        caramel=2,
        fruity=5,
        floral=3,

        description="베리와 시트러스 계열의 선명한 산미",
        brew_methods=["핸드드립"]
    )
]


# ============================================================
# 3. 사용자 취향 프로필
# ============================================================

@dataclass
class UserPreference:
    acidity: float = 3
    sweetness: float = 3
    body: float = 3

    chocolate: float = 3
    nutty: float = 3
    caramel: float = 3
    fruity: float = 3
    floral: float = 3

    brew_method: str = ""


# ============================================================
# 4. 세션 상태
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "coffee_profile" not in st.session_state:
    st.session_state.coffee_profile = UserPreference()

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []


# ============================================================
# 5. OpenAI API Key
# ============================================================

openai_api_key = st.text_input(
    "OpenAI API Key",
    type="password"
)

if not openai_api_key:
    st.info(
        "OpenAI API Key를 입력해주세요.",
        icon="🗝️"
    )
    st.stop()


client = OpenAI(api_key=openai_api_key)


# ============================================================
# 6. 시스템 프롬프트
# ============================================================

SYSTEM_PROMPT = """
당신은 전문 커피 큐레이터입니다.

목표는 사용자의 커피 취향을 대화를 통해 파악하고
그 취향에 맞는 원두를 추천하는 것입니다.

사용자에게 어려운 커피 전문용어를 먼저 사용하지 마세요.

다음 정보를 대화에서 자연스럽게 파악하세요.

1. 산미 선호도
2. 단맛 선호도
3. 바디감 선호도
4. 초콜릿 풍미 선호도
5. 견과류 풍미 선호도
6. 카라멜 풍미 선호도
7. 과일 풍미 선호도
8. 꽃 향 선호도
9. 주로 사용하는 추출 방법

사용자가 이미 알려준 정보는 다시 묻지 마세요.

정보가 충분하지 않다면 한 번에 하나의 질문만 하세요.

사용자의 취향이 충분히 파악되면
다음 형식으로 PROFILE을 출력하세요.

PROFILE:
{
    "acidity": 1-5,
    "sweetness": 1-5,
    "body": 1-5,
    "chocolate": 1-5,
    "nutty": 1-5,
    "caramel": 1-5,
    "fruity": 1-5,
    "floral": 1-5,
    "brew_method": "아메리카노/에스프레소/핸드드립/기타"
}

숫자의 의미:

1 = 매우 싫음
2 = 별로 선호하지 않음
3 = 보통
4 = 좋아함
5 = 매우 좋아함
"""


# ============================================================
# 7. 사용자 취향 분석
# ============================================================

def analyze_preference(messages):

    conversation = "\n".join(
        [
            f"{m['role']}: {m['content']}"
            for m in messages
        ]
    )

    prompt = f"""
다음 대화를 분석해서 사용자의 커피 취향을 추정하세요.

{conversation}

반드시 JSON만 출력하세요.

{{
    "acidity": 1-5,
    "sweetness": 1-5,
    "body": 1-5,
    "chocolate": 1-5,
    "nutty": 1-5,
    "caramel": 1-5,
    "fruity": 1-5,
    "floral": 1-5,
    "brew_method": "아메리카노/에스프레소/핸드드립/기타"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "당신은 커피 취향 분석기입니다. "
                    "반드시 유효한 JSON만 반환하세요."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content


# ============================================================
# 8. 원두 매칭 알고리즘
# ============================================================

def calculate_score(user, coffee):

    weights = {
        "acidity": 0.20,
        "sweetness": 0.15,
        "body": 0.15,

        "chocolate": 0.10,
        "nutty": 0.10,
        "caramel": 0.10,
        "fruity": 0.05,
        "floral": 0.05,

        "brew_method": 0.10
    }

    score = 0

    score += (
        1 - abs(user["acidity"] - coffee.acidity) / 4
    ) * weights["acidity"]

    score += (
        1 - abs(user["sweetness"] - coffee.sweetness) / 4
    ) * weights["sweetness"]

    score += (
        1 - abs(user["body"] - coffee.body) / 4
    ) * weights["body"]

    score += (
        1 - abs(user["chocolate"] - coffee.chocolate) / 4
    ) * weights["chocolate"]

    score += (
        1 - abs(user["nutty"] - coffee.nutty) / 4
    ) * weights["nutty"]

    score += (
        1 - abs(user["caramel"] - coffee.caramel) / 4
    ) * weights["caramel"]

    score += (
        1 - abs(user["fruity"] - coffee.fruity) / 4
    ) * weights["fruity"]

    score += (
        1 - abs(user["floral"] - coffee.floral) / 4
    ) * weights["floral"]

    if user["brew_method"] in coffee.brew_methods:
        score += weights["brew_method"]

    return round(score * 100, 1)


# ============================================================
# 9. 추천 원두 생성
# ============================================================

def recommend_coffees(user_profile):

    results = []

    for coffee in COFFEES:

        score = calculate_score(
            user_profile,
            coffee
        )

        results.append({
            "coffee": coffee,
            "score": score
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:3]


# ============================================================
# 10. 추천 이유 생성
# ============================================================

def generate_recommendation_text(
    user_profile,
    recommendations
):

    coffee_text = ""

    for index, item in enumerate(
        recommendations,
        start=1
    ):

        coffee = item["coffee"]

        coffee_text += f"""
{index}. {coffee.name}

원산지: {coffee.origin}
가공방식: {coffee.process}
로스팅: {coffee.roast}

특징:
{coffee.description}

궁합도:
{item["score"]}%
"""

    prompt = f"""
사용자의 커피 취향:

{user_profile}

추천 원두:

{coffee_text}

각 원두가 왜 사용자에게 잘 맞는지
친근하고 쉽게 설명해주세요.

가장 추천하는 원두부터 순서대로 설명하세요.

커피 전문용어를 과하게 사용하지 마세요.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "당신은 친절한 커피 큐레이터입니다."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# ============================================================
# 11. 기존 대화 출력
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ============================================================
# 12. 챗봇
# ============================================================

if prompt := st.chat_input(
    "예: 산미는 별로고 고소한 커피가 좋아요"
):

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)


    # --------------------------------------------------------
    # GPT 응답
    # --------------------------------------------------------

    messages_for_gpt = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages_for_gpt.extend(
        st.session_state.messages
    )

    with st.chat_message("assistant"):

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_for_gpt,
            stream=True
        )

        answer = st.write_stream(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


    # --------------------------------------------------------
    # 취향 분석
    # --------------------------------------------------------

    try:

        import json

        profile_json = analyze_preference(
            st.session_state.messages
        )

        profile = json.loads(
            profile_json
        )

        st.session_state.coffee_profile = profile

        # ----------------------------------------------------
        # 추천 생성
        # ----------------------------------------------------

        recommendations = recommend_coffees(
            profile
        )

        st.session_state.recommendations = recommendations

    except Exception as e:

        # 취향 정보가 아직 부족하면 무시
        pass


# ============================================================
# 13. 추천 결과 표시
# ============================================================

if st.session_state.recommendations:

    st.divider()

    st.header("☕ 당신에게 맞는 원두")

    recommendations = (
        st.session_state.recommendations
    )

    for index, item in enumerate(
        recommendations,
        start=1
    ):

        coffee = item["coffee"]

        with st.container():

            st.subheader(
                f"{index}위. {coffee.name}"
            )

            st.write(
                f"**궁합도 {item['score']}%**"
            )

            st.write(
                coffee.description
            )

            st.caption(
                f"원산지: {coffee.origin} · "
                f"가공: {coffee.process} · "
                f"로스팅: {coffee.roast}"
            )

            st.write(
                f"추천 추출법: "
                f"{', '.join(coffee.brew_methods)}"
            )
