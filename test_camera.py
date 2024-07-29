import cv2
import time
import json

def get_fps(cap):
    """获取视频的默认帧率（如果可用）"""
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f'Frame rate (if available): {fps} FPS')
    return fps

def calculate_fps(start_time, frame_count):
    """计算并返回当前帧率"""
    elapsed_time = time.time() - start_time
    return frame_count / elapsed_time if elapsed_time > 0 else 0

def main(camera_id):
    cap = cv2.VideoCapture(camera_id)
    time.sleep(1)

    get_fps(cap)

    start_time = time.time()
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print('Camera offline. Exiting...')
            break

        frame_count += 1
        if frame_count >= 10:  # 每处理10帧更新一次帧率显示
            current_fps = calculate_fps(start_time, frame_count)
            print(f'Current Frame rate: {current_fps:.2f} FPS')
            start_time = time.time()
            frame_count = 0

            get_fps(cap)

        cv2.imshow('Video Capture', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    with open('config.json', "r") as f:
        config = json.load(f)
        main(config['camera_id'])
