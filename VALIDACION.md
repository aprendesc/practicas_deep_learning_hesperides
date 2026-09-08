# Validación de las prácticas

Comprobación local completada el 2026-09-08 con Python 3.12.13, macOS y CPU. El entorno se sincronizó con `uv sync --locked`.

**44 de 44 notebooks ejecutados correctamente**, con 357 celdas de código en total. Cada ejecución parte de un kernel independiente. La evidencia por notebook, SHA-256 combinado con el soporte, duración y número de celdas está en [el registro](scripts/editorial/validacion_ejecucion.json).

Se validaron JSON de Jupyter, rutas a imágenes, cobertura de preguntas y correspondencia de todas las celdas de las 34 fuentes. La comparación con el inventario inicial confirma 559 archivos preservados: el corpus `locked/`, los cuatro notebooks previos y sus imágenes. La copia de soporte D2L coincide byte a byte con su original.

El solucionario reproduce 164 ejercicios principales y 76 subapartados de D2L. Se conservan las 17 preguntas de los cuatro cuadernos previos, se añaden las cuatro del autoencoder y las cinco consignas de exploración. Cada entrada contiene respuesta y justificación. En cuestiones experimentales se aporta el razonamiento y el protocolo necesario; no se inventan comparaciones empíricas.

Los seis exploradores pasaron llamadas directas a sus controles extremos. Se verifican internamente la igualdad entre correlación calculada y `conv2d`, la suma unitaria de los pesos de atención y el enmascaramiento del futuro. Se revisaron las siete figuras de referencia y las cinco ilustraciones de ImageGen. En navegador se comprobó que la ilustración se carga y que la animación permite llegar al último fotograma.

La descarga inicial lenta de CIFAR-10 se completó desde el servidor original y se verificó su MD5 (`c58f30108f718f92721af3b95e74349a`). Se corrigió el caso sin GPU del bucle original y se repitió su ejecución satisfactoriamente. Las descargas HTTPS utilizan certificados del sistema con verificación TLS.

## Alcance de la comprobación

Se ha probado el **modo rápido en CPU**; no el entrenamiento completo ni GPU. Los conjuntos descargados se reutilizan desde caché. La ejecución correcta de una demostración no acredita convergencia ni superioridad de una técnica. Los widgets requieren un kernel activo; las figuras de referencia y animaciones permiten revisar resultados en HTML sin ese kernel. El autoencoder es determinista; VAE permanece como explicación conceptual.

Para repetir la comprobación:

```bash
uv sync --locked
uv run python -m ipykernel install --user --name hesperides-lab --display-name "Python 3 (Hespérides)"
uv run python scripts/validar_laboratorios.py
uv run python results/build_respuestas.py
```

El validador reutiliza una ejecución aprobada solo si el notebook y su soporte mantienen el mismo hash. Los notebooks ejecutados, HTML y registros detallados permanecen en `.editorial/ejecuciones/`; los cinco solucionarios están en `results/`. Ambas superficies están excluidas de Git. El registro resumido anterior sí acompaña al material.

| Notebook | Celdas de código | Segundos de la ejecución registrada |
|---|---:|---:|
| [capitulo_1/01_datos_y_tensores.ipynb](capitulo_1/01_datos_y_tensores.ipynb) | 4 | 5.87 |
| [capitulo_1/02_neurona_artificial.ipynb](capitulo_1/02_neurona_artificial.ipynb) | 4 | 5.96 |
| [capitulo_1/03_perceptron.ipynb](capitulo_1/03_perceptron.ipynb) | 4 | 1.59 |
| [capitulo_1/04_neuronas_y_capas.ipynb](capitulo_1/04_neuronas_y_capas.ipynb) | 3 | 1.39 |
| [capitulo_1/05_ndarray.ipynb](capitulo_1/05_ndarray.ipynb) | 25 | 177.94 |
| [capitulo_1/06_image_classification_dataset.ipynb](capitulo_1/06_image_classification_dataset.ipynb) | 11 | 178.91 |
| [capitulo_1/07_mlp.ipynb](capitulo_1/07_mlp.ipynb) | 8 | 56.28 |
| [capitulo_1/08_mlp_implementation.ipynb](capitulo_1/08_mlp_implementation.ipynb) | 8 | 6.09 |
| [capitulo_1/90_explorador_visual.ipynb](capitulo_1/90_explorador_visual.ipynb) | 4 | 66.99 |
| [capitulo_2/01_autograd.ipynb](capitulo_2/01_autograd.ipynb) | 14 | 2.36 |
| [capitulo_2/02_backprop.ipynb](capitulo_2/02_backprop.ipynb) | 1 | 56.02 |
| [capitulo_2/03_softmax_regression.ipynb](capitulo_2/03_softmax_regression.ipynb) | 1 | 11.23 |
| [capitulo_2/04_gd.ipynb](capitulo_2/04_gd.ipynb) | 14 | 2.67 |
| [capitulo_2/05_minibatch_sgd.ipynb](capitulo_2/05_minibatch_sgd.ipynb) | 17 | 6.73 |
| [capitulo_2/06_momentum.ipynb](capitulo_2/06_momentum.ipynb) | 13 | 4.12 |
| [capitulo_2/07_adam.ipynb](capitulo_2/07_adam.ipynb) | 5 | 3.84 |
| [capitulo_2/90_explorador_visual.ipynb](capitulo_2/90_explorador_visual.ipynb) | 3 | 66.03 |
| [capitulo_3/01_generalization.ipynb](capitulo_3/01_generalization.ipynb) | 1 | 10.98 |
| [capitulo_3/02_weight_decay.ipynb](capitulo_3/02_weight_decay.ipynb) | 10 | 3.28 |
| [capitulo_3/03_dropout.ipynb](capitulo_3/03_dropout.ipynb) | 8 | 3.16 |
| [capitulo_3/04_numerical_stability_and_init.ipynb](capitulo_3/04_numerical_stability_and_init.ipynb) | 4 | 2.3 |
| [capitulo_3/05_batch_norm.ipynb](capitulo_3/05_batch_norm.ipynb) | 9 | 3.9 |
| [capitulo_3/06_image_augmentation.ipynb](capitulo_3/06_image_augmentation.ipynb) | 18 | 27.0 |
| [capitulo_3/90_explorador_visual.ipynb](capitulo_3/90_explorador_visual.ipynb) | 3 | 2.14 |
| [capitulo_4/01_conv_layer.ipynb](capitulo_4/01_conv_layer.ipynb) | 11 | 2.27 |
| [capitulo_4/02_padding_and_strides.ipynb](capitulo_4/02_padding_and_strides.ipynb) | 6 | 2.45 |
| [capitulo_4/03_channels.ipynb](capitulo_4/03_channels.ipynb) | 9 | 2.32 |
| [capitulo_4/04_pooling.ipynb](capitulo_4/04_pooling.ipynb) | 11 | 2.36 |
| [capitulo_4/05_lenet.ipynb](capitulo_4/05_lenet.ipynb) | 6 | 3.09 |
| [capitulo_4/06_resnet.ipynb](capitulo_4/06_resnet.ipynb) | 13 | 39.35 |
| [capitulo_4/07_fine_tuning.ipynb](capitulo_4/07_fine_tuning.ipynb) | 14 | 50.52 |
| [capitulo_4/90_explorador_visual.ipynb](capitulo_4/90_explorador_visual.ipynb) | 4 | 2.23 |
| [capitulo_4/91_autoencoder_visual.ipynb](capitulo_4/91_autoencoder_visual.ipynb) | 3 | 2.36 |
| [capitulo_5/01_sequence.ipynb](capitulo_5/01_sequence.ipynb) | 11 | 18.27 |
| [capitulo_5/02_rnn_concise.ipynb](capitulo_5/02_rnn_concise.ipynb) | 7 | 3.44 |
| [capitulo_5/03_bptt.ipynb](capitulo_5/03_bptt.ipynb) | 1 | 4.65 |
| [capitulo_5/04_lstm.ipynb](capitulo_5/04_lstm.ipynb) | 8 | 3.37 |
| [capitulo_5/05_gru.ipynb](capitulo_5/05_gru.ipynb) | 8 | 3.54 |
| [capitulo_5/06_queries_keys_values.ipynb](capitulo_5/06_queries_keys_values.ipynb) | 4 | 4.36 |
| [capitulo_5/07_attention_scoring_functions.ipynb](capitulo_5/07_attention_scoring_functions.ipynb) | 12 | 2.4 |
| [capitulo_5/08_multihead_attention.ipynb](capitulo_5/08_multihead_attention.ipynb) | 5 | 2.56 |
| [capitulo_5/09_self_attention_and_positional_encoding.ipynb](capitulo_5/09_self_attention_and_positional_encoding.ipynb) | 7 | 2.44 |
| [capitulo_5/10_transformer.ipynb](capitulo_5/10_transformer.ipynb) | 22 | 4.21 |
| [capitulo_5/90_explorador_visual.ipynb](capitulo_5/90_explorador_visual.ipynb) | 3 | 1.79 |

Los tiempos incluyen arranque del kernel y, cuando correspondía, descarga. Son evidencia local, no estimaciones de duración docente.
