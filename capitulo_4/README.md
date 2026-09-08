# Capítulo 4 · CNN, conexiones residuales y autoencoders

Localidad, compartición de pesos, reducción espacial, conexiones residuales y reconstrucción mediante un cuello de botella.

Requisito: los conceptos de los capítulos 1–3; cada notebook inicia un kernel independiente.

El orden numérico propone una progresión. El itinerario principal es una selección docente para varias sesiones de trabajo autónomo; no pretende caber completo en una clase de cuarenta minutos. Los apoyos permiten ajustar la profundidad sin eliminar el material original.

| Notebook | Itinerario | Procedencia |
|---|---|---|
| [Convolución](01_conv_layer.ipynb) | Principal | `chapter_convolutional-neural-networks/conv-layer.ipynb` |
| [Padding y stride](02_padding_and_strides.ipynb) | Principal | `chapter_convolutional-neural-networks/padding-and-strides.ipynb` |
| [Canales](03_channels.ipynb) | Apoyo / profundización | `chapter_convolutional-neural-networks/channels.ipynb` |
| [Pooling](04_pooling.ipynb) | Principal | `chapter_convolutional-neural-networks/pooling.ipynb` |
| [CNN completa](05_lenet.ipynb) | Principal | `chapter_convolutional-neural-networks/lenet.ipynb` |
| [Conexiones residuales](06_resnet.ipynb) | Apoyo / profundización | `chapter_convolutional-modern/resnet.ipynb` |
| [Transferencia](07_fine_tuning.ipynb) | Apoyo / profundización | `chapter_computer-vision/fine-tuning.ipynb` |
| [Una convolución por dentro](90_explorador_visual.ipynb) | Principal | `Ampliación Hespérides` |
| [Un autoencoder por dentro](91_autoencoder_visual.ipynb) | Principal | `Ampliación Hespérides` |

Abre el explorador `90` después de la primera explicación y vuelve a él al terminar: formula una predicción, mueve un único control y contrástala con la figura. Sus valores son calculados por el código.

[Entorno y modo de ejecución](../README.md) · [Procedencia y adaptaciones](../PROCEDENCIA.md)

La fuente local no contiene un autoencoder válido. El notebook `91` es una ampliación explícita a partir del patrón MLP original: reconstruye imágenes sintéticas, muestra un latente de dos dimensiones y permite recorrerlo. VAE se explica como contraste conceptual; no se presenta este autoencoder como un VAE entrenado.
