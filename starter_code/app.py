#!/usr/bin/env python3
"""
app.py -- Interfaz web del tutor (Gradio).
Aulife, noviembre 2026.

Reutiliza la lógica de tutor.py y añade:
- Chat con fórmulas bien renderizadas (LaTeX).
- Subida de imágenes/diagramas.
- Respuesta por voz en el navegador (gTTS).

Ejecutar:  py app.py   y abrir http://127.0.0.1:7860
"""

import os
import re
import tempfile

import gradio as gr
from gtts import gTTS

from cargar_documentos import cargar_corpus
from tutor import chat_con_contexto

# Cargar el corpus una sola vez al arrancar.
RUTA_CORPUS = os.path.join(os.path.dirname(__file__), "..", "corpus")
DOCUMENTOS = cargar_corpus(RUTA_CORPUS)

PREGUNTA_IMAGEN = "Describe y explica este diagrama paso a paso."

EJEMPLOS = [
    "Resuelve 2x + 4 = 10",
    "¿Qué es una derivada? Explícamelo con un ejemplo sencillo.",
    "Resuelve x/3 + x/2 + 12 = x",
    "No entiendo el paso 2",
]


# ---------------------------------------------------------------------------
# Voz
# ---------------------------------------------------------------------------

def limpiar_para_voz(texto: str) -> str:
    """Convierte Markdown y LaTeX en texto que suene natural al leerlo."""
    texto = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r" \1 entre \2 ", texto)
    texto = re.sub(r"\\sqrt\{([^{}]*)\}", r" raíz cuadrada de \1 ", texto)
    texto = re.sub(r"\\(cdot|times)", " por ", texto)
    texto = re.sub(r"\\[a-zA-Z]+", " ", texto)       # resto de comandos LaTeX
    texto = re.sub(r"[*#`\x24_>|{}\\]", "", texto)       # símbolos de Markdown
    texto = re.sub(r"^-{3,}[ \t]*(?=\n|\Z)", "", texto, flags=re.M)  # separadores ---
    reemplazos = {
        "^2": " al cuadrado ", "²": " al cuadrado ", "^3": " al cubo ", "³": " al cubo ",
        "=": " igual a ", "+": " más ", "−": " menos ", "×": " por ", "/": " entre ",
    }
    for simbolo, palabra in reemplazos.items():
        texto = texto.replace(simbolo, palabra)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto[:1500]


def texto_a_voz(texto: str) -> str | None:
    """Genera un MP3 con la respuesta y devuelve su ruta (o None si falla)."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as archivo:
            ruta = archivo.name
        gTTS(limpiar_para_voz(texto), lang="es").save(ruta)
        return ruta
    except Exception as e:
        print(f"No se pudo generar la voz: {e}")
        return None


# ---------------------------------------------------------------------------
# Lógica del chat
# ---------------------------------------------------------------------------

def responder(mensaje, imagen, voz_activada, chat, historial):
    """Envía la pregunta al tutor y va actualizando la interfaz."""
    mensaje = (mensaje or "").strip()
    if not mensaje and not imagen:
        yield chat, historial, gr.update(), gr.update(), None
        return
    if not mensaje:
        mensaje = PREGUNTA_IMAGEN

    # Mostrar al momento lo que ha enviado el estudiante.
    chat = chat + [{"role": "user", "content": mensaje}]
    if imagen:
        chat.append({"role": "user", "content": {"path": imagen}})
    chat.append({"role": "assistant", "content": "⏳ *Pensando...*"})
    yield chat, historial, "", None, None

    try:
        respuesta = chat_con_contexto(mensaje, DOCUMENTOS, historial, ruta_imagen=imagen)
    except Exception as e:
        chat[-1] = {"role": "assistant", "content": f"⚠️ Error al contactar con el modelo:\n\n`{e}`"}
        yield chat, historial, "", None, None
        return

    chat[-1] = {"role": "assistant", "content": respuesta}
    historial = (historial + [
        {"role": "user", "content": mensaje},
        {"role": "assistant", "content": respuesta},
    ])[-20:]

    # Mostrar el texto primero y luego generar el audio.
    yield chat, historial, "", None, None
    audio = texto_a_voz(respuesta) if voz_activada else None
    yield chat, historial, "", None, audio


def limpiar():
    """Borra la conversación."""
    return [], [], "", None, None


# ---------------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------------

TEMA = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="violet",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
)

CSS = """
#cabecera {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    border-radius: 16px; padding: 22px 28px; color: white;
}
#cabecera h1 { margin: 0; font-size: 1.8rem; color: white; }
#cabecera p  { margin: 6px 0 0; opacity: .9; color: white; }
#chat { border-radius: 16px; }
.boton-ejemplo { text-align: left !important; }
footer { display: none !important; }
"""

# Delimitadores de fórmulas. Se escriben con códigos (\x24 = símbolo de dólar,
# \x5c = barra invertida) para que el archivo no se rompa al copiarlo y pegarlo.
DOLAR, BARRA = "\x24", "\x5c"
LATEX = [
    {"left": DOLAR * 2, "right": DOLAR * 2, "display": True},
    {"left": DOLAR, "right": DOLAR, "display": False},
    {"left": BARRA + "(", "right": BARRA + ")", "display": False},
    {"left": BARRA + "[", "right": BARRA + "]", "display": True},
]

with gr.Blocks(title="Tutor de Matemáticas · Aulife") as demo:
    historial = gr.State([])

    gr.HTML(
        """<div id="cabecera">
             <h1>🎓 Tutor de Matemáticas y Diagramas</h1>
             <p>Pregunta lo que quieras, sube un diagrama y escucha la explicación.</p>
           </div>"""
    )

    with gr.Row(equal_height=False):
        # Columna principal: el chat.
        with gr.Column(scale=3):
            chat = gr.Chatbot(
                elem_id="chat",
                show_label=False,
                height=560,
                latex_delimiters=LATEX,
                placeholder="### 👋 ¡Hola!\nEscribe una pregunta o elige un ejemplo de la derecha.",
            )
            with gr.Row():
                mensaje = gr.Textbox(
                    placeholder="Escribe tu pregunta… (Enter para enviar)",
                    show_label=False,
                    scale=5,
                    autofocus=True,
                )
                enviar = gr.Button("Enviar ➤", variant="primary", scale=1)

        # Columna lateral: imagen, voz y ejemplos.
        with gr.Column(scale=1, min_width=280):
            imagen = gr.Image(
                label="📎 Diagrama o fórmula (opcional)",
                type="filepath",
                sources=["upload", "clipboard"],
                height=200,
            )
            voz = gr.Checkbox(label="🔊 Leer la respuesta en voz alta", value=True)
            audio = gr.Audio(label="Explicación por voz", autoplay=True, interactive=False)

            gr.Markdown("**💡 Prueba con:**")
            botones = [gr.Button(e, size="sm", elem_classes="boton-ejemplo") for e in EJEMPLOS]

            borrar = gr.Button("🗑️ Nueva conversación", variant="secondary")

    entradas = [mensaje, imagen, voz, chat, historial]
    salidas = [chat, historial, mensaje, imagen, audio]

    mensaje.submit(responder, entradas, salidas)
    enviar.click(responder, entradas, salidas)
    borrar.click(limpiar, None, salidas)
    for boton in botones:
        boton.click(lambda t=boton.value: t, None, mensaje)


if __name__ == "__main__":
    demo.launch(theme=TEMA, css=CSS, inbrowser=True)

