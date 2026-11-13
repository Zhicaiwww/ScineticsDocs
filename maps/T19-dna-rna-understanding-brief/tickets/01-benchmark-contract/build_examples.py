"""Bounded, deterministic research smoke data; no test labels read.
Run with the existing scinetics-data python and PYTHONDONTWRITEBYTECODE=1.
Only this ticket and T18-01 receive writes. Not a training admission script.
"""
import collections, hashlib, json, os, re, sys
from pathlib import Path
from datetime import datetime, timezone
import pyarrow.parquet as pq
ROOT=Path('/nas/nas8/users/wzc/docs')
P=ROOT/'maps/T18-protein-understanding-brief/tickets/01-benchmark-contract'
N=Path(__file__).resolve().parent
T9=ROOT/'maps/T9-item-card/tickets'
def sha(b): return hashlib.sha256(b).hexdigest()
def encoded(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def common(i,track,source,source_hash,locator,inputs,target,capability):
 return dict(id=i,track=track,capability_id=capability,inputs=inputs,target=target,source=str(source),source_sha256=source_hash,source_locator=locator,recipe_version='research-smoke-v1',split='research-smoke-not-training',provenance='source_fields_plus_explicit_rule',production_admission='NOT_REQUESTED',benchmark_answers_read=False)
def protein():
 p=T9/'08-build-wwpdb-structure-pack/samples/v1_3EFW.txt';raw=p.read_bytes();s=raw.decode()
 seq=re.search(r'<\|prot_aa_start\|>([A-Z]+)<\|prot_aa_end\|>',s).group(1)
 assert len(seq)==267
 seqrow=common('T18-01:3EFW:sequence','protein-sequence',p,sha(raw),'line8; entity1',{'sequence':seq,'alphabet':'amino_acid','pdb_id':'3EFW','entity_id':'1'},None,'P-EC-SEQ')
 seqrow.update(sample_role='input_schema_smoke',isolation='No EC/GO/function/name/keyword labels emitted; benchmark entity-membership unverified; excluded from supervised/training views')
 ca=[]
 for line in s.splitlines():
  f=line.split()
  if len(f)==6 and f[0]=='A' and f[2].isdigit(): ca.append(dict(chain=f[0],residue=f[1],label_seq_id=int(f[2]),xyz_A=[float(x) for x in f[3:]]))
 assert len(ca)>=2
 row=common('T18-01:3EFW:structure','protein-structure',p,sha(raw),'lines17-18; model1 chainA CA residues2-3',{'pdb_id':'3EFW','model':1,'atom':'CA','coordinates':ca[:2],'units':'angstrom','partial_structure':True},None,'P-EC-STRUCT')
 row.update(sample_role='input_schema_smoke',isolation=seqrow['isolation'],missing='Full atom graph and functional supervised labels absent; this is not a SaProt 3Di input')
 return [seqrow,row],dict(source_bytes=len(raw),source_records=1,sequence_rows=1,structure_rows=1,supervised_rows=0)
def nucleotide():
 base=Path('/nas/nas6/users/wzc/datasets/_incoming-t14/nt_revised_splice'); manifest=json.loads((base/'MANIFEST.json').read_text())
 meta=next(x for x in manifest['files'] if x['file']=='splice_sites_acceptors/train.parquet');p=base/meta['file']
 assert '/train.parquet' in str(p) and p.stat().st_size<=10000000
 actual=sha(p.read_bytes());assert actual==meta['sha256']
 batch=next(pq.ParquetFile(p).iter_batches(batch_size=2)); rows=[]
 for i,r in enumerate(batch.to_pylist()):
  assert set(r['sequence'].upper())<=set('ACGTN')
  x=common('T19-01:NT-acceptor:train:'+str(i),'DNA',p,actual,'parquet row '+str(i),{'sequence':r['sequence'],'name':r['name'],'task':r['task'],'alphabet':'DNA'},{'native_label':r['label'],'semantic_mapping':None},'D-SPLICE')
  x.update(source_split='train',source_url=meta['source_url'],source_revision=meta['source_commit'],sample_role='native_train_label_smoke',isolation='Native train only; no test rows/labels read. Prior T14 exact cross-split check reported zero; homology/RC not verified here; not admitted',label_semantics_status='UNVERIFIED: do not interpret 0/1 as acceptor/non-acceptor yet')
  rows.append(x)
 # Resolve the T9 short key through the small catalog, not a guessed padding rule.
 cat=Path('/nas/nas8/users/wzc/datasets/_catalog/l1-20261101/nas4-supplemental.parquet')
 cr=pq.read_table(cat,columns=['key','source_uri']).to_pylist();candidates=[x for x in cr if x['key'].startswith('9648aba423ff66ac')]
 assert len(candidates)==1
 rid=candidates[0]['key']+':000046195912'
 sys.path.insert(0,'/nas/nas8/users/wzc/code/scinetics-data/ops')
 from l1_v3 import reader
 r=reader.read_record(rid,dataset='nas4-supplemental',columns=None)
 raw=r['raw_record'];raw=raw.encode() if isinstance(raw,str) else raw
 lines=raw.decode().splitlines();seq=''.join(lines[1:]);assert seq==r['payload']['sequence'] and len(seq)==411
 protected=Path('/nas/nas6/users/wzc/datasets/training-items-v1/t9-07-gene-rna-20261111/protected/nuc_sha256_broad.json')
 b=protected.read_bytes();registry=json.loads(b)
 # Preserve registry structure, then inspect all hash strings (no answers).
 def hashes(x):
  if isinstance(x,dict):
   for k,v in x.items():
    if re.fullmatch('[0-9a-f]{64}',str(k)):yield k
    yield from hashes(v)
  elif isinstance(x,list):
   for v in x:yield from hashes(v)
  elif isinstance(x,str) and re.fullmatch('[0-9a-f]{64}',x):yield x
 hs=set(hashes(registry));assert hs
 variants={seq.upper(),seq.upper().replace('T','U'),seq.upper().translate(str.maketrans('ACGT','TGCA'))[::-1]}
 assert not any(sha(v.encode()) in hs for v in variants)
 x=common('T19-01:RNAcentral:URS000000033F','RNA',r['source_uri'],sha(raw),rid,{'sequence_as_stored':seq,'sequence_rna':seq.replace('T','U'),'normalization':'T-to-U only; original preserved','accession':'URS000000033F'},None,'R-NCRNA')
 x.update(sample_role='input_schema_smoke',source_dataset='RNAcentral27.0',source_split='T9 smoke row train; not benchmark train',isolation='Exact original/T-to-U/reverse-complement hashes absent from inherited T9 protected registry; no family/MRL/RBP target emitted; homolog exclusion not claimed',license='INTERNAL_NONCOMMERCIAL; upstream terms unverified')
 rows.append(x)
 return rows,dict(dna_rows=2,rna_rows=1,supervised_native_label_rows=2,semantic_label_mapping_verified=False,nt_train_sha256=actual,rna_raw_sha256=sha(raw),protected_registry_path=str(protected),protected_registry_sha256=sha(b),protected_hashes=len(hs),rna_protected_hits=0,test_rows_read=0,test_answers_read=0,source_record_id=rid)
def main():
 for out,fn in [(P,protein),(N,nucleotide)]:
  rows,checks=fn();again,checks2=fn();assert encoded(rows)==encoded(again) and checks==checks2
  assert len({r['id'] for r in rows})==len(rows)
  body=b''.join(encoded(r)+b'\n' for r in rows);(out/'examples.jsonl').write_bytes(body)
  loaded=[json.loads(x) for x in (out/'examples.jsonl').read_text().splitlines()];assert loaded==rows
  save(out/'verification.json',dict(at=datetime.now(timezone.utc).isoformat(),artifact_status='PARTIAL_RESEARCH_SMOKE',row_count=len(rows),examples_sha256=sha(body),deterministic_rebuild_equal=True,roundtrip_equal=True,checks=checks,benchmark_score_run=False,production_admission=False,executor_run_id=None,session_id=None,process_id=os.getpid(),host=os.uname().nodename,python=sys.executable))
  print(out.name,out.parent.parent.name,len(rows),sha(body),checks)
if __name__=='__main__':main()
