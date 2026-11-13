"""Independent file/row readback of the two isolated ticket deliverables."""
import csv,hashlib,json,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
import pyarrow.parquet as pq
ROOT=Path('/nas/nas8/users/wzc/docs/maps')
S='/nas/nas8/users/wzc/.hermes/skills/research/grounded-citations/scripts/sources.py'
for name,expected,contracts in [('T20-molecule-reaction-understanding-brief',6,4),('T22-materials-understanding-brief',9,3)]:
    p=ROOT/name/'tickets/01-benchmark-contract'
    subprocess.run(['/nas/nas8/users/wzc/envs/scinetics-data/bin/python',S,'--ledger',str(p/'sources-ledger.json'),'render','--replace-in',str(p/'report.md')],check=True)
    subprocess.run(['/nas/nas8/users/wzc/envs/scinetics-data/bin/python',S,'--ledger',str(p/'sources-ledger.json'),'verify',str(p/'report.md')],check=True)
    rows=[json.loads(l) for l in (p/'examples.jsonl').read_text().splitlines()]
    assert len(rows)==expected and len({r['item_id'] for r in rows})==expected
    assert len(list(csv.DictReader((p/'benchmark-contract.csv').open())))==contracts
    checks=[]
    for r in rows:
        prov=r['provenance'];source=Path(prov['l1_path']);assert source.is_file()
        assert hashlib.sha256(source.read_bytes()).hexdigest()==prov['l1_sha256']
        raw=pq.read_table(source).slice(prov['physical_row'],1).to_pylist()[0]
        assert float(raw['src_'+r['output']['property']])==r['output']['value']
        if r['track']=='materials':
            key=next(iter(r['input']));v=raw['src_'+key];v=json.loads(v) if key=='structure' else v
            assert v==r['input'][key];assert raw['src_source_index']==prov['source_index']
            folds=json.loads(Path(prov['protocol_path']).read_text())['splits'][r['benchmark']][r['fold']]
            assert prov['mbid'] in folds['train'] and prov['mbid'] not in folds['test']
            assert r['fold']=='fold_0'
        else:assert raw['src_smiles']==r['input']['smiles']
        assert r['training_ready'] is False
        checks.append({'item_id':r['item_id'],'source_fields_equal':True})
    required=['report.md','benchmark-contract.csv','brief-draft.md','task.json','examples.jsonl','verification.json']
    assert all((p/f).is_file() for f in required)
    assert 'status: open' in (p/'ticket.md').read_text()
    result={'status':'PASS','at':datetime.now(timezone.utc).isoformat(),'process_id':os.getpid(),'sample_count':len(rows),'contract_count':contracts,'l1_independent_readback':checks,'required_files_present':required,'ticket_status':'open','source_checks_do_not_imply_production_admission':True}
    (p/'delivery-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(name, json.dumps({'samples':len(rows),'contracts':contracts,'readback':'PASS','citations':'PASS','ticket':'open'}))
