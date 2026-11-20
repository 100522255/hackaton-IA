#!/usr/bin/env python3
"""
tutor.py -- Ejemplo de tutor virtual con IA para el aula.
Aulife, noviembre 2026.

Este es un ejemplo de punto de entrada. Conecta con el proxy LiteLLM
y permite hacer preguntas sobre el corpus de documentos.

CÓMO FUNCIONA:
1. Carga los documentos del corpus.
2. Cuando el usuario hace una pregunta, busca los fragmentos relevantes.
3. Envía la pregunta + contexto al modelo de IA.
4. Muestra la respuesta.

QUÉ PUEDES MEJORAR (ideas para el taller):
- Interfaz web con Gradio, Streamlit, Flask o cualquier framework.
- Búsqueda por embeddings en vez de por palabras.
- Memoria de la conversación (ahora mismo cada pregunta es independiente).
- Soporte multimodal (enviar imágenes/diagramas al modelo).
- Ingesta de más formatos: HTML, vídeos de YouTube, presentaciones.
- Evaluación automática: que el tutor haga preguntas al estudiante.
- Personalización: que el tutor adapte el nivel al estudiante.
- Múltiples asignaturas.
"""

import os
import base64
import mimetypes
from dotenv import load_dotenv
from openai import OpenAI
from cargar_documentos import cargar_corpus, buscar_relevantes

# Cargar configuración desde variables de entorno o archivo .env
ruta_env = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(ruta_env)

PROXY_URL = os.getenv("PROXY_URL", "https://aulife-proxy-66041181251.europe-west1.run.app")
API_KEY = os.getenv("API_KEY", "")

# Idea 2: modelo razonador para resolver matemáticas.
MATH_MODEL = os.getenv("MATH_MODEL", "gemini-4-argon")
# Idea 3: modelo para ver y explicar diagramas.
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-4-argon")

client = OpenAI(
    base_url=f"{PROXY_URL}/v1",
    api_key=API_KEY,
)

SYSTEM_PROMPT = """Eres un tutor virtual universitario especializado en matemáticas y en la interpretación de diagramas de Inteligencia Artificial.

Objetivos:
- Resolver problemas paso a paso, numerando claramente cada operación y justificando por qué se realiza.
- Si el estudiante pide ampliar un paso concreto (por ejemplo, «no entiendo el paso 3»), vuelve a explicar únicamente ese paso con un ejemplo o una analogía, sin repetir toda la solución.
- Al analizar una imagen, comienza siempre con una sección «Lo que veo» donde describas elementos, relaciones, etiquetas y texto visible. Después responde a la pregunta del estudiante en una sección «Explicación» y señala qué partes del diagrama justifican la respuesta.
- Si falta información visual o el texto no es legible, indícalo explícitamente y formula una pregunta breve al estudiante.
- Basa tus respuestas en el material del curso proporcionado.
- Responde SOLO en español.
- No des la solución final como un resultado aislado: explica el razonamiento y verifica el resultado.
- Usa fórmulas legibles. Si empleas una analogía, aclara que es una simplificación.
- Termina con una pregunta de comprobación o una sugerencia de seguimiento.
"""


def codificar_imagen(ruta: str) -> tuple[str, str]:
    """Codifica una imagen local y devuelve sus datos base64 y MIME."""
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"No se encontró la imagen: {ruta}")

    tipo_mime, _ = mimetypes.guess_type(ruta)
    if tipo_mime not in ("image/png", "image/jpeg", "image/gif", "image/webp"):
        raise ValueError("Formato no válido. Usa PNG, JPG, JPEG, GIF o WEBP.")

    with open(ruta, "rb") as archivo:
        datos = base64.b64encode(archivo.read()).decode("utf-8")
    return datos, tipo_mime


def chat_con_contexto(
    pregunta: str,
    documentos: list[dict],
    historial: list[dict] | None = None,
    ruta_imagen: str | None = None,
) -> str:
    """Envía una consulta de texto o multimodal al tutor."""
    contexto = buscar_relevantes(pregunta, documentos)
    mensajes = [{"role": "system", "content": SYSTEM_PROMPT}]

    if historial:
        mensajes.extend(historial)

    texto_usuario = f"""Pregunta del estudiante: {pregunta}

Material del curso relevante:
{contexto}

Responde siguiendo las reglas del tutor. Si la pregunta es matemática, usa pasos numerados y justifica cada operación."""

    if ruta_imagen:
        imagen_base64, tipo_mime = codificar_imagen(ruta_imagen)
        contenido = [
            {"type": "text", "text": texto_usuario},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{tipo_mime};base64,{imagen_base64}"},
            },
        ]
        mensajes.append({"role": "user", "content": contenido})
        modelo = IMAGE_MODEL
    else:
        mensajes.append({"role": "user", "content": texto_usuario})
        modelo = MATH_MODEL

    respuesta = client.chat.completions.create(
        model=modelo,
        messages=mensajes,
        temperature=0.3,
        max_tokens=1500,
        extra_body={
            "metadata": {
                "request_type": "app",
                "tags": ["app", "matematicas", "multimodal"],
            }
        },
    )

    return respuesta.choices[0].message.content


def main():
    """Bucle principal del tutor en terminal."""
    print("=" * 60)
    print("  TUTOR DE MATEMÁTICAS Y DIAGRAMAS")
    print("  Aulife -- Noviembre 2026")
    print("=" * 60)
    print()

    print("Cargando documentos del curso...")
    ruta_corpus = os.path.join(os.path.dirname(__file__), '..', 'corpus')
    documentos = cargar_corpus(ruta_corpus)
    historial = []
    ruta_imagen = None

    print("\nComandos:")
    print("  /imagen ruta/a/diagrama.png [pregunta]")
    print("  /limpiar")
    print("  salir")
    print("\nTambién puedes pedir: 'no entiendo el paso 3'.\n")

    while True:
        pregunta = input("Estudiante > ").strip()

        if not pregunta:
            continue
        if pregunta.lower() in ("salir", "exit", "quit"):
            print("\nHasta la próxima. Sigue aprendiendo.")
            break

        if pregunta.lower() == "/limpiar":
            historial = []
            ruta_imagen = None
            print("\nConversación e imagen actuales borradas.\n")
            continue

        if pregunta.lower().startswith("/imagen"):
            contenido_comando = pregunta[len("/imagen"):].strip()

            if not contenido_comando:
                print("\nUso: /imagen ruta/a/diagrama.png ¿Qué representa?\n")
                continue

            partes = contenido_comando.rsplit(" ", 1)
            ruta_candidata = partes[0]

            # Permite rutas sin extensión añadida a la pregunta si existen como un todo.
            if os.path.isfile(contenido_comando):
                ruta_imagen = contenido_comando
                pregunta = "Describe y explica este diagrama paso a paso."
            elif os.path.isfile(ruta_candidata):
                ruta_imagen = ruta_candidata
                pregunta = partes[1]
            elif len(contenido_comando.split()) > 1:
                ruta_imagen = contenido_comando.split()[0]
                pregunta = " ".join(contenido_comando.split()[1:])
            else:
                ruta_imagen = contenido_comando
                pregunta = "Describe y explica este diagrama paso a paso."

            if not os.path.isfile(ruta_imagen):
                print(f"\nError: no se encuentra la imagen '{ruta_imagen}'.\n")
                ruta_imagen = None
                continue

        print("\nTutor: Pensando...\n")

        try:
            respuesta = chat_con_contexto(
                pregunta,
                documentos,
                historial,
                ruta_imagen=ruta_imagen,
            )
            print(f"Tutor > {respuesta}\n")

            historial.append({"role": "user", "content": pregunta})
            historial.append({"role": "assistant", "content": respuesta})
            if len(historial) > 20:
                historial = historial[-20:]

        except Exception as e:
            print(f"Error al contactar con el modelo: {e}\n")
            print("Comprueba la conexión, la clave y que la imagen existe. Puedes seguir intentando.\n")


if __name__ == "__main__":
    main()
