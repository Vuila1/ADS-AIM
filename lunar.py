import ctypes
import cv2
import json
import math
import mss
import os
import sys
import time
import torch
import numpy as np
import win32api
from termcolor import colored
from ultralytics import YOLO

# ============================================
# SYSTEM CONFIGURATION
# ============================================

screensize = {'X': ctypes.windll.user32.GetSystemMetrics(0),
              'Y': ctypes.windll.user32.GetSystemMetrics(1)}
screen_res_x = screensize['X']
screen_res_y = screensize['Y']
screen_x = int(screen_res_x / 2)
screen_y = int(screen_res_y / 2)

# Cấu hình mặc định
aim_height = 10
fov = 350
confidence = 0.45
use_trigger_bot = True  # Mặc định bật trigger bot

# ============================================
# MAIN AIMBOT CLASS - TỐI ƯU TỐC ĐỘ
# ============================================

class UltraFastAimbot:
    """Aimbot với tốc độ chụp màn hình tối đa và fix lỗi giật"""

    def __init__(self):
        # Biến hệ thống
        self.sct = mss.mss()
        self.model = None
        self.running = True

        # Cấu hình detection
        self.box_constant = fov
        self.conf = confidence

        # Tối ưu chụp màn hình
        self.monitor = self.sct.monitors[1]
        self.grab_zone = None
        self.update_grab_zone()

        # Pre-allocate buffers
        self.frame_buffer = None
        self.display_buffer = None

        # FPS tracking
        self.fps = 0
        self.frame_count = 0
        self.fps_time = time.time()

        # Target tracking
        self.target = None
        self.aimbot_enabled = True

        # Trigger bot state
        self.trigger_bot_enabled = use_trigger_bot

        # Anti-jitter settings
        self.last_mouse_move = (0, 0)
        self.mouse_smooth_factor = 0.7  # Giảm để ít giật hơn
        self.min_move_threshold = 3  # Ngưỡng di chuyển tối thiểu
        self.max_move_distance = 100  # Giới hạn khoảng cách di chuyển tối đa

        # Load model
        self.load_model()

        self.display_startup_info()

    def update_grab_zone(self):
        """Cập nhật vùng chụp với tỷ lệ 4:3"""
        # Tỷ lệ 4:3
        width = self.box_constant
        height = int(self.box_constant * 3 / 4)

        # Tính toán vùng chụp quanh tâm màn hình
        left = int(screen_x - width / 2)
        top = int(screen_y - height / 2)

        # Đảm bảo không vượt quá màn hình
        left = max(0, left)
        top = max(0, top)

        # Nếu vượt quá, điều chỉnh
        if left + width > screen_res_x:
            left = screen_res_x - width
        if top + height > screen_res_y:
            top = screen_res_y - height

        self.grab_zone = {
            'left': left,
            'top': top,
            'width': width,
            'height': height
        }

        print(f"[INFO] Capture zone: {width}x{height} (4:3)")

    def display_startup_info(self):
        """Hiển thị thông tin khởi động"""
        print("\n" + "="*60)
        print(colored("🎯 ULTRA FAST AIMBOT - MAXIMUM SPEED", "cyan", attrs=["bold"]))
        print("="*60)
        print(colored("\n[SYSTEM INFO]", "yellow"))
        print(f"  Screen: {screen_res_x}x{screen_res_y}")
        print(f"  Center: ({screen_x}, {screen_y})")
        print(f"  Capture: {self.grab_zone['width']}x{self.grab_zone['height']}")
        print(colored("\n[CONTROLS]", "yellow"))
        print("  F1 : Toggle Aimbot")
        print("  F2 : Toggle Trigger Bot")
        print("  F3 : Exit")
        print("  RMB: Hold to aim")
        print("  Q  : Close window")
        print("="*60)
        print(colored(f"[STATUS] Aimbot: {'ENABLED' if self.aimbot_enabled else 'DISABLED'}", "green"))
        print(colored(f"[STATUS] Trigger Bot: {'ENABLED' if self.trigger_bot_enabled else 'DISABLED'}", "green"))

    def load_model(self):
        """Load model YOLO với tối ưu"""
        try:
            print("[INFO] Loading AI model...")

            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, "lib", "models", "best1.pt")

            if not os.path.exists(model_path):
                print(colored("[WARN] Model not found!", "yellow"))
                print(colored("  Please place model at: lib/models/best.pt", "yellow"))
                return

            # Load model với cài đặt tối ưu
            self.model = YOLO(model_path)

            # Tối ưu hóa model
            if hasattr(self.model.model, 'fuse'):
                self.model.model.fuse()

            # Kiểm tra CUDA
            if torch.cuda.is_available():
                self.model.model.cuda()
                print(colored("✅ CUDA ENABLED - Maximum speed", "green"))
            else:
                print(colored("⚠️  CUDA not available - Using CPU", "yellow"))

        except Exception as e:
            print(colored(f"[ERROR] Failed to load model: {e}", "red"))
            self.model = None

    # ============================================
    # ULTRA FAST CAPTURE - NHƯ CODE MẪU
    # ============================================

    def capture_screen_fast(self):
        """
        Chụp màn hình với tốc độ tối đa
        Giống như code mẫu: sử dụng mss.grab() trực tiếp
        """
        # Sử dụng grab() trực tiếp - phương thức nhanh nhất
        img = np.array(self.sct.grab(self.grab_zone))

        # Tạo buffer nếu chưa có
        if self.frame_buffer is None:
            self.frame_buffer = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)

        # Chuyển đổi BGRA -> BGR (nhanh hơn cv2.cvtColor)
        # Copy từng channel để tránh memory allocation
        np.copyto(self.frame_buffer[:, :, 0], img[:, :, 0])  # Blue
        np.copyto(self.frame_buffer[:, :, 1], img[:, :, 1])  # Green
        np.copyto(self.frame_buffer[:, :, 2], img[:, :, 2])  # Red

        return self.frame_buffer

    def move_mouse_smooth(self, target_x, target_y):
        """
        Di chuyển chuột mượt mà, tránh giật
        """
        # Chỉ di chuyển khi giữ RMB
        if not (win32api.GetAsyncKeyState(0x02) & 0x8000):
            return False

        # Tính toán vector di chuyển
        dx = int((target_x - screen_x) * 1.0)
        dy = int((target_y - screen_y) * 1.0)

        # Giới hạn khoảng cách di chuyển tối đa để tránh giật
        distance = math.sqrt(dx**2 + dy**2)
        if distance > self.max_move_distance:
            scale = self.max_move_distance / distance
            dx = int(dx * scale)
            dy = int(dy * scale)

        # Bỏ qua di chuyển quá nhỏ (giảm rung)
        if abs(dx) < self.min_move_threshold and abs(dy) < self.min_move_threshold:
            return False

        # Áp dụng smoothing để giảm giật
        smooth_dx = int(self.mouse_smooth_factor * dx + (1 - self.mouse_smooth_factor) * self.last_mouse_move[0])
        smooth_dy = int(self.mouse_smooth_factor * dy + (1 - self.mouse_smooth_factor) * self.last_mouse_move[1])

        # Cập nhật last move
        self.last_mouse_move = (dx, dy)

        # Di chuyển chuột
        if abs(smooth_dx) > 0 or abs(smooth_dy) > 0:
            try:
                ctypes.windll.user32.mouse_event(0x0001, smooth_dx, smooth_dy, 0, 0)
                return True
            except Exception as e:
                print(f"[ERROR] Mouse move failed: {e}")
                return False

        return False

    def trigger_click(self):
        """Click chuột trái nhanh"""
        try:
            ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # DOWN
            time.sleep(0.001)  # Delay rất nhỏ để đảm bảo click hoạt động
            ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # UP
        except Exception as e:
            print(f"[ERROR] Click failed: {e}")

    # ============================================
    # FAST DETECTION - TỐI ƯU INFERENCE
    # ============================================

    def detect_targets_fast(self, frame):
        """
        Phát hiện mục tiêu với tốc độ tối đa
        """
        if self.model is None:
            return None

        try:
            # Sử dụng cài đặt tối ưu cho tốc độ
            results = self.model(
                frame,
                verbose=False,
                conf=self.conf,
                imgsz=320,  # Giảm kích thước để tăng tốc
                device='cuda' if torch.cuda.is_available() else 'cpu',
                half=torch.cuda.is_available()
            )

            if not results or len(results) == 0:
                return None

            # Tìm mục tiêu gần tâm nhất
            closest = None
            min_dist = float('inf')

            boxes = results[0].boxes
            if boxes is not None and len(boxes) > 0:
                # Lọc các class hợp lệ (giống code mẫu: 0,1,2,3,5)
                valid_classes = [0, 1, 2, 3, 5]

                for i in range(len(boxes)):
                    box = boxes.xyxy[i].cpu().numpy()
                    cls = int(boxes.cls[i].cpu().numpy())

                    # Chỉ xử lý các class hợp lệ
                    if cls not in valid_classes:
                        continue

                    x1, y1, x2, y2 = map(int, box)

                    # Tính điểm ngắm (center với offset cho headshot)
                    box_height = y2 - y1
                    if box_height <= 0:
                        continue

                    cx = (x1 + x2) // 2
                    cy = y1 + int(box_height * 0.14)  # Headshot ratio giống code mẫu

                    # Kiểm tra xem target có trong FOV không
                    frame_center_x = frame.shape[1] // 2
                    frame_center_y = frame.shape[0] // 2
                    fov_radius = 150  # FOV radius

                    dist = math.sqrt((cx - frame_center_x) ** 2 + (cy - frame_center_y) ** 2)

                    # Chỉ xem xét target trong FOV
                    if dist > fov_radius:
                        continue

                    # Chọn mục tiêu gần nhất
                    if dist < min_dist:
                        min_dist = dist
                        closest = {
                            'box': (x1, y1, x2, y2),
                            'center': (cx, cy),
                            'absolute': (cx + self.grab_zone['left'],
                                         cy + self.grab_zone['top']),
                            'distance': dist
                        }

            return closest

        except Exception as e:
            print(f"[ERROR] Detection failed: {e}")
            return None

    # ============================================
    # VISUALIZATION - HIỆU SUẤT CAO
    # ============================================

    def draw_visualization(self, frame, target=None):
        """Vẽ overlay hiệu suất cao"""
        # Vẽ crosshair
        center_x = frame.shape[1] // 2
        center_y = frame.shape[0] // 2

        # Crosshair đơn giản
        cv2.line(frame, (center_x - 10, center_y), (center_x + 10, center_y), (0, 255, 0), 1)
        cv2.line(frame, (center_x, center_y - 10), (center_x, center_y + 10), (0, 255, 0), 1)

        # Vẽ FOV circle
        cv2.circle(frame, (center_x, center_y), 150, (0, 255, 255), 1)

        # Vẽ target nếu có
        if target is not None:
            x1, y1, x2, y2 = target['box']
            cx, cy = target['center']

            # Bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Target point
            cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)

            # Line to center
            cv2.line(frame, (cx, cy), (center_x, center_y), (255, 0, 0), 1)

        # Hiển thị FPS
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = current_time

        cv2.putText(frame, f"FPS: {self.fps}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Hiển thị trạng thái
        aim_status = "ON" if self.aimbot_enabled else "OFF"
        aim_color = (0, 255, 0) if self.aimbot_enabled else (0, 0, 255)
        cv2.putText(frame, f"AIM: {aim_status}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, aim_color, 2)

        # Hiển thị trigger bot status
        trigger_status = "ON" if self.trigger_bot_enabled else "OFF"
        trigger_color = (0, 255, 0) if self.trigger_bot_enabled else (0, 0, 255)
        cv2.putText(frame, f"TRIGGER: {trigger_status}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, trigger_color, 2)

        # Hiển thị kích thước
        cv2.putText(frame, f"FOV: {self.box_constant}", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        return frame

    # ============================================
    # HOTKEY HANDLING
    # ============================================

    def handle_hotkeys(self):
        """Xử lý phím tắt"""
        # F1: Toggle aimbot
        if win32api.GetAsyncKeyState(0x70) & 0x0001:  # F1
            self.aimbot_enabled = not self.aimbot_enabled
            status = "ENABLED" if self.aimbot_enabled else "DISABLED"
            print(f"[HOTKEY] Aimbot: {status}")
            time.sleep(0.2)

        # F2: Toggle trigger bot
        if win32api.GetAsyncKeyState(0x71) & 0x0001:  # F2
            self.trigger_bot_enabled = not self.trigger_bot_enabled
            status = "ENABLED" if self.trigger_bot_enabled else "DISABLED"
            print(f"[HOTKEY] Trigger Bot: {status}")
            time.sleep(0.2)

        # F3: Exit
        if win32api.GetAsyncKeyState(0x72) & 0x0001:  # F3
            print("\n[INFO] Exiting...")
            self.running = False

    # ============================================
    # MAIN LOOP - VÒNG LẶP CHÍNH
    # ============================================

    def run(self):
        """Chạy vòng lặp chính"""
        if not self.model:
            print(colored("[WARN] Running without model!", "yellow"))

        print("[INFO] Starting ultra-fast capture...")
        print("[INFO] Hold RMB to aim | F1:Toggle Aim | F2:Toggle Trigger | F3:Exit")

        # Frame skip để tăng FPS
        frame_skip = 0

        try:
            while self.running:
                # Xử lý hotkeys
                self.handle_hotkeys()

                # Skip frame để tăng FPS (giống code mẫu)
                frame_skip += 1
                if frame_skip % 2 != 0:
                    cv2.waitKey(1)
                    continue

                # Skip nếu aimbot tắt
                if not self.aimbot_enabled:
                    time.sleep(0.01)
                    # Vẫn hiển thị frame nhưng không xử lý
                    blank = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(blank, "AIMBOT OFF", (200, 240),
                                cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow("ULTRA FAST AIMBOT", blank)
                    cv2.waitKey(1)
                    continue

                # Chụp màn hình với tốc độ tối đa
                frame = self.capture_screen_fast()

                # Phát hiện mục tiêu
                self.target = self.detect_targets_fast(frame)

                # Di chuyển chuột nếu có mục tiêu
                target_locked = False
                if self.target is not None:
                    abs_x, abs_y = self.target['absolute']

                    # Kiểm tra tọa độ hợp lệ (tránh giật lên trời)
                    if (0 <= abs_x < screen_res_x and 0 <= abs_y < screen_res_y):
                        target_locked = self.move_mouse_smooth(abs_x, abs_y)

                        # Trigger bot (nếu bật)
                        if self.trigger_bot_enabled and target_locked:
                            distance = math.sqrt((abs_x - screen_x) ** 2 + (abs_y - screen_y) ** 2)
                            if distance < 30:  # Ngưỡng trigger
                                self.trigger_click()
                    else:
                        print(f"[WARN] Invalid target coordinates: ({abs_x}, {abs_y})")

                # Vẽ visualization
                frame = self.draw_visualization(frame, self.target)

                # Hiển thị (resize để giảm tải)
                if self.display_buffer is None:
                    self.display_buffer = np.zeros((480, 640, 3), dtype=np.uint8)

                # Resize nhanh
                cv2.resize(frame, (640, 480), dst=self.display_buffer)
                cv2.imshow("ULTRA FAST AIMBOT", self.display_buffer)

                # Thoát nếu nhấn Q
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                # Log định kỳ
                if self.frame_count % 100 == 0 and self.fps > 0:
                    target_status = "LOCKED" if target_locked else ("TARGET" if self.target else "NO TARGET")
                    print(f"[STATS] FPS: {self.fps} | Aim: {'ON' if self.aimbot_enabled else 'OFF'} | Trigger: {'ON' if self.trigger_bot_enabled else 'OFF'} | {target_status}")

        except KeyboardInterrupt:
            print("\n[INFO] Stopped by user")
        except Exception as e:
            print(colored(f"[ERROR] {e}", "red"))
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()

    def cleanup(self):
        """Dọn dẹp"""
        print("[INFO] Cleaning up...")
        cv2.destroyAllWindows()

# ============================================
# MAIN
# ============================================

def main():
    """Hàm chính"""
    print(colored("\n" + "="*60, "cyan"))
    print(colored("ULTRA FAST AIMBOT v2.1", "magenta", attrs=["bold"]))
    print(colored("4:3 Capture Ratio | Anti-Jitter | Trigger Toggle", "yellow"))
    print(colored("="*60, "cyan"))

    try:
        aimbot = UltraFastAimbot()
        aimbot.run()
    except Exception as e:
        print(colored(f"\n[ERROR] {e}", "red"))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()