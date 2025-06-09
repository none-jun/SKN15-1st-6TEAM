import streamlit as st
import pandas as pd
import altair as alt
from urllib.error import URLError
import io

st.set_page_config(page_title="Vehicle", page_icon="🌍", layout="wide")

# ---- Custom CSS 스타일 추가 ----
st.markdown(
    """
    <style>
    /* 배경색 및 폰트 */
    .main {
        background-color: #f9f9f9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #333333;
    }
    /* 카드 스타일 */
    .card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    /* 타이틀 스타일 */
    h1 {
        color: #0078D7; /* 파란색 계열 */
        font-weight: 700;
    }
    /* info 박스 스타일 */
    .stAlert > div {
        background-color: #eaf4fc !important;
        color: #666666 !important;
        border-radius: 10px;
        padding: 1rem;
        font-size: 1.1rem;
    }
    /* 버튼 커스텀 */
    div.stButton > button {
        background-color: #0078D7;
        color: white;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #005a9e;
        color: #f0f0f0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


ex_city = ['전체',"서울", "부산", "광주"]
ex_gu = ['전체',"동작구", "부산진구", "광산구"]
ex_car = ['전체',"화물차", "승용차", "소형차"]
ex_fuel = ['전체',"가솔린", "전기"]
ex_sex = ['전체',"남", "여"]

st.markdown("# 🚗 전국 자동차 등록 현황", unsafe_allow_html=True)

# 요약 info 박스에 카드 스타일 적용
st.markdown('', unsafe_allow_html=True)
st.info(
    """
**페이지 요약**

1. **세부 검색 창**
    - **조건:** 지역별, 차종별, 연료별, 성별별
    - **지역:** 서울, 부산, 대구, 인천, 광주, 대전, 울산, 세종, 경기, 충북, 충남, 전남, 경북, 경남, 제주, 강원, 전북
        - **지역별:** 시군구 단위 선택 가능
        - **차종별:** 승용, 승합, 화물, 특수
        - **연료별:** 휘발유, 경유, 엘피지, 전기, 하이브리드
        - **성별:** 남, 여

2. **엑셀 파일 다운로드**
    - 조회한 데이터를 엑셀 파일로 저장할 수 있습니다.
"""
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)

st.markdown('', unsafe_allow_html=True)

st.markdown("### 🔍 조회하기")
col1, col2 = st.columns(2)

with col1:
    selection = st.selectbox("조건 선택", ["선택하세요", "지역별", "차종별", "연료별", "성별별"], key="selection")
    if selection == "지역별":
        sex1 = st.selectbox("시군구 선택", ex_gu)
    elif selection == "차종별":
        age1 = st.selectbox("차종별 선택", ex_car)
    elif selection == "연료별":
        age1 = st.selectbox("연료별 선택", ex_fuel)
    elif selection == "성별별":
        age1 = st.selectbox("성별 선택", ex_sex)
    elif selection == "선택하세요":
        st.info("조건을 선택해주세요.")

with col2:
    city = st.selectbox("지역 선택", ex_city, key="ex_city")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)

# 데이터 가져오기, 그래프 출력 부분 카드 스타일 적용
st.markdown('', unsafe_allow_html=True)

@st.cache_data
def get_UN_data():
    AWS_BUCKET_URL = "http://streamlit-demo-data.s3-us-west-2.amazonaws.com"
    df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
    return df.set_index("Region")

try:
    df = get_UN_data()
    countries = st.multiselect(
        "국가 선택", list(df.index), ["China", "United States of America"]
    )
    if not countries:
        st.error("최소 한 개 이상의 국가를 선택하세요.")
    else:
        data = df.loc[countries]
        data /= 1000000.0
        st.write("### 📊 요약 통계 그래프", data.sort_index())

        data = data.T.reset_index()
        data = pd.melt(data, id_vars=["index"]).rename(
            columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
        )
        chart = (
            alt.Chart(data)
            .mark_bar()
            .encode(
                x="year:T",
                y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
                color="Region:N",
            )
        )
        st.altair_chart(chart, use_container_width=True)
except URLError as e:
    st.error(
        """
        **인터넷 연결이 필요합니다.**
        연결 오류: %s
    """
        % e.reason
    )
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)

# 엑셀 다운로드 카드 스타일 적용
st.markdown('', unsafe_allow_html=True)
st.markdown("### 📥 엑셀 파일 다운로드")
st.write("필요한 데이터를 엑셀 파일로 다운로드할 수 있습니다.")

df = pd.DataFrame(
    {
        "이름": ["홍길동", "김철수", "이영희"],
        "지역": ["서울", "부산", "대전"],
        "등록 차량 수": [1200, 850, 430],
    }
)

def to_excel_bytes(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return output.getvalue()

if st.button("엑셀 생성"):
    excel_bytes = to_excel_bytes(df)
    st.download_button(
        label="📥 엑셀 다운로드",
        data=excel_bytes,
        file_name="vehicle_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.header("전국 자동차 등록 현황")
st.sidebar.markdown("### 🛠️ 사용법")
st.sidebar.markdown(
    """
- 원하는 조건, 지역을 선택하세요.  
- 조건별로 변경되는 추가 조건을 선택하세요
- 요약 통계표와 엑셀 데이터를 받을 수 있습니다.  
- 데이터베이스 연결 상태에 따라 로딩 시간이 걸릴 수 있습니다.
"""
)