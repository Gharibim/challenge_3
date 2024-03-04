from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
import torch
import numpy as np

vad_model, utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    onnx=True,
)
get_speech_ts, _, _, VADIterator, _ = utils

VAD_SAMPLING_RATE = 8000
VAD_WINDOW_SIZE_EXAMPLES = 512

vad_iterator = VADIterator(vad_model, threshold=0.7, sampling_rate=VAD_SAMPLING_RATE)

app = FastAPI()

def int2float(sound):
    abs_max = np.abs(sound).max()
    sound = sound.astype('float32')
    if abs_max > 0:
        sound *= 1/32768
    sound = sound.squeeze()
    return sound

@app.websocket("/api/v1/listen")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    accum_buffer = np.array([])
    duration = 0
    try:
        while True:
            audio_data_bytes = await websocket.receive_bytes()
            audio_data = np.frombuffer(audio_data_bytes, dtype=np.int16)
            # audio_float32 = int2float(audio_data)
            
            duration = round(duration + VAD_WINDOW_SIZE_EXAMPLES / VAD_SAMPLING_RATE, 2)

            accum_buffer = np.concatenate((accum_buffer, audio_data))
            activities = {}
            processed_windows_count = 0

            for i in range(0, len(accum_buffer), VAD_WINDOW_SIZE_EXAMPLES):
                if i + VAD_WINDOW_SIZE_EXAMPLES > len(accum_buffer):
                    break

                processed_windows_count += 1
                speech_dict = vad_iterator(accum_buffer[i: i + VAD_WINDOW_SIZE_EXAMPLES], return_seconds=True)

                if speech_dict:
                    if "start" in speech_dict:
                        activities["start"] = speech_dict["start"]
                    else:
                        activities["end"] = speech_dict["end"]
            accum_buffer = accum_buffer[processed_windows_count * VAD_WINDOW_SIZE_EXAMPLES:]
            await websocket.send_json({"activity": activities, "accum_duration": duration})
    
    except WebSocketDisconnect:  
        print("Client has closed the connection.")
    
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()
