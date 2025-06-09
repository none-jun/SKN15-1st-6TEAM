import streamlit as st
import pandas as pd
import pydeck as pdk
from urllib.error import URLError
import altair as alt
import pymysql


st.set_page_config(page_title="ranking", page_icon="📊")

st.markdown("# 브랜드별 추이")
st.sidebar.header("브랜드별 추이 (연월)")

st.write("")
st.write("")
st.info(
    """ 다나와 사이트 데이터
   - 브랜드별 추이 (연월)
   - 기간 : 2023.01 ~ 2025.05 
"""
)
st.write("")
st.write("")

# ---------------------------------- 컬럼 연결 ---------------------------------- #


# conn = pymysql.connect(host = '192.168.0.22', user = 'team_6' ,passwd='123', database='sk15_6team', port = 3306)
# cur = conn.cursor()

# def get_sql(query):
#   cur.execute(query)
#   return cur.fetchall()

# brand_sql = get_sql('''select distinct(d.brand)
# from danawa d''')
# [b[0] for b in brand_sql]

brand_idx = ['BMW','BYD','DS','GMC','KGM','기아','람보르기니','랜드로버','렉서스','롤스로이스','르노코리아','링컨','마세라티','미니','벤츠','벤틀리','볼보','쉐보레','아우디','재규어','제네시스','지프','캐딜락','테슬라','토요타','페라리','포드','포르쉐','폭스바겐','폴스타','푸조','현대','혼다']

if st.button('조회'):

    # -------------------------------- example 부분 -------------------------------- #

    @st.cache_data
    def get_UN_data():
        AWS_BUCKET_URL = "http://streamlit-demo-data.s3-us-west-2.amazonaws.com"
        df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
        return df.set_index("Region")


    try:
        df = get_UN_data()
        countries = st.multiselect(
            "Choose countries", brand_idx, []
        )
        if not countries:
            st.error("Please select at least one country.")
        else:
            data = df.loc[countries]
            data /= 1000000.0
            st.write("### 요약 통계 그래프", data.sort_index())

            data = data.T.reset_index()
            data = pd.melt(data, id_vars=["index"]).rename(
                columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
            )
            chart = (
                alt.Chart(data)
                .mark_line()
                .encode(
                    x="year:T",
                    y=alt.Y("Gross Agricultural Product ($B):Q"),
                    color="Region:N",
                )
            )

            st.altair_chart(chart, use_container_width=True)
    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**
            Connection error: %s
        """
            % e.reason
        )

