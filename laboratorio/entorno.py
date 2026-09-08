"""Compatibilidad y modo CPU. El algoritmo de cada ejemplo vive en el notebook."""
from pathlib import Path
import hashlib
import os
import random
import numpy as np
import requests
import torch
import torchvision
from matplotlib import pyplot as plt
from torch.utils.data import DataLoader, Subset
from . import d2l_original as d2l

RAIZ = Path(__file__).resolve().parents[1]
RAPIDO = os.environ.get('HESPERIDES_COMPLETO', '0') != '1'

def configurar(semilla=42):
    import truststore
    truststore.inject_into_ssl()  # Usa los certificados del sistema, con verificación TLS.
    random.seed(semilla)
    np.random.seed(semilla)
    torch.manual_seed(semilla)
    torch.set_num_threads(2)
    plt.rcParams.update({'figure.dpi': 110, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.grid': True,
                         'grid.alpha': .18, 'axes.prop_cycle': plt.cycler(color=['#087E8B', '#D99B18', '#775DA6', '#D65F59'])})
    print(f'PyTorch {torch.__version__} · CPU · semilla {semilla} · modo {"rápido" if RAPIDO else "completo"}')

def epocas(n):
    return min(n, 3) if RAPIDO else n

def show_images(imgs, num_rows, num_cols, titles=None, scale=1.5):
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(num_cols*scale, num_rows*scale), squeeze=False)
    for i, (ax, img) in enumerate(zip(axes.flat, imgs)):
        if torch.is_tensor(img):img = img.detach().cpu().numpy()
        ax.imshow(img, cmap='gray' if np.asarray(img).ndim == 2 else None)
        if titles is not None:ax.set_title(titles[i])
    for ax in axes.flat:ax.axis('off')
    fig.tight_layout()
    return axes

def download(url, folder=None, sha1_hash=None):
    if not url.startswith('http'):url, sha1_hash = d2l.DATA_HUB[url]
    url = url.replace('http://', 'https://')
    folder = Path(folder) if folder else RAIZ/'data'
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder/url.rsplit('/',1)[-1]
    if dest.exists() and (not sha1_hash or hashlib.sha1(dest.read_bytes()).hexdigest() == sha1_hash):return str(dest)
    r = requests.get(url, timeout=120);r.raise_for_status()
    if sha1_hash and hashlib.sha1(r.content).hexdigest() != sha1_hash:raise ValueError(f'Hash incorrecto: {url}')
    dest.write_bytes(r.content)
    return str(dest)

_BaseData = d2l.DataModule.__init__
def _data_init(self, root=None, num_workers=0):
    _BaseData(self, str(root or RAIZ/'data'), num_workers)

# Mirror HTTPS mantenido por los autores del conjunto Fashion-MNIST.
torchvision.datasets.FashionMNIST.mirrors = ['https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/']
d2l.DataModule.__init__ = _data_init
d2l.DATA_URL = d2l.DATA_URL.replace('http://','https://')
d2l.DATA_HUB.update({k:(u.replace('http://','https://'),h) for k,(u,h) in d2l.DATA_HUB.items()})
d2l.download = download
d2l.show_images = show_images
d2l.get_dataloader_workers = lambda: 0

_Trainer = d2l.Trainer
class Trainer(_Trainer):
    def __init__(self, max_epochs, num_gpus=0, gradient_clip_val=0):
        super().__init__(epocas(max_epochs), num_gpus=0, gradient_clip_val=gradient_clip_val)
    def prepare_data(self, data):
        super().prepare_data(data)
        if RAPIDO:
            for attr, limit in [('train_dataloader',1024), ('val_dataloader',256)]:
                loader = getattr(self, attr)
                if loader is not None and len(loader.dataset)>limit:
                    ids = torch.randperm(len(loader.dataset),generator=torch.Generator().manual_seed(42))[:limit]
                    setattr(self,attr,DataLoader(Subset(loader.dataset, ids.tolist()),batch_size=min(loader.batch_size,128),shuffle=attr.startswith('train'),num_workers=0))
            self.num_train_batches = len(self.train_dataloader)
            self.num_val_batches = len(self.val_dataloader) if self.val_dataloader is not None else 0
        print(f'Entrenamiento: {self.max_epochs} épocas; {len(self.train_dataloader.dataset)} ejemplos; {self.num_val_batches} lotes de validación')
d2l.Trainer = Trainer

def separar_validacion(train):
    """Reserva el 10% del entrenamiento oficial; no utiliza el test para seleccionar."""
    ids = torch.randperm(len(train), generator=torch.Generator().manual_seed(42)).tolist()
    corte = int(.9*len(ids))
    return Subset(train, ids[:corte]), Subset(train, ids[corte:])

_Fashion = d2l.FashionMNIST
class FashionMNIST(_Fashion):
    def __init__(self, batch_size=64, resize=(28,28)):
        super().__init__(batch_size, resize)
        self.test = self.val
        self.train, self.val = separar_validacion(self.train)
    def text_labels(self, indices):
        labels = ['camiseta','pantalón','jersey','vestido','abrigo','sandalia','camisa','zapatilla','bolso','botín']
        return [labels[int(i)] for i in indices]
d2l.FashionMNIST = FashionMNIST
d2l.separar_validacion = separar_validacion

def limitar_carga(train_iter, val_iter, num_epochs):
    if not RAPIDO:return train_iter,val_iter,num_epochs
    def corto(loader,limite,shuffle):
        ids=torch.randperm(len(loader.dataset),generator=torch.Generator().manual_seed(42))[:limite].tolist()
        return DataLoader(Subset(loader.dataset,ids),batch_size=min(loader.batch_size,16),shuffle=shuffle,num_workers=0)
    return corto(train_iter,128,True),corto(val_iter,64,False),min(num_epochs,3)

d2l.limitar_carga=limitar_carga
_train_ch13=d2l.train_ch13
def train_ch13(net,train_iter,test_iter,loss,trainer,num_epochs,devices=None):
    train_iter,test_iter,num_epochs=limitar_carga(train_iter,test_iter,num_epochs)
    print(f'Demostración CNN: {len(train_iter.dataset)} ejemplos; {num_epochs} épocas')
    return _train_ch13(net,train_iter,test_iter,loss,trainer,num_epochs,devices or [torch.device('cpu')])
d2l.train_ch13=train_ch13
