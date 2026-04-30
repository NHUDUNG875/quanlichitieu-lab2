
# Dự Án Quản Lý Chi Tiêu (Expense Manager)

**Bài tập Thực hành (Lab 2)**

Dự án này là một hệ thống Web Application giúp người dùng ghi chép và quản lý chi tiêu cá nhân. Hệ thống được thiết kế theo kiến trúc **Microservices (Client-Server)** với Backend và Frontend tách biệt hoàn toàn, giao tiếp qua RESTful API và bảo mật bằng chuẩn **Bearer Token** (Firebase Auth & Google OAuth 2.0).

---

## Đường dẫn đến video demo

**[CHÈN LINK VIDEO DEMO YOUTUBE HOẶC GOOGLE DRIVE CỦA EM VÀO ĐÂY]**
*(Lưu ý: Nếu dùng Google Drive, hãy nhớ bật quyền chia sẻ "Bất kỳ ai có đường liên kết đều có thể xem")*

---

## 🛠 Hướng dẫn cài đặt environment

Dự án này yêu cầu máy tính phải có sẵn **Python 3.9+**. 
Vì dự án chia làm 2 phân hệ độc lập (Backend và Frontend), chúng ta cần thiết lập 2 môi trường ảo (virtual environment - `venv`) riêng biệt để tránh xung đột thư viện.

**Bước 1:** Mở thư mục gốc `LAB2/` bằng Terminal (hoặc VS Code).

**Bước 2:** Cài đặt môi trường ảo cho Backend.
```bash
cd BACKEND
python -m venv venv
cd ..
```

**Bước 3:** Cài đặt môi trường ảo cho Frontend.
```bash
cd FRONTEND
python -m venv venv
cd ..
```
## Hướng dẫn chạy Backend
Backend chịu trách nhiệm xử lý logic API và kết nối với cơ sở dữ liệu Firebase Firestore.

**Yêu cầu quan trọng trước khi chạy:** Đảm bảo bạn đã đặt file chìa khóa bảo mật firebase-credentials.json vào bên trong thư mục BACKEND/.

**1. Mở Terminal 1, di chuyển vào thư mục Backend:**
```bash
cd BACKEND
```
**2. Kích hoạt môi trường ảo (venv):**

Trên Windows: `venv\Scripts\activate`

Trên macOS/Linux: `source venv/bin/activate`

**3. Cài đặt các thư viện cần thiết:**
```bash
pip install -r requirements.txt
```
**4. Khởi chạy Server FastAPI:**
```bash
uvicorn main:app --reload
```
> *Backend đã khởi chạy thành công tại: `http://127.0.0.1:8000`*
   > *Tài liệu Swagger UI: `http://127.0.0.1:8000/docs`*

---

## Hướng dẫn chạy Frontend

Frontend cung cấp giao diện Web trực quan (viết bằng Streamlit) cho phép người dùng đăng nhập và thao tác với dữ liệu.

**1. Mở Terminal 2 (Giữ Terminal 1 vẫn đang chạy Backend), di chuyển vào thư mục Frontend:**
   ```bash
   cd FRONTEND
   ```
**2. Kích hoạt môi trường ảo (venv):**

Trên Windows: `venv\Scripts\activate`

Trên macOS/Linux: `source venv/bin/activate`

**3. Cài đặt các thư viện cần thiết:**

```bash
pip install -r requirements.txt
```
**4. Khởi chạy Giao diện Streamlit:**
```bash
streamlit run app.py
```
Trình duyệt sẽ tự động mở giao diện ứng dụng tại: http://localhost:8501

## Hướng dẫn Kiểm thử Hệ thống
Để kiểm thử việc gọi API lấy dữ liệu, giảng viên có thể sử dụng 1 trong 2 phương thức đăng nhập trên giao diện Web:

1. Đăng nhập thủ công: Sử dụng tài khoản test đã tạo trên Firebase.

2. Đăng nhập nhanh: Bấm vào nút "Tiếp tục với Google" để test luồng cấp quyền OAuth 2.0.

Sau khi đăng nhập thành công, Frontend sẽ tự động đính kèm ID Token vào Header của mọi request gửi xuống Backend để vượt qua lớp bảo mật xác thực.