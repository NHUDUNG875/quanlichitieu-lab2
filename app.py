import streamlit as st
import requests

# ==========================================
# CẤU HÌNH (Thay API Key của em vào đây)
# ==========================================
FIREBASE_WEB_API_KEY = "AIzaSyD-JtfIFpQQCEhJ6XYQvIpBCIFfpTSVIXY"
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Expense Manager", page_icon="💰", layout="wide")

# Khởi tạo trạng thái hệ thống
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "id_token" not in st.session_state:
    st.session_state.id_token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# Hàm gọi Firebase để kiểm tra tài khoản
def login_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    return requests.post(url, json=payload)

# ==========================================
# 1. MÀN HÌNH ĐĂNG NHẬP
# ==========================================
if not st.session_state.logged_in:
    st.title("🔐 Đăng nhập hệ thống")
    with st.container():
        email = st.text_input("Email")
        password = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            res = login_user(email, password)
            if res.status_code == 200:
                data = res.json()
                st.session_state.logged_in = True
                st.session_state.id_token = data["idToken"] # Lưu "thẻ thông hành"
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Email hoặc mật khẩu không đúng!")
else:
    # ==========================================
    # 2. GIAO DIỆN CHÍNH (Sau khi đã đăng nhập)
    # ==========================================
    with st.sidebar:
        st.success(f"👤 {st.session_state.user_email}")
        if st.button("Đăng xuất"):
            st.session_state.logged_in = False
            st.session_state.id_token = None
            st.rerun()

    st.title("💰 Quản lý Chi Tiêu Cá Nhân")
    
    # CHUẨN BỊ THẺ THÔNG HÀNH (TOKEN)
    # Đây là dòng quan trọng nhất: kẹp Token vào Header
    headers = {"Authorization": f"Bearer {st.session_state.id_token}"}

    # --- PHẦN NHẬP DỮ LIỆU ---
    st.subheader("📝 Thêm giao dịch mới")
    with st.expander("Bấm để mở form nhập", expanded=True):
        with st.form("transaction_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input("Số tiền (VNĐ)", min_value=0, step=1000)
            with col2:
                trans_type = st.selectbox("Loại giao dịch", ["thu", "chi"])
            
            description = st.text_input("Mô tả chi tiết")
            
            if st.form_submit_button("Lưu Giao Dịch"):
                if amount > 0 and description:
                    payload = {"amount": amount, "type": trans_type, "description": description}
                    
                    # GỬI KÈM HEADERS CÓ TOKEN
                    res = requests.post(f"{BACKEND_URL}/transactions", json=payload, headers=headers)
                    
                    if res.status_code == 200:
                        st.toast("✅ Đã lưu thành công!", icon='🎉')
                    elif res.status_code == 401:
                        st.error("Phiên đăng nhập hết hạn, vui lòng đăng nhập lại!")
                    else:
                        st.error("Lỗi: Không thể lưu dữ liệu.")
                else:
                    st.warning("Vui lòng nhập đủ thông tin!")

    st.markdown("---")

    # --- PHẦN THỐNG KÊ ---
    st.subheader("📊 Lịch sử giao dịch")
    if st.button("🔄 Cập nhật danh sách"):
        # GỬI KÈM HEADERS CÓ TOKEN
        res = requests.get(f"{BACKEND_URL}/transactions", headers=headers)
        
        if res.status_code == 200:
            data = res.json()
            st.metric(label="TỔNG SỐ DƯ", value=f"{int(data['balance']):,} VNĐ")
            
            if data["total_records"] > 0:
                display_data = []
                for item in data["data"]:
                    # Chỉ hiển thị giao dịch của chính người đang đăng nhập (nếu em muốn lọc)
                    clean_item = {
                        "Ngày": item.get("created_at", "N/A"),
                        "Loại": "➕ Thu" if item["type"] == "thu" else "➖ Chi",
                        "Mô tả": item["description"],
                        "Số tiền": f"{int(item['amount']):,} VNĐ"
                    }
                    display_data.append(clean_item)
                st.table(display_data)
            else:
                st.info("Chưa có dữ liệu nào.")
        elif res.status_code == 401:
            st.error("Thẻ thông hành không hợp lệ. Vui lòng đăng xuất và đăng nhập lại!")