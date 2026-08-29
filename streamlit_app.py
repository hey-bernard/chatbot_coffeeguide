import streamlit as st
from openai import OpenAI

# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------

st.set_page_config(
    page_title="Coffee Bean Consultant",
    page_icon="☕",
    layout="wide"
)

# --------------------------------------------------
# 제목
# --------------------------------------------------

st.title("☕ Coffee Bean Consultant")
st.write(
    "나의 커피 취향을 선택하면 취향에 맞는 원두를 찾아드립니다."
)

# --------------------------------------------------
# Session State
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "search_result" not in st.session_state:
    st.session_state.search_result = False


# ==================================================
# 좌측 사이드바
# ==================================================

st.sidebar.title("☕ 원두 찾기")

st.sidebar.subheader("커피 선호도")

roast_preference = st.sidebar.radio(
    "선호하는 로스팅 정도",
    ["약배전", "중배전", "강배전"],
    index=1
)

acidity_preference = st.sidebar.radio(
    "선호하는 산미",
    ["낮음", "보통", "높음"],
    index=1
)

body_preference = st.sidebar.radio(
    "선호하는 바디감",
    ["가벼움", "보통", "묵직함"],
    index=1
)

sweetness_preference = st.sidebar.radio(
    "선호하는 단맛",
    ["낮음", "보통", "높음"],
    index=1
)

flavor_preference = st.sidebar.radio(
    "선호하는 향미",
    [
        "과일 / 베리",
        "꽃 / 플로럴",
        "초콜릿 / 견과류",
        "카라멜 / 브라운슈가",
        "스파이시 / 허브"
    ],
    index=0
)

brew_preference = st.sidebar.radio(
    "주로 사용하는 추출방법",
    [
        "핸드드립",
        "에스프레소",
        "프렌치프레스",
        "모카포트",
        "콜드브루"
    ],
    index=0
)

st.sidebar.divider()

# ==================================================
# 찾기 버튼
# ==================================================

if st.sidebar.button(
    "🔎 내 취향에 맞는 원두 찾기",
    use_container_width=True
):
    st.session_state.search_result = True


# ==================================================
# OpenAI API
# ==================================================

openai_api_key = st.text_input(
    "OpenAI API Key",
    type="password"
)

if not openai_api_key:

    st.info(
        "OpenAI API Key를 입력해주세요.",
        icon="🗝️"
    )

else:

    client = OpenAI(api_key=openai_api_key)

    # ==================================================
    # 화면을 좌우 2개 컬럼으로 구성
    # ==================================================

    left_column, right_column = st.columns(
        [1, 2],
        gap="large"
    )

    # ==================================================
    # 왼쪽 - 현재 선호도
    # ==================================================

    with left_column:

        st.subheader("☕ 나의 커피 취향")

        st.markdown(
            f"""
            **로스팅**
            
            {roast_preference}

            **산미**
            
            {acidity_preference}

            **바디감**
            
            {body_preference}

            **단맛**
            
            {sweetness_preference}

            **선호 향미**
            
            {flavor_preference}

            **추출방법**
            
            {brew_preference}
            """
        )

    # ==================================================
    # 오른쪽 - 검색 결과
    # ==================================================

    with right_column:

        if st.session_state.search_result:

            st.subheader("🔎 추천 원두")

            # ------------------------------------------
            # 선호도 안내
            # ------------------------------------------

            st.success(
                f"""
                **당신의 커피 선호도**

                로스팅: **{roast_preference}**  
                산미: **{acidity_preference}**  
                바디감: **{body_preference}**  
                단맛: **{sweetness_preference}**  
                향미: **{flavor_preference}**  
                추출: **{brew_preference}**
                """
            )

            st.divider()

            # ------------------------------------------
            # AI 추천 요청
            # ------------------------------------------

            preference_prompt = f"""
            사용자의 커피 선호도는 다음과 같습니다.

            - 로스팅: {roast_preference}
            - 산미: {acidity_preference}
            - 바디감: {body_preference}
            - 단맛: {sweetness_preference}
            - 향미: {flavor_preference}
            - 추출방법: {brew_preference}

            위 취향을 분석하여 사용자에게 적합한
            커피 원두의 특징을 추천해주세요.

            다음 형식으로 답변해주세요.

            ### 추천 원두 스타일
            - 추천 산지
            - 추천 가공방식
            - 추천 품종
            - 예상 향미
            - 추천 로스팅

            ### 추천 이유
            사용자의 취향과 연결하여 설명하세요.
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """
                        당신은 커피 생두와 원두를 전문적으로
                        상담하는 커피 전문가입니다.

                        사용자의 취향을 분석하여
                        적합한 커피 원두 스타일을 추천하세요.

                        원산지, 품종, 가공방식, 고도,
                        로스팅 정도 및 향미를 고려하세요.
                        """
                    },
                    {
                        "role": "user",
                        "content": preference_prompt
                    }
                ]
            )

            recommendation = response.choices[0].message.content

            st.markdown(recommendation)

            st.divider()

            # ------------------------------------------
            # 판매처 영역
            # ------------------------------------------

            st.subheader("🛒 원두 판매처")

            st.info(
                "아래 영역에 실제 원두 판매처 데이터를 "
                "연결할 수 있습니다."
            )

            # 예시 판매처
            sellers = [
                {
                    "name": "판매처 A",
                    "bean": "에티오피아 예가체프",
                    "process": "Natural",
                    "price": "1kg 25,000원"
                },
                {
                    "name": "판매처 B",
                    "bean": "브라질 세하도",
                    "process": "Natural",
                    "price": "1kg 22,000원"
                },
                {
                    "name": "판매처 C",
                    "bean": "콜롬비아 후일라",
                    "process": "Washed",
                    "price": "1kg 28,000원"
                }
            ]

            for seller in sellers:

                with st.container(border=True):

                    st.markdown(
                        f"### ☕ {seller['bean']}"
                    )

                    st.write(
                        f"**판매처:** {seller['name']}"
                    )

                    st.write(
                        f"**가공방식:** {seller['process']}"
                    )

                    st.write(
                        f"**가격:** {seller['price']}"
                    )

                    st.button(
                        "판매처 보기",
                        key=seller["name"]
                    )

        else:

            st.subheader("👈 원두를 찾아보세요")

            st.write(
                "왼쪽에서 자신의 커피 선호도를 선택한 후 "
                "**'내 취향에 맞는 원두 찾기'** 버튼을 눌러주세요."
            )

            st.info(
                "선택한 취향을 분석하여 오른쪽에 "
                "추천 원두와 판매처를 표시할 수 있습니다."
            )


# ==================================================
# 채팅 상담
# ==================================================

st.divider()

st.subheader("💬 커피 전문 상담")

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input(
    "예: 산미가 적고 초콜릿 향이 강한 원두를 추천해주세요."
):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    system_prompt = f"""
    당신은 커피 원두와 생두 전문 상담가입니다.

    사용자의 기본 커피 취향:

    - 로스팅: {roast_preference}
    - 산미: {acidity_preference}
    - 바디감: {body_preference}
    - 단맛: {sweetness_preference}
    - 향미: {flavor_preference}
    - 추출방법: {brew_preference}

    사용자의 취향을 고려해서
    생두, 원두, 로스팅, 추출에 대해
    전문적이면서 이해하기 쉽게 상담하세요.

    사용자가 다른 조건을 명시하면
    사용자가 새로 제시한 조건을 우선하세요.
    """

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages.extend(
        {
            "role": m["role"],
            "content": m["content"]
        }
        for m in st.session_state.messages
    )

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True
    )

    with st.chat_message("assistant"):

        response = st.write_stream(stream)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )
