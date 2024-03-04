import asyncio
import websockets
import pyaudio
import json

FORMAT = pyaudio.paInt16  
CHANNELS = 1  
RATE = 8000  
CHUNK = 512  

async def send_audio(uri):
    async with websockets.connect(uri) as websocket:
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

        try:
            print("Recording started...")
            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                await websocket.send(data)
                response = await websocket.recv()
                response = json.loads(response)
                if response['activity']:
                    print(f"Server response: {response}")
        finally:
            print("Cleaning up...")
            stream.stop_stream()
            stream.close()
            p.terminate()

if __name__ == "__main__":
    uri = "ws://18.116.24.57:30007/api/v1/listen"
    asyncio.get_event_loop().run_until_complete(send_audio(uri))