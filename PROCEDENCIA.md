# Procedencia y decisiones editoriales

## Base académica y selección

El índice canónico de Hespérides, `docs/asignatura_deep_learning/raw_sources/indice-curso-deep-learning-llm-hesperides-2026.md`, y las notas `latex_notes/session_01.tex` a `session_05.tex` orientan los cinco capítulos. El reparto no incorpora las sesiones 6–10. Se examinaron los 192 notebooks de `locked/`: 183 tienen JSON válido y nueve están vacíos. No se consultó Legacy.

Los 34 originales seleccionados se identifican en [el manifiesto](scripts/editorial/seleccion.json), con destino, título, capítulo y SHA-256. Se priorizan los conceptos del temario y una progresión desde tensores hasta Transformer; las arquitecturas adicionales, aprendizaje por refuerzo y aplicaciones alejadas del bloque 1–5 no forman parte de esta selección. Cada README de capítulo permite revisar la pertinencia de cada cuaderno.

La fuente académica de las traducciones es *Dive into Deep Learning*, de Aston Zhang, Zachary C. Lipton, Mu Li y Alexander J. Smola, [d2l.ai](https://d2l.ai/). Cada derivado enlaza su lección y conserva el orden, fórmulas, ejemplos y ejercicios. Los identificadores `metadata.origen_celda` permiten volver a la celda original; una celda teórica extensa puede dividirse para intercalar una nota sin omitir contenido.

El [texto de D2L](https://github.com/d2l-ai/d2l-en/blob/master/LICENSE) tiene licencia **CC BY-SA 4.0**, aplicable a estas adaptaciones textuales; se conserva [copia de la licencia](recursos/licencias/D2L-CC-BY-SA-4.0.txt). No se implica respaldo de los autores a esta adaptación. El paquete de código local declara `MIT-0` en `locked/setup.py`; `laboratorio/d2l_original.py` es una copia idéntica de su `d2l/torch.py`. Los avisos del texto no se sustituyen por la licencia del paquete.

## Traducción y ampliaciones

Se utilizó una primera traducción local con Helsinki-NLP/opus-mt-en-es, protegiendo fórmulas, enlaces y código. Después se corrigieron terminología, fragmentos sin traducir, introducciones, comentarios y errores conceptuales detectados. Las traducciones, el glosario y las correcciones explícitas viven en `scripts/editorial/`; los identificadores de las API y los corpus lingüísticos conservan su idioma. Las notas añadidas se rotulan «Nota docente de Hespérides».

Los cinco exploradores `90` y el autoencoder `91` son ampliaciones programadas. No se atribuyen como originales de D2L. El autoencoder reutiliza el patrón MLP y añade una tarea sintética de reconstrucción; el corpus no proporcionaba un notebook de AE/VAE válido. El contraste con VAE es teórico, sin afirmar que se haya implementado su objetivo variacional.

Las cinco ilustraciones conceptuales se generaron con ImageGen y se revisaron visualmente. Sus [prompts](recursos/ilustraciones/prompts.json) registran la intención de cada imagen. Las figuras originales utilizadas se copiaron a `recursos/originales/`. Los gráficos cuantitativos y animaciones son salidas del código, no imágenes generadas que simulan mediciones.

## Adaptaciones ejecutables

El [constructor](scripts/build_laboratorios.py) y [registro por celda](scripts/editorial/adaptaciones.json) hacen visibles los cambios. Se utiliza el soporte local de D2L para conservar sus API sin exigir la instalación de versiones antiguas incompatibles. `laboratorio/entorno.py` añade semilla, CPU, descargas HTTPS verificadas, rutas locales, visualización de imágenes y límites de demostración. Se actualiza la selección de pesos de torchvision y se evita una división por cero en el trazado de lotes pequeños.

Fashion-MNIST reserva un 10 % del entrenamiento oficial para validación, separando el test. Los ejemplos antiguos de CIFAR-10 y hotdog conservan sus conjuntos de evaluación originales: si se comparan hiperparámetros, debe reservarse además validación dentro del entrenamiento. El solucionario explica esta distinción. Los límites rápidos se anuncian al ejecutar y no representan el régimen experimental completo del libro.

Dos erratas originales se señalan expresamente: log-sum-exp cambia por una constante al desplazar sus entradas (softmax sí es invariante); en LeNet la modernización de activaciones se refiere a las sigmoid ocultas, sin sustituir los logits de clasificación por ReLU. Las respuestas a experimentos distinguen lo deducible de lo que requiere medir: no inventan resultados ni proclaman un optimizador o arquitectura ganador.

## Datos, pesos y uso

Los datos descargados y los pesos permanecen en cachés locales excluidas del material versionado. Su disponibilidad en D2L no les asigna automáticamente la licencia del libro.

| Recurso | Procedencia y condiciones de referencia |
|---|---|
| Fashion-MNIST | [Zalando Research](https://github.com/zalandoresearch/fashion-mnist), repositorio con licencia MIT; mirror de los autores |
| CIFAR-10 | [Alex Krizhevsky, Universidad de Toronto](https://www.cs.toronto.edu/~kriz/cifar.html); conservar cita y consultar condiciones de la fuente para redistribución |
| Airfoil Self-Noise | Datos NASA/UCI distribuidos por D2L; [ficha UCI](https://archive.ics.uci.edu/dataset/291/airfoil+self+noise) |
| The Time Machine | H. G. Wells, corpus de texto distribuido por D2L; [Project Gutenberg](https://www.gutenberg.org/ebooks/35), condiciones según jurisdicción y edición |
| Inglés–francés | Pares de traducción de [ManyThings / Tatoeba](https://www.manythings.org/anki/), conservar atribución y condiciones del corpus |
| Hotdog | Paquete didáctico [D2L](https://d2l.ai/chapter_computer-vision/fine-tuning.html); se usa mediante descarga local, no se relicencia como producción propia |
| ResNet18 | Pesos `IMAGENET1K_V1` de [torchvision](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet18.html); uso conforme a sus términos y los del conjunto de entrenamiento |
| Datos sintéticos | Generados dentro de los exploradores con semilla explícita |

La conservación privada de `results/` responde a la separación de respuestas del material del alumno. No se han publicado contenidos ni cambiado permisos externos.
