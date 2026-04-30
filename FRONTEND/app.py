import streamlit as st
import requests
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2

# ==========================================
# 1. CẤU HÌNH TỔNG HỢP (HÃY ĐIỀN ĐỦ 4 MÃ)
# ==========================================
CLIENT_ID = "NHẬP_CLIENT_ID_CỦA_BẠN_VÀO_ĐÂY"
CLIENT_SECRET = "NHẬP_CLIENT_SECRET_CỦA_BẠN_VÀO_ĐÂY"
FIREBASE_WEB_API_KEY = "NHẬP_FIREBASE_API_KEY_CỦA_BẠN_VÀO_ĐÂY"
REDIRECT_URI = "http://localhost:8501"

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Expense Manager", page_icon="💰", layout="wide")

# Khởi tạo trạng thái đăng nhập
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

client = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)

# ==========================================
# 2. CÁC HÀM XỬ LÝ XÁC THỰC
# ==========================================

# Cách 1: Đăng nhập thủ công qua Firebase
def login_manual(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    return requests.post(url, json=payload)

# Cách 2: Xử lý Code từ Google trả về để đổi lấy Token Firebase
async def process_google_login(code):
    # Lấy token từ Google
    token_data = await client.get_access_token(code, REDIRECT_URI)
    google_id_token = token_data["id_token"]
    
    # Đổi sang Token Firebase
    idp_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_WEB_API_KEY}"
    payload = {
        "postBody": f"id_token={google_id_token}&providerId=google.com",
        "requestUri": "http://localhost",
        "returnSecureToken": True
    }
    return requests.post(idp_url, json=payload)

# Kiểm tra nếu có mã code từ Google trên URL
query_params = st.query_params
if "code" in query_params and not st.session_state.auth_token:
    code = query_params.get("code")
    res = asyncio.run(process_google_login(code))
    if res.status_code == 200:
        data = res.json()
        st.session_state.auth_token = data["idToken"]
        st.session_state.user_email = data.get("email")
        st.query_params.clear()
        st.rerun()

# ==========================================
# 3. GIAO DIỆN ĐĂNG NHẬP (2 TRONG 1)
# ==========================================
if not st.session_state.auth_token:
    st.title("💰 Expense Manager Login")
    
    col_a, col_b = st.columns([1, 1], gap="large")
    
    with col_a:
        st.subheader("🔑 Đăng nhập thủ công")
        with st.form("manual_login"):
            m_email = st.text_input("Email")
            m_pass = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("Đăng nhập ngay"):
                res = login_manual(m_email, m_pass)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.auth_token = data["idToken"]
                    st.session_state.user_email = m_email
                    st.rerun()
                else:
                    st.error("Sai email hoặc mật khẩu!")

    with col_b:
        st.subheader("🌐 Đăng nhập nhanh")
        st.write("Sử dụng tài khoản Google để vào hệ thống ngay lập tức mà không cần nhớ mật khẩu.")
        auth_url = asyncio.run(client.get_authorization_url(REDIRECT_URI, scope=["openid", "email", "profile"]))
        st.link_button("🚀 Tiếp tục với Google", auth_url)

# ==========================================
# 4. GIAO DIỆN CHÍNH (SAU ĐĂNG NHẬP)
# ==========================================
else:
    with st.sidebar:
        st.success(f"👤 {st.session_state.user_email}")
        if st.button("Đăng xuất"):
            st.session_state.auth_token = None
            st.rerun()

    st.title("📊 Quản lý Chi tiêu")
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}

    # Form nhập và Bảng hiển thị (Giữ nguyên logic cũ của em)
    st.subheader("📝 Nhập giao dịch")
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        amount = c1.number_input("Số tiền (VNĐ)", min_value=0, step=1000)
        t_type = c2.selectbox("Loại", ["thu", "chi"])
        desc = st.text_input("Mô tả")
        if st.form_submit_button("Lưu"):
            payload = {"amount": amount, "type": t_type, "description": desc}
            requests.post(f"{BACKEND_URL}/transactions", json=payload, headers=headers)
            st.toast("Đã lưu!")

    if st.button("🔄 Tải dữ liệu"):
        res = requests.get(f"{BACKEND_URL}/transactions", headers=headers)
        if res.status_code == 200:
            data = res.json()
            st.metric("SỐ DƯ", f"{int(data['balance']):,} VNĐ")
            
            # THÊM ĐOẠN NÀY ĐỂ LÀM ĐẸP CỘT AMOUNT
            if data["total_records"] > 0:
                for item in data["data"]:
                    # Ép kiểu int để mất đuôi .0000, sau đó thêm dấu phẩy
                    item["amount"] = f"{int(item['amount']):,}" 
                    
                st.table(data["data"])
            else:
                st.info("Chưa có dữ liệu giao dịch nào.")