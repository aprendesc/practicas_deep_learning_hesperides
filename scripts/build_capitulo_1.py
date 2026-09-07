"""Genera el capítulo 1: datos, neurona, perceptrón y capas."""
import json
from pathlib import Path
from textwrap import dedent

OUT = Path(__file__).resolve().parents[1] / "capitulo_1"

def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": dedent(text).strip().splitlines(True)}

def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": dedent(text).strip().splitlines(True)}

def save(name, cells):
    nb = {"cells": cells, "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"}},
        "nbformat": 4, "nbformat_minor": 4}
    (OUT / name).write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

OUT.mkdir(exist_ok=True)
(OUT / "imagenes").mkdir(exist_ok=True)
setup = code("""
import torch
import matplotlib.pyplot as plt
AMARILLO, NEGRO, BLANCO, GRIS = "#F9C80E", "#111111", "#FFFFFF", "#B7B7B7"
torch.set_printoptions(precision=3, sci_mode=False)
print(f"PyTorch {torch.__version__}")
""")

save("01_datos_y_tensores.ipynb", [
md("""
# 1. De los datos a los tensores

**Pregunta guía:** ¿cómo convertimos una observación del mundo en números que una neurona pueda procesar?

Una observación se describe mediante **características**. Cada característica ocupa una posición fija y todas juntas forman un vector. Una neurona no recibe “una empresa” o “una imagen”: recibe una colección ordenada de valores.

## Escalares, vectores y matrices

- Un **escalar** representa un valor.
- Un **vector** reúne las características de una observación.
- Una **matriz** apila observaciones: filas para los casos y columnas para las características.
- Un **tensor** generaliza estas estructuras a cualquier número de ejes.

La forma o `shape` funciona como un contrato: determina qué representa cada eje.
"""), setup,
code("""
liquidez = torch.tensor(0.72)
empresa = torch.tensor([0.72, 0.31, 0.18])
cartera = torch.tensor([
    [0.72, 0.31, 0.18],
    [0.45, 0.67, 0.42],
    [0.81, 0.22, 0.11],
    [0.39, 0.74, 0.55],
])
for nombre, dato in {"escalar": liquidez, "vector": empresa, "matriz": cartera}.items():
    print(f"{nombre:7s} · forma={tuple(dato.shape)} · dimensiones={dato.ndim}")
print("\\nMatriz de observaciones:\\n", cartera)
"""),
md("""
## Leer una matriz como un conjunto de datos

Indexar expresa una pregunta. `X[0]` pide la primera observación; `X[:, 1]` pide la segunda característica para todas las observaciones.
"""),
code("""
print("Primera observación:", cartera[0])
print("Segunda característica:", cartera[:, 1])
print("Media por característica:", cartera.mean(dim=0))
"""),
md("""
## La escala importa

Una característica expresada en millones y otra entre 0 y 1 no son comparables directamente. Estandarizar centra cada columna en cero y la expresa en unidades de desviación típica.
"""),
code("""
media, desviacion = cartera.mean(dim=0), cartera.std(dim=0)
estandarizada = (cartera - media) / desviacion
print(estandarizada)
print("Medias:", estandarizada.mean(dim=0))
print("Desviaciones:", estandarizada.std(dim=0))
"""),
md("""
## Comprueba tu comprensión

1. ¿Qué representan `cartera.shape[0]` y `cartera.shape[1]`?
2. Añade una quinta observación sin alterar el significado de las columnas.
3. Extrae la primera y tercera característica.
4. Explica por qué cambiar el orden de las columnas cambia el significado.

**Conclusión:** representar bien las entradas es el primer requisito de cualquier neurona.
""")])

save("02_neurona_artificial.ipynb", [
md("""
# 2. Anatomía de una neurona artificial

**Pregunta guía:** ¿cómo transforma una neurona varias entradas en una salida?

![Esquema conceptual de una neurona artificial](imagenes/neurona_artificial.png)

Una neurona realiza dos operaciones: combina entradas mediante una **suma ponderada** y aplica una **función de activación**.

## Entradas, pesos y sesgo

Para $x=(x_1,\\ldots,x_d)$:

$$z=w_1x_1+\\cdots+w_dx_d+b=w^Tx+b.$$

- Las **entradas** $x_i$ son características.
- Los **pesos** $w_i$ determinan influencia y sentido.
- El **sesgo** $b$ desplaza el umbral.
- $z$ es la combinación previa a la activación.

Un peso positivo favorece la respuesta cuando crece su entrada; uno negativo la dificulta; uno nulo elimina su influencia.
"""), setup,
code("""
x = torch.tensor([0.8, 0.4, 0.2])
w = torch.tensor([1.5, -1.0, 0.5])
b = torch.tensor(-0.3)
contribuciones = x * w
z = contribuciones.sum() + b
print("Entradas:       ", x)
print("Pesos:          ", w)
print("Contribuciones: ", contribuciones)
print("Sesgo:          ", b.item())
print("Suma ponderada: ", z.item())
"""),
md("""
## Función umbral

El perceptrón clásico utiliza una activación escalón:

$$a(z)=\\begin{cases}1,&z\\geq0\\\\0,&z<0.\\end{cases}$$

La salida es una decisión binaria: sí/no, activo/inactivo o clase 1/clase 0.
"""),
code("""
def escalon(z):
    return (z >= 0).to(torch.int)

salida = escalon(z)
print(f"z = {z.item():.3f} → salida = {salida.item()}")
"""),
md("""
## El sesgo mueve el umbral

Con una entrada y peso positivo, aumentar el sesgo facilita la activación; reducirlo exige una entrada mayor.
"""),
code("""
entradas = torch.linspace(-2, 2, 200)
fig, ax = plt.subplots(figsize=(8, 3.5))
for sesgo, color, estilo in [(-0.8, NEGRO, "-"), (0.0, GRIS, "--"), (0.8, AMARILLO, "-.")]:
    ax.step(entradas, escalon(entradas + sesgo), where="post",
            color=color, linestyle=estilo, linewidth=2, label=f"b={sesgo:+.1f}")
ax.set(xlabel="entrada", ylabel="salida", yticks=[0, 1], title="Efecto del sesgo")
ax.legend(); ax.grid(alpha=.2)
plt.savefig("imagenes/efecto_sesgo.png", dpi=160, bbox_inches="tight")
plt.show()
"""),
md("""
## Comprueba tu comprensión

1. Calcula la salida para $x=(1,0,1)$, $w=(2,-1,0.5)$ y $b=-2$.
2. ¿Qué sucede al multiplicar pesos y sesgo por 10?
3. Propón una característica que merezca un peso negativo.
4. Distingue la suma ponderada $z$ de la salida activada.

**Conclusión:** una neurona proyecta un vector y convierte el resultado en una decisión.
""")])

save("03_perceptron.ipynb", [
md("""
# 3. El perceptrón como clasificador lineal

**Pregunta guía:** ¿qué geometría produce una neurona con activación umbral?

![Dos regiones separadas por una frontera lineal](imagenes/frontera_lineal.png)

La condición $w^Tx+b=0$ define la **frontera de decisión**. En dos dimensiones es una recta; en tres, un plano; en dimensiones superiores, un hiperplano. A cada lado, el signo determina una clase.
"""), setup,
md("""
## Un perceptrón completamente especificado

No vamos a entrenarlo: fijaremos sus parámetros para estudiar su comportamiento. Con $w=(1,1)$ y $b=-1$, la frontera es $x_1+x_2=1$.
"""),
code("""
w, b = torch.tensor([1.0, 1.0]), torch.tensor(-1.0)
def perceptron(X):
    puntuacion = X @ w + b
    return puntuacion, (puntuacion >= 0).to(torch.int)

ejemplos = torch.tensor([[0.1, 0.2], [0.4, 0.8], [0.7, 0.6], [0.9, 0.3]])
puntuaciones, clases = perceptron(ejemplos)
for x, z, clase in zip(ejemplos, puntuaciones, clases):
    print(f"x={x.tolist()} · z={z.item():+.2f} · clase={clase.item()}")
"""),
md("""
## Visualizar la decisión

El vector $w$ es perpendicular a la frontera y apunta hacia la región clasificada como 1. El sesgo cambia la posición sin modificar la orientación.
"""),
code("""
eje = torch.linspace(-0.2, 1.4, 250)
gx, gy = torch.meshgrid(eje, eje, indexing="xy")
_, region = perceptron(torch.stack([gx.flatten(), gy.flatten()], dim=1))
fig, ax = plt.subplots(figsize=(7, 5))
ax.contourf(gx, gy, region.reshape(gx.shape), levels=[-.5,.5,1.5], colors=[BLANCO,"#FFF1A8"])
ax.plot(eje, 1-eje, color=NEGRO, linewidth=2, label=r"$x_1+x_2=1$")
ax.scatter(ejemplos[:,0], ejemplos[:,1], c=[NEGRO if c==0 else AMARILLO for c in clases],
           edgecolor=NEGRO, s=90, zorder=3)
ax.set(xlabel="$x_1$", ylabel="$x_2$", xlim=(-.2,1.4), ylim=(-.2,1.4))
ax.legend(); ax.grid(alpha=.15)
plt.savefig("imagenes/decision_perceptron.png", dpi=160, bbox_inches="tight")
plt.show()
"""),
md("""
## Puertas lógicas

AND y OR son linealmente separables. El mismo peso $(1,1)$ y distintos sesgos producen ambas decisiones.
"""),
code("""
binarios = torch.tensor([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
for nombre, sesgo in {"AND": -1.5, "OR": -0.5}.items():
    salida = ((binarios @ torch.tensor([1.,1.]) + sesgo) >= 0).to(torch.int)
    print(nombre, ":", salida.tolist())
"""),
md("""
## Límite estructural

XOR asigna la misma clase a esquinas opuestas. Ninguna recta separa simultáneamente esas parejas. No es cuestión de elegir mejor los pesos: una neurona umbral solo expresa separaciones lineales.

## Comprueba tu comprensión

1. Dibuja la frontera de $w=(2,-1)$ y $b=0$.
2. ¿Qué cambia al multiplicar $w$ y $b$ por un valor positivo? ¿Y negativo?
3. Encuentra pesos y sesgo para NAND.
4. Explica por qué XOR exige combinar decisiones.

**Conclusión:** el perceptrón es interpretable, pero su capacidad queda limitada por una frontera lineal.
""")])

save("04_neuronas_y_capas.ipynb", [
md("""
# 4. De una neurona a una red por capas

**Pregunta guía:** ¿qué ganamos al organizar varias neuronas?

![Red neuronal organizada en capas](imagenes/red_por_capas.png)

Una red agrupa unidades en tres tipos de capas:

1. La **entrada** contiene las características.
2. Las **capas ocultas** construyen representaciones intermedias.
3. La **salida** produce la respuesta final.

“Oculta” solo significa que no corresponde directamente a los datos observados ni a la respuesta.
"""), setup,
md("""
## Una capa procesa varias neuronas a la vez

Reunimos los pesos en una matriz $W$ y los sesgos en un vector $b$:

$$h=a(XW+b).$$

Cada columna de $W$ contiene los pesos de una neurona. El número de columnas determina cuántas salidas produce la capa.
"""),
code("""
X = torch.tensor([[0.2,0.8,0.4], [0.9,0.1,0.6]])
W = torch.tensor([[1.,-1.,.5,.2], [.5,1.,-.5,.8], [-.2,.4,1.,-1.]])
b = torch.tensor([-.4,-.2,-.3,.1])
z = X @ W + b
h = (z >= 0).to(torch.int)
print("entrada:", X.shape)
print("pesos:  ", W.shape)
print("salida: ", h.shape)
print("\\nActivaciones:\\n", h)
"""),
md("""
## Composición de decisiones

Varias neuronas detectan condiciones parciales; otra puede combinarlas. Esto crea regiones que una sola recta no describe.

El ejemplo implementa XOR con parámetros elegidos a mano:

- Una unidad oculta calcula OR.
- Otra calcula NAND.
- La salida calcula AND sobre ambas señales.

Estudiamos el recorrido de la información, no cómo se obtienen automáticamente los parámetros.
"""),
code("""
X_logico = torch.tensor([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
umbral = lambda z: (z >= 0).to(torch.float32)
or_oculta = umbral(X_logico @ torch.tensor([1.,1.]) - .5)
nand_oculta = umbral(X_logico @ torch.tensor([-1.,-1.]) + 1.5)
H = torch.stack([or_oculta, nand_oculta], dim=1)
xor_salida = umbral(H @ torch.tensor([1.,1.]) - 1.5)
print("x₁ x₂ | OR NAND | XOR")
for x, h, y in zip(X_logico, H, xor_salida):
    print(f" {int(x[0])}  {int(x[1])} |  {int(h[0])}    {int(h[1])}  |  {int(y)}")
"""),
md("""
## Anchura, profundidad y propagación hacia delante

La **anchura** es el número de neuronas de una capa. La **profundidad** cuenta transformaciones sucesivas. Una red con capa oculta suele llamarse perceptrón multicapa.

Aquí solo necesitamos la propagación **hacia delante**:

$$x\\longrightarrow h\\longrightarrow y.$$

Cada capa recibe la salida anterior. El ajuste automático de parámetros pertenece a una etapa posterior.

## Comprueba tu comprensión

1. Identifica las formas de $X$, $W$, $b$ y $h$.
2. ¿Por qué cada columna de $W$ representa una neurona?
3. Sigue manualmente $(1,0)$ a través de OR, NAND y AND.
4. Distingue entrada, capa oculta y salida.
5. Explica qué aporta la composición frente a una frontera.

**Cierre:** un perceptrón convierte características en una decisión lineal; una red organiza perceptrones en capas para componer decisiones.
""")])

print("Generados 4 notebooks conceptuales")
