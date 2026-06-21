import cv2
import numpy as np
import pyrealsense2 as rs

clicked_points = []

POINT_NAMES = [
    "1_LeftBottom",
    "2_LeftTop",
    "3_RightTop",
    "4_RightBottom"
]

depth_frame_global = None


def mouse_callback(event, x, y, flags, param):
    global clicked_points
    global depth_frame_global

    if event == cv2.EVENT_LBUTTONDOWN:

        if len(clicked_points) >= 4:
            print("이미 4개 점을 모두 찍었습니다. r 키로 초기화하세요.")
            return

        depth_mm = 0

        if depth_frame_global:
            depth_mm = depth_frame_global.get_distance(x, y) * 1000

        clicked_points.append((x, y))

        idx = len(clicked_points)

        print(
            f"[{idx}/4] {POINT_NAMES[idx-1]} "
            f"pixel=({x},{y}) "
            f"depth={depth_mm:.1f} mm"
        )

        if len(clicked_points) == 4:

            print("\n==============================")
            print("PIXEL_PTS")
            print("==============================")

            print("PIXEL_PTS = np.float32([")

            for px, py in clicked_points:
                print(f"    [{px}, {py}],")

            print("])")

            print("\n기록 순서")
            print("P1 = Left Bottom")
            print("P2 = Left Top")
            print("P3 = Right Top")
            print("P4 = Right Bottom")


def main():

    global depth_frame_global

    pipeline = rs.pipeline()
    config = rs.config()

    config.enable_stream(
        rs.stream.color,
        640,
        480,
        rs.format.bgr8,
        30
    )

    config.enable_stream(
        rs.stream.depth,
        640,
        480,
        rs.format.z16,
        30
    )

    print("D435 시작 중...")

    pipeline.start(config)

    print("D435 연결 성공")

    print("\n사용 순서")
    print("1. 로봇을 P1(Left Bottom) 위치로 이동")
    print("2. 화면에서 TCP 끝점을 클릭")
    print("3. P2 → P3 → P4 순서로 반복")
    print("4. ESC 종료")
    print("5. r 초기화\n")

    window_name = "Calibration Helper"

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)

    try:

        while True:

            frames = pipeline.wait_for_frames()

            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()

            if not color_frame or not depth_frame:
                continue

            depth_frame_global = depth_frame

            frame = np.asanyarray(
                color_frame.get_data()
            )

            display = frame.copy()

            for i, (px, py) in enumerate(clicked_points):

                cv2.circle(
                    display,
                    (px, py),
                    7,
                    (0, 0, 255),
                    -1
                )

                cv2.putText(
                    display,
                    str(i + 1),
                    (px + 10, py - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

            next_idx = len(clicked_points)

            if next_idx < 4:
                guide = (
                    f"Click {POINT_NAMES[next_idx]}"
                )
            else:
                guide = (
                    "Done. Press r to retry"
                )

            cv2.putText(
                display,
                guide,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            h, w = display.shape[:2]

            cx = w // 2
            cy = h // 2

            center_depth = (
                depth_frame.get_distance(cx, cy)
                * 1000
            )

            cv2.circle(
                display,
                (cx, cy),
                5,
                (255, 0, 0),
                -1
            )

            cv2.putText(
                display,
                f"Center Height: {center_depth:.1f} mm",
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.imshow(
                window_name,
                display
            )

            key = cv2.waitKey(1) & 0xFF

            if key == 27:
                break

            elif key == ord('r'):
                clicked_points.clear()
                print("\n초기화 완료\n")

    finally:

        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()