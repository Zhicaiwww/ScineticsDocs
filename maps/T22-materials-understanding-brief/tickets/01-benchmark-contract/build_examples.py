"""Read-only L1 sample: three tasks, fold_0 only; never a global train pool."""
import json, hashlib, gzip, re, os
from pathlib import Path
from fractions import Fraction
from collections import Counter
from datetime import datetime, timezone
import pyarrow.parquet as pq
OUT=Path(__file__).resolve().parent
BASE=Path('/nas/nas6/users/wzc/datasets')
PROTOCOL=BASE/'_incoming-t14/matbench_v0.1_protocol/matbench_v0.1_validation.json'
SPECS={'matbench_steels':('composition','yield strength','MPa'), 'matbench_expt_gap':('composition','gap expt','eV'), 'matbench_dielectric':('structure','n','unitless')}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pack(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def composition(inp,kind):
    if kind=='structure':
        c=Counter()
        for site in inp['sites']:
            for sp in site['species']: c[sp['element']]+=Fraction(str(sp['occu']))
    else:
        tok=re.findall(r'[A-Z][a-z]?|\d*\.\d+|\d+|[()]',inp)
        assert ''.join(tok)==inp,('unsupported composition',inp)
        def parse(i=0):
            c=Counter()
            while i<len(tok) and tok[i]!=')':
                if tok[i]=='(':
                    sub,i=parse(i+1);assert tok[i]==')';i+=1
                else:
                    assert re.fullmatch('[A-Z][a-z]?',tok[i]);sub={tok[i]:Fraction(1)};i+=1
                n=Fraction(1)
                if i<len(tok) and re.fullmatch(r'\d*\.?\d+',tok[i]): n=Fraction(tok[i]);i+=1
                for e,a in sub.items():c[e]+=a*n
            return c,i
        c,i=parse();assert i==len(tok)
    total=sum(c.values());return '|'.join(f'{e}:{v/total}' for e,v in sorted(c.items()))

def main():
    protocol=json.loads(PROTOCOL.read_text())['splits']; inputs={}; blocked=set(); meta={}; issues=[]
    for name,(kind,target,unit) in SPECS.items():
        root=BASE/name/'l1/20261112-t14'; p=next((root/'units').glob('*/data/*.parquet'))
        rows=pq.read_table(p,columns=['src_source_index','src_'+kind]).to_pylist(); n=len(rows)
        folds=protocol[name]['fold_0']; train=set(folds['train']);test=set(folds['test']);assert not train&test
        indexed=[]
        for pos,r in enumerate(rows):
            ix=r['src_source_index']; mbid=name.replace('matbench','mb').replace('_','-')+'-'+str(ix+1).zfill(len(str(n)))
            inp=json.loads(r['src_structure']) if kind=='structure' else r['src_composition']
            try: key=composition(inp,kind)
            except Exception as e: issues.append({'dataset':name,'index':ix,'error':str(e)});continue
            indexed.append((pos,ix,mbid,inp,key))
            if mbid in test:blocked.add(key)
        assert {x[2] for x in indexed}==train|test, 'all identities must resolve before sampling'
        inputs[name]=indexed
        meta[name]={'l1_path':str(p),'l1_sha256':sha(p),'rows':n,'fold':'fold_0','train_val_ids':len(train),'test_ids':len(test),'id_overlap':len(train&test)}
    examples=[]
    for name,(kind,target,unit) in SPECS.items():
        p=Path(meta[name]['l1_path']); native=BASE/'_incoming-t14'/name/(name+'.json.gz')
        original=json.loads(gzip.decompress(native.read_bytes())); columns=original['columns']; labels=pq.read_table(p,columns=['src_'+target]).column(0).to_pylist()
        n=0
        for pos,ix,mbid,inp,key in inputs[name]:
            if mbid not in set(protocol[name]['fold_0']['train']) or key in blocked:continue
            native_pos=original['index'].index(ix);native_input=original['data'][native_pos][columns.index(kind)];native_target=original['data'][native_pos][columns.index(target)]
            assert inp==native_input and labels[pos]==native_target
            examples.append({'item_id':f'{name}:fold_0:{mbid}','track':'materials','benchmark':name,'protocol':'matbench_v0.1','fold':'fold_0','split':'train_val','purpose':'research_sample_only','training_ready':False,'input':{kind:inp},'composition_key':key,'structure_unit':'angstrom; fractional abc' if kind=='structure' else None,'output':{'property':target,'value':native_target,'unit':unit},'conditions':{'temperature_K':None,'pressure_Pa':None,'measurement_or_calculation_settings':None,'missing_reason':'not provided in this native benchmark row; no defaults inferred'},'provenance':{'l1_path':str(p),'l1_sha256':meta[name]['l1_sha256'],'physical_row':pos,'source_index':ix,'mbid':mbid,'native_path':str(native),'native_sha256':sha(native),'protocol_path':str(PROTOCOL),'protocol_sha256':sha(PROTOCOL),'input_target_native_equal':True},'join_policy':{'actual_join':'L1 source_index -> native index -> official mbid -> fold','cross_source_join_executed':False,'future_key':'source/version + composition + structure fingerprint + property + conditions; formula is not structure identity','l2_required_now':False},'isolation':{'own_fold_train_val':True,'selected_three_tasks_fold0_test_composition_match':False,'all_folds_training_claim':False,'unselected_tasks_and_structure_equivalence':'unknown; not admitted for joint 13-task training'}})
            n+=1
            if n==3:break
        assert n==3,(name,n)
    text=''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in examples); (OUT/'examples.jsonl').write_text(text)
    back=[json.loads(s) for s in (OUT/'examples.jsonl').read_text().splitlines()];assert len(back)==9 and len({x['item_id'] for x in back})==9
    assert all(x['fold']=='fold_0' and x['composition_key'] not in blocked for x in back)
    result={'status':'PASS_SCOPED_LOCAL_SAMPLE','updated_at':datetime.now(timezone.utc).isoformat(),'process_id':os.getpid(),'samples':len(back),'by_dataset':dict(Counter(x['benchmark'] for x in back)),'fold':'fold_0','source_input_target_equal':len(back),'test_identity_scope':'three selected tasks, fold_0, source index/mbid and normalized composition; no test labels exported','test_composition_keys':len(blocked),'parse_issues':issues,'inputs':meta,'protocol_sha256':sha(PROTOCOL),'examples_sha256':sha(OUT/'examples.jsonl'),'production_admission':False,'unverified':['other folds and other 10 tasks not joint-training cleared','same-composition polymorph/structure equivalence not inferred','conditions absent','scorer/model not run']}
    (OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
