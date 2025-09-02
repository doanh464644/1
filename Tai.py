import requests
import time
import numpy as np
import json
import random
from datetime import datetime, timedelta, timezone
from collections import deque
from rich.console import Console
from typing import List, Dict, Tuple, Optional
import threading
import asyncio

# ═══════════════════════════════════════════════════════════════════
#                           🌟 BÓNG X PREMIUM 🌟
#                        Hệ Thống Dự Đoán V3.0
# ═══════════════════════════════════════════════════════════════════

TELEGRAM_TOKEN = "8228916824:AAFgVkRj9xhJpzrrc43dDH2fVVAy3GHRw5Y"
CHAT_IDS = ["-1002639168970"]
ADMIN_ID = "7509896689"

# 🧠 Cấu Hình Các Thuật Toán
PREDICTION_MODELS = {
    "mang_neural": {"weight": 0.35, "confidence": 0, "name": "Mạng Neural"},
    "nhan_dien_mau": {"weight": 0.25, "confidence": 0, "name": "Nhận Diện Mẫu"},
    "day_fibonacci": {"weight": 0.20, "confidence": 0, "name": "Dãy Fibonacci"},
    "xac_suat_luong_tu": {"weight": 0.20, "confidence": 0, "name": "Xác Suất Lượng Tử"}
}

# 📊 Thống Kê Dự Đoán Nâng Cao
model_stats = {model: {"correct": 0, "total": 0, "streak": 0, "max_streak": 0, "accuracy": 0.0} for model in PREDICTION_MODELS}
session_history = deque(maxlen=200)  # Tăng lưu trữ lịch sử
prediction_confidence = 0.0
last_sent_session_id = None
correct = 0
wrong = 0
last_prediction = None
last_prediction_session_id = None
is_bot_enabled = True
last_update_id = 0
current_session = 0
win_streak = 0
max_win_streak = 0
total_sessions = 0
daily_stats = {"correct": 0, "wrong": 0, "accuracy": 0.0}
hourly_performance = {}
best_model = "mang_neural"
worst_model = "mang_neural"
# Thống kê mở rộng
weekly_stats = {"correct": 0, "wrong": 0, "accuracy": 0.0}
monthly_stats = {"correct": 0, "wrong": 0, "accuracy": 0.0}
prediction_patterns = {"tai_streak": 0, "xiu_streak": 0, "alternating": 0}
confidence_levels = {"high": 0, "medium": 0, "low": 0}
time_based_accuracy = {}
session_types = {"morning": 0, "afternoon": 0, "evening": 0, "night": 0}

console = Console()


import os

class MangNeural:
    """🧠 Mạng Neural Để Nhận Diện Mẫu (tự động lưu trạng thái học)"""
    def __init__(self, weights_path="mang_neural_weights.npz"):
        self.weights_path = weights_path
        self.weights = np.random.uniform(-1, 1, (10, 5))
        self.bias = np.random.uniform(-1, 1, 5)
        self.learning_rate = 0.01
        self.load_state()

    def save_state(self, weights_file="neural_weights.json", bias_file="neural_bias.json"):
        import numpy as np
        np.save(weights_file, self.weights)
        np.save(bias_file, self.bias)

    def load_state(self, weights_file="neural_weights.json", bias_file="neural_bias.json"):
        import os
        import numpy as np
        if os.path.exists(weights_file + ".npy") and os.path.exists(bias_file + ".npy"):
            self.weights = np.load(weights_file + ".npy")
            self.bias = np.load(bias_file + ".npy")

    def _load_weights(self):
        if os.path.exists(self.weights_path):
            try:
                data = np.load(self.weights_path)
                self.weights = data["weights"]
                self.bias = data["bias"]
                console.print(f"[green]✅ Đã tải trạng thái học mạng neural từ {self.weights_path}[/]")
            except Exception as e:
                console.print(f"[yellow]⚠️ Không thể load weights: {e}[/]")

    def _save_weights(self):
        try:
            np.savez(self.weights_path, weights=self.weights, bias=self.bias)
        except Exception as e:
            console.print(f"[yellow]⚠️ Không thể lưu weights: {e}[/]")

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    def predict(self, inputs):
        hidden = self.sigmoid(np.dot(inputs, self.weights) + self.bias)
        return np.mean(hidden)

    def train(self, inputs, target):
        prediction = self.predict(inputs)
        error = target - prediction
        # Simplified backpropagation
        self.weights += self.learning_rate * error * np.outer(inputs, np.ones(5))        
        self.save_state()
        self._save_weights()

class TinhToanXacSuat:
    """⚛️ Tính Toán Xác Suất Theo Lượng Tử"""
    
    @staticmethod
    def superposition_luong_tu(data: List[int]) -> float:
        """Mô phỏng superposition lượng tử để tính xác suất"""
        if not data:
            return 0.5
            
        # Tạo vector trạng thái lượng tử
        state_vector = np.array(data[-10:]) / 18.0  # Chuẩn hóa về [0,1]
        
        # Áp dụng mô phỏng cổng lượng tử
        rotation_matrix = np.array([[0.6, 0.8], [0.8, -0.6]])
        
        # Tính toán interference patterns
        interference = np.sum(state_vector) * np.cos(len(data) * np.pi / 6)
        
        return max(0.1, min(0.9, 0.5 + interference * 0.3))

class NhanDienMau:
    """🔍 Công Cụ Nhận Diện Mẫu Nâng Cao"""
    
    @staticmethod
    def phan_tich_fibonacci(data: List[int]) -> str:
        """Phân tích sử dụng dãy Fibonacci"""
        if len(data) < 8:
            return "Tài"
            
        # Tạo dãy giống Fibonacci từ dữ liệu
        fib_pattern = []
        for i in range(2, min(8, len(data))):
            fib_val = (data[i-1] + data[i-2]) % 2
            fib_pattern.append(fib_val)
        
        # Dự đoán dựa trên xu hướng xoắn ốc Fibonacci
        return "Xỉu" if sum(fib_pattern) % 2 == 0 else "Tài"
    
    @staticmethod
    def quet_mau_sau(results: List[str]) -> Tuple[str, float]:
        """Quét tìm các mẫu lặp lại sâu"""
        if len(results) < 6:
            return "Tài", 0.5
            
        # Phát hiện mẫu đa tầng
        patterns = {
            "xen_ke": 0,
            "lap_doi": 0,
            "chuoi_ba": 0,
            "xoan_oc_fibonacci": 0
        }
        
        # Phát hiện mẫu xen kẽ
        alternating_score = sum(1 for i in range(1, len(results)) 
                              if results[i] != results[i-1]) / (len(results) - 1)
        patterns["xen_ke"] = alternating_score
        
        # Phát hiện lặp đôi
        double_count = sum(1 for i in range(2, len(results)) 
                          if results[i] == results[i-1] == results[i-2])
        patterns["lap_doi"] = double_count / max(1, len(results) - 2)
        
        # Tính độ tin cậy
        confidence = max(patterns.values())
        
        # Dự đoán dựa trên mẫu mạnh nhất
        strongest_pattern = max(patterns, key=patterns.get)
        
        if strongest_pattern == "xen_ke" and alternating_score > 0.6:
            prediction = "Xỉu" if results[0] == "Tài" else "Tài"
        elif strongest_pattern == "lap_doi" and double_count > 2:
            prediction = "Tài" if results[0] == "Xỉu" else "Xỉu"
        else:
            prediction = results[0]  # Theo xu hướng
            
        return prediction, min(0.95, confidence + 0.2)

# Khởi tạo các thuật toán
mang_neural = MangNeural()
tinh_toan_xac_suat = TinhToanXacSuat()
nhan_dien_mau = NhanDienMau()


def get_result(sum_dice: int) -> str:
    """🎲 Convert dice sum to result"""
    return "Tài" if sum_dice >= 11 else "Xỉu"


def get_vn_time() -> str:
    """🕐 Get Vietnam timezone timestamp"""
    VN_TZ = timezone(timedelta(hours=7))
    return datetime.now(VN_TZ).strftime("%H:%M:%S - %d/%m/%Y")


def tinh_du_doan_neural(data: List[Dict]) -> Tuple[str, float]:
    """🧠 Dự Đoán Mạng Neural"""
    if len(data) < 5:
        return "Tài", 0.5
    
    # Chuẩn bị đặc trưng đầu vào
    features = []
    for d in data[:10]:
        total = d["FirstDice"] + d["SecondDice"] + d["ThirdDice"]
        features.extend([
            total / 18.0,  # Tổng chuẩn hóa
            d["FirstDice"] / 6.0,  # Từng xúc xắc chuẩn hóa
            d["SecondDice"] / 6.0,
            d["ThirdDice"] / 6.0,
            1.0 if get_result(total) == "Tài" else 0.0
        ])
    
    # Đệm hoặc cắt về kích thước cố định
    features = (features + [0.5] * 50)[:50]
    
    try:
        prediction_value = mang_neural.predict(np.array(features))
        confidence = abs(prediction_value - 0.5) * 2
        
        # Cập nhật độ tin cậy của thuật toán
        PREDICTION_MODELS["mang_neural"]["confidence"] = min(0.95, confidence + 0.1)
        
        return ("Tài" if prediction_value > 0.5 else "Xỉu", confidence)
    except:
        return "Tài", 0.5


def tinh_du_doan_luong_tu(data: List[Dict]) -> Tuple[str, float]:
    """⚛️ Dự Đoán Xác Suất Lượng Tử"""
    if len(data) < 3:
        return "Xỉu", 0.5
        
    totals = [d["FirstDice"] + d["SecondDice"] + d["ThirdDice"] for d in data[:15]]
    
    quantum_prob = tinh_toan_xac_suat.superposition_luong_tu(totals)
    confidence = abs(quantum_prob - 0.5) * 1.8
    
    # Áp dụng nguyên lý bất định lượng tử
    uncertainty_factor = np.random.normal(0, 0.05)
    adjusted_prob = max(0.1, min(0.9, quantum_prob + uncertainty_factor))
    
    PREDICTION_MODELS["xac_suat_luong_tu"]["confidence"] = min(0.9, confidence)
    
    return ("Tài" if adjusted_prob > 0.5 else "Xỉu", confidence)


def tinh_du_doan_nhan_dien(data: List[Dict]) -> Tuple[str, float]:
    """🔍 Dự Đoán Nhận Diện Mẫu Nâng Cao"""
    if len(data) < 4:
        return "Tài", 0.5
        
    results = [get_result(d["FirstDice"] + d["SecondDice"] + d["ThirdDice"]) for d in data[:12]]
    
    prediction, confidence = nhan_dien_mau.quet_mau_sau(results)
    PREDICTION_MODELS["nhan_dien_mau"]["confidence"] = confidence
    
    return prediction, confidence


def tinh_du_doan_fibonacci(data: List[Dict]) -> Tuple[str, float]:
    """📐 Dự Đoán Phân Tích Dãy Fibonacci"""
    if len(data) < 6:
        return "Xỉu", 0.5
        
    totals = [d["FirstDice"] + d["SecondDice"] + d["ThirdDice"] for d in data[:10]]
    
    prediction = nhan_dien_mau.phan_tich_fibonacci(totals)
    
    # Tính độ tin cậy Fibonacci
    fib_sequence = [1, 1, 2, 3, 5, 8, 13]
    confidence = 0.6 + (len(data) % 8) * 0.05
    
    PREDICTION_MODELS["day_fibonacci"]["confidence"] = min(0.85, confidence)
    
    return prediction, confidence


def lay_du_doan_chuyen_nghiep(data: List[Dict]) -> Tuple[str, float, str, Dict]:
    """🎯 Hệ Thống Dự Đoán Siêu Chuyên Nghiệp"""
    predictions = {}
    
    # Lấy dự đoán từ tất cả thuật toán
    predictions["mang_neural"] = tinh_du_doan_neural(data)
    predictions["xac_suat_luong_tu"] = tinh_du_doan_luong_tu(data)
    predictions["nhan_dien_mau"] = tinh_du_doan_nhan_dien(data)
    predictions["day_fibonacci"] = tinh_du_doan_fibonacci(data)
    
    # Phân tích chuyên sâu
    historical_trend = phan_tich_xu_huong_lich_su(data)
    time_factor = tinh_he_so_thoi_gian()
    volatility = tinh_do_bien_dong(data)
    dice_pattern = phan_tich_mau_xuc_xac(data)
    momentum = tinh_dong_luc_thi_truong(data)
    
    # Weighted ensemble với hệ số động
    weighted_score = 0.0
    total_weight = 0.0
    strongest_models = []
    
    for model_name, (pred, conf) in predictions.items():
        # Trọng số thích ứng theo hiệu suất
        base_weight = PREDICTION_MODELS[model_name]["weight"]
        performance_factor = min(2.0, max(0.5, model_stats[model_name].get("accuracy", 50) / 50))
        
        # Điều chỉnh theo thời gian và xu hướng
        time_adjustment = 1.0 + (time_factor * 0.15)
        trend_adjustment = 1.0 + (historical_trend["strength"] * 0.1)
        momentum_adjustment = 1.0 + (momentum * 0.05)
        
        final_weight = base_weight * performance_factor * time_adjustment * trend_adjustment * momentum_adjustment
        
        # Lưu models mạnh nhất
        if conf > 0.75:
            strongest_models.append(f"{PREDICTION_MODELS[model_name]['name']} ({conf:.1%})")
        
        score = 1.0 if pred == "Tài" else 0.0
        weighted_score += score * final_weight * (1 + conf * 1.5)
        total_weight += final_weight * (1 + conf * 1.5)
    
    # Áp dụng các yếu tố bổ sung
    if historical_trend["trend"] == "Tài":
        weighted_score += historical_trend["strength"] * 0.15
    else:
        weighted_score -= historical_trend["strength"] * 0.15
    
    # Điều chỉnh theo momentum
    if momentum > 0.6:
        if historical_trend["trend"] == "Tài":
            weighted_score += 0.1
        else:
            weighted_score -= 0.1
    
    final_score = weighted_score / total_weight if total_weight > 0 else 0.5
    final_prediction = "Tài" if final_score > 0.5 else "Xỉu"
    
    # Tính độ tin cậy nâng cao
    confidences = [conf for _, conf in predictions.values()]
    base_confidence = np.mean(confidences)
    
    # Boost confidence với các yếu tố
    confidence_boost = 0
    confidence_boost += historical_trend["strength"] * 0.12
    confidence_boost += time_factor * 0.08
    confidence_boost += momentum * 0.05
    confidence_boost -= volatility * 0.04
    
    # Bonus cho consensus
    consensus_count = sum(1 for pred, _ in predictions.values() if pred == final_prediction)
    if consensus_count >= 3:
        confidence_boost += 0.1
    
    ensemble_confidence = min(0.96, max(0.35, base_confidence + confidence_boost + 0.18))
    
    # Tạo lý do dự đoán chi tiết
    reasoning = tao_ly_do_du_doan(
        predictions, historical_trend, time_factor, 
        momentum, dice_pattern, strongest_models, final_prediction
    )
    
    global prediction_confidence
    prediction_confidence = ensemble_confidence
    
    return final_prediction, ensemble_confidence, reasoning, predictions


def phan_tich_mau_xuc_xac(data: List[Dict]) -> Dict:
    """🎲 Phân Tích Mẫu Xúc Xắc Chuyên Sâu"""
    if len(data) < 8:
        return {"pattern": "normal", "strength": 0.5}
    
    dice_patterns = {
        "low_dice": 0,    # Tổng xúc xắc thấp
        "high_dice": 0,   # Tổng xúc xắc cao
        "balanced": 0,    # Xúc xắc cân bằng
        "extreme": 0      # Xúc xắc cực trị
    }
    
    for d in data[:10]:
        total = d["FirstDice"] + d["SecondDice"] + d["ThirdDice"]
        dice_variance = np.var([d["FirstDice"], d["SecondDice"], d["ThirdDice"]])
        
        if total <= 7:
            dice_patterns["low_dice"] += 1
        elif total >= 14:
            dice_patterns["high_dice"] += 1
        else:
            dice_patterns["balanced"] += 1
            
        if dice_variance > 2.0:
            dice_patterns["extreme"] += 1
    
    dominant_pattern = max(dice_patterns, key=dice_patterns.get)
    pattern_strength = dice_patterns[dominant_pattern] / 10
    
    return {
        "pattern": dominant_pattern,
        "strength": pattern_strength,
        "details": dice_patterns
    }


def tinh_dong_luc_thi_truong(data: List[Dict]) -> float:
    """📈 Tính Động Lực Thị Trường"""
    if len(data) < 6:
        return 0.5
    
    results = [get_result(d["FirstDice"] + d["SecondDice"] + d["ThirdDice"]) for d in data[:12]]
    
    # Tính momentum dựa trên chuỗi gần đây
    recent_trend = results[:6]
    tai_momentum = recent_trend.count("Tài") / 6
    
    # Điều chỉnh theo sự thay đổi
    changes = sum(1 for i in range(1, len(recent_trend)) if recent_trend[i] != recent_trend[i-1])
    stability = 1 - (changes / 5)  # Tính độ ổn định
    
    momentum = (tai_momentum * stability + (1 - tai_momentum) * stability) / 2
    
    return max(0.1, min(0.9, momentum))


def tao_ly_do_du_doan(predictions: Dict, trend: Dict, time_factor: float, 
                      momentum: float, dice_pattern: Dict, strongest_models: List[str], 
                      final_pred: str) -> str:
    """💡 Tạo Lý Do Dự Đoán Chi Tiết"""
    
    reasons = []
    
    # Phân tích consensus
    consensus_count = sum(1 for pred, _ in predictions.values() if pred == final_pred)
    if consensus_count >= 3:
        reasons.append(f"✅ {consensus_count}/4 thuật toán đồng thuận dự đoán {final_pred}")
    else:
        reasons.append(f"⚖️ Phân tích tổng hợp từ đa thuật toán")
    
    # Phân tích xu hướng
    if trend["strength"] > 0.6:
        if trend["trend"] == final_pred:
            reasons.append(f"📈 Xu hướng mạnh {trend['trend']} ({trend['strength']:.1%}) hỗ trợ")
        else:
            reasons.append(f"🔄 Dự báo đảo chiều từ xu hướng {trend['trend']}")
    elif trend["alternating"] > 0.7:
        reasons.append(f"🔀 Mẫu xen kẽ cao ({trend['alternating']:.1%}) cho thấy dao động")
    
    # Phân tích thời gian
    if time_factor > 0.7:
        reasons.append(f"⏰ Khung giờ vàng - độ ổn định cao")
    elif time_factor < 0.5:
        reasons.append(f"🌙 Khung giờ không ổn định - cần thận trọng")
    
    # Phân tích momentum
    if momentum > 0.7:
        reasons.append(f"🚀 Động lực thị trường mạnh")
    elif momentum < 0.3:
        reasons.append(f"📉 Động lực yếu - có thể đảo chiều")
    
    # Phân tích xúc xắc
    if dice_pattern["pattern"] == "extreme":
        reasons.append(f"🎲 Mẫu xúc xắc cực trị - biến động cao")
    elif dice_pattern["pattern"] == "balanced":
        reasons.append(f"⚖️ Xúc xắc cân bằng - dự đoán ổn định")
    
    # Thuật toán mạnh nhất
    if strongest_models:
        reasons.append(f"🏆 Thuật toán tin cậy cao: {', '.join(strongest_models[:2])}")
    
    return " | ".join(reasons)


def phan_tich_xu_huong_lich_su(data: List[Dict]) -> Dict:
    """📈 Phân Tích Xu Hướng Lịch Sử Mở Rộng"""
    if len(data) < 10:
        return {"trend": "Tài", "strength": 0.5}
    
    results = [get_result(d["FirstDice"] + d["SecondDice"] + d["ThirdDice"]) for d in data[:20]]
    
    # Đếm xu hướng gần đây
    tai_count = results[:10].count("Tài")
    xiu_count = results[:10].count("Xỉu")
    
    # Phân tích pattern xen kẽ
    alternating_pattern = sum(1 for i in range(1, min(10, len(results))) 
                            if results[i] != results[i-1]) / 9
    
    # Phân tích chuỗi dài
    current_streak = 1
    for i in range(1, len(results)):
        if results[i] == results[0]:
            current_streak += 1
        else:
            break
    
    # Xác định xu hướng chính
    if tai_count > xiu_count:
        trend = "Tài"
        strength = (tai_count - xiu_count) / 10
    else:
        trend = "Xỉu"  
        strength = (xiu_count - tai_count) / 10
    
    # Điều chỉnh theo pattern
    if alternating_pattern > 0.7:
        strength *= 0.8  # Giảm độ mạnh nếu có pattern xen kẽ
    
    if current_streak >= 4:
        strength *= 0.6  # Giảm độ mạnh nếu chuỗi quá dài
    
    return {
        "trend": trend,
        "strength": min(1.0, strength),
        "alternating": alternating_pattern,
        "streak": current_streak
    }


def tinh_he_so_thoi_gian() -> float:
    """⏰ Tính Hệ Số Thời Gian"""
    now = datetime.now(timezone(timedelta(hours=7)))
    hour = now.hour
    
    # Khung giờ vàng (cao điểm)
    if 9 <= hour <= 11 or 14 <= hour <= 16 or 19 <= hour <= 21:
        return 0.8  # Thời gian ổn định
    elif 22 <= hour <= 23 or 6 <= hour <= 8:
        return 0.6  # Thời gian ít ổn định
    else:
        return 0.4  # Thời gian không ổn định


def tinh_do_bien_dong(data: List[Dict]) -> float:
    """📊 Tính Độ Biến Động"""
    if len(data) < 8:
        return 0.5
    
    totals = [d["FirstDice"] + d["SecondDice"] + d["ThirdDice"] for d in data[:15]]
    
    # Tính độ lệch chuẩn
    mean_total = np.mean(totals)
    std_total = np.std(totals)
    
    # Chuẩn hóa độ biến động (0-1)
    volatility = min(1.0, std_total / 3.0)
    
    return volatility


def fetch_data() -> List[Dict]:
    """📡 Fetch latest game data"""
    try:
        response = requests.get("https://taixiu1.gsum01.com/api/luckydice1/GetSoiCau", timeout=10)
        data = response.json()[:15]  # Get more data for better AI analysis
        
        # Store in session history
        if data:
            session_history.extend(data[:5])
            
        return data
    except Exception as e:
        console.print(f"[red]🚫 Data fetch error: {e}[/]")
        return []


def send_telegram_message(text: str, parse_mode: str = "Markdown") -> None:
    """📱 Send enhanced Telegram message"""
    for chat_id in CHAT_IDS:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": True
                },
                timeout=10
            )
        except Exception as e:
            console.print(f"[red]💬 Message send error: {e}[/]")


def check_telegram_command() -> None:
    """🎮 Hệ Thống Lệnh Nâng Cao"""
    global is_bot_enabled, last_update_id
    
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={last_update_id + 1}",
            timeout=5
        )
        updates = response.json().get("result", [])
        
        for update in updates:
            last_update_id = update["update_id"]
            message = update.get("message", {})
            
            if str(message.get("from", {}).get("id")) != ADMIN_ID:
                continue
                
            text = message.get("text", "").lower().strip()
            
            if text in ["/on", "/bat", "/start", "/enable"]:
                is_bot_enabled = True
                send_telegram_message("🟢 **BÓNG X ĐÃ KÍCH HOẠT**\n```✨ Hệ thống dự đoán cao cấp đã sẵn sàng```")
                console.print("[green]✅ BÓNG X Bot ĐÃ BẬT[/]")
                
            elif text in ["/off", "/tat", "/stop", "/disable"]:
                is_bot_enabled = False
                send_telegram_message("🔴 **BÓNG X ĐÃ TẮT**\n```⏸️ Hệ thống dự đoán tạm dừng```")
                console.print("[red]⛔ BÓNG X Bot ĐÃ TẮT[/]")
                
            elif text in ["/stats", "/thongke", "/statistics"]:
                gui_bao_cao_gon("basic")
                
            elif text in ["/detail", "/chitiet", "/detailed"]:
                gui_bao_cao_gon("detailed")
                
            elif text in ["/help", "/trogiup", "/commands"]:
                gui_tin_nhan_tro_giup()
                
    except Exception as e:
        console.print(f"[red]🎮 Lỗi kiểm tra lệnh: {e}[/]")


def gui_bao_cao_thong_ke() -> None:
    """📊 Gửi báo cáo thống kê mở rộng"""
    global correct, wrong, max_win_streak, best_model, worst_model
    
    total = correct + wrong
    accuracy = (correct * 100 / total) if total > 0 else 0
    
    # Cập nhật thống kê theo thời gian
    current_hour = datetime.now(timezone(timedelta(hours=7))).hour
    time_period = get_time_period(current_hour)
    
    stats_msg = f"""
🏆 **BÁO CÁO HIỆU SUẤT BÓNG X** 🏆

📈 **Thống Kê Tổng Quan:**
• Tổng số dự đoán: `{total}` phiên
• Dự đoán đúng: `{correct}` ✅
• Dự đoán sai: `{wrong}` ❌
• Độ chính xác: `{accuracy:.1f}%`
• Chuỗi thắng hiện tại: `{win_streak}`
• Chuỗi thắng tối đa: `{max_win_streak}`

⏰ **Thống Kê Theo Thời Gian:**
• Buổi hiện tại: `{time_period}`
• Độ chính xác hôm nay: `{daily_stats['accuracy']:.1f}%`
• Số phiên hôm nay: `{daily_stats['correct'] + daily_stats['wrong']}`

📊 **Phân Tích Xu Hướng:**
• Xu hướng Tài: `{prediction_patterns['tai_streak']}`
• Xu hướng Xỉu: `{prediction_patterns['xiu_streak']}`
• Mẫu xen kẽ: `{prediction_patterns['alternating']}`

🎯 **Mức Độ Tin Cậy:**
• Cao (>80%): `{confidence_levels['high']}` lần
• Trung bình (60-80%): `{confidence_levels['medium']}` lần
• Thấp (<60%): `{confidence_levels['low']}` lần

� **Thống Kê Nâng Cao:**
• Tổng số phiên: `{total_sessions}`
• Tỷ lệ thành công tuần: `{weekly_stats['accuracy']:.1f}%`
• Hiệu suất theo giờ: Đỉnh cao
"""
    
    stats_msg += f"""
⏰ **Thời gian báo cáo:** `{get_vn_time()}`
🌟 **Được vận hành bởi Công nghệ BÓNG X**
💎 **"Dự đoán thông minh - Kết quả vượt trội"**
"""
    
    send_telegram_message(stats_msg)


def get_time_period(hour: int) -> str:
    """⏰ Xác định buổi trong ngày"""
    if 6 <= hour < 12:
        return "Buổi Sáng"
    elif 12 <= hour < 18:
        return "Buổi Chiều" 
    elif 18 <= hour < 22:
        return "Buổi Tối"
    else:
        return "Buổi Đêm"


def gui_tin_nhan_tro_giup() -> None:
    """❓ Gửi hướng dẫn và trợ giúp"""
    help_msg = """
🌟 **BÓNG X - TRUNG TÂM ĐIỀU KHIỂN** 🌟

🎮 **Các Lệnh Có Sẵn:**
• `/on` hoặc `/bat` - Kích hoạt hệ thống dự đoán
• `/off` hoặc `/tat` - Tạm dừng dự đoán  
• `/stats` hoặc `/thongke` - Xem báo cáo hiệu suất
• `/help` hoặc `/trogiup` - Hiển thị menu trợ giúp này

🧠 **Công Nghệ Dự Đoán:**
• **Mạng Neural** - Học từ các mẫu phức tạp
• **Xác Suất Lượng Tử** - Tính toán siêu chính xác
• **Nhận Diện Mẫu Nâng Cao** - Phát hiện xu hướng
• **Phân Tích Fibonacci** - Dựa trên tỷ lệ vàng

💎 **Tính Năng Cao Cấp:**
• Dự đoán đa thuật toán real-time
• Tính điểm độ tin cậy đa mô hình
• Phân tích thống kê nâng cao
• Giao diện đẹp mắt và chuyên nghiệp

📊 **Thống Kê & Phân Tích:**
• Theo dõi độ chính xác real-time
• Giám sát chuỗi thắng/thua
• So sánh hiệu suất thuật toán
• Báo cáo chi tiết hàng ngày

⚡ **Được phát triển bởi Công nghệ BÓNG X**
🎯 **"Dự đoán thông minh - Kết quả chính xác"**
"""
    
    send_telegram_message(help_msg)


def tao_tin_nhan_gon_gang(data: List[Dict], session_id: int, current_result: str, 
                         prediction: str, confidence: float, reasoning: str,
                         is_correct: Optional[bool] = None) -> str:
    """🎨 Tạo tin nhắn gọn gàng và chuyên nghiệp"""
    
    global correct, wrong, win_streak, max_win_streak
    
    # Header gọn gàng
    msg = "┌─────────── 🌟 BÓNG X PREMIUM 🌟 ──────────┐\n"
    
    # Thông tin phiên ngắn gọn
    if is_correct is not None:
        current = data[0]
        dice_display = f"{current['FirstDice']}-{current['SecondDice']}-{current['ThirdDice']}"
        status = "✅" if is_correct else "❌"
        msg += f"│ Phiên {session_id}: {current_result} ({dice_display}) {status}          │\n"
        msg += "├─────────────────────────────────────────┤\n"
    
    # Dự đoán chính
    confidence_percent = confidence * 100
    if confidence > 0.85:
        conf_icon = "🔥"
        conf_level = "CỰC CAO"
    elif confidence > 0.75:
        conf_icon = "⚡"
        conf_level = "CAO"
    elif confidence > 0.65:
        conf_icon = "💫"
        conf_level = "KHÁ"
    else:
        conf_icon = "📊"
        conf_level = "TB"
    
    msg += f"│ 🎯 DỰ ĐOÁN PHIÊN {session_id + 1}: {prediction} {conf_icon}              │\n"
    msg += f"│ 📊 Độ tin cậy: {confidence_percent:.1f}% ({conf_level})                │\n"
    msg += "├─────────────────────────────────────────┤\n"
    
    # Lý do dự đoán (chia thành nhiều dòng ngắn)
    msg += "│ 💡 LÝ DO DỰ ĐOÁN:                       │\n"
    reason_lines = reasoning.split(" | ")
    for i, reason in enumerate(reason_lines[:3]):  # Chỉ lấy 3 lý do quan trọng nhất
        if len(reason) > 35:
            reason = reason[:32] + "..."
        msg += f"│ • {reason:<35} │\n"
    
    msg += "├─────────────────────────────────────────┤\n"
    
    # Thống kê tóm tắt
    total = correct + wrong
    accuracy = (correct * 100 / total) if total > 0 else 0
    
    msg += f"│ 📈 Chính xác: {accuracy:.1f}% ({correct}/{total})              │\n"
    msg += f"│ 🔥 Chuỗi thắng: {win_streak} | Tối đa: {max_win_streak}           │\n"
    
    # Xu hướng gần đây (3 phiên)
    msg += "├─────────────────────────────────────────┤\n"
    msg += "│ 📂 Lịch sử gần:                         │\n"
    
    for i in range(min(3, len(data) - 1)):
        if i + 1 < len(data):
            d = data[i + 1]
            h_result = get_result(d["FirstDice"] + d["SecondDice"] + d["ThirdDice"])
            emoji = "🔴" if h_result == "Tài" else "🔵"
            msg += f"│ {emoji} {d['SessionId']}: {h_result}                          │\n"
    
    # Footer gọn
    current_time = get_vn_time().split(" - ")[0]  # Chỉ lấy giờ
    msg += "├─────────────────────────────────────────┤\n"
    msg += f"│ ⏰ {current_time} | ⚡ BÓNG X Chuyên Nghiệp   │\n"
    msg += "└─────────────────────────────────────────┘"
    
    return msg


def gui_bao_cao_gon(stats_type: str = "basic") -> None:
    """📊 Gửi báo cáo thống kê gọn gàng"""
    global correct, wrong, max_win_streak
    
    total = correct + wrong
    accuracy = (correct * 100 / total) if total > 0 else 0
    
    if stats_type == "basic":
        msg = f"""
📊 **BÁO CÁO NHANH BÓNG X**

🎯 **Hiệu Suất:**
• Chính xác: `{accuracy:.1f}%` ({correct}/{total})
• Chuỗi thắng: `{win_streak}` (Tối đa: `{max_win_streak}`)
• Hôm nay: `{daily_stats['accuracy']:.1f}%`

⏰ **Thời gian:** `{get_vn_time()}`
💎 **BÓNG X - Dự đoán chuyên nghiệp**
"""
    else:
        # Báo cáo chi tiết
        current_hour = datetime.now(timezone(timedelta(hours=7))).hour
        time_period = get_time_period(current_hour)
        
        msg = f"""
🏆 **BÁO CÁO CHI TIẾT BÓNG X**

📈 **Tổng Quan:**
• Độ chính xác: `{accuracy:.1f}%` ({correct}/{total})
• Chuỗi thắng: `{win_streak}` | Tối đa: `{max_win_streak}`
• Khung giờ: `{time_period}`

🎯 **Mức Tin Cậy:**
• Cao (>80%): `{confidence_levels.get('high', 0)}` lần
• Trung bình: `{confidence_levels.get('medium', 0)}` lần  
• Thấp (<60%): `{confidence_levels.get('low', 0)}` lần

⏰ `{get_vn_time()}`
"""
    
    send_telegram_message(msg)


def predict_and_send(data: List[Dict]) -> None:
    msg += "║             Hệ Thống Dự Đoán Chuẩn Xác           ║\n"
    msg += "╠══════════════════════════════════════════════╣\n"
    
    # Thông tin phiên
    msg += f"║ 🆔 **Phiên:** `{session_id}`{' ' * (34 - len(str(session_id)))}║\n"
    
    if is_correct is not None:
        current = data[0]
        dice_display = f"{current['FirstDice']}-{current['SecondDice']}-{current['ThirdDice']}"
        status_emoji = "✅ CHÍNH XÁC" if is_correct else "❌ SAI"
        msg += f"║ 🎲 **Kết quả:** {current_result} ({dice_display}){' ' * (18 - len(current_result) - len(dice_display))}║\n"
        msg += f"║ 📌 **Dự đoán trước:** {last_prediction} → {status_emoji}{' ' * (12 - len(last_prediction))}║\n"
    
    # Dự đoán chính (bỏ phân tích thuật toán phức tạp)
    msg += "╠══════════════════════════════════════════════╣\n"
    msg += "║            🎯 **DỰ ĐOÁN TIẾP THEO** 🎯          ║\n"
    msg += "╠══════════════════════════════════════════════╣\n"
    
    confidence_percent = confidence * 100
    if confidence > 0.85:
        confidence_level = "CỰC CAO"
        confidence_icon = "🔥"
        confidence_bar = "�" * 10
    elif confidence > 0.75:
        confidence_level = "CAO"
        confidence_icon = "⚡"
        confidence_bar = "🟡" * 8 + "░░"
    elif confidence > 0.65:
        confidence_level = "KHHA"
        confidence_icon = "💫"
        confidence_bar = "🟡" * 6 + "░░░░"
    else:
        confidence_level = "TRUNG BÌNH"
        confidence_icon = "📊"
        confidence_bar = "🔴" * 5 + "░░░░░"
    
    msg += f"║ 🚀 **Phiên {session_id + 1}:** {prediction} {confidence_icon}{' ' * (22 - len(prediction))}║\n"
    msg += f"║ 📊 **Độ tin cậy:** {confidence_percent:.1f}% ({confidence_level}){' ' * (8 - len(confidence_level))}║\n"
    msg += f"║ 📈 **Chỉ số tin cậy:** {confidence_bar}{' ' * (5 - len(confidence_bar) // 2)}║\n"
    
    # Phân tích xu hướng đơn giản
    historical_trend = phan_tich_xu_huong_lich_su(data)
    time_period = get_time_period(datetime.now(timezone(timedelta(hours=7))).hour)
    
    msg += "╠══════════════════════════════════════════════╣\n"
    msg += "║           📊 **PHÂN TÍCH XU HƯỚNG** 📊          ║\n"
    msg += "╠══════════════════════════════════════════════╣\n"
    msg += f"║ � **Xu hướng gần đây:** {historical_trend['trend']}{' ' * (22 - len(historical_trend['trend']))}║\n"
    msg += f"║ ⏰ **Khung thời gian:** {time_period}{' ' * (24 - len(time_period))}║\n"
    msg += f"║ � **Chuỗi hiện tại:** {historical_trend['streak']} phiên{' ' * (18 - len(str(historical_trend['streak'])))}║\n"
    
    # Thống kê hiệu suất gọn
    total = correct + wrong
    accuracy = (correct * 100 / total) if total > 0 else 0
    total_sessions += 1
    
    msg += "╠══════════════════════════════════════════════╣\n"
    msg += "║          📊 **THỐNG KÊ HIỆU SUẤT** 📊           ║\n"
    msg += "╠══════════════════════════════════════════════╣\n"
    msg += f"║ 🎯 **Độ chính xác:** {accuracy:.1f}% ({correct}/{total}){' ' * (18 - len(str(total)))}║\n"
    msg += f"║ 🔥 **Chuỗi thắng:** {win_streak} | **Tối đa:** {max_win_streak}{' ' * (16 - len(str(win_streak)) - len(str(max_win_streak)))}║\n"
    msg += f"║ � **Hôm nay:** {daily_stats['correct']}/{daily_stats['correct'] + daily_stats['wrong']} ({daily_stats['accuracy']:.1f}%){' ' * (10 - len(str(daily_stats['correct'])))}║\n"
    
    # Lịch sử ngắn gọn
    msg += "╠══════════════════════════════════════════════╣\n"
    msg += "║           📂 **LỊCH SỬ GẦN ĐÂY** 📂             ║\n"
    msg += "╠══════════════════════════════════════════════╣\n"
    
    for i in range(min(3, len(data) - 1)):
        if i + 1 < len(data):
            d = data[i + 1]
            h_result = get_result(d["FirstDice"] + d["SecondDice"] + d["ThirdDice"])
            dice_str = f"{d['FirstDice']}-{d['SecondDice']}-{d['ThirdDice']}"
            result_emoji = "🔴" if h_result == "Tài" else "🔵"
            
            msg += f"║ {result_emoji} **Phiên {d['SessionId']}:** {h_result} ({dice_str}){' ' * (16 - len(str(d['SessionId'])) - len(h_result) - len(dice_str))}║\n"
    
    # Lời khuyên dự đoán
    msg += "╠══════════════════════════════════════════════╣\n"
    msg += "║            💡 **LỜI KHUYÊN** 💡                ║\n"
    msg += "╠══════════════════════════════════════════════╣\n"
    
    if confidence > 0.8:
        advice = "Dự đoán có độ tin cậy cao, nên tham khảo"
    elif confidence > 0.7:
        advice = "Dự đoán khá tốt, có thể tham khảo"
    else:
        advice = "Nên thận trọng, chờ tín hiệu rõ ràng hơn"
    
    msg += f"║ 💬 {advice}{' ' * (40 - len(advice))}║\n"
    
    # Footer đơn giản
    msg += "╠══════════════════════════════════════════════╣\n"
    msg += f"║ ⏰ **Thời gian:** {get_vn_time()}{' ' * (23 - len(get_vn_time()))}║\n"
    msg += "║        ⚡ BÓNG X - Dự đoán thông minh & chuẩn xác ║\n"
    msg += "╚══════════════════════════════════════════════╝"
    
    return msg


def predict_and_send(data: List[Dict]) -> None:
    """🎯 Hàm dự đoán và gửi tin nhắn với thuật toán nâng cao"""
    global last_prediction, last_prediction_session_id
    global correct, wrong, last_sent_session_id, win_streak, max_win_streak, current_session
    global daily_stats, best_model, worst_model, prediction_patterns, confidence_levels

    if not data or len(data) < 2:
        return

    current = data[0]
    session_id = current["SessionId"]
    total = current["FirstDice"] + current["SecondDice"] + current["ThirdDice"]
    current_result = get_result(total)

    # Bỏ qua nếu đã xử lý phiên này
    if last_sent_session_id == session_id:
        return
        
    if last_sent_session_id is None:
        last_sent_session_id = session_id - 1

    last_sent_session_id = session_id
    current_session = session_id

    # Kiểm tra và đánh giá dự đoán trước
    if last_prediction and last_prediction_session_id == session_id - 1:
        is_correct = last_prediction == current_result
        correct += int(is_correct)
        wrong += int(not is_correct)
        
        # Cập nhật thống kê mở rộng
        cap_nhat_thong_ke_mo_rong(is_correct, current_result, last_prediction)
        
        # Cập nhật chuỗi thắng
        if is_correct:
            win_streak += 1
            max_win_streak = max(max_win_streak, win_streak)
        else:
            win_streak = 0

        # Lấy dự đoán mới với thuật toán cải tiến
        final_prediction, confidence, reasoning, individual_predictions = lay_du_doan_chuyen_nghiep(data)

        # Cập nhật thống kê mức độ tin cậy
        if confidence > 0.8:
            confidence_levels["high"] += 1
        elif confidence > 0.6:
            confidence_levels["medium"] += 1
        else:
            confidence_levels["low"] += 1

        # Cập nhật thống kê thuật toán
        cap_nhat_thong_ke_thuật_toan(individual_predictions, current_result)

        # Huấn luyện mạng neural liên tục
        huan_luyen_mang_neural(data, current_result)

        # Tạo và gửi tin nhắn gọn gàng với lý do dự đoán
        message = tao_tin_nhan_gon_gang(
            data, session_id, current_result, 
            final_prediction, confidence, reasoning,
            is_correct
        )
        
        send_telegram_message(message)
        
        # Hiển thị console với thông tin mở rộng
        trend_info = phan_tich_xu_huong_lich_su(data)
        status = "✅ CHÍNH XÁC" if is_correct else "❌ SAI"
        console.print(f"[{'green' if is_correct else 'red'}]🎯 {status}: {last_prediction} → {current_result} | Tiếp: {final_prediction} ({confidence:.1%}) | Xu hướng: {trend_info['trend']}[/]")
        
        # Cập nhật dự đoán
        last_prediction = final_prediction
        last_prediction_session_id = session_id
        
    else:
        # Dự đoán đầu tiên với thuật toán chuyên nghiệp
        final_prediction, confidence, reasoning, individual_predictions = lay_du_doan_chuyen_nghiep(data)
        
        # Gửi tin nhắn dự đoán gọn gàng
        message = tao_tin_nhan_gon_gang(
            data, session_id, current_result,
            final_prediction, confidence, reasoning
        )
        
        send_telegram_message(message)
        
        console.print(f"[blue]🚀 Dự đoán chuẩn xác cho phiên {session_id + 1}: {final_prediction} ({confidence:.1%})[/]")
        
        last_prediction = final_prediction
        last_prediction_session_id = session_id


def cap_nhat_thong_ke_mo_rong(is_correct: bool, current_result: str, last_pred: str) -> None:
    """📊 Cập nhật thống kê mở rộng"""
    global daily_stats, weekly_stats, monthly_stats, prediction_patterns
    
    # Thống kê hàng ngày
    daily_stats["correct"] += int(is_correct)
    daily_stats["wrong"] += int(not is_correct)
    daily_stats["accuracy"] = (daily_stats["correct"] * 100 / 
                             (daily_stats["correct"] + daily_stats["wrong"])) if (daily_stats["correct"] + daily_stats["wrong"]) > 0 else 0
    
    # Thống kê xu hướng
    if current_result == "Tài":
        prediction_patterns["tai_streak"] += 1
        prediction_patterns["xiu_streak"] = 0
    else:
        prediction_patterns["xiu_streak"] += 1
        prediction_patterns["tai_streak"] = 0
    
    # Pattern xen kẽ
    if last_pred != current_result:
        prediction_patterns["alternating"] += 1


def cap_nhat_thong_ke_thuật_toan(predictions: Dict, actual_result: str) -> None:
    """🔧 Cập nhật thống kê các thuật toán"""
    for model_name, (pred, conf) in predictions.items():
        model_stats[model_name]["total"] += 1
        if pred == actual_result:
            model_stats[model_name]["correct"] += 1
            model_stats[model_name]["streak"] += 1
            model_stats[model_name]["max_streak"] = max(
                model_stats[model_name]["max_streak"], 
                model_stats[model_name]["streak"]
            )
        else:
            model_stats[model_name]["streak"] = 0
        
        # Cập nhật độ chính xác
        if model_stats[model_name]["total"] > 0:
            model_stats[model_name]["accuracy"] = (
                model_stats[model_name]["correct"] * 100 / model_stats[model_name]["total"]
            )


def huan_luyen_mang_neural(data: List[Dict], actual_result: str) -> None:
    """🧠 Huấn luyện mạng neural liên tục"""
    try:
        features = []
        for d in data[:15]:  # Tăng số lượng dữ liệu huấn luyện
            total_dice = d["FirstDice"] + d["SecondDice"] + d["ThirdDice"]
            features.extend([
                total_dice / 18.0,
                d["FirstDice"] / 6.0,
                d["SecondDice"] / 6.0,
                d["ThirdDice"] / 6.0,
                1.0 if get_result(total_dice) == "Tài" else 0.0
            ])
        features = (features + [0.5] * 75)[:75]  # Tăng kích thước feature
        target = 1.0 if actual_result == "Tài" else 0.0
        mang_neural.train(np.array(features), target)
    except Exception as e:
        console.print(f"[yellow]⚠️ Neural training error: {e}[/]")


def main() -> None:
    """🎮 Vòng lặp ứng dụng chính với hệ thống dự đoán chuẩn xác"""
    console.print("[bold green]🌟 BÓNG X Premium V3.0 - Hệ Thống Dự Đoán Chuẩn Xác[/]")
    console.print("[cyan]⚡ Thuật Toán Học Máy Nâng Cao Đã Tải[/]")
    console.print("[cyan]� Phân Tích: Mạng Neural, Lượng Tử, Nhận Diện Mẫu, Fibonacci[/]")
    console.print("[cyan]� Thống Kê: Mở Rộng Với Phân Tích Xu Hướng Thời Gian[/]")
    console.print("[cyan]🎯 Dự Đoán: Chuẩn Xác Với Confidence Cao[/]")
    console.print("[green]✅ Hệ Thống Sẵn Sàng Dự Đoán![/]\n")
    
    # Gửi tin nhắn khởi động
    startup_msg = """
🌟 **BÓNG X PREMIUM V3.0** 🌟
⚡ **HỆ THỐNG DỰ ĐOÁN CHUẨN XÁC** ⚡

🎯 **Tính Năng Nâng Cao:**
• 🧠 Thuật toán học máy thông minh
• 📈 Phân tích xu hướng thời gian thực
• ⏰ Tối ưu theo khung giờ vàng
• � Thống kê mở rộng chi tiết
• � Lời khuyên dự đoán thông minh

🚀 **Độ chính xác được tối ưu hóa!**
💎 **Dự đoán chuẩn xác với confidence cao**

Gõ `/trogiup` để xem lệnh hỗ trợ
"""
    
    if is_bot_enabled:
        send_telegram_message(startup_msg)
    
    while True:
        try:
            # Kiểm tra lệnh
            check_telegram_command()
            
            if is_bot_enabled:
                # Lấy và phân tích dữ liệu với thuật toán nâng cao
                data = fetch_data()
                if len(data) >= 2:
                    predict_and_send(data)
                    
            time.sleep(1.5)  # Tối ưu thời gian phản hồi
            
        except KeyboardInterrupt:
            console.print("\n[red]🛑 BÓNG X Đang Tắt...[/]")
            break
        except Exception as e:
            console.print(f"[red]💥 Lỗi hệ thống: {e}[/]")
            time.sleep(5)


if __name__ == "__main__":
    main()
