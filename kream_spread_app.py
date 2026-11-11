import streamlit as st

st.set_page_config(
    page_title="내 신발 시세 & 방출 비교기",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .card {
        background-color: #1e1e1e;
        color: #ffffff;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 14px;
        border: 1px solid #333333;
    }
    .platform-btn-kream {
        display: block;
        width: 100%;
        text-align: center;
        background-color: #222222;
        color: #ffffff !important;
        border: 1px solid #555555;
        padding: 10px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        margin-top: 8px;
    }
    .platform-btn-stockx {
        display: block;
        width: 100%;
        text-align: center;
        background-color: #006340;
        color: #ffffff !important;
        padding: 10px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        margin-top: 8px;
    }
    .platform-btn-bunjang {
        display: block;
        width: 100%;
        text-align: center;
        background-color: #e03131;
        color: #ffffff !important;
        padding: 10px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        margin-top: 8px;
    }
    .badge {
        background: #333;
        color: #00ff88;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("📦 내 창고 신발 방출 & 시세 비교기")
st.caption("SKU(품번) 하나로 크림 · 스탁X · 번개장터 실시간 시세를 0.1초 만에 비교")

# 세션 상태에 인벤토리 보관
if "inventory" not in st.session_state:
    st.session_state.inventory = [
        {"sku": "GX0054", "name": "아디다스 이지 NSLTD 부츠 카키", "memo": "창고 보관 중 / 탈취 후 처분 예정"},
        {"sku": "1201A019-108", "name": "아식스 젤 카야노 14 크림 블랙", "memo": "최근 출고 / 시세 모니터링"},
        {"sku": "CW2288-111", "name": "나이키 에어포스 1 '07 로우 올백", "memo": "환금성 최강 스테디셀러"}
    ]

# 1. 새 상품 검색 및 인벤토리 추가
st.subheader("🔍 품번(SKU) 시세 조회")

col_input1, col_input2 = st.columns([3, 1])
with col_input1:
    search_sku = st.text_input("신발 박스 라벨 품번 입력", placeholder="예: GX0054, B75806, DD1391-100").strip().upper()
with col_input2:
    search_name = st.text_input("상품 메모 (선택)", placeholder="예: 270 사이즈")

if search_sku:
    kream_url = f"https://kream.co.kr/search?keyword={search_sku}"
    stockx_url = f"https://stockx.com/search?s={search_sku}"
    bunjang_url = f"https://m.bunjang.co.kr/search/products?q={search_sku}"
    
    st.markdown(f"""
    <div class="card">
        <span class="badge">검색 결과 · SKU: {search_sku}</span>
        <h3 style="margin: 8px 0;">{search_name if search_name else search_sku}</h3>
        <p style="font-size:12px; color:#aaa; margin:0 0 10px 0;">아래 버튼을 누르면 해당 플랫폼 시세·호가 화면으로 바로 이동합니다.</p>
        <a class="platform-btn-kream" href="{kream_url}" target="_blank">👟 KREAM 크림 실시간 호가 확인 ↗</a>
        <a class="platform-btn-stockx" href="{stockx_url}" target="_blank">🟢 StockX 스탁X 글로벌 시세 확인 ↗</a>
        <a class="platform-btn-bunjang" href="{bunjang_url}" target="_blank">⚡ 번개장터 최근 실거래·매물 확인 ↗</a>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕ 내 방출 목록에 추가하기"):
        st.session_state.inventory.append({
            "sku": search_sku,
            "name": search_name if search_name else search_sku,
            "memo": "직접 추가된 상품"
        })
        st.success(f"'{search_sku}'이(가) 내 방출 목록에 추가되었습니다!")
        st.rerun()

# 2. 내 창고 방출 보관함
st.markdown("---")
st.subheader(f"📋 내 방출 인벤토리 ({len(st.session_state.inventory)}개)")

for idx, item in enumerate(st.session_state.inventory):
    sku = item['sku']
    k_url = f"https://kream.co.kr/search?keyword={sku}"
    s_url = f"https://stockx.com/search?s={sku}"
    b_url = f"https://m.bunjang.co.kr/search/products?q={sku}"
    
    with st.expander(f"🏷️ [{sku}] {item['name']}", expanded=(idx==0)):
        st.caption(f"메모: {item['memo']}")
        st.markdown(f"""
        <div style="display:flex; flex-direction:column; gap:6px; margin: 10px 0;">
            <a class="platform-btn-kream" href="{k_url}" target="_blank">👟 크림 실시간 호가 ↗</a>
            <a class="platform-btn-stockx" href="{s_url}" target="_blank">🟢 스탁X 글로벌 시세 ↗</a>
            <a class="platform-btn-bunjang" href="{b_url}" target="_blank">⚡ 번개장터 중고·신품 시세 ↗</a>
        </div>
        """, unsafe_allow_html=True)

# 3. 플랫폼별 실수령액 비교 계산기
st.markdown("---")
st.subheader("🧮 플랫폼별 실제 정산액 비교 계산기")
st.caption("예상 판매가를 입력하면 수수료를 뺀 실제 통장 입금액을 비교합니다.")

target_price = st.number_input("판매 목표 금액 (원)", value=200000, step=10000)

kream_fee = int(target_price * 0.033) # 크림 일반 판매 수수료 약 3.3%
kream_net = target_price - kream_fee

stockx_fee = int(target_price * 0.095) # 스탁X 판매자 수수료 + 정산 수수료 약 9.5%
stockx_net = target_price - stockx_fee

bunjang_fee = 0 # 일반 번개 직거래 시 0원, 번개페이는 약 3.5%
bunjang_net = target_price

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="크림 실수령액", value=f"{kream_net:,}원", delta=f"-{kream_fee:,}원 (3.3%)")
with col2:
    st.metric(label="스탁X 실수령액", value=f"{stockx_net:,}원", delta=f"-{stockx_fee:,}원 (9.5%)")
with col3:
    st.metric(label="번장 직거래", value=f"{bunjang_net:,}원", delta="수수료 0원")
