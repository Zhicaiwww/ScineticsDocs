"""Small direct-L1 property examples, not an official-train membership claim."""
import json,csv,hashlib,os
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import pyarrow.parquet as pq
from rdkit import Chem,rdBase
from rdkit.Chem.Scaffolds import MurckoScaffold
OUT=Path(__file__).resolve().parent
BASE=Path('/nas/nas6/users/wzc/datasets/l1-v3/f1/source-42887feb0c12')
TEST=Path('/nas/nas7/AI4AI/benchmarks/scientific-v1/prepared/SMolInstruct/raw/test')
SPECS={'esol':('9bcd27e10bede260e1fc','measured log solubility in mols per litre','log10(mol/L)','Compound ID'), 'lipo':('a69f48d636e04f671897','exp','logD','CMPD_CHEMBLID')}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def keys(s):
    m=Chem.MolFromSmiles(s.strip());assert m is not None,'unparseable SMILES'
    Chem.RemoveStereochemistry(m)
    return Chem.MolToSmiles(m),MurckoScaffold.MurckoScaffoldSmiles(mol=m)
def main():
    testkeys=set();scaffolds=set();frozen=[]
    for p in [TEST/'property_prediction-esol.jsonl', TEST/'property_prediction-lipo.jsonl']:
        n=0
        for line in p.open():
            r=json.loads(line); k,scaf=keys(r['input']);testkeys.add(k);scaffolds.add(scaf);n+=1
        frozen.append({'path':str(p),'sha256':sha(p),'rows':n,'read_fields':['input'],'answers_exported':False})
    examples=[];counts={}
    for name,(unitid,target,unit,idcol) in SPECS.items():
        root=BASE/unitid;md=json.loads((root/'unit.json').read_text());original=Path(md['shell']['consts']['source_uri']);native=list(csv.DictReader(original.open())) if original.exists() else None
        p=next((root/'data').glob('*.parquet'));t=pq.read_table(p,columns=['src_smiles','src_'+target,'src_'+idcol]);n=0;scanned=0;rejected=0
        for pos,r in enumerate(t.to_pylist()):
            scanned+=1;s=r['src_smiles'];k,scaf=keys(s)
            if k in testkeys or scaf in scaffolds:rejected+=1;continue
            if native is not None: assert native[pos]['smiles']==s and float(native[pos][target])==float(r['src_'+target])
            examples.append({'item_id':f'moleculenet:{name}:{unitid}:{pos}','track':'small_molecule','benchmark':f'SMolInstruct-property_prediction-{name}','purpose':'research_candidate_only','training_ready':False,'split':'source_pool_minus_fixed_property_test_entities_and_scaffolds','official_train_membership':'unknown; no train/validation manifest available locally','input':{'smiles':s,'canonical_no_stereo_smiles':k},'output':{'property':target,'value':float(r['src_'+target]),'unit':unit},'conditions':{'pH':None,'temperature_K':None,'missing_reason':'not provided at row level; no inferred default'},'provenance':{'dataset':'source-42887feb0c12','source_version':md['shell']['consts']['source_version'],'source_id':r['src_'+idcol],'l1_path':str(p),'l1_sha256':sha(p),'physical_row':pos,'native_path':str(original),'native_sha256':sha(original) if native is not None else None,'native_row_equal':True if native is not None else None,'native_locator_available':native is not None},'join_policy':{'actual_join':'L1 unit/ordinal + source ID; original CSV locator retained but only compared when present','cross_source_join_executed':False,'future_key':'canonical parent + stereochemistry + assay/property + unit/conditions; ChEMBL ID/CID mapping must have evidence','l2_required_now':False},'isolation':{'canonical_no_stereo_test_hit':False,'murcko_scaffold_test_hit':False,'protected_scope':'all two selected local SMolInstruct property test input files; hashes in verification.json','remaining':'validation and non-property evaluation scopes not cleared; no production training'}})
            n+=1
            if n==3:break
        counts[name]={'sample_count':n,'scanned_until_sample':scanned,'rejected_test_entity_or_scaffold':rejected}
        assert n==3,(name,n)
    (OUT/'examples.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in examples))
    back=[json.loads(s) for s in (OUT/'examples.jsonl').read_text().splitlines()]
    assert len(back)==6 and all(keys(x['input']['smiles'])[0] not in testkeys and keys(x['input']['smiles'])[1] not in scaffolds for x in back)
    result={'status':'PASS_SCOPED_RESEARCH_CANDIDATE','updated_at':datetime.now(timezone.utc).isoformat(),'process_id':os.getpid(),'samples':len(back),'by_track':{'small_molecule':len(back),'reaction':0},'by_endpoint':counts,'native_parity_count':sum(x['provenance']['native_row_equal'] is True for x in back),'l1_readback_count':len(back),'rdkit_version':rdBase.rdkitVersion,'protected_inputs':frozen,'protected_molecule_keys':len(testkeys),'protected_scaffold_keys':len(scaffolds),'examples_sha256':sha(OUT/'examples.jsonl'),'production_admission':False,'blocked':['official molecule train/validation membership not established; these are not benchmark-train examples','reaction HTE native training rows plus fixed test membership/condition mapping not located; no invented yield','no general test-contamination claim outside the two selected property tasks']}
    (OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
