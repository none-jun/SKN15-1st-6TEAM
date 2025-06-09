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

# --- 브랜드 리스트 ---
brand_idx = [
    "BMW",
    "BYD",
    "DS",
    "GMC",
    "KGM",
    "기아",
    "람보르기니",
    "랜드로버",
    "렉서스",
    "롤스로이스",
    "르노코리아",
    "링컨",
    "마세라티",
    "미니",
    "벤츠",
    "벤틀리",
    "볼보",
    "쉐보레",
    "아우디",
    "재규어",
    "제네시스",
    "지프",
    "캐딜락",
    "테슬라",
    "토요타",
    "페라리",
    "포드",
    "포르쉐",
    "폭스바겐",
    "폴스타",
    "푸조",
    "현대",
    "혼다",
]


@st.cache_data(show_spinner=False)
def get_brand_df(brand_list):
    """DB에서 선택 브랜드 데이터 불러오기"""
    conn = pymysql.connect(
        host="192.168.0.22",
        user="team_6",
        passwd="123",
        database="sk15_6team",
        port=3306,
    )
    cur = conn.cursor()

    def get_sql(query):
        cur.execute(query)
        return cur.fetchall()

    brand = ", ".join([f"'{b}'" for b in brand_list])

    brand_query = get_sql(f"""
        SELECT *
        FROM danawa d
        WHERE brand IN ({brand})
    """)

    columns_query = get_sql("DESC danawa")
    col = [desc[0] for desc in columns_query]

    return pd.DataFrame(brand_query, columns=col)


# 레이아웃 : 브랜드 선택 + 조회 버튼을 한 줄에 배치

with st.form("search_form"):
    col1, col2 = st.columns([5, 1])
    with col1:
        brand_list = st.multiselect("브랜드 선택", brand_idx)
    with col2:
        search_clicked = st.form_submit_button("조회")


if search_clicked:
    if not brand_list:
        st.error("최소 하나의 브랜드를 선택해주세요.")
    else:
        try:
            df = get_brand_df(brand_list)

            # 날짜 처리
            df["ym"] = pd.to_datetime(df["ym"], errors="coerce")
            df["ym"] = df["ym"].dt.strftime("%Y-%m")

            st.markdown("")
            st.markdown("### 📊 요약 통계표")
            st.dataframe(df, use_container_width=True)

            # Altair 차트 생성
            chart = (
                alt.Chart(df)
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
                    width=1100, height=600, title="연도별 브랜드 판매량 시계열 차트"
                )
                # .configure_title(
                #     fontSize=10, fontWeight="bold", anchor="start", color="#2c3e50"
                # )
            )
            # st.markdown("")
            st.altair_chart(chart, use_container_width=True)
            
            
# -------------------------------- 원 차트 만드는 부분 ------------------------------- #
                        
        

            df["year"] = pd.to_datetime(df["ym"]).dt.year
            pie_data = df.groupby(["year", "origin_type"])["sales_count"].sum().reset_index()

            # 연도별 원형차트 여러 개
            years = pie_data["year"].unique()

            st.write('### 연도별 국내/해외 판매량 비교')

            n_per_row = 3
            for i in range(0, len(years), n_per_row):
                cols = st.columns(n_per_row)
                for j, year in enumerate(years[i:i + n_per_row]):
                    with cols[j]:
                        filtered = pie_data[pie_data["year"] == year].copy()
                        total = filtered["sales_count"].sum()
                        filtered["percent"] = (filtered["sales_count"] / total * 100).round(1).astype(str) + '%'

                        base = alt.Chart(filtered).encode(
                            color=alt.Color("origin_type:N", title="유형"),
                            tooltip=["origin_type:N", "sales_count:Q"]
                        )
                        
                        pie = base.mark_arc(opacity=0.7).encode(
                            theta=alt.Theta("sales_count:Q", title="판매량"),
                        )
                        
                        # 텍스트 위치: 중간 각도 구해서 radius 지정
                        text = base.mark_text(radius=100, size=10).encode(
                            theta=alt.Theta("sales_count:Q", stack="center"),
                            text="percent"
                        )
                        
                        pie_chart = (pie + text).properties(
                            title=f"{year}년",
                            width=250,
                            height=250
                        ).configure_title(
                            fontSize=14,
                            anchor="middle",
                            dy=20
                        )
                        
                        st.altair_chart(pie_chart, use_container_width=True)

                    
# ------------------------------ 원형 차트 막대그래프 버전 ------------------------------ #
                    
                    
            # df["year"] = pd.to_datetime(df["ym"]).dt.year
            # bar_data = df.groupby(["year", "origin_type"])["sales_count"].sum().reset_index()
            # years = bar_data["year"].unique()

            # st.write('### 연도별 국내/해외 판매량 비교')

            # n_per_row = 3
            # for i in range(0, len(years), n_per_row):
            #     cols = st.columns(n_per_row)
            #     for j, year in enumerate(years[i:i + n_per_row]):
            #         with cols[j]:
            #             filtered = bar_data[bar_data["year"] == year]
            #             bar_chart = (
            #                 alt.Chart(filtered)
            #                 .mark_bar(opacity=0.7)
            #                 .encode(
            #                     x=alt.X("origin_type:N", title="유형"),
            #                     y=alt.Y("sales_count:Q", title="판매량"),
            #                     color=alt.Color("origin_type:N", legend=None),
            #                     tooltip=["origin_type:N", "sales_count:Q"]
            #                 )
            #                 .properties(
            #                     title=f"{year}년",
            #                     width=250,
            #                     height=250
            #                 )
            #                 .configure_title(
            #                     fontSize=14,
            #                     anchor="middle"
            #                 )
            #             )
            #             st.altair_chart(bar_chart, use_container_width=True)

                                
                        

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
