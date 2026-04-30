from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, firestore, auth
import uuid
from datetime import datetime

# 1. Khởi tạo Firebase Admin (Dùng file JSON chìa khóa vạn năng)
cred = credentials.Certificate("firebase-credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI(title="Expense Manager API - Secured")
    
# Schema dữ liệu cho Giao dịch
class Transaction(BaseModel):
    amount: float
    type: str # "thu" hoặc "chi"
    description: str

# ==========================================
# HÀM BẢO VỆ (SECURITY DEPENDENCY)
# ==========================================
def verify_token(authorization: str = Header(None)):
    """
    Hàm này đóng vai trò 'bảo vệ cổng'. 
    Nó sẽ kiểm tra xem request có gửi kèm Token hợp lệ không.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Thiếu thẻ thông hành (Token)!")
    
    # Lấy chuỗi Token sau chữ "Bearer "
    id_token = authorization.split("Bearer ")[1]
    
    try:
        # Nhờ Firebase Auth xác minh chiếc thẻ này
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token # Trả về thông tin người dùng nếu hợp lệ
    except Exception:
        raise HTTPException(status_code=401, detail="Thẻ thông hành không hợp lệ hoặc đã hết hạn!")

# ==========================================
# CÁC ENDPOINTS (ĐÃ ĐƯỢC LẮP Ổ KHÓA)
# ==========================================

@app.post("/transactions")
def create_transaction(transaction: Transaction, user=Depends(verify_token)):
    # Chỉ khi verify_token thành công, code ở đây mới được chạy
    try:
        new_id = str(uuid.uuid4())
        new_record = transaction.dict()
        new_record["id"] = new_id
        new_record["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Lưu thêm email người dùng để biết ai là người nhập
        new_record["user_email"] = user.get("email") 
        
        db.collection("transactions").document(new_id).set(new_record)
        return {"message": "Thêm thành công", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transactions")
def get_transactions(user=Depends(verify_token)):
    try:
        docs = db.collection("transactions").stream()
        transactions = []
        balance = 0
        
        for doc in docs:
            data = doc.to_dict()
            transactions.append(data)
            # Tính toán số dư
            if data["type"] == "thu":
                balance += data["amount"]
            else:
                balance -= data["amount"]
                
        return {
            "total_records": len(transactions),
            "balance": balance,
            "data": transactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))