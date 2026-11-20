# Write-up: Tutor matemático multimodal

> Aulife -- Noviembre 2026
> Universidad Carlos UC3M

## 1. Enfoque y arquitectura

El proyecto combina las ideas 2 y 3: un tutor que resuelve problemas matemáticos paso a paso y otro capaz de interpretar diagramas, gráficas y esquemas cargados por el estudiante.

Arquitectura:
1. El programa carga el corpus de `corpus/`.
2. Para una pregunta textual, busca fragmentos relevantes por coincidencia de palabras.
3. Para una imagen, el comando `/imagen` codifica el archivo en base64 y crea un mensaje multimodal.
4. Se añade el historial reciente y se envía la consulta al proxy compatible con OpenAI.
5. El resultado se muestra en terminal y se conserva hasta diez interacciones recientes.

## 2. Decisiones técnicas

### Modelo elegido
- Se usa `gemini-4-argon` para matemáticas y análisis de imágenes porque está recomendado para razonamiento de calidad y se ajusta a las dos modalidades.
- Puede configurarse por separado mediante `MATH_MODEL` e `IMAGE_MODEL` en `starter_code/.env`.
- Se utiliza `temperature=0.3` para favorecer respuestas consistentes y verificables. El límite de salida es de 1500 tokens.

### Método de búsqueda en el corpus
- Se mantiene inicialmente la búsqueda por coincidencia de palabras del starter code.
- Es una solución deliberadamente sencilla que permite demostrar el funcionamiento RAG sin añadir dependencias adicionales.
- Como mejora futura se plantea TF-IDF o embeddings semánticos.

### Prompt del sistema
- Obliga a presentar las soluciones matemáticas como pasos numerados y justificadas.
- Permite ampliar un solo paso solicitado por el estudiante.
- Exige describir primero «Lo que veo» al analizar una imagen y después explicar su significado.
- Indica al modelo que no invente si falta información o si la imagen no es legible.

### Interfaz de usuario
- Se usa una interfaz de terminal por su sencillez y facilidad de demostración durante el taller.
- El comando `/imagen` permite cambiar de imagen o hacer preguntas de seguimiento.
- `/limpiar` reinicia el historial y la imagen seleccionada.

### Formatos de corpus procesados
- Texto plano `.txt` y Markdown `.md` mediante `cargar_documentos.py`.
- PDF mediante PyPDF2 si está instalado.
- Imágenes PNG, JPG, JPEG, GIF y WEBP mediante codificación base64.

## 3. Despliegue

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r starter_code/requirements.txt
copy starter_code\.env.ejemplo starter_code\.env
python starter_code/verificar_setup.py
python starter_code/tutor.py
```

Las credenciales se leen de `starter_code/.env`, excluido de Git mediante `.gitignore`.

## 4. Resultados

Pendiente de añadir las respuestas obtenidas durante las pruebas finales con el modelo y las credenciales del taller.

### Ejemplo 1
- **Pregunta:** [problema matemático probado]
- **Respuesta del tutor:** [respuesta generada]
- **Valoración:** [correctitud, claridad y utilidad]

### Ejemplo 2
- **Pregunta:** [petición para ampliar un paso concreto]
- **Respuesta del tutor:** [respuesta generada]
- **Valoración:** [valoración breve]

### Ejemplo 3
- **Pregunta:** [pregunta sobre un diagrama cargado]
- **Respuesta del tutor:** [respuesta generada]
- **Valoración:** [valoración breve]

## 5. Dificultades encontradas

- La búsqueda básica por palabras puede ignorar sinónimos o relaciones semánticas.
- Las imágenes deben estar disponibles en el sistema local y tener un formato compatible.
- Es necesario separar claramente las credenciales de desarrollo del repositorio público.
- Una imagen puede contener texto pequeño o ilegible, por lo que el modelo debe pedir confirmación si no puede verlo.

## 6. Posibles mejoras

- Implementar búsqueda TF-IDF o embeddings para recuperar mejor el corpus.
- Añadir entrada por voz siguiendo `ejemplo_voz.py`.
- Incorporar una interfaz web con Gradio o Streamlit.
- Permitir cargar varias imágenes y PDFs en la misma sesión.
- Añadir validación matemática independiente para comprobar operaciones y resultados.
- Guardar sesiones y permitir exportar el write-up de una resolución.

## 7. Conclusiones

- Un prompt específico mejora mucho la consistencia frente a una petición general.
- La combinación de texto estructurado e imágenes permite convertir apuntes estáticos en explicaciones interactivas.
- Mantener el historial ayuda a preguntar por pasos concretos sin repetir todo el contexto.
