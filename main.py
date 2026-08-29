import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# ==========================================
# 1. MÔ HÌNH SINH THÁI CÓ VÒNG LẶP PHẢN HỒI (BÙN ĐÁY)
# ==========================================
def calc_F(O, T, Density, Aeration):
    # Đổi nhiệt độ C sang nhiệt độ tuyệt đối Kelvin
    T_K = T + 273.15
    
    # Tính Nồng độ Oxy bão hòa (Osat) theo phương trình chuẩn APHA quốc tế
    ln_Osat = -139.34411 + (1.575701e5 / T_K) - (6.642308e7 / (T_K**2)) + (1.243800e10 / (T_K**3)) - (8.621949e11 / (T_K**4))
    Osat = np.exp(ln_Osat)
    
    # Các tham số trích xuất từ nghiên cứu thực tiễn ao cá tra (AGU & CTU)
    k1 = 0.1 + (Aeration * 0.05)     # Hệ số truyền khí K_La (0.1 - 0.6 /giờ)
    W_fish = Density * 0.006         # Nhu cầu hô hấp quần đàn (mg/L/giờ)
    M_sed = 3.5                      # SOD cực đại của bùn đáy (mg/L/giờ)
    K = 1.5                          # Ngưỡng bùng nổ bùn đáy (mg/L)
    
    # Hàm Cung và Cầu Oxy
    cung = k1 * (Osat - O)
    cau = W_fish + M_sed * (K**2) / (K**2 + O**2)
    
    # Phương trình tốc độ biến thiên dO/dt
    return cung - cau

# ==========================================
# 2. KHỞI TẠO GIAO DIỆN
# ==========================================
T_init, Density_init, Aeration_init = 30.0, 30.0, 2.0
O_vals = np.linspace(0, 10, 500)

fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(bottom=0.4)

ax.axhline(0, color='black', lw=2) # Trục hoành y=0 (Ranh giới sự sống)

F_init = calc_F(O_vals, T_init, Density_init, Aeration_init)
net_line, = ax.plot(O_vals, F_init, color='blue', lw=3)

# Điểm đánh dấu trạng thái ao
point_safe, = ax.plot([], [], marker='o', markersize=10, color='green')

ax.set_xlim(0, 10)
ax.set_ylim(-8, 4) # Đã ép trục tung lại để NHÌN RÕ RỆT cái bướu
ax.set_xlabel("Nồng độ Oxy hòa tan O (mg/L)", fontsize=12)
ax.set_ylabel("Tốc độ biến thiên Oxy F(O)", fontsize=12)
ax.set_title("AQUA-WARNING: DỰ BÁO TIPPING POINT AO NUÔI CÁ TRA", fontsize=14, fontweight='bold')
ax.grid(True, linestyle='--', alpha=0.6)

warning_text = ax.text(5, 2.5, "", color='green', fontsize=15, 
                       fontweight='bold', ha='center', 
                       bbox=dict(facecolor='white', edgecolor='green', boxstyle='round,pad=0.5'))

# ==========================================
# 3. TẠO THANH TRƯỢT
# ==========================================
ax_T = plt.axes([0.15, 0.25, 0.7, 0.03], facecolor='lightcyan')
ax_D = plt.axes([0.15, 0.17, 0.7, 0.03], facecolor='mistyrose')
ax_A = plt.axes([0.15, 0.09, 0.7, 0.03], facecolor='honeydew')

slider_T = Slider(ax_T, 'Nhiệt độ (°C)', 25.0, 45.0, valinit=T_init, valstep=0.5)
slider_D = Slider(ax_D, 'Mật độ cá (con/m²)', 10.0, 100.0, valinit=Density_init, valstep=1.0)
slider_A = Slider(ax_A, 'Mức sục khí (0-10)', 0.0, 10.0, valinit=Aeration_init, valstep=1.0)

# ==========================================
# 4. THUẬT TOÁN ĐIỀU KHIỂN (ĐÃ BỔ SUNG 3 TRẠNG THÁI MÀU)
# ==========================================
def update(val):
    F = calc_F(O_vals, slider_T.val, slider_D.val, slider_A.val)
    net_line.set_ydata(F)
    
    # Tìm các điểm cắt trục hoành để lấy tọa độ nồng độ Oxy cân bằng
    crossings = np.where(np.diff(np.sign(F)))[0]
    valid_crossings = [O_vals[i] for i in crossings if O_vals[i] > 1.0]
    
    # Tìm giá trị Cực đại của hàm số để đo "Sức chịu đựng" (Resilience)
    max_F = np.max(F)
    
    # Kịch bản 1: Đỉnh núi chìm dưới trục hoành -> Sụp đổ
    if max_F < 0:
        point_safe.set_data([], []) # Ẩn chấm xanh
        warning_text.set_text("VƯỢT ĐIỂM LẬT - BÙN ĐÁY BÙNG NỔ, CÁ CHẾT!")
        warning_text.set_color('red')
        warning_text.get_bbox_patch().set_edgecolor('red')
        ax.set_facecolor('#ffcccc') # Màu đỏ nền
        
    # Kịch bản 2: Đỉnh núi sát trục hoành -> Cảnh báo nguy hiểm (Màu Vàng/Cam)
    elif 0 <= max_F < 0.8:
        if len(valid_crossings) > 0:
            highest_O_root = max(valid_crossings)
            point_safe.set_data([highest_O_root], [0]) 
            warning_text.set_text(f"CẢNH BÁO NGUY HIỂM (Oxy = {highest_O_root:.1f} mg/L)")
        else:
            point_safe.set_data([], [])
            warning_text.set_text("CẢNH BÁO NGUY HIỂM - SẮP CHẠM ĐIỂM LẬT!")
            
        warning_text.set_color('#d95f02') # Màu cam đậm cho chữ
        warning_text.get_bbox_patch().set_edgecolor('#d95f02')
        ax.set_facecolor('#fff2cc') # Màu vàng nhạt nền
        
    # Kịch bản 3: Đỉnh núi cao -> An toàn (Màu Xanh)
    else:
        if len(valid_crossings) > 0:
            highest_O_root = max(valid_crossings)
            point_safe.set_data([highest_O_root], [0])
            warning_text.set_text(f"AO AN TOÀN (Oxy = {highest_O_root:.1f} mg/L)")
        else:
            point_safe.set_data([], [])
            warning_text.set_text("AO AN TOÀN - OXY DỒI DÀO")
            
        warning_text.set_color('green')
        warning_text.get_bbox_patch().set_edgecolor('green')
        ax.set_facecolor('#e6ffe6') # Màu xanh nền
        
    fig.canvas.draw_idle()

slider_T.on_changed(update)
slider_D.on_changed(update)
slider_A.on_changed(update)
update(0)
plt.show()