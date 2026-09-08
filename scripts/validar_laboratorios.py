"""Ejecuta cada notebook en un kernel nuevo y conserva evidencia local por hash."""
import concurrent.futures
import hashlib
import base64
import mimetypes
import re
import json
import os
from pathlib import Path
import time
import sys
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.editorial/ejecuciones';OUT.mkdir(parents=True,exist_ok=True)
def run(path):
    name=str(path.relative_to(ROOT));start=time.time()
    fingerprint=hashlib.sha256(path.read_bytes()+b''.join(f.read_bytes() for f in sorted((ROOT/'laboratorio').glob('*.py')))).hexdigest()
    report=OUT/(path.parent.name+'_'+path.stem+'.json')
    if report.exists():
        old=json.loads(report.read_text())
        if old.get('sha256')==fingerprint and old.get('status')=='passed':return old
    n=nbformat.read(path,as_version=4);nbformat.validate(n)
    result={'notebook':name,'sha256':fingerprint,'status':'failed'}
    try:
        NotebookClient(n,timeout=600,kernel_name='hesperides-lab',resources={'metadata':{'path':str(path.parent)}}).execute()
        result['status']='passed'
    except Exception as exc:
        result['error']=str(exc)[-8000:]
    result['seconds']=round(time.time()-start,2)
    result['code_cells']=sum(c.cell_type=='code' for c in n.cells)
    nbformat.write(n,OUT/(path.parent.name+'_'+path.name))
    if result['status']=='passed':
        html,_=HTMLExporter().from_notebook_node(n)
        def embed(m):
            target=(path.parent/m[1]).resolve()
            if not target.is_file():return m[0]
            mime=mimetypes.guess_type(str(target))[0] or 'application/octet-stream'
            return 'src="data:'+mime+';base64,'+base64.b64encode(target.read_bytes()).decode()+'"'
        html=re.sub(r'src="(\.\./[^"]+)"',embed,html)
        (OUT/(path.parent.name+'_'+path.stem+'.html')).write_text(html)
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(result['status'],name,result['seconds'],flush=True)
    return result
if __name__=='__main__':
    selected=sys.argv[1:]
    paths=[ROOT/p for p in selected] if selected else sorted(ROOT.glob('capitulo_*/*.ipynb'))
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,paths))
    (ROOT/'.editorial/validacion.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print('PASSED',sum(r['status']=='passed' for r in results),'/',len(results),flush=True)
