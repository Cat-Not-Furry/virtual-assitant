## Asistente de Voz "Jarvis" para Linux<br>

Un asistente de voz personal, offline-first y altamente personalizable, construido con Python para sistemas GNU/Linux.<br>Se activa con una palabra clave, verifica la identidad del hablante mediante una huella de voz y ejecuta una variedad de comandos, desde abrir aplicaciones hasta leer libros en voz alta.<br>
<br>
Características Principales:
Palabra de Activación (Wake Word): Utiliza pvporcupine para una detección de la palabra "Jarvis" de bajo consumo y siempre activa.<br>
Reconocimiento de Voz Offline: Emplea vosk para una transcripción de voz a texto rápida y privada, sin depender de la nube.<br>
Verificación de Hablante: Usa speechbrain para crear una huella de voz única, asegurando que el asistente solo responda a su propietario.<br>
Voz Natural (TTS): Integra piper-tts para generar respuestas habladas con una voz fluida y de alta calidad, funcionando completamente offline.<br>
Lector de Libros: Capaz de leer archivos .txt, .pdf y .epub en un hilo secundario, permitiendo la interrupción por voz o con Ctrl+C.<br>
Control del Sistema: Abre aplicaciones, controla la reproducción multimedia (playerctl, si tu distro lo tiene) y realiza búsquedas en la web.<br>
Modular y Extensible: Añadir nuevos comandos es tan simple como definir una función y registrarla en un diccionario.

<h3>Requisitos<br>
Lenguaje: Python 3.11<br>
Entorno: pyenv + venv<br>
Wake Word: Picovoice Porcupine<br>
Speech-to-Text (STT): Vosk<br>
Speaker Verification: SpeechBrain<br>
Text-to-Speech (TTS): Piper TTS<br>
Audio I/O: PyAudio</h3>

## Instalación y Configuración.

>[!WARNING]
>Este proyecto fue desarrollado en Arch Linux. La instalación en otras distribuciones puede requerir ajustes en los nombres de los paquetes del sistema.
<br>

## 1. Configurar el Entorno de Python
<h3>Se recomienda usar pyenv para gestionar la versión de Python y evitar conflictos con el sistema.</h3>

### Instalar pyenv y dependencias para compilar Python

```bash
sudo (tu gestor de paquetes) install pyenv base-devel openssl zlib xz tk
```

### Configurar pyenv en tu shell (añadir a ~/.bashrc o ~/.zshrc)

```bash
EDITOR ~/.(tu shell)rc
```

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
```

### Reinicia tu terminal e instala Python 3.11

```bash
source ~/.(tu shell).rc
pyenv install 3.11.9
```

### Asigna esta versión de Python al directorio del proyecto

```bash
cd /ruta/al/proyecto
pyenv local 3.11.9
```

## 2. Crear Entorno Virtual e Instalar Dependencias
### Crear el venv (usará Python 3.11)

```bash
python -m venv venv
```

### Activar el venv

```bash
source venv/bin/activate
```

### Instalar librerías de Python desde el archivo requirements.txt

```pip
pip install -r requirements.txt
```

## 3. Instalar Dependencias del Sistema
### Herramientas de audio y control multimedia

```bash
sudo (tu gestor de paquetes) portaudio espeak-ng playerctl
```

### Instalar Piper TTS (binario pre-compilado recomendado)
### Descargar el archivo (tu arquitectura)-linux-gnu.tar.gz desde la página de releases de <a href="https://github.com/rhasspy/piper/releases">Piper</a>

```bash
tar -xvf piper_*.tar.gz
sudo mv piper /opt/
sudo ln -s /opt/piper/piper /usr/local/bin/piper
```

## 4. Descargar Modelos
<h3>Este proyecto requiere varios modelos que no se incluyen en el repositorio.<br>
Modelo Vosk (STT): Descarga un modelo en español desde <a href="https://alphacephei.com/vosk/models">Vosk Models</a> y descomprímelo en la raíz del proyecto.<br>
Modelo Piper (TTS): Descarga un modelo de voz en español desde <a href="https://huggingface.co/rhasspy/piper-voices/tree/main/es/es_MX/ald/medium">Piper Samples</a> y colócalo en una carpeta.<br>
Actualiza la ruta en el script.</h3>

```python
/home/usuario/la/carpeta/para/piper.onnx
```

## 5. Configuración de Claves y Huella de Voz
<h3>Claves API: Edita asistente.py y añade tus claves para TU_CLAVE_DE_PICOVOICE.<br>
Huella de Voz:<br>
Ejecuta el script crear_huella.py:<br>
<br>
    
```bash
python crear_huella.py
```

Sigue las instrucciones para grabar tu voz.<br>
Esto generará el archivo mi_huella.pt, que el asistente principal usará para reconocerte.<br>
Uso<br>
Una vez completada la configuración, ejecuta el asistente desde la raíz del proyecto.</h3>

>[!NOTE]
>Asegúrate de que tu venv esté activado
>
>```bash
>source venv/bin/activate
>```

### Ejecuta el script (se recomienda redirigir stderr para una salida limpia)

```bash
python asistente.py 2>/dev/null
```

<h3>El asistente se iniciará, cargará los modelos y comenzará a escuchar la palabra de activación "Jarvis".<br>
¿Cómo Añadir Nuevos Comandos?<br>
Añadir nuevas habilidades es muy sencillo:<br>
Crea una función: Escribe una nueva función en asistente.py que realice la acción deseada.</h3>

<h3>def mi_nueva_funcion():<br>
    hablar("Ejecutando mi nueva e increíble función.")<br>
    # ... tu código aquí ...</h3>

### Regístrala en el diccionario: Añade la función y la frase que la activará al diccionario comandos_disponibles.

<h3>comandos_disponibles = {<br>
    # ... otros comandos ...<br>
    "haz algo increíble": mi_nueva_funcion</h3>
}

### ¡Y listo! El asistente ahora reconocerá y ejecutará tu nuevo comando.

#### Ideado por Cat-Not-Furry, diseñado y programado por Cat-Not-Furry y <a href="https://gemini.google.com/">Gemini</a>
