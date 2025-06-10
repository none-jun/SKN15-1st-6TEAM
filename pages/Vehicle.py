import streamlit as st
import pandas as pd
import altair as alt
from urllib.error import URLError
import io
import pymysql

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
    /* 버튼 커스텀 */
    div.stButton > button {
        background-color: #0078D7;
        color: white;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        margin-top: 25px;

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

city_list = [
    "전체",
    "강원",
    "경기",
    "경남",
    "경북",
    "광주",
    "대구",
    "대전",
    "부산",
    "서울",
    "세종",
    "울산",
    "인천",
    "전남",
    "전북",
    "제주",
    "충남",
    "충북",
]
# 구 리스트는 너무 많아서 밑에서 쿼리해서 가져옴
cartype_list = ["전체", "승용차", "승합차", "화물차", "특수차량"]
fuel_list = [
    "전체",
    "CNG",
    "LNG",
    "경유",
    "기타연료",
    "등유",
    "수소",
    "알코올",
    "엘피지",
    "전기",
    "총계",
    "태양열",
    "하이브리드(CNG+전기)",
    "하이브리드(LNG+전기)",
    "하이브리드(LPG+전기)",
    "하이브리드(경유+전기)",
    "하이브리드(휘발유+전기)",
    "휘발유",
    "수소전기",
]
sex_list = ["전체", "남성", "여성"]


st.markdown("# 🚗 전국 자동차 등록 현황", unsafe_allow_html=True)

# 요약 info 박스에 카드 스타일 적용
st.markdown("", unsafe_allow_html=True)
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

"""
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("### 🔍 조회하기")


# -------------------------- 지역,차종,연료,성별 선택 부분 각각 함수 ------------------------- #

try:
    # -------------------------------- 연료 선택 시 함수 -------------------------------- #
    # @st.cache_resource
    def get_connection():
        """DB 커넥션 생성 및 캐싱"""
        return pymysql.connect(
            host="222.112.208.67",
            user="team_6",
            passwd="123",
            database="sk15_6team",
            port=3306,
        )

    def run_query(conn, query):
        """주어진 커넥션으로 쿼리 실행하고 결과 반환"""
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    @st.cache_data
    def get_fuel(city, fuel):
        """연료별 데이터 불러오기"""
        conn = get_connection()

        conditions = []
        if fuel != "전체":
            conditions.append(f"fuel_type IN ('{fuel}')")
        if city != "전체":
            conditions.append(f"region IN ('{city}')")

        where_clause = " AND ".join(conditions)

        fuel_query = run_query(
            conn,
            f"""
            SELECT *
            FROM fuel_stats f
            {"WHERE " + where_clause if where_clause else ""}
        """,
        )

        columns_query = run_query(conn, "DESC fuel_stats")
        col = [desc[0] for desc in columns_query]

        df_fuel = pd.DataFrame(fuel_query, columns=col)

        # 소계만 가져오기 , 날짜 처리
        df_fuel = df_fuel[df_fuel["vehicle_type"] == "소계"].drop(
            ["vehicle_type"], axis=1
        )
        df_fuel.reset_index(drop=True, inplace=True)
        df_fuel["ym"] = pd.to_datetime(df_fuel["ym"], errors="coerce").dt.strftime(
            "%Y-%m"
        )

        return df_fuel

    # -------------------------------- 지역 선택 시 함수 -------------------------------- #

    def get_gu_list(city):
        conn = get_connection()

        conditions = ["CHAR_LENGTH(district) > 2"]  # 기본 조건 추가

        if city != "전체":
            conditions.append(f"region LIKE '{city}%'")

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT DISTINCT district
            FROM car_stats
            WHERE {where_clause}
            ORDER BY district
        """

        gulist_query = run_query(conn, query)

        gu_list = ["전체"] + [row[0] for row in gulist_query]

        return gu_list

    @st.cache_data
    def get_city(city, gu):
        """지역별 데이터 불러오기"""
        conn = get_connection()

        # 지역 리스트 가져오기

        conditions = []
        if city != "전체":
            conditions.append(f"region IN ('{city}')")
        if gu != "전체":
            conditions.append(f"district IN ('{gu}')")

        where_clause = " AND ".join(conditions)

        fuel_query = run_query(
            conn,
            f"""
            SELECT *
            FROM car_stats f
            {"WHERE " + where_clause if where_clause else ""}
        """,
        )

        columns_query = run_query(conn, "DESC car_stats")
        col = [desc[0] for desc in columns_query]

        df_loc = pd.DataFrame(fuel_query, columns=col)

        # 소계만 가져오기 , 날짜 처리
        # df_loc = df_loc[df_loc['vehicle_type'] == '소계'].drop(['vehicle_type'], axis=1)
        # df_loc.reset_index(drop=True, inplace=True)
        df_loc["ym"] = pd.to_datetime(df_loc["ym"], errors="coerce").dt.strftime(
            "%Y-%m"
        )

        return df_loc

    # -------------------------------- 차종 선택 시 함수 -------------------------------- #

    @st.cache_data
    def get_cartype(city, cartype):
        conn = get_connection()

        # 조건 설정
        conditions = []
        if city != "전체":
            conditions.append(f"region IN ('{city}')")

        # 차종별 SQL 컬럼 선택
        if cartype == "승용차":
            sql_col = "f.passenger"
            col_names = ["passenger"]
        elif cartype == "승합차":
            sql_col = "f.ven"
            col_names = ["ven"]
        elif cartype == "화물차":
            sql_col = "f.truck"
            col_names = ["truck"]
        elif cartype == "특수차량":
            sql_col = "f.special"
            col_names = ["special"]
        else:
            col_list = ["f.passenger", "f.ven", "f.truck", "f.special"]
            sql_col = ", ".join(col_list)
            col_names = ["passenger", "ven", "truck", "special"]

        where_clause = " AND ".join(conditions)

        # 쿼리 실행
        query_result = run_query(
            conn,
            f"""
            SELECT f.ym, f.region, {sql_col}
            FROM vehicle_region f
            {"WHERE " + where_clause if where_clause else ""}
        """,
        )

        # 컬럼명 지정
        cols = ["ym", "region"] + col_names

        # 데이터프레임 생성
        df_type = pd.DataFrame(query_result, columns=cols)

        # 통합 total 컬럼 생성
        if cartype == "전체":
            df_type["total"] = df_type[["passenger", "ven", "truck", "special"]].sum(
                axis=1
            )
        else:
            df_type = df_type.rename(columns={col_names[0]: "total"})

        # 날짜 포맷 처리
        df_type["ym"] = pd.to_datetime(df_type["ym"], errors="coerce").dt.strftime(
            "%Y-%m"
        )

        return df_type

        # -------------------------------- 성별 선택 시 함수 -------------------------------- #

    @st.cache_data
    def get_sex(city, sex):
        conn = get_connection()

        # 조건 설정
        conditions = ["CHAR_LENGTH(age_group) > 2"]
        if city != "전체":
            conditions.append(f"region IN ('{city}')")
        if sex != "전체":
            conditions.append(f"gender IN ('{sex}')")

        where_clause = " AND ".join(conditions)

        # 쿼리 실행
        query_result = run_query(
            conn,
            f"""
            SELECT *
            FROM vehicle_by_demographic
            {"WHERE " + where_clause if where_clause else ""}
        """,
        )

        # 올바른 테이블에서 컬럼 정보 가져오기
        columns_query = run_query(conn, "DESC vehicle_by_demographic")
        col = [desc[0] for desc in columns_query]

        # 데이터프레임 생성
        df_sex = pd.DataFrame(query_result, columns=col)

        # 날짜 포맷 처리
        df_sex = df_sex.drop("id", axis=1)
        df_sex["ym"] = pd.to_datetime(df_sex["ym"], errors="coerce").dt.strftime(
            "%Y-%m"
        )

        return df_sex

    # ----------------------------- selectbox로 조건 선택 ----------------------------- #

    # if selection ==
    col1, col2 = st.columns(2)

    with col2:
        city = st.selectbox("지역 선택", city_list, key="city_list")
        search_clicked = st.button("조회")

    with col1:
        selection = st.selectbox(
            "조건 선택",
            ["선택하세요", "지역별", "차종별", "연료별", "성별별"],
            key="selection",
        )
        if selection == "지역별" and city:
            gu = st.selectbox("시군구 선택", get_gu_list(city))

        elif selection == "차종별":
            cartype = st.selectbox("차종별 선택", cartype_list)
        elif selection == "연료별":
            fuel = st.selectbox("연료별 선택", fuel_list)
        elif selection == "성별별":
            sex = st.selectbox("성별 선택", sex_list)
        elif selection == "선택하세요":
            st.info("조건을 선택해주세요.")

    # ------------------------------- 연료 구분 클릭 시 동작 ------------------------------ #

    if selection == "연료별" and search_clicked:
        df_fuel = get_fuel(city, fuel)
        st.write("### 📊 요약 통계")
        st.dataframe(df_fuel, use_container_width=True)

        chart = (
            alt.Chart(df_fuel)
            .mark_bar()
            .encode(
                x=alt.X(
                    "ym:T", title="", axis=alt.Axis(labelFontSize=12, labelPadding=5)
                ),
                y=alt.Y("registration_count:Q", title=""),
                color=alt.Color("fuel_type:N", title=""),
                tooltip=["ym:T", "fuel_type:N", "registration_count:Q"],
            )
        )
        st.altair_chart(chart, use_container_width=True)

    # ------------------------------ 지역 > 구 클릭 시 동작 ------------------------------ #

    if selection == "지역별" and search_clicked:
        df_loc = get_city(city, gu)
        st.write("### 📊 요약 통계")
        st.dataframe(df_loc, use_container_width=True)

        chart = (
            alt.Chart(df_loc)
            .mark_bar()
            .encode(
                x=alt.X(
                    "ym:T", title="", axis=alt.Axis(labelFontSize=12, labelPadding=5)
                ),
                y=alt.Y("total:Q", title="", scale=alt.Scale(type="log")),
                color=alt.Color("district:N", title=""),
                tooltip=["ym:T", "district:N", "total:Q"],
            )
        )
        labels = (
            alt.Chart(df_loc)
            .mark_text(
                align="center",
                baseline="bottom",
                dy=-2,  # 막대 위에 약간 띄움
                fontSize=10,
            )
            .encode(x="ym:T", y="total:Q", text=alt.Text("total:Q"))
        )

        st.altair_chart(chart + labels, use_container_width=True)

    # ------------------------------ 차종별 클릭 시 동작 ------------------------------ #

    if selection == "차종별" and search_clicked:
        try:
            df_type = get_cartype(city, cartype)
            st.write("### 📊 요약 통계")
            st.dataframe(df_type, use_container_width=True)
            # st.write(df_type)  # 확인용

            # 0 이하 제거 (로그 스케일 대비)
            df_type = df_type[df_type["total"] > 0]

            chart = (
                alt.Chart(df_type)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "ym:T",
                        title="",
                        axis=alt.Axis(labelFontSize=12, labelPadding=5),
                    ),
                    y=alt.Y("total:Q", title="", scale=alt.Scale(type="log")),
                    color=alt.Color("district:N", title=""),
                    tooltip=["ym:T", "district:N", "total:Q"],
                )
            )

            labels = (
                alt.Chart(df_type)
                .mark_text(align="center", baseline="bottom", dy=-2, fontSize=10)
                .encode(
                    x="ym:T", y="total:Q", text=alt.Text("total:Q"), angle=alt.value(60)
                )
            )

            st.altair_chart(chart + labels, use_container_width=True)

        except Exception as e:
            st.error(f"에러 발생: {e}")

    # ------------------------------- 성별 구분 클릭 시 동작 ------------------------------ #

    if selection == "성별별" and search_clicked:
        df_sex = get_sex(city, sex)
        st.write("### 📊 요약 통계")
        st.dataframe(df_sex, use_container_width=True)

        chart = (
            alt.Chart(df_sex)
            .mark_bar()
            .encode(
                x=alt.X(
                    "gender:N",
                    title="",
                    axis=alt.Axis(labelFontSize=12, labelPadding=5),
                ),
                y=alt.Y("count:Q", title=""),
                color=alt.Color("age_group:N", title=""),
                tooltip=["gender:N", "age_group:N", "count:Q"],
            )
        )
        st.altair_chart(chart, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)


except URLError as e:
    st.error(
        """
        **인터넷 연결이 필요합니다.**
        연결 오류: %s
    """
        % e.reason
    )
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ----------------------------- 엑셀 다운로드 카드 스타일 적용 ---------------------------- #

st.markdown("", unsafe_allow_html=True)
st.markdown("### 📥 엑셀 파일 다운로드")
st.write("필요한 데이터를 엑셀 파일로 다운로드할 수 있습니다.")

df = pd.DataFrame(
    {
        "이름": ["홍길동", "김철수", "이영희"],
        "지역": ["서울", "부산", "대전"],
        "등록 차량 수": [1200, 850, 430],
    }
)

# def to_excel_bytes(df):
#     output = io.BytesIO()
#     with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#         df.to_excel(writer, index=False, sheet_name="Sheet1")
#     return output.getvalue()

# if st.button("엑셀 생성"):
#     excel_bytes = to_excel_bytes(df_fuel)
#     st.download_button(
#         label="📥 엑셀 다운로드",
#         data=excel_bytes,
#         file_name="vehicle_data.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#     )
# st.markdown('</div>', unsafe_allow_html=True)


# ----------------------------------- 사이드바 ----------------------------------- #

st.sidebar.header("전국 자동차 등록 현황")
st.sidebar.markdown("### 🛠️ 사용법")
st.sidebar.markdown(
    """
- 원하는 조건, 지역을 선택하세요.  
- 조건별로 변경되는 추가 조건을 선택하세요
- 데이터베이스 연결 상태에 따라 로딩 시간이 걸릴 수 있습니다.
"""
)
