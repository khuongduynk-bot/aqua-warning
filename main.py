@app.post("/predict")
def predict_tipping_point(data: PondData):
    O_vals = np.linspace(0, 10, 100)
    F_vals = calc_F(O_vals, data.T, data.D, data.A)
    max_F = np.max(F_vals)
    
    if max_F < 0:
        status = "RED"
        message = "VƯỢT ĐIỂM LẬT - BÙN ĐÁY BÙNG NỔ"
        
        # Tin nhắn khi đã toang (ĐỎ)
        alert_msg_red = (
            f"🚨 *BÁO ĐỘNG ĐỎ: AO NUÔI ĐÃ VƯỢT ĐIỂM LẬT* 🚨\n\n"
            f"📊 *Thông số hiện tại:*\n"
            f"🌡️ Nhiệt độ: {data.T} °C\n"
            f"🐟 Mật độ: {data.D} con/m²\n"
            f"💨 Sục khí: {data.A} giờ/ngày\n\n"
            f"❌ HỆ SINH THÁI SUY SỤP! Yêu cầu cấp cứu ao ngay lập tức!"
        )
        send_telegram_alert(alert_msg_red)
        
    elif 0 <= max_F < 0.8:
        status = "YELLOW"
        message = "CẢNH BÁO NGUY HIỂM - SẮP CHẠM ĐIỂM LẬT"
        
        # BỔ SUNG: Tin nhắn cảnh báo sớm (VÀNG)
        alert_msg_yellow = (
            f"⚠️ *CẢNH BÁO SỚM: AO NUÔI SẮP CHẠM ĐIỂM LẬT* ⚠️\n\n"
            f"📊 *Thông số hiện tại:*\n"
            f"🌡️ Nhiệt độ: {data.T} °C\n"
            f"🐟 Mật độ: {data.D} con/m²\n"
            f"💨 Sục khí: {data.A} giờ/ngày\n\n"
            f"⚡ Sức chịu đựng của ao đang cạn kiệt. Hãy bật thêm quạt nước hoặc giảm lượng thức ăn để phòng ngừa!"
        )
        send_telegram_alert(alert_msg_yellow)
        
    else:
        status = "GREEN"
        message = "AO AN TOÀN"
        
    return {
        "status": status,
        "message": message,
        "max_resilience": float(max_F),
        "graph_x": O_vals.tolist(),
        "graph_y": F_vals.tolist()
    }
