from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Cấp phép CORS để trình duyệt Web không chặn kết nối
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
def predict_tipping_point(data: PondData):
    O_vals = np.linspace(0, 10, 100)
    F_vals = calc_F(O_vals, data.T, data.D, data.A)
    max_F = np.max(F_vals)
    
    if max_F < 0:
        status = "RED"
        message = "VƯỢT ĐIỂM LẬT - BÙN ĐÁY BÙNG NỔ"
    elif 0 <= max_F < 0.8:
        status = "YELLOW"
        message = "CẢNH BÁO NGUY HIỂM - SẮP CHẠM ĐIỂM LẬT"
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
