import streamlit as st

st.set_page_config(page_title="자동차 통계 홈", layout="wide")

st.markdown("<h1 style='text-align: center;'>🚘 내게 맞는 자동차 통계, 어디서부터 봐야 할지 막막하셨죠?</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #4A6AD0;'>브랜드별 통계와 전국 등록현황을 한눈에 비교하세요.</h2>", unsafe_allow_html=True)

st.markdown("---")

spacer1, col1, col2, spacer2 = st.columns([0.1, 1, 1, 0.1])

with col1:
    st.image("https://img.icons8.com/external-flatart-icons-outline-flatarticons/512/external-car-car-service-flatart-icons-outline-flatarticons.png", width=80)
    st.markdown("<h3 style='margin-top:10px;'>🚗 브랜드별 판매 통계</h3>", unsafe_allow_html=True)
    st.markdown("""
    
국내외 자동차 브랜드별 판매 실적
월별 비교, 점유율 추세 시각화
인기 브랜드와 하락 브랜드 확인
""")
st.button("👉 브랜드 통계 보러가기", use_container_width=True)

with col2:
    st.image("https://img.icons8.com/ios-filled/500/region-code.png", width=80)
    st.markdown("<h3 style='margin-top:10px;'>📍 전국 등록 현황</h3>", unsafe_allow_html=True)
    st.markdown("""
    
시도/시군구별 차량 등록 대수
차종별 등록 현황 (승용, 승합, 화물 등)
지역별 차량 특성 파악 가능
""")
st.button("👉 지역 통계 보러가기", use_container_width=True)

st.markdown("---")

st.markdown("<h4 style='text-align: center;'>🚀 데이터 기반으로 자동차 시장을 쉽게 이해해보세요!</h4>", unsafe_allow_html=True)