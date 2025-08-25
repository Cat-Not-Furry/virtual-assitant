# asistente.py

import os
import threading
import time
import json
import pvporcupine
import pyaudio
import struct
import subprocess
from datetime import datetime
import vosk
import torch
import numpy as np
from speechbrain.inference.speaker import SpeakerRecognition
import re
import webbrowser
import requests

# --- CONFIGURACIÓN GENERAL ---

# Modelo de Reconocimiento de Voz (STT)
MODEL_PATH = "vosk-model-es-0.42"

# Palabra de Activación (Wake Word)
PICOVOICE_ACCESS_KEY = "TU_CLAVE_DE_PICOVOICA_AQUI" # TU CLAVE DE PICOVOICE
WAKE_WORD = "jarvis"

# ---CONFIGURACIÓN DE TERCEROS ---
PIPER_MODEL_PATH = "LA_RUTA_DEL_MODELO" # EJEMPLO: ~/VIRTUAL-ASSITANT/piper-model/es_MX-ald-medium.onnx

# --- CONSTANTES DE AUDIO ---
RATE = 16000 # Tasa de muestreo (Hertz)
CHUNK = 1024 # Tamaño del buffer de audio

# --- VARIABLES GLOBALES PARA EL LECTOR ---
lector_thread = None
parar_lectura = threading.Event()

# --- CONFIGURACIÓN DE HUELLA DE VOZ ---
print("Cargando verificación de voz...")
verification = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec-ecapa-voxceleb"
)
print("Cargando la huella...")
TU_HUELLA = torch.load("mi_huella.pt")

#p Para listar comandos
print("Listar comandos: qué puedes hacer")

# --- DEFINICIÓN DE ACCIONES Y COMANDOS ---

def hablar(texto):
    """Función para que el asistente hable."""
    print(f"Asistente: {texto}")
    if not os.path.exists(PIPER_MODEL_PATH):
        print(f"Error: No se encontró el modelo de voz de PIper en la ruta: {PIPER_MODEL_PATH}")
        return

    comando_piper = f'echo "{texto}" | piper --model {PIPER_MODEL_PATH} --output_file - | aplay -r 22050 -f S16_LE -t raw -'
    subprocess.run(comando_piper, shell=True, stderr=subprocess.DEVNULL)

def listar_comandos():
    """Lee en voz alta todos los comandos disponibles."""
    hablar("Puedo hacer lo siguiente:")
    for comando in comandos_disponibles.keys():
        hablar(comando)

def abrir_navegador():
    """Abre el navegador en segundo plano."""
    hablar("Navegador abierto.")
    subprocess.Popen(["TU_NAVEGADOR"])

def abrir_gestor_archivos():
    """Abre el gestor de archivos en segundo plano."""
    hablar("Gestor listo")
    subprocess.Popen(["TU_GESTOR_DE_ARCHIVOS"])

def abrir_terminal():
    """Abre la terminal en segundo plano."""
    hablar("Terminal lista.")
    subprocess.Popen(["TU_TERMINAL"])

""""Si tu distro usa playerctl."""
"""
def anterior_cancion():
    hablar("Pasando a la anterior.")
    subprocess.Popen(["playerctl", "previous"])

def pausar_multimedia():
    hablar("Pausando.")
    subprocess.Popen(["playerctl", "pause"])

def reanudar_multimedia():
    hablar("Reanudando.")
    subprocess.Popen(["playerctl", "play"])

def siguiente_cancion():
    hablar("Pasando a la siguiente.")
    subprocess.Popen(["playerctl", "next"])
"""

def de_nada():
    """Contesta el agradecimiento."""
    hablar("De nada, fue un placer.")

def decir_hora():
    """Dice la hora actual."""
    hora_actual = datetime.now().strftime("%I:%M %p")
    hablar(f"Son las {hora_actual}")

# --- NUEVOS COMANDOS DE LECTURA ---
def empezar_a_leer():
    """Inicia la lectura de un libro en un hilo secundario."""
    global lector_thread, parar_lectura
    
    # Ruta al libro que quieres leer (puedes cambiarla)
    ruta_libro = os.path.expanduser("PEGA_LA_CARPETA_DE_TUS_LIBROS") 

    if not os.path.exists(ruta_libro):
        hablar(f"No encontré el libro en la ruta {ruta_libro}")
        return

    # Si ya hay un hilo leyendo, no hagas nada
    if lector_thread and lector_thread.is_alive():
        hablar("Ya estoy leyendo un libro.")
        return

    texto_del_libro = extraer_texto_de_archivo(ruta_libro)
    if texto_del_libro:
        hablar("Muy bien, comenzando la lectura.")
        parar_lectura.clear() # Reinicia el evento de parada
        lector_thread = threading.Thread(target=hilo_lector, args=(texto_del_libro, parar_lectura))
        lector_thread.start()

def detener_lectura():
    """Detiene el hilo de lectura actual."""
    global lector_thread
    if lector_thread and lector_thread.is_alive():
        hablar("Ok, deteniendo la lectura.")
        parar_lectura.set() # Envía la señal para parar
    else:
        hablar("No estaba leyendo nada.")

# --- NUEVAS FUNCIONES PARA LECTURA DE LIBROS ---

import PyPDF2
from ebooklib import epub
from bs4 import BeautifulSoup

def _extraer_de_txt(ruta):
    """Extrae texto de un archivo .txt."""
    with open(ruta, 'r', encoding='utf-8') as f:
        return f.read()

def _extraer_de_pdf(ruta):
    """Extrae texto de un archivo .pdf."""
    texto = ""
    with open(ruta, 'rb') as f:
        lector_pdf = PyPDF2.PdfReader(f)
        for pagina in lector_pdf.pages:
            texto += pagina.extract_text()
    return texto

def _extraer_de_epub(ruta):
    """Extrae texto de un archivo .epub."""
    libro = epub.read_epub(ruta)
    texto = ""
    for item in libro.get_items_of_type(9): # 9 es el tipo para documentos de texto
        soup = BeautifulSoup(item.get_content(), 'html.parser')
        texto += soup.get_text()
    return texto

def extraer_texto_de_archivo(ruta):
    """Detecta el tipo de archivo y extrae el texto."""
    if ruta.endswith('.txt'):
        return _extraer_de_txt(ruta)
    elif ruta.endswith('.pdf'):
        return _extraer_de_pdf(ruta)
    elif ruta.endswith('.epub'):
        return _extraer_de_epub(ruta)
    else:
        hablar("Lo siento, no puedo leer ese formato de archivo.")
        return None

def hilo_lector(texto_libro, evento_parar):
    """Esta función se ejecuta en un hilo separado para leer el libro."""
    frases = texto_libro.replace('\n', ' ').split('. ')
    
    for frase in frases:
        if evento_parar.is_set():
            print("Hilo de lectura detenido.")
            break
        
        if frase.strip():
            hablar(frase.strip() + ".")
            # AÑADE ESTA LÍNEA para dar una pausa y permitir que el hilo principal escuche
            time.sleep(0.1) 
    
    # Esta línea se ejecuta solo si el libro termina sin ser interrumpido
    if not evento_parar.is_set():
        hablar("He terminado de leer.")

# --- FIN DE NUEVAS FUNCIONES ---

# Diccionario que conecta frases clave con las funciones a ejecutar.
comandos_disponibles = {
    "qué puedes hacer": listar_comandos,
    "abre el navegador": abrir_navegador,
    "abre el gestor de archivos": abrir_gestor_archivos,
    "abre la terminal": abrir_terminal,
    "anterior": anterior_cancion,
    "pausa": pausar_multimedia,
    "reproduce": reanudar_multimedia,
    "siguiente": siguiente_cancion,
    "empieza a leer": empezar_a_leer,
    "para de leer": detener_lectura,
    "detente": detener_lectura,
    "gracias": de_nada,
    "qué hora es": decir_hora
}

# --- INICIALIZACIÓN DE SERVICIOS DE AUDIO ---

# 1. Configurar Vosk con vocabulario específico
vosk.SetLogLevel(-1)
model = vosk.Model(MODEL_PATH)

frases_clave = list(comandos_disponibles.keys())
frases_clave.extend([WAKE_WORD, "nada", "descansa", "busca en google"])
vocabulario = json.dumps(frases_clave)

recognizer = vosk.KaldiRecognizer(model, 16000, vocabulario)

# 2. Configurar Porcupine para la palabra de activación
porcupine = pvporcupine.create(
    access_key=PICOVOICE_ACCESS_KEY,
    keywords=[WAKE_WORD]
)

# 3. Configurar PyAudio para la grabación
pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

def ejecutar_comando(comando):
    """Procesa y ejecuta los comandos usando el diccionario."""
    comando = comando.lower()

    # --- Lógica para comandos con argumentos ---
    match_busqueda = re.search(r'busca en google (.+)', comando)
    if match_busqueda:
        termino_busqueda = match_busqueda.group(1)
        if termino_busqueda:
            hablar(f"Buscando '{termino_busqueda}' en Google.")
            webbrowser.open(f"https://www.google.com/search?q={termino_busqueda.replace(' ', '+')}")
            return True # Comando ejecutado

    if "nada" in comando or "descansa" in comando:
        hablar("Hasta luego.")
        return False

    for frase_clave, funcion in comandos_disponibles.items():
        if frase_clave in comando:
            funcion()
            return True

    hablar("Error al interpretar.")
    return True

# --- BUCLE PRINCIPAL ---
print(f"Escuchando la palabra de activación ('{WAKE_WORD}')...")
hablar("Bienvenido")

# Mantenemos el bloque try/finally externo para asegurar la limpieza final
try:
    while True:
        try:
            # 1. Escuchar la palabra de activación
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            if porcupine.process(pcm) >= 0:
                print("¡Palabra de activación detectada!")

                # --- INICIO DE LA VERIFICACIÓN DE VOZ (SILENCIOSA) ---
                print("Verificando huella de voz...")
                # ... (la lógica de verificación que ya tienes) ...
                frames_verificacion = []
                for _ in range(0, int(RATE / CHUNK * 2)):
                    data = audio_stream.read(CHUNK, exception_on_overflow=False)
                    frames_verificacion.append(data)

                audio_data = np.frombuffer(b''.join(frames_verificacion), dtype=np.int16)
                signal = torch.from_numpy(audio_data.copy()).float()
                
                huella_actual = verification.encode_batch(signal)
                similitud = verification.similarity(TU_HUELLA, huella_actual)
                
                score = similitud.squeeze().item() 
                prediction = score > 0.5 # Puedes bajarlo
                
                if prediction and score > 0.5: # Lo recomiendo bajar si esta en fase de pruebas
                    print(f"Voz reconocida. Similitud: {score:.2f}")
                    hablar("¿Qué necesitas?.")
                    # 2. Escuchar el comando después de la activación
                    while True:
                        data = audio_stream.read(4096, exception_on_overflow=False)
                        if recognizer.AcceptWaveform(data):
                            result_json = json.loads(recognizer.Result())
                            comando_texto = result_json.get("text", "")

                            if comando_texto:
                                print(f"Usuario: {comando_texto}")
                                if not ejecutar_comando(comando_texto):
                                    raise KeyboardInterrupt 
                                break 
                else:
                    print(f"Voz no reconocida. Similitud: {score:.2f}")
                    hablar("No reconozco esa voz.")

        except KeyboardInterrupt:
            # Capturamos Ctrl+C aquí dentro del bucle
            if lector_thread and lector_thread.is_alive():
                # Si está leyendo, solo detenemos la lectura
                print("\nInterrumpiendo la lectura...")
                detener_lectura()
                continue # Y continuamos el bucle principal
            else:
                # Si no está leyendo, rompemos el bucle para salir
                raise KeyboardInterrupt # Lanzamos la excepción de nuevo para que la capture el try/except externo

finally:
    # Este bloque se ejecuta al final, sin importar cómo salimos del bucle
    print("Hasta luego.")
    
    # Detener la lectura si todavía está activa al salir
    if lector_thread and lector_thread.is_alive():
        detener_lectura()

    # Limpieza de recursos al cerrar
    if porcupine is not None:
        porcupine.delete()
    if audio_stream is not None:
        audio_stream.close()
    if pa is not None:
        pa.terminate()
