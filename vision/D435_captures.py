import cv2
import os
import time
import numpy as np
import pyrealsense2 as rs


# ===============================
# 저장 경로 설정
# ===============================
SAVE_DIR = r"C:\SMART_FACTORY\captures"

# 폴더 없으면 자동 생성
os.makedirs(SAVE_DIR, exist_ok=True)


# ===============================
# D435 설정
# ===============================
pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(
    rs.stream.color,
    640,
    480,
    rs.format.bgr8,
    30
)


try:
    pipeline.start(config)

    print("D435 카메라 실행 성공")
    print("S 키: 이미지 저장")
    print("ESC 키: 종료")

    while True:
        frames = pipeline.wait_for_frames()

        color_frame = frames.get_color_frame()

        if not color_frame:
            continue

        frame = np.asanyarray(color_frame.get_data())

        # 화면 안내 문구
        cv2.putText(
            frame,
            "Press S to Save Image",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.imshow("D435 Capture Tool", frame)

        key = cv2.waitKey(1)

        # ===============================
        # S 키 누르면 저장
        # ===============================
        if key == ord('s') or key == ord('S'):

            timestamp = time.strftime("%Y%m%d_%H%M%S")

            filename = f"capture_{timestamp}.jpg"

            save_path = os.path.join(SAVE_DIR, filename)

            cv2.imwrite(save_path, frame)

            print(f"이미지 저장 완료: {save_path}")

        # ===============================
        # ESC 종료
        # ===============================
        elif key == 27:
            break

except Exception as e:
    print("오류 발생:", e)

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
    print("프로그램 종료")