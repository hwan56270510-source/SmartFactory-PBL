"""
wlkata_controller.py
wlkata_mirobot 패키지 기반 WLKATA 제어 모듈
"""

import time
from wlkata_mirobot import WlkataMirobot


class WlkataArm:
    def __init__(self, port="/dev/ttyUSB0", baudrate=115200, enabled=True, move_speed=1500):
        self.port = port
        self.baudrate = baudrate
        self.enabled = enabled
        self.move_speed = move_speed
        self.bot = None

    def connect(self):
        if not self.enabled:
            print("[WLKATA] enabled=False: 실제 로봇 연결하지 않음")
            return True

        try:
            print(f"[WLKATA] wlkata_mirobot 연결 시도: {self.port}")
            self.bot = WlkataMirobot(portname=self.port)
            time.sleep(1.0)
            print("[WLKATA] wlkata_mirobot 연결 성공")
            return True

        except Exception as e:
            print("[WLKATA][ERROR] 연결 실패:", e)
            self.bot = None
            return False

    def close(self):
        print("[WLKATA] 연결 종료")

    def home(self):
        if not self.enabled:
            print("[WLKATA] SIM home")
            return True

        if self.bot is None:
            print("[WLKATA][ERROR] bot 객체 없음")
            return False

        try:
            print("[WLKATA] home 시작")
            self.bot.home()
            time.sleep(15)
            print("[WLKATA] home 완료")
            return True

        except Exception as e:
            print("[WLKATA][ERROR] home 실패:", e)
            return False

    def move_to(self, x, y, z, theta=0, speed=None):
        if not self.enabled:
            print(f"[WLKATA] SIM move_to x={x}, y={y}, z={z}, theta={theta}")
            return True

        if self.bot is None:
            print("[WLKATA][ERROR] bot 객체 없음")
            return False

        try:
            x = float(x)
            y = float(y)
            z = float(z)
            theta = float(theta)

            print(f"[WLKATA] move_to x={x:.2f}, y={y:.2f}, z={z:.2f}, theta={theta:.2f}")

            self.bot.linear_interpolation(x, y, z, 0, 0, theta)

            time.sleep(2.0)
            return True

        except Exception as e:
            print("[WLKATA][ERROR] move_to 실패:", e)
            return False

    def gripper_close(self):
        if not self.enabled:
            print("[WLKATA] SIM gripper_close")
            return True

        if self.bot is None:
            print("[WLKATA][ERROR] bot 객체 없음")
            return False

        try:
            print("[WLKATA] gripper CLOSE / 집게 닫기")
            self.bot.set_gripper(65)
            time.sleep(1.0)
            return True

        except Exception as e:
            print("[WLKATA][ERROR] gripper_close 실패:", e)
            return False


    def gripper_open(self):
        if not self.enabled:
            print("[WLKATA] SIM gripper_open")
            return True

        if self.bot is None:
            print("[WLKATA][ERROR] bot 객체 없음")
            return False

        try:
            print("[WLKATA] gripper OPEN / 집게 열기")
            self.bot.set_gripper(45)
            time.sleep(1.0)
            return True

        except Exception as e:
            print("[WLKATA][ERROR] gripper_open 실패:", e)
            return False
    def suction_on(self):
        print("[WLKATA] suction_on 사용 안 함")
        return True

    def suction_off(self):
        print("[WLKATA] suction_off 사용 안 함")
        return True