# Prácticas de Deep Learning · Universidad de las Hespérides

Material práctico de Deep Learning e Inteligencia Artificial del Máster en Finanzas Cuantitativas y Métodos Computacionales. La selección sigue el índice de la asignatura y los apuntes de las sesiones 1–5.

Por ahora, el workshop del alumnado publica únicamente el capítulo 1. Los capítulos posteriores se desbloquearán conforme avance la asignatura.

| Capítulo | Contenido | Exploración visual |
|---|---|---|
| [1](workshop/clases_sincronas/capitulo_1.ipynb) | Intuición, tensores y MLP | Cómo cambian las representaciones entre capas; animación del aprendizaje |

## Ejecutar

Desde esta carpeta, con [uv](https://docs.astral.sh/uv/) instalado:

```bash
uv sync --locked
uv run python -m ipykernel install --user --name hesperides-lab --display-name "Python 3 (Hespérides)"
uv run jupyter lab
```

Selecciona **Python 3 (Hespérides)** y ejecuta las celdas en orden con «Restart Kernel and Run All». Python 3.12 y las versiones de dependencias están fijados en `uv.lock`. Cada cuaderno puede abrirse de forma independiente desde su carpeta. Los notebooks son autocontenidos; la primera ejecución de algunos de ellos necesita Internet para descargar datos, que después se reutilizan desde la caché del usuario.

El modo predeterminado usa CPU. Para que los mecanismos puedan recorrerse en un portátil, el soporte `Trainer` limita a tres épocas y 1024/256 ejemplos de entrenamiento/validación; las demostraciones CNN con el bucle antiguo usan hasta 128/64 ejemplos, lotes de 16 y tres épocas. Los ejemplos sintéticos y los exploradores tienen su configuración explícita en las celdas. Estos límites no permiten comparar de forma concluyente la calidad de arquitecturas.

Para usar el régimen de entrenamiento completo de las fuentes, cierra los kernels e inicia:

```bash
HESPERIDES_COMPLETO=1 uv run jupyter lab
```

Esto elimina los límites del soporte; puede requerir bastante más tiempo y memoria. La ejecución comprobada es la del modo rápido en CPU.

Los controles interactivos necesitan un kernel activo en JupyterLab. Las animaciones de capas y convolución incluyen reproducción, pausa y selección de fotogramas. Cada explorador contiene también una figura de referencia para las exportaciones estáticas. Las ilustraciones de ImageGen son conceptuales; las curvas, mapas y animaciones se calculan con Python.

## Guía docente

`professor/`, excluida de Git, contiene el catálogo docente completo: los cinco capítulos, respuestas, justificaciones y orientación para dirigir las actividades. Su capítulo 1 es el espejo enriquecido del material actualmente publicado. Además, `professor/resources/` conserva las notas, fuentes, medios, datos y herramientas privadas de construcción.

La documentación de procedencia, la evidencia de validación y las herramientas de reconstrucción se conservan exclusivamente en el área docente.
