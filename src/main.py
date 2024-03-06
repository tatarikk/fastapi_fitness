import time

import cv2
import mediapipe as mp
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect

from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserRead, UserCreate
from operations.router import router as router_operation
from pages.router import router as router_pages
from train.router import router as router_exercises

templates = Jinja2Templates(directory="templates")

app = FastAPI(
    title="Fitness App"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

pcs = set()
pcs_ws = set()
video_frames = []  # Это было добавлено

mpPose = mp.solutions.pose
pose = mpPose.Pose(static_image_mode=False, model_complexity=0, smooth_landmarks=False, enable_segmentation=False)
mpDraw = mp.solutions.drawing_utils

jump_started = False
repetitions_count = 0
pTime = 0

new_width = 128
new_height = 128

desired_fps = 120


def process_image(frame):
    global jump_started, repetitions_count, pTime

    frame_resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_NEAREST)

    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)

    if results.pose_landmarks:
        point_30_y = results.pose_landmarks.landmark[30].y
        point_29_y = results.pose_landmarks.landmark[29].y
        point_25_y = results.pose_landmarks.landmark[25].y
        point_26_y = results.pose_landmarks.landmark[26].y
        point_15_y = results.pose_landmarks.landmark[15].y
        point_16_y = results.pose_landmarks.landmark[16].y
        point_13_y = results.pose_landmarks.landmark[13].y
        point_14_y = results.pose_landmarks.landmark[14].y

        if (
                (point_30_y < point_25_y or point_29_y < point_26_y) and
                (point_15_y < point_13_y and point_16_y < point_14_y) and
                not jump_started
        ):
            jump_started = True
            repetitions_count += 1
            # print("Выполнен прыжок:", repetitions_count)
        elif point_30_y >= point_25_y and point_29_y >= point_26_y:
            jump_started = False

        mpDraw.draw_landmarks(imgRGB, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
        for id, lm in enumerate(results.pose_landmarks.landmark):
            h, w, c = imgRGB.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(imgRGB, (int(cx), int(cy)), 5, (255, 0, 0), cv2.FILLED)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # time.sleep(1 / desired_fps)

    cv2.putText(imgRGB, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return imgRGB, fps, repetitions_count


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()

            # Преобразование байтов в изображение
            nparr = np.frombuffer(data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            video_frames.append(img)  # Это было добавлено
            track_img, fps, repetitions_count = process_image(img)
            # print(repetitions_count)

            # Сохраняем одно изображение
            # cv2.imwrite('saved_image.jpg', img)

            # Отправляем изображение обратно на клиент
            _, img_encoded = cv2.imencode('.jpg', track_img)
            # await websocket.send_bytes(img_encoded.tobytes())  # если хотим видеть точки, включить
            await websocket.send_text(str(repetitions_count))
    except WebSocketDisconnect:
        print("Клиент закрыл соединение")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


# Это было добавлено
@app.get("/download_video")
async def download_video():
    async def video_generator():
        for frame in video_frames:
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield jpeg.tobytes()

    return StreamingResponse(video_generator(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/highknees")
def read_root():
    return FileResponse('static/videoread.html')


@app.get("/highknees")
async def play_music():
    return FileResponse("static/track.mp3")


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(router_pages)
app.include_router(router_operation)
app.include_router(router_exercises)
