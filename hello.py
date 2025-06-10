
import streamlit as st
import base64
import os
st.set_page_config(page_title="자동차 통계 홈", layout="wide")

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64_1 = get_base64_image("./image 3.png")
img_base64_2 = get_base64_image("./image 4.png") # 나중에 등록 현황 이미지 넣을 경우

st.markdown("""
<style>
.page-wrapper {
    padding: 100px 20px 80px 20px;
}
.title-box {
    text-align: center;
    margin-bottom: 80px;
}
.title-box h2 {
    font-size: 40px;
    font-weight: 700;
    line-height: 1.6;
    margin-bottom: 12px;
}
.title-box p {
    color: #666;
    font-size: 18px;
}
.section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1100px;
    margin: 0 auto;
    padding: 60px 0;
    flex-wrap: wrap;
    gap: 60px;
}
.section.reverse {
    flex-direction: row-reverse;
}
.text-box {
    max-width: 520px;
    flex: 1;
}
.text-box h1, .text-box h3 {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 20px;
}
.text-box ul {
    font-size: 17px;
    line-height: 1.8;
    color: #444;
    padding-left: 20px;
}
.image-box {
    flex-shrink: 0;
}
@media screen and (max-width: 900px) {
    .section {
        flex-direction: column !important;
        text-align: center;
    }
    .image-box, .text-box {
        margin-bottom: 30px;
    }
}
.image-box img {
    width: 100%;
    max-width: 480px;
    height: auto;
    background-color: #eee;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="page-wrapper">
    <!-- 상단 제목 -->
    <div class="title-box">
        <h2>자동차 시장의 모든 데이터를 한 곳에</h2>
        <p>판매량부터 등록현황까지, 차량 데이터 모음집</p>
    </div>
    <!-- ✅ 브랜드: 이미지 오른쪽 -->
    <!-- 브랜드별 판매 통계: 이미지 오른쪽 / 텍스트 왼쪽 -->
    <div class="section">
        <div class="text-box">
            <div style="color:#1E3A8A; font-size:35px; font-weight:700; margin-bottom:16px;">🚗어떤 차가 실제로 팔리고 있을까?</div>
            <div style="font-size:20px; font-weight:700; line-height:1.2;">
            월별 판매 트렌드 확인하기
            </div>
            <div style="margin-top:16px;">
                <a href="/brand" target="_self" style="display:inline-block; padding:10px 18px; background-color:#3478f6; color:white; border-radius:6px; text-decoration:none; font-weight:600; margin-top:20px;">
                자세히 보기 →
                </a>
            </div>
        </div>  <!-- ✅ text-box 닫힘 -->
            <div class="image-box">
            <img src="data:image/png;base64,{img_base64_1}" />
        </div>
    </div>
    <!-- 전국 등록 현황: 이미지 왼쪽 / 텍스트 오른쪽 -->
    <div class="section">
        <div class="image-box">
            <img src="data:image/png;base64,{img_base64_2}" />
        </div>
        <div class="text-box">
            <div style="color:#3478f6; font-size:30px; font-weight:600; margin-bottom:30px;">전국 등록 현황</div>
            <div style="font-size:20px; font-weight:700; line-height:1.5;">
                지역별 등록 현황을<br>
                차종과 지역 특성에 따라 비교해보세요.
            </div>
            <a href="/Vehicle" target="_self" style="display:inline-block; padding:10px 18px; background-color:#3478f6; color:white; border-radius:6px; text-decoration:none; font-weight:600; margin-top:20px;">
                자세히 보기 →
            </a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
