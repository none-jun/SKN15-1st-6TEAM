import streamlit as st
import pandas as pd
import altair as alt
import pymysql
from urllib.error import URLError
import numpy as np

# 페이지 설정
st.set_page_config(page_title="브랜드별 판매 추이", page_icon="📊", layout="wide")

# --- 스타일 커스텀 CSS ---
st.markdown(
    """
    <style>
    /* 배경색 및 폰트 */
    .main {
        background-color: #f9fafb;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* 헤더 스타일 */
    h1 {
        color: #0078D7;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    h3 {
        padding-top : 50px;
        padding-bottom : 30px;
        
    }
    /* info 박스 스타일 */
    .stAlert > div {
        background-color: #eaf4fc !important;
        color: #666666 !important;
        border-radius: 10px;
        padding: 1rem;
        font-size: 1.1rem;
        
    }
    /* 멀티셀렉트 박스 스타일 */
    .stMultiSelect > div[role="listbox"] {
        min-height: 6rem;
    }
    /* 버튼 스타일 */
    div.stButton > button {
        background-color: #3178c6;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        margin-top: 25px;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #255a9b;
    }
    /* 차트 제목 */
    .vega-embed .title {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        fill: #2c3e50 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 헤더
st.markdown("# 📊 브랜드별 판매 추이")
st.sidebar.header("브랜드별 판매 추이 (연월)")

# 설명 박스 (info)
st.write("")  # 여백
st.info(
    """
    **다나와 사이트 데이터 기반** 
    - 브랜드별 판매 추이 (연월 단위)  
    - 조회 기간: 2023.01 ~ 2025.05  
    - 최소 1개 이상 브랜드 선택 후 '조회' 버튼 클릭  
    """
)

st.write("")  # 여백
@st.cache_data(show_spinner=False)
def load_brand_index():
    """brand_type 테이블에서 고유 브랜드명 가져오기"""
    conn = pymysql.connect(
        host="222.112.208.67",
        user="team_6",
        passwd="123",
        database="sk15_6team",
        port=3306,
    )
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT brand FROM brand_type ORDER BY brand;")
    brands = [row[0] for row in cur.fetchall()]
    conn.close()
    return brands

# --- 브랜드 리스트 ---
brand_idx = load_brand_index()


@st.cache_data(show_spinner=False)
def get_brand_df(brand_list):
    """DB에서 선택 브랜드 데이터 불러오기"""
    conn = pymysql.connect(
        host="222.112.208.67",
        # host="192.168.0.22",
        user="team_6",
        passwd="123",
        database="sk15_6team",
        port=3306,
    )
    cur = conn.cursor()

    brand = ", ".join([f"'{b}'" for b in brand_list])

    sql = f"""
        SELECT
            bt.brand,
            bt.origin_type,
            b.ym AS ym,
            b.sales_count AS sales_count
        FROM brand_type bt
        JOIN brands b ON bt.brand = b.brand
        WHERE bt.brand IN ({brand})
    """
    cur.execute(sql)
    rows = cur.fetchall()
    col = [desc[0] for desc in cur.description]

    return pd.DataFrame(rows, columns=col)

@st.cache_data(show_spinner=False)
def load_models_by_brands(brands):
    if not brands:
        return []

    # 🔧 작은따옴표로 감싸기
    brand_str = ', '.join(f"'{b}'" for b in brands)

    conn = pymysql.connect(
        host="222.112.208.67",
        user="team_6",
        passwd="123",
        database="sk15_6team",
        port=3306,
    )
    cur = conn.cursor()
    cur.execute(f"""
        SELECT DISTINCT model 
        FROM brand_model 
        WHERE brand IN ({brand_str})
        ORDER BY model;
    """)
    models = [row[0] for row in cur.fetchall()]
    conn.close()
    return models

@st.cache_data(show_spinner=False)
def get_model_df(model_list):
    if not model_list:
        return pd.DataFrame()

    model_str = ", ".join(f"'{m}'" for m in model_list)

    conn = pymysql.connect(
        host="222.112.208.67",
        user="team_6",
        passwd="123",
        database="sk15_6team",
        port=3306,
    )
    cur = conn.cursor()

    query = f"""
        SELECT model, ym, sales_count
        FROM models
        WHERE model IN ({model_str})
    """
    cur.execute(query)
    rows = cur.fetchall()
    col = [desc[0] for desc in cur.description]
    conn.close()
    return pd.DataFrame(rows, columns=col)

# 레이아웃 : 브랜드 선택 + 조회 버튼을 한 줄에 배치

# with st.form("search_form"):
#     col1, col2 = st.columns([5, 1])
#     with col1:
#         brand_list = st.multiselect("브랜드 선택", brand_idx)
#     with col2:
#         search_clicked = st.form_submit_button("조회")

# # 모델 선택은 form 밖에서 실시간으로 반응
# if brand_list:
#     model_list = load_models_by_brands(brand_list)
#     model_options = ['전체'] + model_list

#     selected_models = st.multiselect("모델 선택", model_options)

#     # '전체' 선택 시 실제 모델 전체로 대체
#     if '전체' in selected_models or not selected_models:
#         filtered_models = model_list
#     else:
#         filtered_models = selected_models
# else:
#     model_list = []
#     filtered_models = []
#     selected_models = []
col1, col2 = st.columns([5, 5])

with col1:
    brand_list = st.multiselect("브랜드 선택", brand_idx)

# 모델 선택은 브랜드 선택 직후 바로 반응
if brand_list:
    model_list = load_models_by_brands(brand_list)
    model_options = ['전체'] + model_list
else:
    model_list = []
    model_options = []

with col2:
    selected_models = st.multiselect("모델 선택", model_options)

# 선택된 모델 처리
if '전체' in selected_models or not selected_models:
    filtered_models = model_list
else:
    filtered_models = selected_models

# 조회 버튼
search_clicked = st.button("조회")

if search_clicked:
    if not brand_list:
        st.error("최소 하나의 브랜드를 선택해주세요.")
    else:
        try:
            brand_df = get_brand_df(brand_list)

            # 날짜 처리
            brand_df["ym"] = pd.to_datetime(brand_df["ym"], errors="coerce")
            brand_df["ym"] = brand_df["ym"].dt.strftime("%Y-%m")
            brand_df_sum = (
                brand_df.groupby("brand")["sales_count"]
                .sum()
                .reset_index()
                .sort_values(by="sales_count", ascending=False)
            )

            
            st.markdown("### 📊 브랜드 요약 통계표")
            st.dataframe(brand_df_sum, use_container_width=True)
            st.write('### 📈연도별 브랜드 판매량')


            # Altair 차트 생성
            chart = (
                alt.Chart(brand_df)
                .mark_line(point=True)
                .encode(
                    x=alt.X(
                        "ym:T",
                        title="월",
                        axis=alt.Axis(format="%Y-%m", tickCount="month"),
                    ),
                    y=alt.Y("sales_count:Q", title="판매량"),
                    color=alt.Color("brand:N", title="브랜드"),
                    tooltip=["ym:T", "brand:N", "sales_count:Q"],
                )
                .properties(

                    width=1100, height=600, title=""

                )
                # .configure_title(
                #     fontSize=10, fontWeight="bold", anchor="start", color="#2c3e50"
                # )
            )
            # st.markdown("")
            st.altair_chart(chart, use_container_width=True)

            ######모델
            if filtered_models:
                model_df = get_model_df(filtered_models)

            # 날짜 처리
                model_df["ym"] = pd.to_datetime(model_df["ym"], errors="coerce")
                model_df["ym"] = model_df["ym"].dt.strftime("%Y-%m")
                model_df_sum = (
                    model_df.groupby("model")["sales_count"]
                    .sum()
                    .reset_index()
                    .sort_values(by="sales_count", ascending=False)
                )

                st.markdown("### 📊 모델 요약 통계표")
                st.dataframe(model_df_sum, use_container_width=True)
                st.write('### 📈연도별 모델 판매량')


                # Altair 차트 생성
                chart = (
                    alt.Chart(model_df)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X(
                            "ym:T",
                            title="월",
                            axis=alt.Axis(format="%Y-%m", tickCount="month"),
                        ),
                        y=alt.Y("sales_count:Q", title="판매량"),
                        color=alt.Color("model:N", title="모델"),
                        tooltip=["ym:T", "model:N", "sales_count:Q"],
                    )
                    .properties(

                        width=1100, height=600, title=""

                    )
                # .configure_title(
                #     fontSize=10, fontWeight="bold", anchor="start", color="#2c3e50"
                # )
                )
                # st.markdown("")
                st.altair_chart(chart, use_container_width=True)
            
            
# -------------------------------- 원 차트 만드는 부분 ------------------------------- #
                        
        
            # 데이터 전처리
            st.write('### 🌐연도별 평균 국내차/수입차 판매량')
            brand_df["year"] = pd.to_datetime(brand_df["ym"]).dt.year
            bar_data = brand_df.groupby(["year", "origin_type"])["sales_count"].mean().reset_index()

            # 막대 그래프
            bar_chart = (
                alt.Chart(bar_data)
                .mark_bar()
                .encode(
                    x=alt.X("year:O", title="연도"),
                    y=alt.Y("sales_count:Q", title="판매량"),
                    color=alt.Color("origin_type:N", title="유형"),
                    tooltip=["year:O", "origin_type:N", "sales_count:Q"]
                )
                .properties(
                    title="",
                    width=700,
                    height=400
                )
                .configure_title(
                    fontSize=18,
                    anchor="start"
                )
            )

            st.altair_chart(bar_chart, use_container_width=True)



        except URLError as e:
            st.error(f"인터넷 연결 오류: {e.reason}")
        except Exception as e:
            st.error(f"데이터 로딩 중 오류가 발생했습니다: {e}")

# 사이드바 꾸미기
st.sidebar.markdown("### 🛠️ 사용법")
st.sidebar.markdown(
    """
- 원하는 브랜드를 여러 개 선택하세요.  
- 조회 버튼을 눌러 데이터를 불러옵니다.  
- 요약 통계표와 시계열 차트를 확인할 수 있습니다.  
- 데이터베이스 연결 상태에 따라 로딩 시간이 걸릴 수 있습니다.
"""
)
