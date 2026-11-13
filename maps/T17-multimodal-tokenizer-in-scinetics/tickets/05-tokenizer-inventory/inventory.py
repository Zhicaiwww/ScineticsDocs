#!/usr/bin/env python3
import hashlib, json, os
from pathlib import Path

ROOTS = [Path('/nas/nas8/users/wzc/docs'), Path('/nas/nas8/users/wzc/experiments'), Path('/nas/nas8/users/yjx')]
seen = set()
for root in ROOTS:
    if not root.exists(): continue
    for p in root.rglob('tokenizer.json'):
        if p in seen: continue
        seen.add(p)
        try:
            d=json.loads(p.read_text()); model=d.get('model',{}); vocab=model.get('vocab',{}); added=d.get('added_tokens',[])
            print(json.dumps({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'base_bpe_entries':len(vocab),'added_tokens':len(added),'total_vocab':len(vocab),'min_id':min(vocab.values()) if vocab else None,'max_id':max(vocab.values()) if vocab else None,'added_min_id':min((x.get('id') for x in added),default=None),'added_max_id':max((x.get('id') for x in added),default=None)},ensure_ascii=False))
        except Exception as e:
            print(json.dumps({'path':str(p),'error':type(e).__name__+': '+str(e)}))
