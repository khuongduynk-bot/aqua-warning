from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PondData(BaseModel):
    T: float
    D: float
    A: float
    O: float

# ================= CẤU HÌNH TELEGRAM =================
TELEGRAM_TOKEN = "8896827968:AAEDS2EOormXaM0CnnDe7mzDcedDDYPc9M4"
CHAT_ID = "-1004396439890"

def send_telegram_alert(message_text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Lỗi khi gửi Telegram:", e)
# =====================================================

def calc_F(O, T, Density, Aeration):
    T_K = T + 273.15
    ln_Osat = -139.34411 + (1.575701e5 / T_K) - (6.642308e7 / (T_K**2)) + \
              (1.243800e10 / (T_K**3)) - (8.621949e11 / (T_K**4))
    Osat = np.exp(ln_Osat)
    k1 = 0.1 + (Aeration * 0.05)
    W_fish = Density * 0.006
    M_sed = 3.5
    K = 1.5
    return k1 * (Osat - O) - (W_fish + M_sed * (K**2) / (K**2 + O**2))

@app.post("/predict")
async def predict_tipping_point(data: PondData):
   # 1. TÍNH TOÁN LÝ THUYẾT (LUÔN CHẠY ĐỂ VẼ ĐỒ THỊ)
    O_vals = np.linspace(0, 10, 100)
    F_vals = calc_F(O_vals, data.T, data.D, data.A)
    max_F = np.max(F_vals)

    # 2. XÁC ĐỊNH TRẠNG THÁI DỰA TRÊN LÝ THUYẾT
    if max_F < 0:
        status = "RED"
        message = "VƯỢT ĐIỂM LẬT - BÙN ĐÁY BÙNG NỔ"
    elif 0 <= max_F < 0.8:
        status = "YELLOW"
        message = "CẢNH BÁO NGUY HIỂM - SẮP CHẠM ĐIỂM LẬT"
    else:
        status = "GREEN"
        message = "AO AN TOÀN"

    # 3. CHỐT CHẶN PHẦN CỨNG: GHI ĐÈ BẰNG OXY THỰC TẾ
    if data.O <= 2.5:
        status = "RED"
        message = f"BÁO ĐỘNG KHẨN: Lượng Oxy ({data.O} mg/L) rớt xuống mức nguy hiểm gây ngạt!"
    elif data.O <= 3.5 and status != "RED":
        status = "YELLOW"
        message = f"LƯU Ý: Lượng Oxy ({data.O} mg/L) đang suy giảm, cần tăng sục khí."

    # 4. GỬI TIN NHẮN TELEGRAM THEO TRẠNG THÁI CUỐI CÙNG
    if status == "RED":
        alert_msg_red = (
            f"🚨 *BÁO ĐỘNG ĐỎ: AO NUÔI VƯỢT ĐIỂM LẬT HOẶC THIẾU OXY* 🚨\n\n"
            f"📊 *Thông số hiện tại:*\n"
            f"🌡 Nhiệt độ: {data.T} °C\n"
            f"🐟 Mật độ: {data.D} con/m²\n"
            f"💨 Sục khí: {data.A} giờ/ngày\n"
            f"💧 Oxy hòa tan: {data.O} mg/L\n\n"
            f"❌ {message}\nYêu cầu cấp cứu ao ngay lập tức!"
        )
        send_telegram_alert(alert_msg_red)
        
    elif status == "YELLOW":
        alert_msg_yellow = (
            f"⚠️ *CẢNH BÁO SỚM: AO NUÔI ĐANG SUY YẾU* ⚠️\n\n"
            f"📊 *Thông số hiện tại:*\n"
            f"🌡 Nhiệt độ: {data.T} °C\n"
            f"🐟 Mật độ: {data.D} con/m²\n"
            f"💨 Sục khí: {data.A} giờ/ngày\n"
            f"💧 Oxy hòa tan: {data.O} mg/L\n\n"
            f"⚡ {message}\nHãy bật thêm quạt nước để phòng ngừa!"
        )
        send_telegram_alert(alert_msg_yellow)
        
    return {
        "status": status,
        "message": message,
        "max_resilience": float(max_F),
        "graph_x": O_vals.tolist(),
        "graph_y": F_vals.tolist()
    }
