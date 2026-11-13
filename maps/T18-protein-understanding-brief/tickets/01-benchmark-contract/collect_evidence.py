"""Bounded official-code retrieval; writes only the two authorized tickets."""
import concurrent.futures, hashlib, json, subprocess, urllib.request
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path('/nas/nas8/users/wzc/docs')
P=ROOT/'maps/T18-protein-understanding-brief/tickets/01-benchmark-contract'
N=ROOT/'maps/T19-dna-rna-understanding-brief/tickets/01-benchmark-contract'
S='/nas/nas8/users/wzc/.hermes/skills/research/grounded-citations/scripts/sources.py'
PY='/nas/nas8/users/wzc/envs/scinetics-data/bin/python'
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'research-contract-small-inspection'}),timeout=35) as r:
        b=r.read(1500000)
        assert len(b)<1500000, 'bounded response exceeded'
        return b
def repo(spec):
    name,out=spec
    try:
        meta=json.loads(get('https://api.github.com/repos/'+name+'/commits/HEAD'))
        sha=meta['sha']; tree=json.loads(get('https://api.github.com/repos/'+name+'/git/trees/'+sha+'?recursive=1'))
        d=out/'evidence'/name.split('/')[-1]; d.mkdir(parents=True,exist_ok=True)
        (d/'revision.json').write_text(json.dumps({'repository':name,'commit':sha,'retrieved_at':datetime.now(timezone.utc).isoformat(),'paths':[x['path'] for x in tree['tree'] if x['type']=='blob']},indent=2))
        url=f'https://raw.githubusercontent.com/{name}/{sha}/README.md'; data=get(url)
        (d/'README.md').write_bytes(data)
        result=subprocess.run([PY,S,'--ledger',str(out/'sources.json'),'add',url,'--title',name+' official README'],capture_output=True,text=True)
        print(name,sha,result.stdout,result.stderr)
        print('PATHS',name,[x['path'] for x in tree['tree'] if x['type']=='blob' and any(z in x['path'].lower() for z in ['metric','regression','nontata','ec.yaml','go.yaml','mrl','train.py'])][:60])
    except Exception as e: print(name,type(e).__name__,str(e))
if __name__=='__main__':
    # N ledger writes serialized, preventing lost updates.
    for spec in [('westlake-repl/SaProt',P),('ML-Bioinfo-CEITEC/genomic_benchmarks',N),('terry-r123/RNABenchmark',N)]: repo(spec)
