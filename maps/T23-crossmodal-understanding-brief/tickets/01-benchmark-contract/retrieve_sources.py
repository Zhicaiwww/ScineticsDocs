"""Bounded primary-source retrieval; no dataset tasks or test payloads."""
from pathlib import Path
import urllib.request, concurrent.futures, json, hashlib, subprocess
ROOT=Path('/nas/nas8/users/wzc/docs/maps')
S=Path('/nas/nas8/users/wzc/.hermes/skills/research/grounded-citations/scripts/sources.py')
sets={
'T21-cell-understanding-brief':[
('scgpt-data','https://raw.githubusercontent.com/bowang-lab/scGPT/main/data/README.md'),
('scgpt-paper','https://www.nature.com/articles/s41592-024-02201-0'),
('geneformer-paper','https://www.nature.com/articles/s41586-023-06139-9'),
('scgpt-figshare','https://api.figshare.com/v2/articles/24954519/versions/1'),
],
'T23-crossmodal-understanding-brief':[
('molt5-readme','https://raw.githubusercontent.com/blender-nlp/MolT5/main/README.md'),
('molt5-paper','https://arxiv.org/html/2204.11817v5'),
('moleculeqa-readme','https://raw.githubusercontent.com/hcaoaf/MoleculeQA/main/README.md'),
('ddb-readme','https://raw.githubusercontent.com/scaleapi/DrugDiscoveryBench/main/README.md'),
('biomatrix-readme','https://raw.githubusercontent.com/QizhiPei/BioMatrix/main/README.md'),
]}
def fetch(arg):
 name,slug,url=arg;p=ROOT/name/'tickets/01-benchmark-contract';(p/'sources').mkdir(exist_ok=True)
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as r:
   b=r.read(2500000);status=r.status
  (p/'sources'/f'{slug}.txt').write_bytes(b)
  return name,dict(slug=slug,url=url,status=status,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:return name,dict(slug=slug,url=url,error=str(e))
rows=list(concurrent.futures.ThreadPoolExecutor(6).map(fetch,[(n,s,u) for n,ss in sets.items() for s,u in ss]))
for name in sets:
 p=ROOT/name/'tickets/01-benchmark-contract'; rr=[r for n,r in rows if n==name]
 (p/'sources/retrieval.json').write_text(json.dumps(rr,indent=2))
 for r in rr:
  if 'error' not in r:subprocess.run(['python3',str(S),'--ledger',str(p/'sources/ledger.json'),'add',r['url'],'--title',r['slug']],check=True)
 print(name,json.dumps(rr))
