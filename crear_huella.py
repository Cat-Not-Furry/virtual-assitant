import torch
import torchaudio
from speechbrain.inference.speaker import SpeakerRecognition
import pyaudio
import wave
import numpy as np

# --- CONFIGURACIÓN ---
NOMBRE_ARCHIVO_HUELLA = "mi_huella.pt"
NOMBRE_ARCHIVO_TEMP = "enrollment.wav"
DURACION_GRABACION = 10  # Segundos
FORMATO = pyaudio.paInt16
CANALES = 1
RATE = 16000
CHUNK = 1024

# --- Cargar el modelo pre-entrenado ---
print("Cargando modelo de reconocimiento de voz...")
# El modelo se descargará automáticamente la primera vez
verification = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb", 
    savedir="pretrained_models/spkrec-ecapa-voxceleb"
)
print("Modelo cargado.")

# --- Grabar tu voz ---
audio = pyaudio.PyAudio()
print(f"\n¡ATENCIÓN! Se grabarán {DURACION_GRABACION} segundos de tu voz.")
print("Habla de forma clara y continua. Por ejemplo, puedes leer un párrafo de un libro.")
input("Presiona Enter para comenzar a grabar...")

stream = audio.open(format=FORMATO, channels=CANALES, rate=RATE, input=True, frames_per_buffer=CHUNK)
print("Grabando...")
frames = []
for _ in range(0, int(RATE / CHUNK * DURACION_GRABACION)):
    data = stream.read(CHUNK)
    frames.append(data)
print("Grabación finalizada.")

stream.stop_stream()
stream.close()
audio.terminate()

# Guardar la grabación en un archivo temporal
with wave.open(NOMBRE_ARCHIVO_TEMP, 'wb') as wf:
    wf.setnchannels(CANALES)
    wf.setsampwidth(audio.get_sample_size(FORMATO))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

# --- Generar y guardar la huella de voz (embedding) ---
print(f"Procesando la grabación y creando la huella de voz...")

# --- REEMPLAZO PARA torchaudio.load ---
# Lee el archivo .wav manualmente para evitar problemas de backend
with wave.open(NOMBRE_ARCHIVO_TEMP, 'rb') as wf:
    num_frames = wf.getnframes()
    audio_bytes = wf.readframes(num_frames)
    
# Convierte los bytes a un array de numpy
audio_numpy = np.frombuffer(audio_bytes, dtype=np.int16)

# Convierte el array a un tensor de PyTorch y normalízalo (muy importante)
signal = torch.from_numpy(audio_numpy).float()
signal = signal / 32768.0 # Normaliza el audio a un rango de -1 a 1
# --- FIN DEL REEMPLAZO ---

# Codifica la señal de audio para obtener el embedding (la huella)
embedding = verification.encode_batch(signal)

# Guardar el tensor del embedding en un archivo
torch.save(embedding, NOMBRE_ARCHIVO_HUELLA)

print(f"\n¡Listo! Tu huella de voz ha sido guardada en '{NOMBRE_ARCHIVO_HUELLA}'")
