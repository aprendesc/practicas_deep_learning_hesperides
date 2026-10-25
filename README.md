# Prácticas de Deep Learning · Universidad de las Hespérides

## Instalación breve

Necesitas Git y Python 3.12. Clona el repositorio y crea un entorno aislado:

```sh
git clone https://github.com/aprendesc/practicas_deep_learning_hesperides.git
cd practicas_deep_learning_hesperides
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m ipykernel install --prefix .venv --name practicas_deep_learning_hesperides --display-name "Python (Deep Learning)"
python -m jupyter lab
```

En Windows, activa el entorno con `.venv\Scripts\activate` en lugar de `source`.
En JupyterLab selecciona el kernel **Python (Deep Learning)** del entorno y abre un notebook de `practicas/`.
Si ya tienes otro entorno, puedes usar un nombre de carpeta diferente en el primer comando y activarlo.

## Prácticas

Las prácticas están agrupadas por capítulos en `practicas/capitulo_*/`. La numeración de práctica mantiene el recorrido recomendado de la lista siguiente, también cuando un ejercicio integra contenidos de varios capítulos.

Completa el código iniciado. Los objetivos y pequeñas indicaciones están en cada enunciado; las referencias teóricas son opcionales. Ejecuta en orden desde la carpeta del notebook. No se incluyen comprobaciones automáticas: verifica los resultados de tu código. Una celda posterior puede fallar mientras un hueco siga sin completar.

- [01 · Descenso de gradiente en una función escalar](practicas/capitulo_02/practica_01_descenso_de_gradiente_en_una_funcion_escalar.ipynb)
- [02 · Regresión lineal mediante descenso de gradiente](practicas/capitulo_02/practica_02_regresion_lineal_mediante_descenso_de_gradiente.ipynb)
- [03 · Implementación de SGD y momentum](practicas/capitulo_02/practica_03_implementacion_de_sgd_y_momentum.ipynb)
- [04 · Forward pass y backpropagation en una red neuronal](practicas/capitulo_01/practica_04_forward_pass_y_backpropagation_en_una_red_neuronal.ipynb)
- [05 · Implementación de un MLP con NumPy](practicas/capitulo_01/practica_05_implementacion_de_un_mlp_con_numpy.ipynb)
- [06 · Diferenciación automática con autograd](practicas/capitulo_02/practica_06_diferenciacion_automatica_con_autograd.ipynb)
- [07 · Entrenamiento y evaluación de un MLP con PyTorch](practicas/capitulo_03/practica_07_entrenamiento_y_evaluacion_de_un_mlp_con_pytorch.ipynb)
- [08 · Correlación bidimensional y clasificación con una CNN](practicas/capitulo_04/practica_08_correlacion_bidimensional_y_clasificacion_con_una_cnn.ipynb)
- [09 · Aprendizaje de representaciones con autoencoders](practicas/capitulo_04/practica_09_aprendizaje_de_representaciones_con_autoencoders.ipynb)
- [10 · Implementación de scaled dot-product attention](practicas/capitulo_05/practica_10_implementacion_de_scaled_dot_product_attention.ipynb)

Los datos de práctica están incluidos en el repositorio.

Los entrenamientos usan CPU, datos sintéticos y presupuestos de ejecución acotados y explícitos en las celdas. No descargan modelos ni datasets. Las figuras representan cálculos del ejemplo y no resultados de arquitecturas de gran escala. PyTorch ocupa más espacio que el repositorio y se instala en el entorno, no se versiona.

## Exámenes

`examenes/` contiene únicamente `.gitkeep` para conservar la carpeta en Git. No hay exámenes publicados. Aquí aparecerán los exámenes práctico y teórico cuando se pongan a disposición.
