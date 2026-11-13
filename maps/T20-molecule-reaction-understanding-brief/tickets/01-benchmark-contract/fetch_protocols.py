import urllib.request, json, base64, hashlib, subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path('/nas/nas8/users/wzc/docs/maps')
DIRS={k:ROOT/v/'tickets/01-benchmark-contract' for k,v in [('mol','T20-molecule-reaction-understanding-brief'),('mat','T22-materials-understanding-brief')]}
S='/nas/nas8/users/wzc/.hermes/skills/research/grounded-citations/scripts/sources.py'
def fetch(spec):
    k,repo,path,name=spec
    url=f'https://api.github.com/repos/{repo}/contents/{path}'
    try:
        d=json.load(urllib.request.urlopen(url,timeout=40)); b=base64.b64decode(d['content'])
        dest=DIRS[k]/'evidence'/name; dest.parent.mkdir(exist_ok=True); dest.write_bytes(b)
        return k,{'url':d['html_url'],'api_url':url,'git_blob_sha':d['sha'],'sha256':hashlib.sha256(b).hexdigest(),'local_path':str(dest),'status':'retrieved'}
    except Exception as e: return k,{'api_url':url,'status':'failed','error':str(e)}
specs=[('mol','OSU-NLP-Group/LLM4Chem','README.md','llm4chem-readme.md'),('mol','OSU-NLP-Group/LLM4Chem','compute_metrics.py','compute_metrics.py'),('mol','ChemFoundationModels/ChemLLMBench','README.md','chemllm-readme.md'),('mol','ChemFoundationModels/ChemLLMBench','data/Readme.md','chemllm-data.md'),('mat','materialsproject/matbench','README.md','matbench-readme.md'),('mat','materialsproject/matbench','matbench/task.py','matbench-task.py'),('mat','materialsproject/matbench','matbench/matbench_v0.1_dataset_metadata.json','matbench-metadata.json')]
results=list(ThreadPoolExecutor(5).map(fetch,specs))
for k,directory in DIRS.items():
    records=[v for key,v in results if key==k]
    (directory/'source-retrieval.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    for r in records:
        if r['status']=='retrieved':
            subprocess.run(['/nas/nas8/users/wzc/envs/scinetics-data/bin/python',S,'--ledger',str(directory/'sources-ledger.json'),'add',r['url']],check=True)
    print(k,json.dumps(records,ensure_ascii=False))
