# COGNITIVE AGENT

# 1.Enfoque y arquitectura

1.1 ¿Qué hace nuestro tutor que lo diferencia del starter code?  
Nuestro proyecto parte del código inicial proporcionado, pero lo hemos modificado para crear un tutor especializado en matemáticas y ciencias, teniendo en cuenta las necesidades de estudiantes con discapacidades visuales.

Las principales diferencias son:

* El tutor divide los problemas en pasos y explica qué se hace y por qué se realiza cada operación.  
* Usa frases cortas, lenguaje sencillo y expresiones matemáticas fáciles de leer.  
* Permite enviar imágenes de gráficos, diagramas y ejercicios matemáticos para que el modelo los describa y explique.  
* Si el estudiante no entiende un paso concreto, el tutor se centra únicamente en ese paso y lo explica de una manera más sencilla.  
* Permite guardar los últimos mensajes para que el estudiante pueda hacer preguntas de seguimiento sin empezar desde cero.  
* Permite configurar por separado el modelo usando para preguntas de texto y el utilizado para preguntas con imágenes.

1.2 Arquitectura general

Interfaz de terminal: permite al estudiante introducir preguntas, enviar imágenes y gestionar la conversación.

Carga del corpus: utilice cargar\_corpus() para cargar los documentos del curso.

Búsqueda de información: utiliza buscar\_relevantes() para encontrar fragmentos de los documentos relacionados con la pregunta.

Procesamiento de imágenes: utiliza codificar\_imagen() para convertir las imágenes a Base64 y prepararlas para enviarlas al modelo.

Gestión del contexto: combina la pregunta del estudiante, los documentos relevantes, el histórico y las instrucciones del sistema.

Modelo de IA: se comunica con el modelo a través de LiteLLM, Proxy y genera una respuesta adaptada a las necesidades del estudiante.

1.3 Funcionamiento

1) El estudiante introduce una pregunta por texto o por imagen.  
2) El programa busca información relacionada con la pregunta en el corpus del curso.  
3) Se prepara el mensaje incluyendo la pregunta, el material relevante y las instrucciones del tutor.  
4) Si el estudiante ha enviado una imagen, esta se convierte a Base64 y se incluye en la petición.  
5) El sistema selecciona el modelo correspondiente según el tipo de consulta: texto o imagen.  
6) Se envía la petición al modelo mediante LiteLLM Proxy.  
7) Modelo genera una respuesta siguiendo las instrucciones del System Prompt.  
8) La respuesta se muestra por texto y por voz (voz opcional) y se guarda junto con la pregunta en el historial de conversación.

# 2.Decisiones técnicas

2.1 Modelos utilizados

Hemos configurado 2 modelos diferentes para separar el tratamiento de las preguntas de texto y las preguntas que incluyen imágenes:  
MATH\_MODEL: modelo usado para resolver problemas matemáticos y responder preguntas de texto.  
y IMAGE\_MODEL: modelo utilizado para interpretar imágenes y explicar diagramas.

Se usa gemini-4-argon para matemáticas y análisis de imágenes porque está recomendado para razonamiento de calidad y se ajusta a las dos modalidades.  
Temperature 0.3 y max\_tokens de 1500\.  
Temperature: 0,3, valor relativamente bajo para favorecer respuestas más estables y coherentes, especialmente en la resolución de problemas matemáticos.

Max\_tokens: 1500, permite generar respuestas más completas, con espacio suficiente para explicar los diferentes pasos y justificar las operaciones.

2.2. Método de búsqueda en el corpus

El sistema utiliza la función buscar\_relevantes() para recuperar información del material del curso relacionado con la pregunta del estudiante.

Los fragmentos recuperados se incorporan al mensaje enviado al modelo, de manera que la respuesta pueda apoyarse en los contenidos proporcionados.

Este funcionamiento sigue el enfoque de RAG (Retrieval-Augmented Generation), que combina la recuperación de información con la generación de respuestas mediante IA.  
El método concreto de búsqueda (palabras clave, TF-IDF, incrustaciones u otros) se confirmar revisando la implementación de buscar\_relevantes() en cargar\_documentos.py.

2.3. System Prompt

Hemos diseñado un System Prompt específico para adaptar el comportamiento del modelo a las necesidades de nuestro proyecto.

Las instrucciones principales son:

- Estructura numerada: las explicaciones deben organizarse en pasos claramente identificados.

- Justificación de cada paso: el tutor debe explicar qué operación realiza y por qué es necesaria.

- Lenguaje accesible: debe utilizar frases cortas, directas y fáciles de comprender.

- Descripción de imágenes: cuando se recibe una imagen, debe comenzar con la sección «Descripción Visual:», identificando los elementos, etiquetas y relaciones importantes antes de explicar el ejercicio.

- Modo Zoom: si el estudiante indica que no entiende un paso concreto, el tutor debe centrarse únicamente en ese paso y dividir la explicación en partes más sencillas.

- Comprobación: debe verificar el resultado y terminar con una pregunta sencilla para comprobar la comprensión.

Además, el tutor debe responder exclusivamente en español y basar sus explicaciones en el material del curso proporcionado.

2.4. Interfaz

El estudiante puede interactuar directamente con el tutor mediante la interfaz, sin necesidad de desarrollar una aplicación web adicional.  
Además de introducir preguntas normales, hemos añadido 3 comandos:

* /imagen ruta/a/diagrama.png \[pregunta\]: permite enviar una imagen y realizar una pregunta sobre ella.

* /limpiar: elimina el historial de conversación y la imagen actual.

* salir: finaliza la ejecución del programa.

2.5. Formatos del corpus

El sistema carga los documentos del curso desde una carpeta llamada corpus, utilizando la función cargar\_corpus(). Los documentos se utilizan para buscar información relevante mediante buscar\_relevantes().

Respecto a las imágenes, el sistema admite los formatos PNG, JPG, JPEG, GIF y WEBP. Para procesarlas, comprueba el tipo MIME, lee el archivo y convierte su contenido a Base64 antes de enviarlo al modelo.

Los formatos concretos admitidos para los documentos del corpus se confirman revisando cargar\_documentos.py.

# 3.Despliegue

Para ejecutar el proyecto es necesario disponer de Python y de las dependencias utilizadas, además de configurar las variables de entorno necesarias para conectarse al servicio de IA.

El procedimiento general es:  
1\. Instalar las dependencias del proyecto.  
2\. Configure el archivo .env con la URL del proxy, la clave API y los modelos que se quieran utilizar.  
3\. Colocar los documentos del curso en la carpeta corpus.  
4\. Ejecutar el archivo tutor.py.  
5\. Introducir preguntas en formato texto o incluido una imagen, o utilizar el comando /imagen para enviar un diagrama.  
El programa utiliza python-dotenv para cargar automáticamente la configuración del archivo .env y la biblioteca openai para comunicarse con LiteLLM Proxy mediante una API compatible con OpenAI.

# 5\. Dificultades encontradas

Durante el desarrollo del proyecto, algunas de las principales dificultades que pueden aparecer son:

\- Procesamiento de imágenes: ha sido necesario implementar un mecanismo para comprobar los formatos admitidos, leer las imágenes y convertirlas a Base64 para enviarlas al modelo.

\- Adaptación del comportamiento del modelo: ha sido necesario diseñar un System Prompt detallado para conseguir que las respuestas sigan una estructura clara y accesible.

\- Gestión de diferentes tipos de consultas: el sistema debe distinguir entre preguntas normales y preguntas que incluyen imágenes para seleccionar el modelo correspondiente.

\- Memoria de conversación: ha sido necesario implementar un historial que permita mantener el contexto de las interacciones anteriores y limitar su tamaño.

\- Accesibilidad: uno de los retos principales es conseguir que las explicaciones sean comprensibles para estudiantes con diferentes necesidades, evitando respuestas demasiado largas o complejas.

# 6\. Posibles mejoras

Aunque el sistema ya incorpora funcionalidades de explicación matemática e interpretación de imágenes, existen diferentes aspectos que podrían mejorarse en futuras versiones:

1\.  Interfaz web: desarrolle una interfaz gráfica con Flask, Gradio o Streamlit para facilitar el acceso al tutor.

2\. Búsqueda semántica: incorporar embeddings para mejorar la recuperación de información relevante del corpus.

3\. Interacción por voz: permitirá que los estudiantes formulen preguntas mediante voz y reciban las respuestas mediante síntesis de voz, especialmente útil para personas con discapacidad visual.

4\. Mayor accesibilidad: agregue opciones para modificar el tamaño de letra, el contraste y la presentación de las respuestas.

5\. Evaluación del aprendizaje: incorpore ejercicios y preguntas automáticas para comprobar si el estudiante ha entendido las explicaciones.

6\. Personalización: adaptar la dificultad y la extensión de las respuestas al nivel de cada estudiante.

7\. Ampliación de formatos: permite cargar más tipos de documentos, como presentaciones, páginas web y otros materiales educativos.

# 7\. Conclusiones

El proyecto consiste en desarrollar un tutor virtual especializado en matemáticas y ciencias, diseñado para facilitar el aprendizaje de estudiantes con diferentes necesidades de accesibilidad.

A partir del código inicial proporcionado, hemos incorporado explicaciones paso a paso, justificación de las operaciones, interpretación de imágenes y memoria de conversación.

Una de las principales características del proyecto es que no busca únicamente proporcionar respuestas correctas, sino ayudar al estudiante a comprender el razonamiento que hay detrás de cada problema.

Además, el modo de explicación de pasos específicos permite adaptar las respuestas a las dificultades individuales de cada estudiante.

En conclusión, consideramos que el proyecto demuestra cómo la inteligencia artificial puede utilizarse como herramienta de apoyo educativo, ofreciendo explicaciones más claras, personalizadas y accesibles.  
