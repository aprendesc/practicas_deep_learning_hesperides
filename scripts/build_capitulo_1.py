"""Genera los notebooks del capítulo 1."""
import json
from pathlib import Path
from textwrap import dedent

OUT = Path(__file__).resolve().parents[1] / "capitulo_1"

def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": dedent(source).strip().splitlines(True)}

def code(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": dedent(source).strip().splitlines(True)}

def save(name, cells):
    OUT.mkdir(exist_ok=True)
    (OUT / "imagenes").mkdir(exist_ok=True)
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }
    (OUT / name).write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

setup = code("""
import random
import torch
import matplotlib.pyplot as plt

SEMILLA = 42
random.seed(SEMILLA)
torch.manual_seed(SEMILLA)
torch.set_printoptions(precision=3, sci_mode=False)
print(f"PyTorch {torch.__version__} · semilla {SEMILLA}")
""")

save("01_tensores_y_datos.ipynb", [
    md("""
    # 1. Tensores y datos

    **Objetivo.** Representar datos numéricos con tensores y dominar las operaciones necesarias para construir modelos.

    **Al terminar podrás:** crear tensores; razonar sobre forma, eje y tipo; seleccionar y transformar datos; reconocer *broadcasting*; y preparar un conjunto tabular sencillo.

    Un tensor es una colección rectangular de números. Un escalar tiene orden 0, un vector orden 1, una matriz orden 2 y, a partir de ahí, hablamos de tensores de orden superior. La propiedad `shape` describe cuántos elementos hay en cada eje.
    """),
    setup,
    code("""
    escalar = torch.tensor(3.0)
    vector = torch.tensor([1.0, 2.0, 3.0])
    matriz = torch.arange(12, dtype=torch.float32).reshape(3, 4)
    imagenes = torch.zeros(8, 3, 32, 32)

    for nombre, x in {"escalar": escalar, "vector": vector, "matriz": matriz, "lote": imagenes}.items():
        print(f"{nombre:7s}: shape={tuple(x.shape)}, ndim={x.ndim}, dtype={x.dtype}")
    matriz
    """),
    md("""
    ## Indexación, reducción y cambio de forma

    Los índices eligen observaciones o características. Las reducciones (`sum`, `mean`, `max`) eliminan un eje, salvo que pidamos conservarlo con `keepdim=True`. Cambiar la forma no cambia los datos: solo su organización lógica.
    """),
    code("""
    print("primera fila:", matriz[0])
    print("última columna:", matriz[:, -1])
    print("media global:", matriz.mean())
    print("media por columna:", matriz.mean(dim=0))
    print("transpuesta:\\n", matriz.T)
    """),
    md("""
    ## *Broadcasting*

    PyTorch puede combinar tensores de formas distintas cuando sus dimensiones, comparadas desde la derecha, son iguales o una de ellas vale 1. Aquí sumamos un sesgo distinto a cada columna sin copiarlo por todas las filas.
    """),
    code("""
    sesgo = torch.tensor([10.0, 20.0, 30.0, 40.0])
    resultado = matriz + sesgo
    print("formas:", matriz.shape, "+", sesgo.shape, "->", resultado.shape)
    resultado
    """),
    md("""
    ## De una tabla a características y objetivo

    Cada fila representa una observación; cada columna, una característica. Separamos una matriz $X$ de entradas y un vector $y$ de objetivos. Estandarizar evita que una escala numérica domine a las demás.
    """),
    code("""
    datos = torch.tensor([
        [45.0, 1.0, 210.0],
        [62.0, 2.0, 290.0],
        [80.0, 3.0, 360.0],
        [95.0, 3.0, 410.0],
    ])
    X, y = datos[:, :2], datos[:, 2]
    media, escala = X.mean(dim=0), X.std(dim=0)
    X_estandarizado = (X - media) / escala
    print("X:\\n", X)
    print("y:", y)
    print("medias tras estandarizar:", X_estandarizado.mean(dim=0))
    """),
    md("""
    ## Práctica

    1. Crea un tensor de forma `(2, 3, 4)` con los enteros del 0 al 23.
    2. Calcula su media sobre el último eje y anticipa la forma del resultado.
    3. Comprueba que la desviación típica de cada columna estandarizada es 1.
    4. Explica por qué no deberíamos estandarizar el objetivo usando información del conjunto de prueba.

    **Idea clave:** antes de depurar una red neuronal, comprueba siempre formas, tipos y escalas.
    """),
])

save("02_matematicas_y_autograd.ipynb", [
    md("""
    # 2. Matemáticas y diferenciación automática

    **Objetivo.** Conectar vectores, matrices, derivadas y gradientes con el mecanismo que permite aprender a una red neuronal.

    Una capa lineal calcula $y=Xw+b$. Aprender consiste en ajustar $w$ y $b$ para reducir una pérdida. El gradiente indica la variación local de esa pérdida respecto de cada parámetro.
    """),
    setup,
    md("""
    ## Álgebra lineal de una predicción

    Para un lote de $n$ observaciones con $d$ características, $X$ tiene forma $(n,d)$ y $w$ forma $(d,1)$. El producto matricial produce $n$ predicciones.
    """),
    code("""
    X = torch.tensor([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    w = torch.tensor([[0.5], [-1.0]])
    b = torch.tensor(2.0)
    y = X @ w + b
    print("X", X.shape, "w", w.shape, "y", y.shape, sep=" · ")
    y
    """),
    md("""
    ## Derivada y gradiente

    En una dimensión, la derivada es la pendiente local. Para $f(x)=x^2$, $f'(x)=2x$. En varias dimensiones, el gradiente reúne las derivadas parciales. Las diferencias finitas proporcionan una comprobación numérica.
    """),
    code("""
    def f(x):
        return x**2

    x0, h = 3.0, 1e-4
    aproximacion = (f(x0 + h) - f(x0 - h)) / (2 * h)
    print("diferencias finitas:", aproximacion)
    print("derivada exacta:", 2 * x0)
    """),
    md("""
    ## Diferenciación automática

    Con `requires_grad=True`, PyTorch registra las operaciones en un grafo dinámico. `backward()` aplica la regla de la cadena desde el resultado hasta los parámetros.
    """),
    code("""
    x = torch.tensor([2.0, -1.0], requires_grad=True)
    perdida = 3 * x[0]**2 + 2 * x[0] * x[1] + x[1]**2
    perdida.backward()
    analitico = torch.tensor([6*x[0] + 2*x[1], 2*x[0] + 2*x[1]])
    print("pérdida:", perdida.item())
    print("gradiente automático:", x.grad)
    print("gradiente analítico:", analitico)
    """),
    md("""
    ## Descenso por el gradiente

    Para minimizar $f(x)=(x-4)^2$, repetimos $x\\leftarrow x-\\eta f'(x)$. La tasa $\\eta$ controla la longitud del paso.
    """),
    code("""
    x = torch.tensor(-3.0, requires_grad=True)
    historia = []
    for paso in range(20):
        perdida = (x - 4) ** 2
        perdida.backward()
        with torch.no_grad():
            x -= 0.1 * x.grad
        x.grad.zero_()
        historia.append(perdida.item())

    print("x final:", round(x.item(), 4))
    plt.plot(historia, marker="o")
    plt.xlabel("paso"); plt.ylabel("pérdida"); plt.yscale("log"); plt.grid(alpha=.3);
    plt.savefig("imagenes/descenso_gradiente.png", dpi=160, bbox_inches="tight")
    plt.show()
    """),
    md("""
    ## Preguntas

    1. ¿Qué ocurre con tasas de aprendizaje 0, 0.1, 1 y 1.1?
    2. ¿Por qué actualizamos `x` dentro de `torch.no_grad()`?
    3. ¿Por qué debemos poner el gradiente a cero después de cada paso?

    **Idea clave:** la retropropagación calcula gradientes; el optimizador decide cómo usarlos.
    """),
])

save("03_regresion_lineal.ipynb", [
    md("""
    # 3. Regresión lineal desde cero

    **Objetivo.** Construir el primer modelo entrenable sin ocultar el proceso: datos, predicción, pérdida, gradientes y actualización.

    Generamos observaciones mediante $y=2x_1-3.4x_2+4.2+\\epsilon$ y comprobamos si el entrenamiento recupera los parámetros.
    """),
    setup,
    code("""
    n = 1000
    X = torch.randn(n, 2)
    w_real = torch.tensor([[2.0], [-3.4]])
    b_real = 4.2
    y = X @ w_real + b_real + 0.01 * torch.randn(n, 1)

    plt.scatter(X[:150, 1], y[:150], s=12, alpha=.6)
    plt.xlabel("segunda característica"); plt.ylabel("objetivo"); plt.grid(alpha=.2);
    plt.savefig("imagenes/datos_regresion.png", dpi=160, bbox_inches="tight")
    plt.show()
    """),
    md("""
    ## Modelo y pérdida

    La pérdida cuadrática media es $L=\\frac{1}{n}\\sum_i(\\hat y_i-y_i)^2$. Penaliza especialmente los errores grandes y es diferenciable.
    """),
    code("""
    w = torch.randn(2, 1, requires_grad=True)
    b = torch.zeros(1, requires_grad=True)

    def predecir(entradas):
        return entradas @ w + b

    def mse(prediccion, objetivo):
        return ((prediccion - objetivo) ** 2).mean()

    print("pérdida inicial:", mse(predecir(X), y).item())
    """),
    md("""
    ## Entrenamiento por mini-lotes

    Una época recorre una vez todos los ejemplos. Cada mini-lote produce una estimación barata y ruidosa del gradiente.
    """),
    code("""
    tasa, lote, epocas = 0.05, 32, 12
    historia = []
    for epoca in range(epocas):
        indices = torch.randperm(n)
        for inicio in range(0, n, lote):
            idx = indices[inicio:inicio + lote]
            perdida = mse(predecir(X[idx]), y[idx])
            perdida.backward()
            with torch.no_grad():
                w -= tasa * w.grad
                b -= tasa * b.grad
            w.grad.zero_(); b.grad.zero_()
        historia.append(mse(predecir(X), y).item())

    print("w aprendido:", w.detach().flatten(), "· real:", w_real.flatten())
    print("b aprendido:", round(b.item(), 3), "· real:", b_real)
    plt.plot(range(1, epocas + 1), historia, marker="o")
    plt.xlabel("época"); plt.ylabel("MSE"); plt.yscale("log"); plt.grid(alpha=.3);
    plt.savefig("imagenes/perdida_regresion.png", dpi=160, bbox_inches="tight")
    plt.show()
    """),
    md("""
    ## Práctica y diagnóstico

    1. Compara tasas `0.001`, `0.05` y `0.5`.
    2. Separa el 20 % antes de entrenar y calcula allí el MSE.
    3. Aumenta el ruido y observa la diferencia entre parámetros reales y estimados.
    4. Explica por qué una pérdida baja en entrenamiento no garantiza generalización.

    **Idea clave:** entrenar es repetir: predecir, medir el error, diferenciar y actualizar.
    """),
])

save("04_clasificacion_y_perceptron.ipynb", [
    md("""
    # 4. Clasificación binaria y perceptrón

    **Objetivo.** Comprender cómo una combinación lineal define una frontera de decisión y entrenar el perceptrón clásico.

    Para $x\\in\\mathbb{R}^d$, calculamos $z=w^Tx+b$. El perceptrón asigna clase 1 si $z\\geq0$ y clase 0 en caso contrario. La ecuación $w^Tx+b=0$ define la frontera.
    """),
    setup,
    code("""
    n = 120
    clase_0 = torch.randn(n, 2) * 0.65 + torch.tensor([-1.5, -1.0])
    clase_1 = torch.randn(n, 2) * 0.65 + torch.tensor([1.2, 1.4])
    X = torch.cat([clase_0, clase_1])
    y = torch.cat([torch.zeros(n), torch.ones(n)])
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap="coolwarm", edgecolor="white", s=35)
    plt.xlabel("x₁"); plt.ylabel("x₂"); plt.grid(alpha=.2);
    plt.savefig("imagenes/datos_clasificacion.png", dpi=160, bbox_inches="tight")
    plt.show()
    """),
    md("""
    ## Regla de aprendizaje

    Ante una predicción incorrecta actualizamos

    $$w\\leftarrow w+\\eta(y-\\hat y)x,\\qquad b\\leftarrow b+\\eta(y-\\hat y).$$

    Si los datos son linealmente separables, el algoritmo converge a alguna frontera que los separa.
    """),
    code("""
    w = torch.zeros(2)
    b = torch.tensor(0.0)
    errores = []
    for epoca in range(15):
        fallos = 0
        for i in torch.randperm(len(X)):
            pred = (X[i] @ w + b >= 0).float()
            error = y[i] - pred
            if error != 0:
                w += 0.1 * error * X[i]
                b += 0.1 * error
                fallos += 1
        errores.append(fallos)

    predicciones = (X @ w + b >= 0).float()
    print("w:", w, "b:", b.item())
    print("exactitud:", (predicciones == y).float().mean().item())
    print("errores por época:", errores)
    """),
    code("""
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap="coolwarm", edgecolor="white", s=35)
    xs = torch.linspace(X[:, 0].min(), X[:, 0].max(), 100)
    ys = -(w[0] * xs + b) / w[1]
    plt.plot(xs, ys, "k--", label="frontera")
    plt.xlabel("x₁"); plt.ylabel("x₂"); plt.legend(); plt.grid(alpha=.2);
    plt.savefig("imagenes/frontera_perceptron.png", dpi=160, bbox_inches="tight")
    plt.show()
    """),
    md("""
    ## El límite del perceptrón: XOR

    XOR no puede separarse con una única recta. No es un fallo de entrenamiento, sino una limitación de la familia de modelos.
    """),
    code("""
    X_xor = torch.tensor([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
    y_xor = torch.tensor([0., 1., 1., 0.])
    plt.scatter(X_xor[:, 0], X_xor[:, 1], c=y_xor, cmap="coolwarm", s=120, edgecolor="black")
    plt.xticks([0, 1]); plt.yticks([0, 1]); plt.grid(alpha=.2);
    plt.savefig("imagenes/problema_xor.png", dpi=160, bbox_inches="tight")
    plt.show()
    """),
    md("""
    ## Preguntas

    1. ¿Qué representa la dirección de $w$?
    2. Añade ruido hasta que las clases se solapen. ¿Qué ocurre con los errores?
    3. Intenta dibujar una recta que resuelva XOR. ¿Qué pieza arquitectónica falta?

    **Idea clave:** una neurona lineal solo crea una frontera lineal; combinar neuronas permite fronteras no lineales.
    """),
])

save("05_redes_y_backpropagation.ipynb", [
    md("""
    # 5. Redes neuronales y retropropagación

    **Objetivo.** Construir una red como composición de capas y observar cómo la regla de la cadena distribuye el gradiente por todos sus parámetros.

    Una capa oculta calcula $H=\\phi(XW_1+b_1)$ y la salida $\\hat y=HW_2+b_2$. Sin una activación no lineal $\\phi$, dos capas lineales equivalen a una sola.
    """),
    setup,
    md("""
    ## Activaciones

    ReLU aplica $\\max(0,x)$. Introduce no linealidad y mantiene gradientes positivos en su región activa. Sigmoid comprime valores a $(0,1)$.
    """),
    code("""
    z = torch.linspace(-5, 5, 300)
    fig, ax = plt.subplots(1, 2, figsize=(9, 3))
    ax[0].plot(z, torch.relu(z)); ax[0].set_title("ReLU")
    ax[1].plot(z, torch.sigmoid(z)); ax[1].set_title("Sigmoid")
    for a in ax:
        a.grid(alpha=.3); a.axhline(0, color="black", lw=.5); a.axvline(0, color="black", lw=.5)
    fig.savefig("imagenes/funciones_activacion.png", dpi=160, bbox_inches="tight")
    plt.show()
    """),
    md("""
    ## Propagación hacia delante y hacia atrás

    Conservamos el gradiente de la representación oculta para inspeccionarlo. Normalmente PyTorch lo utiliza internamente.
    """),
    code("""
    X = torch.tensor([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
    y = torch.tensor([[0.], [1.], [1.], [0.]])
    W1 = torch.randn(2, 4, requires_grad=True)
    b1 = torch.zeros(4, requires_grad=True)
    W2 = torch.randn(4, 1, requires_grad=True)
    b2 = torch.zeros(1, requires_grad=True)

    H = torch.relu(X @ W1 + b1)
    H.retain_grad()
    logits = H @ W2 + b2
    perdida = torch.nn.functional.binary_cross_entropy_with_logits(logits, y)
    perdida.backward()

    print("formas: X", X.shape, "H", H.shape, "salida", logits.shape)
    print("pérdida:", perdida.item())
    for nombre, p in {"W1": W1, "b1": b1, "H": H, "W2": W2, "b2": b2}.items():
        print(f"{nombre}: norma del gradiente = {p.grad.norm().item():.4f}")
    """),
    md("""
    ## Verificación numérica

    Las diferencias finitas permiten comprobar un gradiente concreto. La aproximación no será idéntica, pero debe ser muy cercana.
    """),
    code("""
    def perdida_con_w(valor):
        W = W1.detach().clone()
        W[0, 0] = valor
        h = torch.relu(X @ W + b1.detach())
        salida = h @ W2.detach() + b2.detach()
        return torch.nn.functional.binary_cross_entropy_with_logits(salida, y)

    eps = 1e-3
    valor = W1.detach()[0, 0]
    numerico = (perdida_con_w(valor + eps) - perdida_con_w(valor - eps)) / (2 * eps)
    print("automático:", W1.grad[0, 0].item())
    print("numérico:", numerico.item())
    """),
    md("""
    ## Preguntas

    1. Elimina ReLU y demuestra que las capas se reducen a una transformación lineal.
    2. ¿Qué significa que la norma del gradiente de una capa sea casi cero?
    3. ¿Por qué usamos una pérdida que recibe *logits*?

    **Idea clave:** la red predice hacia delante; la retropropagación reutiliza el grafo para calcular las derivadas hacia atrás.
    """),
])

save("06_perceptron_multicapa.ipynb", [
    md("""
    # 6. Perceptrón multicapa

    **Objetivo.** Entrenar un MLP completo, primero con operaciones explícitas y después con las abstracciones de PyTorch.

    Resolveremos XOR. La capa oculta transforma el espacio de entrada; la capa de salida separa linealmente esa nueva representación.
    """),
    setup,
    code("""
    X_base = torch.tensor([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
    y_base = torch.tensor([[0.], [1.], [1.], [0.]])
    X = X_base.repeat(100, 1) + 0.04 * torch.randn(400, 2)
    y = y_base.repeat(100, 1)
    perm = torch.randperm(len(X))
    train, test = perm[:320], perm[320:]
    print(f"observaciones: {len(X)} · entrenamiento: {len(train)} · prueba: {len(test)}")
    """),
    md("""
    ## Implementación explícita

    Los parámetros son tensores entrenables. La entropía cruzada binaria con *logits* combina sigmoid y la pérdida de forma numéricamente estable.
    """),
    code("""
    W1 = (torch.randn(2, 8) * 0.5).requires_grad_()
    b1 = torch.zeros(8, requires_grad=True)
    W2 = (torch.randn(8, 1) * 0.5).requires_grad_()
    b2 = torch.zeros(1, requires_grad=True)
    parametros = [W1, b1, W2, b2]

    def mlp(entradas):
        return torch.relu(entradas @ W1 + b1) @ W2 + b2

    historia = []
    for epoca in range(2001):
        perdida = torch.nn.functional.binary_cross_entropy_with_logits(mlp(X[train]), y[train])
        perdida.backward()
        with torch.no_grad():
            for p in parametros:
                p -= 0.1 * p.grad
                p.grad.zero_()
        if epoca % 100 == 0:
            historia.append((epoca, perdida.item()))

    with torch.no_grad():
        pred = (mlp(X[test]) >= 0).float()
        exactitud = (pred == y[test]).float().mean().item()
    print(f"pérdida final={historia[-1][1]:.4f} · exactitud test={exactitud:.3f}")
    plt.plot([e for e, _ in historia], [v for _, v in historia], marker="o")
    plt.xlabel("época"); plt.ylabel("entropía cruzada"); plt.grid(alpha=.3);
    plt.savefig("imagenes/perdida_mlp.png", dpi=160, bbox_inches="tight")
    plt.show()
    """),
    md("""
    ## Frontera de decisión

    La probabilidad predicha muestra la frontera no lineal aprendida por la composición de capas.
    """),
    code("""
    gx, gy = torch.meshgrid(torch.linspace(-.3, 1.3, 160), torch.linspace(-.3, 1.3, 160), indexing="xy")
    rejilla = torch.stack([gx.flatten(), gy.flatten()], dim=1)
    with torch.no_grad():
        prob = torch.sigmoid(mlp(rejilla)).reshape(gx.shape)
    plt.contourf(gx, gy, prob, levels=20, cmap="coolwarm", alpha=.75)
    plt.colorbar(label="P(clase 1)")
    plt.scatter(X_base[:, 0], X_base[:, 1], c=y_base[:, 0], cmap="coolwarm", edgecolor="black", s=100)
    plt.xlabel("x₁"); plt.ylabel("x₂");
    plt.savefig("imagenes/frontera_mlp.png", dpi=160, bbox_inches="tight")
    plt.show()
    """),
    md("""
    ## La misma arquitectura con `torch.nn`

    `nn.Sequential` registra las capas y sus parámetros. El optimizador aplica las actualizaciones, pero el ciclo conceptual no cambia.
    """),
    code("""
    modelo = torch.nn.Sequential(
        torch.nn.Linear(2, 8),
        torch.nn.ReLU(),
        torch.nn.Linear(8, 1),
    )
    criterio = torch.nn.BCEWithLogitsLoss()
    optimizador = torch.optim.Adam(modelo.parameters(), lr=0.03)

    for _ in range(300):
        optimizador.zero_grad()
        perdida = criterio(modelo(X[train]), y[train])
        perdida.backward()
        optimizador.step()

    with torch.no_grad():
        pred = (modelo(X[test]) >= 0).float()
    print(modelo)
    print("exactitud test:", (pred == y[test]).float().mean().item())
    """),
    md("""
    ## Reto final

    1. Cambia el número de neuronas ocultas entre 1, 2, 4, 8 y 32.
    2. Sustituye ReLU por `Tanh` y razona qué cambia.
    3. Introduce validación y detén el entrenamiento cuando su pérdida deje de mejorar.
    4. Explica por qué el MLP resuelve XOR y el perceptrón simple no.

    **Cierre:** ya tenemos los componentes esenciales: tensores, transformaciones lineales, activaciones, pérdida, gradientes, optimización y evaluación.
    """),
])

print(f"Generados 6 notebooks en {OUT}")
