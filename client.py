from flask import Flask, render_template, Response
import cv2
import numpy as np
import pyautogui
import pyaudio
import io

app = Flask(__name__)

# Set the dimensions of the captured area
CAPTURE_WIDTH = 1920
CAPTURE_HEIGHT = 1080

# Set up audio parameters
AUDIO_RATE = 44100
AUDIO_CHANNELS = 2
AUDIO_BUFFER_SIZE = 1024
index = 1

# Create a PyAudio object
p = pyaudio.PyAudio()
stream_audio = p.open(format=pyaudio.paInt16,
                      channels=AUDIO_CHANNELS,
                      rate=AUDIO_RATE,
                      input=True,
                      input_device_index=index,
                      frames_per_buffer=AUDIO_BUFFER_SIZE)

def generate_video():
    while True:
        try:
            # Get the position and size of the primary screen
            x, y, width, height = 0, 0, CAPTURE_WIDTH, CAPTURE_HEIGHT

            # Capture the content of the screen
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Video Error: {e}")
            break

def generate_audio():
    CHUNK = 1024
    sampleRate = 44100
    bitsPerSample = 16
    channels = 2
    wav_header = genHeader(sampleRate, bitsPerSample, channels)

    first_run = True
    while True:
        try:
            if first_run:
                data = wav_header + stream_audio.read(CHUNK)
                first_run = False
            else:
                data = stream_audio.read(CHUNK)
            yield (data)
        except Exception as e:
            print(f"Audio Error: {e}")
            break

def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000 * 10 ** 6
    o = bytes("RIFF", 'ascii')  # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4, 'little')  # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE", 'ascii')  # (4byte) File type
    o += bytes("fmt ", 'ascii')  # (4byte) Format Chunk Marker
    o += (16).to_bytes(4, 'little')  # (4byte) Length of above format data
    o += (1).to_bytes(2, 'little')  # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2, 'little')  # (2byte)
    o += (sampleRate).to_bytes(4, 'little')  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4, 'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2, 'little')  # (2byte)
    o += (bitsPerSample).to_bytes(2, 'little')  # (2byte)
    o += bytes("data", 'ascii')  # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4, 'little')  # (4byte) Data size in bytes
    return o

@app.route('/')
def index():
    return render_template('index3.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/audio_feed')
def audio_feed():
    return Response(generate_audio(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)