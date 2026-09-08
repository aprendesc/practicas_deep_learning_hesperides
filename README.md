# Prácticas de Deep Learning · Universidad de las Hespérides

Laboratorio de los cinco primeros capítulos de Deep Learning e Inteligencia Artificial del Máster en Finanzas Cuantitativas y Métodos Computacionales. La selección sigue el índice de la asignatura y los apuntes de las sesiones 1–5.

Hay **44 notebooks**: cuatro prácticas previas conservadas, 34 adaptaciones al español de *Dive into Deep Learning* y seis ampliaciones visuales. Cada capítulo distingue un recorrido principal de los materiales de apoyo.

| Capítulo | Contenido | Exploración visual |
|---|---|---|
| [1](capitulo_1/README.md) | Intuición, tensores y MLP | Cómo cambian las representaciones entre capas; animación del aprendizaje |
| [2](capitulo_2/README.md) | Retropropagación, pérdidas y optimización | Trayectorias de SGD, momentum y Adam |
| [3](capitulo_3/README.md) | Regularización, estabilidad y diagnóstico | Complejidad, regularización y error de validación |
| [4](capitulo_4/README.md) | CNN, ResNet y autoencoders | Ventana convolucional animada y recorrido del espacio latente |
| [5](capitulo_5/README.md) | Secuencias, atención y Transformer | Consultas, claves, pesos, valores y máscara causal |

## Ejecutar

Desde esta carpeta, con [uv](https://docs.astral.sh/uv/) instalado:

```bash
uv sync --locked
uv run python -m ipykernel install --user --name hesperides-lab --display-name "Python 3 (Hespérides)"
uv run jupyter lab
```

Selecciona **Python 3 (Hespérides)** y ejecuta las celdas en orden con «Restart Kernel and Run All». Python 3.12 y las versiones de dependencias están fijados en `uv.lock`. Cada cuaderno puede abrirse de forma independiente desde su carpeta. La primera ejecución necesita Internet para los datos; las siguientes reutilizan `data/` y la caché de PyTorch.

El modo predeterminado usa CPU. Para que los mecanismos puedan recorrerse en un portátil, el soporte `Trainer` limita a tres épocas y 1024/256 ejemplos de entrenamiento/validación; las demostraciones CNN con el bucle antiguo usan hasta 128/64 ejemplos, lotes de 16 y tres épocas. Los ejemplos sintéticos y los exploradores tienen su configuración explícita en las celdas. Estos límites no permiten comparar de forma concluyente la calidad de arquitecturas.

Para usar el régimen de entrenamiento completo de las fuentes, cierra los kernels e inicia:

```bash
HESPERIDES_COMPLETO=1 uv run jupyter lab
```

Esto elimina los límites del soporte; puede requerir bastante más tiempo y memoria. La ejecución comprobada es la del modo rápido en CPU.

Los controles interactivos necesitan un kernel activo en JupyterLab. Las animaciones de capas y convolución incluyen reproducción, pausa y selección de fotogramas. Cada explorador contiene también una figura de referencia para las exportaciones estáticas. Las ilustraciones de ImageGen son conceptuales; las curvas, mapas y animaciones se calculan con Python.

## Guía docente

Los cinco documentos `results/respuestas_capitulo_1.md` a `results/respuestas_capitulo_5.md` contienen los enunciados, respuestas y justificaciones. Incluyen los 164 ejercicios principales y 76 subapartados de los 34 originales seleccionados, las respuestas previas del capítulo 1 y las ampliaciones visuales. `results/` conserva su exclusión de Git para mantener separado el solucionario docente. El comando `uv run python results/build_respuestas.py` reconstruye los cinco documentos desde las respuestas editables y coteja el número de ejercicios y subapartados con las fuentes.

[Procedencia, licencias y cambios](PROCEDENCIA.md) · [Evidencia de validación](VALIDACION.md)

La reconstrucción de los derivados se realiza con `uv run python scripts/build_laboratorios.py` y requiere el corpus local `locked/`. Para estudiar o ejecutar los notebooks ya construidos no hace falta distribuir ese corpus. `scripts/editorial/seleccion.json` identifica cada original y su SHA-256. Las fuentes y los cuatro notebooks previos permanecen intactos.
