"""Read-only bounded pilot. Writes only the two authorized tickets."""
from pathlib import Path
import json, hashlib, datetime, os, csv
import pyarrow.parquet as pq
ROOT=Path('/nas/nas8/users/wzc/docs/maps')
T21=ROOT/'T21-cell-understanding-brief/tickets/01-benchmark-contract'
T23=ROOT/'T23-crossmodal-understanding-brief/tickets/01-benchmark-contract'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def save(p,rows):p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
# Exact prior scoped selection, not old HOLD fields and not a new admission decision.
a=Path('/nas/nas6/users/wzc/datasets/training-items-v1/t9-26-leakage-20261112/review3')
m=json.loads((a/'admission-manifest.json').read_text())
assert sha((a/'selection.parquet').read_bytes())==m['selection_sha256']
sels=pq.read_table(a/'selection.parquet',filters=[('dataset','=','chebi20'),('admission','=','ADMIT_SCOPED_TRAIN')]).to_pylist()
allowed={(r['item_id'],r['content_sha256']):r for r in sels}
rows=[]
for p in sorted((Path(m['base_directory'])/'chebi20').glob('*/items.parquet')):
 for batch in pq.ParquetFile(p).iter_batches(batch_size=128):
  for r in batch.to_pylist():
   key=(r['item_id'],r['content_sha256'])
   if key not in allowed:continue
   s=allowed[key];assert s['source_split']==r['source_split']=='train'
   assert sha(r['body'].encode())==r['content_sha256']
   smi=r['body'].split('SMILES: ',1)[1].split('\n',1)[0]
   desc=r['body'].split('Description: ',1)[1].rstrip('\n')
   from rdkit import Chem
   mol=Chem.MolFromSmiles(smi);assert mol is not None
   rows.append(dict(example_id='T23-pilot-'+str(len(rows)+1),item_kind='molecule_text_pair',input={'modality':'molecular_graph_serialized_SMILES','smiles':smi},output={'description':desc},scientific_capability='molecule-to-function-text alignment; not factual accuracy proof',source_item_id=r['item_id'],source_item_file=str(p),source_body_sha256=r['content_sha256'],source_body=r['body'],source_record={'l1_unit_id':r['l1_unit_id'],'l1_unit_row':r['l1_unit_row'],'l1_record_id':r['l1_record_id'],'source_field':r['source_field']},source_split='train',pilot_partition='research_train_example',admission='ADMIT_SCOPED_TRAIN',admission_scope=s['scope_id'],admission_manifest=str(a/'admission-manifest.json'),license=r['license_tag'],derived_check={'heavy_atom_count':mol.GetNumHeavyAtoms(),'method':'RDKit graph parsing; no new biological claim'},ddb_content_used=False))
   if len(rows)==3:break
  if len(rows)==3:break
 if len(rows)==3:break
assert len(rows)==3
save(T23/'examples.jsonl',rows)
# Existing experiment summaries are valid real source examples, NOT cell tensors.
b=Path('/nas/nas6/users/wzc/datasets/training-items-v1/t9-12-cell-agg-20261112')
licenses={r['item_id']:r for r in pq.read_table(b/'patch/license_retag_t913/items_all.parquet').to_pylist()}
cell=[]
for batch in pq.ParquetFile(b/'items/exp/items.parquet').iter_batches(batch_size=32):
 for r in batch.to_pylist():
  if r['mode']!='single_cell' or r['split']!='train':continue
  assert licenses[r['item_id']]['tag_class']=='CLEAN_ALLOW'
  assert sha(r['body'].encode())==r['content_sha256']
  refs=pq.read_table(b/'items/exp/facets.parquet',filters=[('item_id','=',r['item_id'])],columns=['facet_kind','refs_json','rule_id','state']).to_pylist()
  cell.append(dict(example_id='T21-pilot-'+str(len(cell)+1),item_kind='study_summary',input={'modality':'study_metadata_and_aggregate_text','body':r['body']},output=None,scientific_capability='study evidence organization only; no cell-type/disease target',study_id=r['anchor_value'],donor_id=None,cell_id=None,measurement_level='study_aggregate',observation_or_intervention='not_determined_from_summary',expression_vector_present=False,source_split=r['split'],pilot_partition='research_only_not_training',training_eligible=False,hold_reason='No per-cell tensor/donor mapping or selected benchmark study isolation; source train tag not enough',source_item_id=r['item_id'],source_body_sha256=r['content_sha256'],source_item_file=str(b/'items/exp/items.parquet'),source_refs=refs,license=licenses[r['item_id']]))
  if len(cell)==3:break
 if len(cell)==3:break
assert len(cell)==3
save(T21/'examples.jsonl',cell)
# Minimal executable field/negative checks, not a full-library audit.
def valid(x):
 if x['item_kind']=='study_summary':return not x['expression_vector_present'] and not x['training_eligible'] and x['cell_id'] is None and x['donor_id'] is None
 return x['source_split']=='train' and x['admission']=='ADMIT_SCOPED_TRAIN' and not x['ddb_content_used'] and sha(x['source_body'].encode())==x['source_body_sha256']
for p,rs in [(T21,cell),(T23,rows)]:
 assert all(valid(x) for x in rs)
 bad=json.loads(json.dumps(rs[0]))
 if p==T21:bad['training_eligible']=True
 else:bad['source_split']='test'
 assert not valid(bad)
 out=dict(checked_at=now,status='PASS_BOUNDED_ARTIFACT_CHECKS',examples=len(rs),unique_source_items=len({r['source_item_id'] for r in rs}),body_hash_checks=len(rs),field_checks_passed=True,negative_control_rejected=True,benchmark_scoring_run=False,model_training_run=False,global_audit_run=False,examples_sha256=sha((p/'examples.jsonl').read_bytes()),limitations=['Convenience sample of first qualifying records, not representative.','No model capability claim.','No cross-source equivalence or global contamination certification.'])
 if p==T21:
  out.update(expression_samples=0,study_summary_samples=len(rs),training_eligible_samples=0,blocker='Exact hPancreas/CINEMA payload absent; only prior http-error metadata present in bounded candidate paths.')
  out['bounded_path_checks']={}
  for n in ['hpancreas','hpancreas_figshare_v1','cinema_ot']:
   q=Path('/nas/nas6/users/wzc/datasets/_incoming-t14')/n
   out['bounded_path_checks'][str(q)]={'h5ad_files':[str(x) for x in q.glob('**/*.h5ad')],'errors':[{'file':str(x),'returncode':json.loads(x.read_text()).get('returncode'),'stderr':json.loads(x.read_text()).get('stderr')} for x in q.glob('*.http.json')]}
 else:out.update(scoped_train_samples=len(rs),selection_checksum_verified=True,selection_scope=m['scope_id'],scoped_pool_rows_observed=len(sels),drugdiscoverybench_prompt_answer_rubric_reads=0)
 dump(p/'verification.json',out)
 dump(p/'task.json',dict(task_id=('T21-01' if p==T21 else 'T23-01'),parent_task_id='benchmark-items-61b03a8e38',user_request='快速benchmark契约、真实独立小样与任务书草案；不训练不关闭ticket',project_path='/nas/nas8/users/wzc/docs',executor='Hermes focused subagent / gpt-6-astra',native_session_id=None,native_session_note='Runtime did not expose a native session ID; not invented.',execution={'mode':'local read-only small-sample inspection','pid_at_build':os.getpid(),'scheduler_run_id':None,'gpu_used':False},status='draft',assignee=None,reviewer=None,ticket_status='open',log_path=str(p/'verification.json'),updated_at=now,artifacts=['report.md','benchmark-contract.csv','brief-draft.md','task.json','examples.jsonl','verification.json'],scope='independent research pilot, no L1/L2/frozen release writes'))
 print(p.name,p.parent.parent.name,json.dumps(out,ensure_ascii=False))
