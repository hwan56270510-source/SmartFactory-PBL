"""
vision_hybrid_socket_calibrated.py
Windows Anaconda 실행용
YOLO marked_wire 검출 + D435 Depth + Robot 좌표 변환 + Socket 전송
"""

import cv2
import json
import socket
import time
import numpy as np
import pyrealsense2 as rs
from ultralytics import YOLO


# =========================================================
# 1. 기본 설정
# =========================================================
MODEL_PATH = "best.pt"
OUTPUT_JSON = "robot_command.json"

ROBOT_SERVER_IP = "192.168.0.2"
ROBOT_SERVER_PORT = 5000
SOCKET_TIMEOUT = 5.0

CONF_THRESHOLD = 0.4
YOLO_WIRE_CLASS = "marked_wire"
USE_OPENCV_MODULE = False
SAVE_INTERVAL = 20.0  # 로봇의 긴 동선을 고려하여 20초로 여유 있게 설정

SEND_SOCKET = True

USE_CALIBRATION = True

# Depth 사용 ON
USE_DEPTH = True

# 카메라 렌즈에서 바닥까지 측정한 거리
GROUND_DEPTH_MM = 330.0

# Depth 실패 시 사용할 기본 Z
Z_FIXED = 60

# 로봇 기준 흡착 시작 기본 높이
PICK_Z_BASE = 60

# 물체를 너무 누르지 않기 위한 여유값
PICK_Z_OFFSET = 5.0


# =========================================================
# 2. 캘리브레이션 좌표
# =========================================================
PIXEL_PTS = np.float32([
    [371, 39],    # P1: Right Top
    [245, 71],    # P2: Left Top
    [284, 214],   # P3: Left Bottom
    [411, 172],   # P4: Right Bottom
])

ROBOT_PTS = np.float32([
    [180.0, -50.0],  # P1: Right Top
    [260.0, -50.0],  # P2: Left Top
    [260.0,  50.0],  # P3: Left Bottom
    [180.0,  50.0],  # P4: Right Bottom
])
def is_calibration_valid():
    if PIXEL_PTS.shape != (4, 2) or ROBOT_PTS.shape != (4, 2):
        return False

    if len({tuple(p) for p in ROBOT_PTS.tolist()}) < 4:
        print("[CALIB][ERROR] ROBOT_PTS 중복 좌표 있음")
        return False

    if len({tuple(p) for p in PIXEL_PTS.tolist()}) < 4:
        print("[CALIB][ERROR] PIXEL_PTS 중복 좌표 있음")
        return False

    if abs(cv2.contourArea(PIXEL_PTS)) < 100:
        print("[CALIB][ERROR] PIXEL_PTS 면적 너무 작음")
        return False

    if abs(cv2.contourArea(ROBOT_PTS)) < 10:
        print("[CALIB][ERROR] ROBOT_PTS 면적 너무 작음")
        return False

    return True


CALIBRATION_VALID = is_calibration_valid()
_H = cv2.getPerspectiveTransform(PIXEL_PTS, ROBOT_PTS) if CALIBRATION_VALID else None

print("[CALIB] valid =", CALIBRATION_VALID)


def pixel_to_robot_xy(px, py):
    if not USE_CALIBRATION:
        return float(px), float(py)

    if not CALIBRATION_VALID or _H is None:
        return None, None

    pt = np.array([[[float(px), float(py)]]], dtype=np.float32)
    result = cv2.perspectiveTransform(pt, _H)

    return float(result[0][0][0]), float(result[0][0][1])


# =========================================================
# 3. Depth 처리
# =========================================================
def get_depth_mm(depth_frame, px, py, depth_scale, radius=5):
    h = depth_frame.get_height()
    w = depth_frame.get_width()

    vals = []

    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            nx = px + dx
            ny = py + dy

            if 0 <= nx < w and 0 <= ny < h:
                d = depth_frame.get_distance(nx, ny) * depth_scale

                if d > 10:
                    vals.append(d)

    return float(np.median(vals)) if vals else 0.0


def resolve_z(depth_frame, cx, cy, depth_scale):
    if USE_DEPTH and depth_frame is not None and depth_scale is not None:
        depth_mm = get_depth_mm(depth_frame, int(cx), int(cy), depth_scale)

        if depth_mm > 0:
            object_height = GROUND_DEPTH_MM - depth_mm

            robot_z = PICK_Z_BASE + object_height + PICK_Z_OFFSET

            print(
                f"[DEPTH] depth={depth_mm:.1f}mm, "
                f"object_height={object_height:.1f}mm, "
                f"robot_z={robot_z:.1f}"
            )

            return robot_z

    return Z_FIXED


# =========================================================
# 4. JSON 저장 / Socket 전송
# =========================================================
def save_command(command):
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(command, f, indent=4, ensure_ascii=False)


def send_command_to_robot(command):
    if not SEND_SOCKET:
        print("[SOCKET] OFF - 전송 안 함:", command)
        return True

    if not CALIBRATION_VALID:
        print("[SOCKET][BLOCKED] 캘리브레이션 비정상")
        return False

    try:
        message = json.dumps(command, ensure_ascii=False) + "\n"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(1.0)
            client.connect((ROBOT_SERVER_IP, ROBOT_SERVER_PORT))
            client.sendall(message.encode("utf-8"))

            # 여기서 서버 응답을 기다리지 않음
            # response = client.recv(1024).decode("utf-8").strip()

        print("Socket 전송 완료:", command)
        return True

    except Exception as e:
        print("Socket 전송 실패:", e)
        return False

# =========================================================
# 5. 명령 생성
# =========================================================
def make_wire_command(cx, cy, conf, depth_frame=None, depth_scale=None):
    robot_x, robot_y = pixel_to_robot_xy(cx, cy)
    robot_z = resolve_z(depth_frame, cx, cy, depth_scale)

    return {
        "robot_id": 1,
        "task": "vision_task",
        "target": "marked_wire",
        "method": "yolo",

        "pixel_x": int(cx),
        "pixel_y": int(cy),

        "x": None if robot_x is None else round(robot_x, 2),
        "y": None if robot_y is None else round(robot_y, 2),
        "z": round(robot_z, 2),
        "theta": 0,

        "confidence": round(float(conf), 3),
        "calibration_valid": CALIBRATION_VALID,
        "timestamp": time.time(),
    }


# =========================================================
# 6. 메인
# =========================================================
def main():
    print("YOLO 모델 로딩 중...")
    model = YOLO(MODEL_PATH)
    
    # --- 추가된 부분: 구동 환경(CPU/GPU) 확인 ---
    import torch
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\n====================================")
    print(f"[SYSTEM] 현재 YOLO 연산 장치: {device.upper()}")
    print(f"====================================")
    if device == 'cpu':
        print("[WARNING] 현재 CPU로 구동 중입니다! 프레임 저하 및 딜레이가 발생합니다.")
        print("[WARNING] 실시간성을 위해 GPU(CUDA) 환경 세팅이 강력히 권장됩니다.\n")
    # -----------------------------------
    
    print("YOLO 모델 로딩 완료")
    print(f"현재 모델      : {MODEL_PATH}")
    print(f"캘리브레이션   : {'ON' if USE_CALIBRATION else 'OFF'} / valid={CALIBRATION_VALID}")
    print(f"Depth 사용     : {'ON' if USE_DEPTH else 'OFF'}")
    print(f"Socket 전송    : {'ON' if SEND_SOCKET else 'OFF'}")

    pipeline = rs.pipeline()
    config = rs.config()

    config.enable_stream(
        rs.stream.color,
        640,
        480,
        rs.format.bgr8,
        30
    )

    if USE_DEPTH:
        config.enable_stream(
            rs.stream.depth,
            640,
            480,
            rs.format.z16,
            30
        )

    last_saved_time = 0

    try:
        profile = pipeline.start(config)

        depth_scale = None
        align = None

        if USE_DEPTH:
            sensor = profile.get_device().first_depth_sensor()
            depth_scale = sensor.get_depth_scale() * 1000.0
            align = rs.align(rs.stream.color)

        print("D435 카메라 실행 성공")
        print("ESC 키를 누르면 종료됩니다.")

        while True:
            frames = pipeline.wait_for_frames()

            if align:
                frames = align.process(frames)

            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame() if USE_DEPTH else None

            if not color_frame:
                continue

            frame = np.asanyarray(color_frame.get_data())
            display = frame.copy()

            selected_command = None

            results = model(
                frame,
                conf=CONF_THRESHOLD,
                verbose=False
            )

            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = model.names[cls_id]

                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2

                    rx, ry = pixel_to_robot_xy(cx, cy)
                    rz = resolve_z(depth_frame, cx, cy, depth_scale)

                    cv2.rectangle(
                        display,
                        (int(x1), int(y1)),
                        (int(x2), int(y2)),
                        (255, 80, 0),
                        2
                    )

                    cv2.circle(
                        display,
                        (int(cx), int(cy)),
                        5,
                        (255, 80, 0),
                        -1
                    )

                    if rx is None:
                        label = (
                            f"YOLO:{class_name} {conf:.2f} | "
                            f"P({int(cx)},{int(cy)}) | CALIB ERROR"
                        )
                    else:
                        label = (
                            f"YOLO:{class_name} {conf:.2f} | "
                            f"R({rx:.1f},{ry:.1f},{rz:.1f})"
                        )

                    cv2.putText(
                        display,
                        label,
                        (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 80, 0),
                        2
                    )

                    if class_name == YOLO_WIRE_CLASS:
                        selected_command = make_wire_command(
                            cx,
                            cy,
                            conf,
                            depth_frame,
                            depth_scale
                        )

            current_time = time.time()

            if selected_command is not None and current_time - last_saved_time > SAVE_INTERVAL:
                save_command(selected_command)
                print("JSON 저장:", selected_command)

                if send_command_to_robot(selected_command):
                    last_saved_time = current_time

            cv2.putText(
                display,
                f"Calib:{'ON' if USE_CALIBRATION else 'OFF'} "
                f"valid:{CALIBRATION_VALID} "
                f"Depth:{'ON' if USE_DEPTH else 'OFF'} "
                f"Socket:{'ON' if SEND_SOCKET else 'OFF'}",
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 220, 220),
                2
            )

            cv2.imshow("Smart Factory Vision - Depth Pick", display)

            if cv2.waitKey(1) == 27:
                break

    except Exception as e:
        print("오류 발생:", e)
        import traceback
        traceback.print_exc()

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()
        print("비전 시스템 종료")


if __name__ == "__main__":
    main()