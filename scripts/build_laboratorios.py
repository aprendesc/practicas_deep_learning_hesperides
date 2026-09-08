"""Construye los derivados de D2L y las ampliaciones visuales; nunca escribe en locked."""
import copy
import hashlib
import json
import re
from pathlib import Path
from editorial import exploradores as vis

ROOT=Path(__file__).resolve().parents[1]
ITEMS=json.loads((ROOT/'scripts/editorial/seleccion.json').read_text())
TRANS=json.loads((ROOT/'scripts/editorial/traducciones.json').read_text())
CORRECTIONS=ROOT/'scripts/editorial/correcciones.json'
OVERRIDES=json.loads(CORRECTIONS.read_text()) if CORRECTIONS.exists() else {}
LABELS={}
for f in (ROOT/'locked').rglob('*.ipynb'):
    try:n=json.loads(f.read_text())
    except ValueError:continue
    text='\n'.join(''.join(c['source']) for c in n['cells'])
    url='https://d2l.ai/'+str(f.relative_to(ROOT/'locked')).replace('.ipynb','.html')
    for label in re.findall(r':label:`([^`]+)`',text):LABELS[label]=url

NOTAS={
1:'Una forma correcta no garantiza un significado correcto: fija qué representa cada eje antes de calcular. En el primer entrenamiento, distingue logits, probabilidades y etiquetas. La ilustración presenta una intuición; el explorador final muestra coordenadas realmente calculadas por una red pequeña.',
2:'Sigue tres objetos diferentes: el valor de la pérdida, su gradiente y la actualización que calcula el optimizador. Comprueba formas y reinicia los gradientes antes de cada paso. En el explorador se mantienen función y punto inicial para comparar trayectorias; una misma tasa no significa el mismo desplazamiento efectivo para todos los métodos.',
3:'Para comparar modelos, conserva la partición y empareja las semillas. Selecciona hiperparámetros con validación y reserva el test para el final. La versión D2L de Fashion-MNIST llama «val» al test oficial: en estos derivados se separa validación del entrenamiento oficial. El modo rápido demuestra mecanismos; no permite extraer una clasificación definitiva de técnicas.',
4:'Comprueba primero las formas y el supuesto arquitectónico: localidad, compartición de pesos o conexión residual. El explorador permite seguir ventana, multiplicaciones y suma. En PyTorch, Conv2d implementa correlación cruzada; en aprendizaje profundo se suele llamar convolución a esta operación. El autoencoder 91 amplía el patrón MLP con reconstrucción; VAE se trata como contraste conceptual, al no existir un original válido en las fuentes locales.',
5:'Escribe qué información puede ver cada posición. Una máscara causal impide consultar el futuro; una máscara de padding excluye posiciones que no son datos. Comprueba que cada fila de atención suma uno antes de aplicar dropout. Los mapas de atención describen mezclas de valores, pero por sí solos no prueban una explicación causal del modelo.'}
GLOSSARY={'NumpPy':'NumPy','Numpy':'NumPy','una brisa':'sencillo','características asesinas':'funcionalidades especialmente útiles','ensuciar nuestras manos':'ponernos manos a la obra','marcos modernos':'bibliotecas modernas','marco de aprendizaje profundo':'biblioteca de aprendizaje profundo','marcos de aprendizaje profundo':'bibliotecas de aprendizaje profundo','*tensors*':'*tensores*','multipercapa':'multicapa','backpropagación':'retropropagación','propagación hacia atrás':'retropropagación','propagación hacia adelante':'propagación hacia delante','normalización por lotes':'normalización por lotes (BatchNorm)','normalización de lotes':'normalización por lotes (BatchNorm)','abandono escolar':'dropout','abandono de la escuela':'dropout','decaimiento del peso':'decaimiento de pesos','descenso de gradiente':'descenso por gradiente','entrenar y probar':'entrenamiento y test','## Resumen':'## Resumen','## Comenzando':'## Primeros pasos'}

GLOSSARY.update(json.loads((ROOT/'scripts/editorial/glosario.json').read_text()))

def md(s,**meta):return dict(cell_type='markdown',metadata=meta,source=s)
def code(s,**meta):return dict(cell_type='code',metadata=meta,source=s,execution_count=None,outputs=[])
def tidy(s):
    for a,b in GLOSSARY.items():s=s.replace(a,b)
    s=re.sub(r'(?m)^(#{1,5})\s+(?:#\s*)?\*?\*?\s*(.*?)\s*(?:\*\*|###|#)?$',lambda m:m[1]+' '+m[2],s)
    s=s.replace('../img/','../recursos/originales/').replace('(img/','(../recursos/originales/')
    s=re.sub(r':label:`([^`]+)`',lambda m:f'<a id="{m[1]}"></a>',s)
    s=re.sub(r':(?:numref|ref|eqref):`([^`]+)`',lambda m:f'[Referencia {m[1]}]({LABELS.get(m[1],"https://d2l.ai/")}#{m[1].replace("_","-")})',s)
    s=re.sub(r':(?:cite|citet):`([^`]+)`',lambda m:f'[{m[1]}](https://d2l.ai/chapter_references/zreferences.html)',s)
    s=re.sub(r'^:(?:width|height):.*$','',s,flags=re.M)
    s=s.replace('[Discussions]','[Debate del original]')
    return s

SETUP='''from pathlib import Path
import sys
RAIZ = Path.cwd() if (Path.cwd() / "laboratorio").exists() else Path.cwd().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
from laboratorio import d2l, configurar, epocas
configurar()
'''

THEORY=json.loads((ROOT/'scripts/editorial/teoria.json').read_text())
changes=[]
for e in ITEMS:
    n=json.loads((ROOT/e['source']).read_text()); translated=TRANS[e['source']]
    cells=[]
    for i,c in enumerate(n['cells']):
        s=OVERRIDES.get(e['source'],{}).get(str(i),translated[i])
        if c['cell_type']=='markdown':new=md(tidy(s),origen_celda=i)
        else:
            s=s.replace('from d2l import torch as d2l','from laboratorio import d2l')
            s=s.replace('../img/','../recursos/originales/')
            s=s.replace('torchvision.models.resnet18(pretrained=True)','torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1)')
            # Etiquetas visibles; no se cambia el significado de variables o API.
            for a,b in {'grad of relu':'gradiente de ReLU','grad of sigmoid':'gradiente de sigmoid','grad of tanh':'gradiente de tanh','Key positions':'Posiciones de claves','Query positions':'Posiciones de consultas','Keys':'Claves','Queries':'Consultas','Column (encoding dimension)':'Columna (dimensión)','Row (position)':'Fila (posición)','Head %d':'Cabeza %d','1-step preds':'Predicción a un paso','multistep preds':'Predicción recursiva','time (sec)':'tiempo (s)'}.items():s=s.replace(a,b)
            # La clase introductoria del notebook debe usar la misma partición que el soporte.
            if e['source'].endswith('/image-classification-dataset.ipynb') and i==3:
                s+='\n        self.train, self.val = d2l.separar_validacion(self.train)\n'
            if e['source'].endswith('/image-classification-dataset.ipynb') and i==17:
                s=s.replace('raise NotImplementedError','return d2l.show_images(imgs, num_rows, num_cols, titles, scale)')
            if e['source'].endswith('/image-augmentation.ipynb') and i==29:
                s=s.replace('    timer, num_batches', '    devices = devices or [torch.device("cpu")]\n    train_iter, test_iter, num_epochs = d2l.limitar_carga(train_iter, test_iter, num_epochs)\n    timer, num_batches').replace('num_batches // 5', 'max(1, num_batches // 5)')
            s='\n'.join(tidy(line) if line.lstrip().startswith('#') else line for line in s.split('\n'))
            if s!=translated[i]:changes.append({'notebook':e['target'],'source_cell':i,'change':'Compatibilidad, etiquetas, partición o cómputo; cotejar celda con locked.'})
            new=code(s,origen_celda=i)
        cells.append(new)
    intro=f'''# {e['title']}

**Capítulo {e['chapter']} · Universidad de las Hespérides**

Adaptación al español de *Dive into Deep Learning*, Aston Zhang, Zachary C. Lipton, Mu Li y Alexander J. Smola.
Fuente: `{e['source']}` · [Lección original](https://d2l.ai/{e['source'].removeprefix('locked/').replace('.ipynb','.html')}).
Texto adaptado bajo [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). [Procedencia y cambios](../PROCEDENCIA.md).
Se conserva la secuencia de las celdas y de los ejercicios; las notas de Hespérides se identifican expresamente.

**Entorno:** ejecuta `uv sync` en la raíz y selecciona su Python como kernel. Las descargas se realizan una vez y quedan en `data/`.
Por defecto, el soporte limita los entrenamientos de `Trainer` a tres épocas y 1024/256 ejemplos para CPU.
Para repetir el régimen completo, inicia Jupyter con `HESPERIDES_COMPLETO=1`. Los ejemplos visuales pequeños conservan su propia configuración explícita.
Los datos de texto en inglés o francés son entradas de los experimentos originales y mantienen su idioma.
'''
    note=md(f'### Nota docente de Hespérides\n\n{THEORY.get(Path(e['target']).name, NOTAS[e['chapter']])}\n\nVínculo con los apuntes: sesión {e["chapter"]}, «{e["title"]}».\n')
    # Insertar antes de los ejercicios incluso en originales de una sola celda Markdown.
    last=cells[-1]
    if len(cells)<=2 and last['cell_type']=='markdown' and '## Ejercicios' in last['source']:
        body,questions=last['source'].split('## Ejercicios',1)
        cells=cells[:-1]+[md(body,origen_celda=len(n['cells'])-1),note,md('## Ejercicios'+questions,origen_celda=len(n['cells'])-1)]
    else:cells.insert(max(1,len(cells)//2),note)
    if e['source'].endswith('/softmax-regression.ipynb'):
        cells.insert(-1,md('**Errata del original:** en el ejercicio de log-partición, la igualdad de invariancia planteada debe revisarse. Comprueba su validez antes de intentar demostrarla.'))
    if e['source'].endswith('/lenet.ipynb'):
        cells.insert(-1,md('**Errata del original:** el ejercicio de modernización menciona sustituir softmax por ReLU. En esta arquitectura las activaciones ocultas son sigmoid; el clasificador entrega logits. Interpreta y justifica la corrección sin sustituir la salida de clasificación por ReLU.'))
    n['cells']=[md(intro),code(SETUP)]+cells
    n['metadata']={'kernelspec':{'display_name':'Python 3 (Hespérides)','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'},'hesperides':{'source':e['source'],'sha256':e['sha256'],'chapter':e['chapter'],'adaptation':'Traducción con revisión y ampliaciones docentes'}}
    n['nbformat_minor']=5
    for i,c in enumerate(n['cells']):c['id']=hashlib.sha256((e['target']+str(i)).encode()).hexdigest()[:12]
    target=ROOT/e['target'];target.parent.mkdir(exist_ok=True);target.write_text(json.dumps(n,ensure_ascii=False,indent=1)+'\n')

visuals=[('Capas y representaciones',vis.CAPAS,vis.CAPAS_ANIMACION,
'Las dos coordenadas de cada capa se muestran completas: no hay una proyección oculta. Cada punto conserva su clase y su identidad. El ejemplo usa todos sus puntos para entrenamiento; ilustra representaciones, no estima generalización.'),
('El viaje del optimizador',vis.OPTIMIZACION,None,
'La curvatura es quince veces mayor en el segundo eje. Prueba tasas pequeñas y grandes y avanza paso a paso. Los parámetros se mantienen en un recuadro fijo: una trayectoria que sale de él puede estar divergiendo; el gráfico de pérdida lo confirma. Esta función no contiene ruido de minibatch.'),
('Ajustar y generalizar',vis.GENERALIZACION,None,
'Compara la curva verdadera, las observaciones y el modelo. Grado y regularización actúan de formas distintas. Aquí la validación orienta la selección; no es un test final independiente. Los puntos y errores son resultados calculados, con semilla fija.'),
('Una convolución por dentro',vis.CONVOLUCION,vis.CONVOLUCION_ANIMACION,
'La ventana recorre 36 posiciones. Observa los productos locales y su suma: cada uno corresponde exactamente a una celda del mapa de respuesta. La operación utiliza stride 1 y padding 0. Cambia el filtro para distinguir respuesta a orientación de simple suavizado.'),
('Atención, paso a paso',vis.ATENCION,None,
'Los vectores son didácticos y están escritos en la celda: no son embeddings aprendidos del castellano. La fila seleccionada permite seguir puntuaciones, softmax, productos por valores y suma final. La máscara causal deja disponible la posición actual y bloquea las posteriores. Variar temperatura aquí modifica la atención, no el sampling de un modelo del lenguaje.')]
for ch,(title,program,animation,explanation) in enumerate(visuals,1):
    cs=[md(f'# {title}\n\n**Explorador de Hespérides · Capítulo {ch}**\n\nAmpliación programada sobre los conceptos de los notebooks D2L de este capítulo.\n\n{explanation}\n\n![Ilustración conceptual](../recursos/ilustraciones/capitulo_{ch}.png)\n\n*Ilustración conceptual generada con ImageGen. Los resultados cuantitativos son los del código.*'),code(vis.COMUN),code(program)]
    if animation:cs.extend([md('## El proceso en movimiento\n\nPuedes reproducir, pausar y recorrer los fotogramas. La animación se genera a partir de los estados calculados arriba.'),code(animation)])
    cs.append(md('## Comprobación\n\nModifica un control cada vez y describe qué cambia y qué permanece constante. Compara tu observación con las preguntas del capítulo.'))
    cs.insert(3,md('## Vista de referencia\n\nEsta figura conserva el estado inicial también en una exportación sin kernel. Los controles anteriores se utilizan en Jupyter.'))
    cs.insert(4,code({1:'ver_capas(30)',2:'ver_optimizacion(.08,30)',3:'ver_generalizacion(5,.001)',4:"ver_convolucion(14, 'Borde vertical')",5:'ver_atencion(2,1.,True)'}[ch]))
    name=f'capitulo_{ch}/90_explorador_visual.ipynb'
    for i,c in enumerate(cs):c['id']=hashlib.sha256((name+str(i)).encode()).hexdigest()[:12]
    nb={'cells':cs,'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}}}
    (ROOT/name).write_text(json.dumps(nb,ensure_ascii=False,indent=1)+'\n')
(ROOT/'scripts/editorial/adaptaciones.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')


cs=[md('''# Un autoencoder por dentro

**Ampliación autoral de Hespérides · Capítulo 4**

Reutilizamos el patrón MLP de `locked/chapter_multilayer-perceptrons/mlp-implementation.ipynb`: capas afines y activaciones compuestas con `nn.Sequential`. La tarea de reconstrucción y los datos sintéticos son nuevos. No es una traducción de un supuesto notebook de autoencoders en `locked`.

Un encoder transforma 256 píxeles en dos números; un decoder intenta reconstruir la imagen a partir de ellos. La pérdida compara la reconstrucción con la entrada. Aquí la familia de imágenes depende principalmente de dos coordenadas —la posición de una mancha—, de modo que el cuello de botella tiene una justificación concreta. Esto no demuestra que dos números puedan preservar cualquier imagen.

Primero inspecciona una imagen y su reconstrucción. Después recorre el espacio latente. Lejos de los puntos vistos, el decoder extrapola sin garantía de producir una muestra válida. Las dos coordenadas aprendidas no tienen por qué coincidir con las coordenadas físicas ni tener una interpretación única.
'''),code(vis.COMUN),code(vis.AUTOENCODER),code('ver_reconstruccion(280)\nrecorrer_latente(0.,0.)'),md('''## Del autoencoder al VAE

Un autoencoder determinista optimiza reconstrucción. Un VAE introduce una distribución latente y un objetivo variacional que equilibra reconstrucción y divergencia respecto a una prior. El ejemplo anterior **no es un VAE**: no tiene muestreo mediante reparametrización ni término KL. La derivación de VAE queda vinculada a los apuntes de la sesión 4, no sustituida por esta demostración.

## Preguntas

1. ¿Por qué un espacio latente de dimensión dos puede funcionar para esta familia de imágenes y no para cualquier conjunto de fotografías?
2. ¿Por qué una reconstrucción convincente no demuestra que las coordenadas latentes sean interpretables o únicas?
3. ¿Qué riesgo tiene mover los controles lejos de los puntos latentes observados?
4. ¿Qué elementos faltan para que este modelo sea un VAE?
''')]
for i,c in enumerate(cs):c['id']=f'autoencoder-{i}'
(ROOT/'capitulo_4/91_autoencoder_visual.ipynb').write_text(json.dumps({'cells':cs,'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}}},ensure_ascii=False,indent=1)+'\n')

print('34 derivados, 5 exploradores y 1 autoencoder construidos.')
