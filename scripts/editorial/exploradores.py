"""Código visible que se inserta en los notebooks visuales de Hespérides."""
COMUN = '''import numpy as np
import torch
from torch import nn
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML, display
import ipywidgets as widgets
from ipywidgets import interact

torch.manual_seed(42)
np.random.seed(42)
torch.set_num_threads(2)
plt.rcParams.update({"figure.dpi": 100, "axes.spines.top": False,
                     "axes.spines.right": False, "animation.embed_limit": 40})
'''

CAPAS = r'''
# Dos medias lunas: el orden de los puntos se mantiene a través de las capas.
generador = torch.Generator().manual_seed(42)
t = torch.linspace(0, np.pi, 120)
X = torch.cat([torch.stack([torch.cos(t), torch.sin(t)], 1),
               torch.stack([1-torch.cos(t), .5-torch.sin(t)], 1)])
X += .06 * torch.randn(X.shape, generator=generador)
y = torch.cat([torch.zeros(120), torch.ones(120)])
red = nn.Sequential(nn.Linear(2, 2), nn.Tanh(), nn.Linear(2, 2),
                    nn.Tanh(), nn.Linear(2, 1))
optimizador = torch.optim.Adam(red.parameters(), lr=.025)
historia, perdidas = [], []
for epoca in range(601):
    optimizador.zero_grad()
    logits = red(X).squeeze(1)
    perdida = nn.functional.binary_cross_entropy_with_logits(logits, y)
    perdida.backward()
    optimizador.step()
    perdidas.append(perdida.item())
    if epoca % 10 == 0:
        with torch.no_grad():
            h1 = red[:2](X); h2 = red[:4](X)
            historia.append((epoca, h1.numpy().copy(), h2.numpy().copy(),
                             red[4].weight.numpy().copy(), red[4].bias.item()))

def ver_capas(paso=0):
    epoca, h1, h2, w, b = historia[paso]
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.2))
    for ax, puntos, titulo in zip(axes, [X.numpy(), h1, h2],
                                ['Entrada', 'Capa oculta 1', 'Capa oculta 2']):
        ax.scatter(*puntos.T, c=y, cmap='coolwarm', s=13, vmin=0, vmax=1)
        ax.set(title=titulo, xlabel='Coordenada 1', ylabel='Coordenada 2')
    # En la última representación, la salida es una frontera afín.
    xx, yy = np.meshgrid(np.linspace(-1.1, 1.1, 80), np.linspace(-1.1, 1.1, 80))
    score = w[0, 0]*xx + w[0, 1]*yy + b
    if score.min() < 0 < score.max():axes[2].contour(xx, yy, score, levels=[0], colors='black')
    axes[1].set(xlim=(-1.1, 1.1), ylim=(-1.1, 1.1))
    axes[2].set(xlim=(-1.1, 1.1), ylim=(-1.1, 1.1))
    axes[3].plot(perdidas, color='#087E8B')
    axes[3].axvline(epoca, color='#D99B18')
    axes[3].set(title=f'Época {epoca}', xlabel='Época', ylabel='Pérdida de entrenamiento')
    fig.tight_layout()
    plt.show()

interact(ver_capas, paso=widgets.IntSlider(min=0, max=len(historia)-1, value=30,
                                         description='Instante', continuous_update=False));
'''
CAPAS_ANIMACION = r'''
# Animación autónoma: también funciona en una exportación HTML sin kernel.
fig, ax = plt.subplots(figsize=(5, 4))
puntos = ax.scatter(*historia[0][2].T, c=y, cmap='coolwarm', s=18, vmin=0, vmax=1)
ax.set(xlim=(-1.1, 1.1), ylim=(-1.1, 1.1), xlabel='Coordenada 1', ylabel='Coordenada 2')
def avanzar(i):
    puntos.set_offsets(historia[i][2])
    ax.set_title(f'Representación aprendida · época {historia[i][0]}')
    return puntos,
animacion = FuncAnimation(fig, avanzar, frames=len(historia), interval=100, blit=False)
plt.close(fig)
display(HTML(animacion.to_jshtml()))
'''
OPTIMIZACION = r'''
# Misma función y mismo punto inicial para comparar las trayectorias.
def trayectoria(metodo, tasa, pasos=80):
    x = torch.tensor([-3., 2.], requires_grad=True)
    clase = {'SGD': torch.optim.SGD, 'Momentum': torch.optim.SGD, 'Adam': torch.optim.Adam}[metodo]
    extra = {'momentum': .85} if metodo == 'Momentum' else {}
    opt = clase([x], lr=tasa, **extra)
    puntos = [x.detach().numpy().copy()]
    for _ in range(pasos):
        opt.zero_grad()
        perdida = .5 * (x[0]**2 + 15*x[1]**2)
        perdida.backward(); opt.step()
        puntos.append(x.detach().numpy().copy())
        if not torch.isfinite(x).all() or x.abs().max() > 1e5:break
    return np.array(puntos)

def ver_optimizacion(tasa=.08, paso=30):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    xx, yy = np.meshgrid(np.linspace(-4, 4, 150), np.linspace(-3, 3, 150))
    axes[0].contour(xx, yy, .5*(xx**2+15*yy**2), levels=[.1,.5,1,2,4,8,16,32,64], colors='#cccccc')
    for metodo, color in zip(['SGD','Momentum','Adam'], ['#087E8B','#D99B18','#775DA6']):
        p = trayectoria(metodo, tasa)
        k = min(paso, len(p)-1)
        axes[0].plot(*p[:k+1].T, '.-', color=color, label=metodo)
        axes[0].scatter(*p[k], s=65, color=color)
        axes[1].semilogy(.5*(p[:,0]**2+15*p[:,1]**2)+1e-12, color=color, label=metodo)
    axes[0].set(xlim=(-4,4), ylim=(-3,3), xlabel='Parámetro 1', ylabel='Parámetro 2', title='Trayectorias calculadas')
    axes[1].axvline(paso, color='black', alpha=.3)
    axes[1].set(xlabel='Actualización', ylabel='Pérdida (escala logarítmica)', title='Convergencia o divergencia')
    axes[0].legend();fig.tight_layout();plt.show()

interact(ver_optimizacion, tasa=widgets.FloatLogSlider(value=.08, base=10, min=-3, max=-.5, step=.05,
                                                      description='Tasa', continuous_update=False),
         paso=widgets.IntSlider(value=30,min=0,max=80,description='Paso',continuous_update=False));
'''
GENERALIZACION = r'''
# La función verdadera se conoce porque aquí los datos son sintéticos.
rng = np.random.default_rng(42)
x_train = np.sort(rng.uniform(-1, 1, 24)); x_val = np.sort(rng.uniform(-1, 1, 80))
y_train = np.sin(np.pi*x_train) + rng.normal(0,.22,len(x_train))
y_val = np.sin(np.pi*x_val) + rng.normal(0,.22,len(x_val))
xx = np.linspace(-1,1,300)

def ajuste(grado, regularizacion):
    # Base de Legendre para no confundir sobreajuste con una Vandermonde mal condicionada.
    A = np.polynomial.legendre.legvander(x_train, grado)
    penalizacion = np.eye(grado+1);penalizacion[0,0] = 0
    sistema = np.vstack([A, np.sqrt(regularizacion*len(A))*penalizacion])
    objetivo = np.concatenate([y_train, np.zeros(grado+1)])
    return np.linalg.lstsq(sistema, objetivo, rcond=None)[0]

def ver_generalizacion(grado=5, regularizacion=.001):
    w = ajuste(grado, regularizacion)
    predecir = lambda x: np.polynomial.legendre.legvander(x, grado) @ w
    fig, axes = plt.subplots(1,2,figsize=(11,4))
    axes[0].scatter(x_train,y_train,color='#087E8B',label='Entrenamiento')
    axes[0].scatter(x_val,y_val,facecolors='none',edgecolors='#D99B18',alpha=.5,label='Validación')
    axes[0].plot(xx,np.sin(np.pi*xx),'k--',label='Señal verdadera')
    axes[0].plot(xx,predecir(xx),color='#775DA6',label='Modelo')
    axes[0].set(ylim=(-2,2),title=f'Grado {grado} · λ={regularizacion:g}',xlabel='x',ylabel='y')
    errores=[]
    for d in range(1,19):
        wd=ajuste(d,regularizacion)
        errores.append([np.mean((np.polynomial.legendre.legvander(x,d)@wd-y)**2)
                        for x,y in [(x_train,y_train),(x_val,y_val)]])
    axes[1].semilogy(range(1,19),errores)
    axes[1].axvline(grado,color='black',alpha=.3)
    axes[1].set(xlabel='Grado',ylabel='MSE',title='Ajuste y generalización')
    axes[1].legend(['Entrenamiento','Validación']);axes[0].legend(fontsize=8)
    fig.tight_layout();plt.show()

interact(ver_generalizacion,grado=widgets.IntSlider(value=5,min=1,max=18,description='Grado',continuous_update=False),
         regularizacion=widgets.FloatLogSlider(value=.001,base=10,min=-7,max=1,step=.5,
                                              description='λ',continuous_update=False));
'''
CONVOLUCION = r'''
# Cada posición usa los mismos nueve pesos. PyTorch calcula correlación cruzada.
imagen = np.zeros((8,8));imagen[1:7,3:6] = 1
filtros = {'Borde vertical': np.array([[-1,0,1],[-1,0,1],[-1,0,1]]),
           'Borde horizontal': np.array([[-1,-1,-1],[0,0,0],[1,1,1]]),
           'Promedio': np.ones((3,3))/9}

def ver_convolucion(posicion=14, filtro='Borde vertical'):
    K = filtros[filtro]
    salida = nn.functional.conv2d(torch.tensor(imagen)[None,None],torch.tensor(K,dtype=torch.float64)[None,None])[0,0].numpy()
    fila,col = divmod(posicion,6)
    parche = imagen[fila:fila+3,col:col+3]
    producto = parche*K
    assert np.isclose(producto.sum(),salida[fila,col])
    fig, axes = plt.subplots(1,4,figsize=(13,3))
    matrices=[imagen,K,producto,salida]
    titulos=['Entrada y ventana','Filtro compartido','Productos locales',f'Suma = {producto.sum():.2f}']
    for ax,M,titulo in zip(axes,matrices,titulos):
        ax.imshow(M,cmap='coolwarm',vmin=-3,vmax=3)
        ax.set_title(titulo);ax.set_xticks([]);ax.set_yticks([])
        if M.shape==(3,3):
            for (i,j),v in np.ndenumerate(M):ax.text(j,i,f'{v:.2g}',ha='center',va='center')
    axes[0].add_patch(plt.Rectangle((col-.5,fila-.5),3,3,fill=False,edgecolor='#D99B18',lw=3))
    axes[3].add_patch(plt.Rectangle((col-.5,fila-.5),1,1,fill=False,edgecolor='#D99B18',lw=3))
    fig.tight_layout();plt.show()

interact(ver_convolucion,posicion=widgets.IntSlider(value=14,min=0,max=35,description='Ventana',continuous_update=False),
         filtro=list(filtros));
'''
CONVOLUCION_ANIMACION = r'''
K=filtros['Borde vertical']
salida=nn.functional.conv2d(torch.tensor(imagen)[None,None],torch.tensor(K,dtype=torch.float64)[None,None])[0,0].numpy()
fig,axes=plt.subplots(1,2,figsize=(7,3.5))
axes[0].imshow(imagen,cmap='gray',vmin=0,vmax=1)
ventana=plt.Rectangle((-.5,-.5),3,3,fill=False,edgecolor='#D99B18',lw=3);axes[0].add_patch(ventana)
mapa=axes[1].imshow(np.full((6,6),np.nan),cmap='coolwarm',vmin=-3,vmax=3)
axes[0].set_title('El mismo filtro en cada posición');axes[1].set_title('Mapa de respuesta')
def avanzar_ventana(paso):
    fila,col=divmod(paso,6);ventana.set_xy((col-.5,fila-.5))
    parcial=np.full((6,6),np.nan);parcial.flat[:paso+1]=salida.flat[:paso+1];mapa.set_data(parcial)
    return ventana,mapa
animacion=FuncAnimation(fig,avanzar_ventana,frames=36,interval=180)
plt.close(fig);display(HTML(animacion.to_jshtml()))
'''
ATENCION = r'''
# Vectores didácticos fijos: inspeccionamos el mecanismo, no un modelo del lenguaje entrenado.
tokens=['El','gato','mira','la','luna']
Q=torch.tensor([[1.,0.,0.],[0.,1.,0.],[.2,.8,.5],[1.,.1,0.],[0.,.3,1.]])
K=torch.tensor([[1.,0.,0.],[0.,1.,.2],[.2,.5,.5],[.8,.1,0.],[0.,.2,1.]])
V=torch.tensor([[1.,0.],[0.,1.],[.5,.5],[.8,.2],[.1,.9]])

def calcular_atencion(temperatura,causal):
    scores=Q@K.T/np.sqrt(Q.shape[1])/temperatura
    if causal:scores=scores.masked_fill(torch.triu(torch.ones(5,5,dtype=torch.bool),diagonal=1),-torch.inf)
    A=torch.softmax(scores,dim=-1)
    assert torch.allclose(A.sum(-1),torch.ones(5))
    if causal:assert torch.equal(torch.triu(A,diagonal=1),torch.zeros_like(A))
    return scores,A,A@V

def ver_atencion(consulta=2,temperatura=1.,causal=True):
    scores,A,O=calcular_atencion(temperatura,causal)
    fig,axes=plt.subplots(1,4,figsize=(14,3.4),gridspec_kw={'width_ratios':[1,1,1,.8]})
    axes[0].imshow(np.ma.masked_invalid(scores.numpy()),cmap='coolwarm',vmin=-2,vmax=2)
    axes[1].imshow(A,cmap='YlGnBu',vmin=0,vmax=1)
    for ax,titulo in zip(axes[:2],['QKᵀ / √d / temperatura','Softmax por fila']):
        ax.set(xticks=range(5),yticks=range(5),xticklabels=tokens,yticklabels=tokens,title=titulo,xlabel='Claves',ylabel='Consultas')
        ax.add_patch(plt.Rectangle((-.5,consulta-.5),5,1,fill=False,edgecolor='#D99B18',lw=2))
    contribuciones=A[consulta,:,None]*V
    axes[2].imshow(contribuciones,cmap='YlGnBu',vmin=0,vmax=1,aspect='auto')
    axes[2].set(yticks=range(5),yticklabels=tokens,xticks=[0,1],title='Peso × valor',xlabel='Componente de V')
    axes[3].bar([0,1],O[consulta],color=['#087E8B','#D99B18'])
    axes[3].set(ylim=(0,1),xticks=[0,1],title=f'Suma para «{tokens[consulta]}»',xlabel='Componente de salida')
    fig.tight_layout();plt.show()

interact(ver_atencion,consulta=widgets.IntSlider(value=2,min=0,max=4,description='Consulta',continuous_update=False),
         temperatura=widgets.FloatSlider(value=1,min=.1,max=3,step=.1,description='Temperatura',continuous_update=False),
         causal=True);
'''

AUTOENCODER = r'''
# Familia sintética bidimensional de imágenes: una mancha cambia de posición.
g = torch.Generator().manual_seed(7)
centros = 1.4*torch.rand((320,2), generator=g)-.7
coord = torch.linspace(-1,1,16)
gy,gx = torch.meshgrid(coord,coord,indexing='ij')
imagenes = torch.exp(-((gx[None]-centros[:,0,None,None])**2 +
                       (gy[None]-centros[:,1,None,None])**2)/.075)
entradas=imagenes.flatten(1)
encoder=nn.Sequential(nn.Linear(256,64),nn.ReLU(),nn.Linear(64,2))
decoder=nn.Sequential(nn.Linear(2,64),nn.ReLU(),nn.Linear(64,256),nn.Sigmoid())
opt=torch.optim.Adam(list(encoder.parameters())+list(decoder.parameters()),lr=.008)
curva=[]
for epoca in range(450):
    opt.zero_grad()
    reconstruccion=decoder(encoder(entradas[:256]))
    perdida=nn.functional.mse_loss(reconstruccion,entradas[:256])
    perdida.backward();opt.step();curva.append(perdida.item())
with torch.no_grad():
    Z=encoder(entradas)
    reconstruidas=decoder(Z).reshape(-1,16,16)
    media=Z[:256].mean(0);escala=Z[:256].std(0).clamp_min(1e-6)
    Zn=(Z-media)/escala
    mse_val=nn.functional.mse_loss(reconstruidas[256:],imagenes[256:]).item()
print(f'MSE final de validación: {mse_val:.5f} · 64 imágenes no usadas para ajustar')

def ver_reconstruccion(indice=280):
    fig,ax=plt.subplots(1,4,figsize=(13,3))
    ax[0].imshow(imagenes[indice],cmap='magma',vmin=0,vmax=1);ax[0].set_title('Original')
    ax[1].imshow(reconstruidas[indice],cmap='magma',vmin=0,vmax=1);ax[1].set_title('Reconstrucción')
    ax[2].imshow((reconstruidas[indice]-imagenes[indice]).abs(),cmap='magma',vmin=0,vmax=.3);ax[2].set_title('Error absoluto')
    ax[3].scatter(*Zn.T,c=centros[:,0],cmap='viridis',s=9)
    ax[3].scatter(*Zn[indice],facecolor='none',edgecolor='red',s=120)
    ax[3].set(title='Dos coordenadas latentes',xlabel='z₁ estandarizada',ylabel='z₂ estandarizada')
    for a in ax[:3]:a.axis('off')
    fig.tight_layout();plt.show()
interact(ver_reconstruccion,indice=widgets.IntSlider(value=280,min=0,max=319,
                                                   description='Imagen',continuous_update=False));

def recorrer_latente(z1=0.,z2=0.):
    with torch.no_grad():
        z=torch.tensor([z1,z2])*escala+media
        imagen_decodificada=decoder(z).reshape(16,16)
    fig,ax=plt.subplots(1,2,figsize=(7,3))
    ax[0].scatter(*Zn[:256].T,c=centros[:256,0],cmap='viridis',s=10)
    ax[0].scatter(z1,z2,color='red',marker='x',s=100)
    ax[0].set(xlim=(-3,3),ylim=(-3,3),title='Consulta en el espacio latente',xlabel='z₁',ylabel='z₂')
    ax[1].imshow(imagen_decodificada,cmap='magma',vmin=0,vmax=1);ax[1].set_title('Salida del decoder');ax[1].axis('off')
    fig.tight_layout();plt.show()
interact(recorrer_latente,
         z1=widgets.FloatSlider(value=0,min=-3,max=3,step=.1,continuous_update=False),
         z2=widgets.FloatSlider(value=0,min=-3,max=3,step=.1,continuous_update=False));
'''
