"""
robot_socket_server_integrated.py
Raspberry Pi 실행용

동작:
1. Windows 비전 코드에서 marked_wire 좌표 수신
2. 해당 로봇 좌표로 이동
3. 그리퍼 접기 1회
4. 그리퍼 펴기 1회
5. 종료
"""

import socket
import json
import time
from wlkata_controller import WlkataArm


HOST = "0.0.0.0"
PORT = 5000

ROBOT_ENABLED = True
WLKATA_PORT = "/dev/ttyUSB0"
WLKATA_BAUD = 115200
MOVE_SPEED = 1500
HOME_ON_START = False

MIN_PICK_Z = 30
SAFE_Z = 120
WORK_Z = 60

arm = WlkataArm(
    port=WLKATA_PORT,
    baudrate=WLKATA_BAUD,
    enabled=ROBOT_ENABLED,
    move_speed=MOVE_SPEED,
)


def clamp_pick_z(z):
    try:
        z = float(z)
    except Exception:
        return 60
    return max(z, MIN_PICK_Z)


def validate_xy(x, y):
    if not (-300 <= x <= 350):
        print(f"[SAFETY][ERROR] X 범위 초과: {x}")
        return False
    if not (-250 <= y <= 250):
        print(f"[SAFETY][ERROR] Y 범위 초과: {y}")
        return False
    return True


def robot_move_to(x, y, z, theta=0):
    print(f"[ROBOT] move_to x={x}, y={y}, z={z}, theta={theta}")
    return arm.move_to(x, y, z, theta)


def gripper_close():
    print("[GRIPPER] CLOSE / 접기")
    return arm.gripper_close()


def gripper_open():
    print("[GRIPPER] OPEN / 펴기")
    return arm.gripper_open()

SAFE_Z = 120
WORK_Z = 69
DROP_X = 260
DROP_Y = -50

def execute_vision_task(x, y, z, theta):

    print("[TASK] 그리퍼 열기 -> 접근 -> 하강 -> 집기 -> 상승 -> 집은 채로 이동")

    if not validate_xy(x, y):
        return False

    # 0. 집기 전에 그리퍼를 먼저 열어둠
    gripper_open()
    time.sleep(1.0)

    # 1. 목표 상공으로 이동
    robot_move_to(x, y, SAFE_Z, theta)
    time.sleep(1.0)

    # 2. 손톱만큼 더 내려가서 집기
    robot_move_to(x, y, WORK_Z, theta)
    time.sleep(0.5)

    # 3. 그리퍼 닫기
    gripper_close()
    time.sleep(1.0)

    # 4. 집은 채로 상승
    robot_move_to(x, y, SAFE_Z, theta)
    time.sleep(1.0)

    # 5. 집은 채로 [260, -50] 상공 이동
    robot_move_to(260, -50, SAFE_Z, theta)
    time.sleep(1.0)

    print("[TASK] 완료 - 물체를 집은 채로 이동 완료")
    return True

def handle_robot_command(command):
    task = command.get("task")
    x = command.get("x")
    y = command.get("y")
    z = command.get("z")
    theta = command.get("theta", 0)

    print("\n===== 로봇 명령 수신 =====")
    print("task:", task, "| x:", x, "y:", y, "z:", z)

    if task != "vision_task":
        print("[WARNING] vision_task가 아닙니다:", task)
        return False

    if x is None or y is None or z is None:
        print("[ERROR] x, y, z 값 없음")
        return False

    try:
        x = float(x)
        y = float(y)
        z = float(z)
        theta = float(theta)
    except ValueError:
        print("[ERROR] 좌표값 변환 실패")
        return False

    result = execute_vision_task(x, y, z, theta)

    print("===== 로봇 명령 완료 =====\n")
    return result


def main():
    print("로봇 Socket 서버 시작")
    print(f"대기 주소: {HOST}:{PORT}")
    print(f"WLKATA_PORT: {WLKATA_PORT}")

    connected = arm.connect()

    if connected and ROBOT_ENABLED and HOME_ON_START:
        arm.home()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)

        print("[Socket] 서버 대기 중...")

        while True:
            conn, addr = server.accept()
            print("비전 시스템 연결됨:", addr)

            with conn:
                buffer = ""

                while True:
                    data = conn.recv(4096)

                    if not data:
                        break

                    buffer += data.decode("utf-8")

                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()

                        if not line:
                            continue

                        try:
                            command = json.loads(line)

                            result = handle_robot_command(command)

                            response = {
                                "ok": bool(result),
                                "message": "robot_task_done" if result else "robot_task_failed",
                                "timestamp": time.time(),
                            }

                            conn.sendall(
                                (json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8")
                            )

                        except json.JSONDecodeError as e:
                            print("[ERROR] JSON 파싱 실패:", e)

                            response = {
                                "ok": False,
                                "message": "json_error",
                            }

                            conn.sendall(
                                (json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8")
                            )


if __name__ == "__main__":
    try:
        main()
    finally:
        arm.close()