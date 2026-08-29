import streamlit as st
from openai import OpenAI

# --------------------------------------------------
# 기본 화면
# --------------------------------------------------

st.title("☕ Coffee Bean Consultant")

st.write(
    "커피 원두와 생두에 대해 전문적으로 상담받을 수 있는 "
    "AI 커피 컨설턴트입니다."
)

# --------------------------------------------------
# 사이드바 - 커피 선호도
# --------------------------------------------------

st.sidebar.title("☕ 나의 커피 취향")

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

# --------------------------------------------------
# OpenAI API Key
# --------------------------------------------------

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

    # OpenAI Client
    client = OpenAI(api_key=openai_api_key)

    # --------------------------------------------------
    # 사용자 커피 선호도
    # --------------------------------------------------

    preference_text = f"""
사용자의 기본 커피 선호도는 다음과 같습니다.

- 로스팅 정도: {roast_preference}
- 산미: {acidity_preference}
- 바디감: {body_preference}
- 단맛: {sweetness_preference}
- 선호 향미: {flavor_preference}
- 주 추출방법: {brew_preference}
"""

    # --------------------------------------------------
    # AI 전문 상담가 System Prompt
    # --------------------------------------------------

    system_prompt = f"""
당신은 커피 원두와 생두를 전문적으로 상담하는
AI Coffee Bean Consultant입니다.

당신의 주요 전문 분야는 다음과 같습니다.

1. 생두
- 국가 및 지역별 생두 특성
- 품종
- 가공방식
- 고도
- 수확시기
- 생두 품질
- 결점두
- 생두 보관
- 생두 구매

2. 로스팅
- 약배전 / 중배전 / 강배전
- 로스팅 프로파일
- 건조구간
- 마이야르 구간
- 1차 크랙
- 디벨롭먼트
- 배출온도
- 로스팅 수율

3. 커피 추출
- 핸드드립
- 에스프레소
- 프렌치프레스
- 모카포트
- 콜드브루
- 분쇄도
- 물 온도
- 추출시간
- 추출비율

4. 커핑 및 향미
- 산미
- 단맛
- 쓴맛
- 바디
- 밸런스
- 애프터
- 향미 특성

-----------------------------------
사용자의 기본 커피 선호도
-----------------------------------

{preference_text}

-----------------------------------
상담 원칙
-----------------------------------

사용자의 질문에 답변할 때 위의 기본 커피 선호도를
가능하면 적극적으로 반영하세요.

예를 들어 사용자가 생두 추천을 요청하면
사용자의 선호하는 로스팅, 산미, 바디감, 단맛,
향미를 고려하여 추천하세요.

사용자가 로스팅 방법을 질문하면
사용자의 취향에 맞는 로스팅 방향을 제안하세요.

사용자가 추출방법을 질문하면
사용자가 주로 사용하는 추출방법을 고려하세요.

단, 사용자가 명시적으로 다른 취향이나 조건을 제시하면
새롭게 제시된 조건을 우선합니다.

전문용어는 사용하되 필요한 경우 쉽게 설명하세요.

가능하면 답변을 다음과 같은 구조로 작성하세요.

1. 결론
2. 분석
3. 추천 방법
4. 추가로 고려할 사항

확실하지 않은 정보는 사실처럼 단정하지 마세요.
"""

    # --------------------------------------------------
    # Session State
    # --------------------------------------------------

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # --------------------------------------------------
    # 이전 대화 표시
    # --------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --------------------------------------------------
    # Chat Input
    # --------------------------------------------------

    if prompt := st.chat_input(
        "예: 산미가 적고 초콜릿 향이 강한 생두를 추천해주세요."
    ):

        # 사용자 질문 저장
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        # 사용자 질문 표시
        with st.chat_message("user"):
            st.markdown(prompt)

        # --------------------------------------------------
        # AI에게 전달할 메시지
        # --------------------------------------------------

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

        # --------------------------------------------------
        # OpenAI API 호출
        # --------------------------------------------------

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
        )

        # --------------------------------------------------
        # AI 응답 출력
        # --------------------------------------------------

        with st.chat_message("assistant"):

            response = st.write_stream(stream)

        # AI 응답 저장
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )
