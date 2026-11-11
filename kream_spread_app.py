import streamlit as st
import pandas as pd
import requests
import json
import time

st.set_page_config(page_title="KREAM 실시간 스프레드 체커", page_icon="👟", layout="centered")

st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #28a745;
    }
    .tight-spread {
        color: #e03131;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("👟 KREAM 스프레드 갭 체커")
st.caption("구매희망가와 판매희망가(호가 갭)가 가장 좁은 실시간 환금성 종목 모니터링")

# 기본 감시 대상 (유동성 최상위 스테디셀러 품목)
DEFAULT_TARGETS = [
    {"name": "Apple 에어팟 프로 2세대 USB-C (국내정품)", "id": "180295", "cat": "테크"},
    {"name": "Nike 에어포스 1 '07 로우 화이트", "id": "28", "cat": "스니커즈"},
    {"name": "Adidas 삼바 OG 클라우드 화이트", "id": "84705", "cat": "스니커즈"},
    {"name": "Adidas 삼바 OG 코어 블랙", "id": "84706", "cat": "스니커즈"},
    {"name": "Nintendo Switch OLED 본체 화이트 (국내정품)", "id": "37752", "cat": "테크"},
    {"name": "Asics 젤 카야노 14 화이트 미드나잇", "id": "100142", "cat": "스니커즈"},
    {"name": "Supreme Hanes 태그리스 티셔츠 화이트 (3팩)", "id": "3213", "cat": "잡화"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://kream.co.kr/",
    "x-kream-api-version": "39",
    "x-kream-web-request-secret": "kream-djscjsghdkd",
}

@st.cache_data(ttl=60)
def fetch_product_spread(product_id):
    """크림 상품 호가(Ask/Bid) 조회 및 스프레드 계산"""
    url = f"https://api.kream.co.kr/api/p/products/{product_id}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json()
            market_price = data.get("market_price", {})
            lowest_ask = market_price.get("lowest_ask")  # 즉시구매가(최저 판매가)
            highest_bid = market_price.get("highest_bid") # 즉시판매가(최고 구매가)
            
            if lowest_ask and highest_bid:
                spread = lowest_ask - highest_bid
                spread_pct = round((spread / highest_bid) * 100, 2)
                return {
                    "lowest_ask": lowest_ask,
                    "highest_bid": highest_bid,
                    "spread": spread,
                    "spread_pct": spread_pct,
                    "status": "정상"
                }
    except Exception as e:
        pass
    return None

col1, col2 = st.columns([3, 1])
with col1:
    max_gap = st.slider("최대 허용 스프레드 (원)", 1000, 30000, 5000, step=1000)
with col2:
    if st.button("🔄 실시간 새로고침"):
        st.cache_data.clear()
        st.rerun()

results = []
progress_bar = st.progress(0)

for idx, target in enumerate(DEFAULT_TARGETS):
    data = fetch_product_spread(target["id"])
    if data:
        results.append({
            "상품명": target["name"],
            "카테고리": target["cat"],
            "즉시구매가 (판매호가)": f"{data['lowest_ask']:,}원",
            "즉시판매가 (구매호가)": f"{data['highest_bid']:,}원",
            "호가 갭 (스프레드)": data["spread"],
            "스프레드율": f"{data['spread_pct']}%",
            "링크": f"https://kream.co.kr/products/{target['id']}",
            "raw_spread": data["spread"]
        })
    progress_bar.progress((idx + 1) / len(DEFAULT_TARGETS))

progress_bar.empty()

if results:
    # 스프레드가 가장 작은 순서대로 정렬
    results.sort(key=lambda x: x["raw_spread"])
    
    # 필터링
    filtered = [r for r in results if r["raw_spread"] <= max_gap]
    
    st.subheader(f"🎯 갭 {max_gap:,}원 이하 추천 종목 ({len(filtered)}개)")
    
    for item in filtered:
        with st.container():
            st.markdown(f"""
            <div class="metric-card">
                <h4>{item['상품명']} <span style="font-size:12px; color:#888;">[{item['카테고리']}]</span></h4>
                <p style="margin:5px 0;">
                    즉시구매가: <b>{item['즉시구매가 (판매호가)']}</b> | 
                    즉시판매가: <b>{item['즉시판매가 (구매호가)']}</b>
                </p>
                <p style="margin:5px 0; font-size:16px;">
                    호가 갭: <span class="tight-spread">{item['호가 갭 (스프레드)']:,}원</span> ({item['스프레드율']})
                </p>
                <a href="{item['링크']}" target="_blank" style="text-decoration:none; background:#222; color:#fff; padding:5px 10px; border-radius:5px; font-size:12px;">크림 바로가기 ↗</a>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("📊 전체 종목 순위표 보기"):
        df = pd.DataFrame(results).drop(columns=["raw_spread"])
        st.dataframe(df, use_container_width=True)
else:
    st.info("데이터를 불러오는 중이거나 장중 호가 데이터가 갱신 중입니다.")
