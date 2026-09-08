# Capítulo 2 · Retropropagación, pérdidas y optimización

Del grafo computacional a la actualización de parámetros. El explorador compara SGD, momentum y Adam sobre exactamente la misma función.

Requisito: los conceptos de los capítulos 1–1; cada notebook inicia un kernel independiente.

El orden numérico propone una progresión. El itinerario principal es una selección docente para varias sesiones de trabajo autónomo; no pretende caber completo en una clase de cuarenta minutos. Los apoyos permiten ajustar la profundidad sin eliminar el material original.

| Notebook | Itinerario | Procedencia |
|---|---|---|
| [Diferenciación automática](01_autograd.ipynb) | Principal | `chapter_preliminaries/autograd.ipynb` |
| [Grafo y regla de la cadena](02_backprop.ipynb) | Principal | `chapter_multilayer-perceptrons/backprop.ipynb` |
| [Softmax, entropía cruzada y pérdida probabilística](03_softmax_regression.ipynb) | Principal | `chapter_linear-classification/softmax-regression.ipynb` |
| [Descenso por gradiente](04_gd.ipynb) | Principal | `chapter_optimization/gd.ipynb` |
| [SGD por minibatches](05_minibatch_sgd.ipynb) | Apoyo / profundización | `chapter_optimization/minibatch-sgd.ipynb` |
| [Momentum](06_momentum.ipynb) | Apoyo / profundización | `chapter_optimization/momentum.ipynb` |
| [Adam y comparación controlada con SGD](07_adam.ipynb) | Apoyo / profundización | `chapter_optimization/adam.ipynb` |
| [El viaje del optimizador](90_explorador_visual.ipynb) | Principal | `Ampliación Hespérides` |

Abre el explorador `90` después de la primera explicación y vuelve a él al terminar: formula una predicción, mueve un único control y contrástala con la figura. Sus valores son calculados por el código.

[Entorno y modo de ejecución](../README.md) · [Procedencia y adaptaciones](../PROCEDENCIA.md)
