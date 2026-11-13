# Tokenizer inventory (scripted)

The script and raw output are `../inventory.py`, `../inventory-output.jsonl`, and the bounded path list `../tokenizer-paths.txt`. Values below come from actual JSON files; repeated paths with the same SHA are one artifact family.

| Family / representative path | SHA-256 | base vocab | added | added ID range | status |
|---|---|---:|---:|---|---|
| Qwen3.5 smoke/native family (`experiments/configured_training/qwen35_0_8b_fp8_smoke/model/tokenizer.json`) | `06b9509352d2af50381ab2247e083b80d32d5c0aba91c272ca9ff729b6a0e523` | 248044 | 33 | 248044–248076 | current scinetics smoke artifact |
| scientific 264k family (`fp8-performance-node16.../model/tokenizer.json`) | `30ee2b55134f78f551430528da6583f975bb5f59cc92f4e89ef831fa1a08576c` | 248044 | 16428 | 248044–264471 | historical scientific candidate |
| v0/2B scientific family (`yjx/.../distributed-smoke-output-v2/tokenizer.json`) | `a317c62f56c56b5b9659b8aba34822825437430d9e81a819cbff32fc7d6fb05d` | 248044 | 16421 | 248044–264464 | historical v0-aligned family |
| yjx v1 tokenizer (`RSI-BioMatrix-Qwen35-2B-v1/tokenizer/tokenizer.json`) | `9e26f03914f488566ce96c5b19110e4ae6e1422bc3d9a927e475d7f9eaba9aa4` | 248044 | 16387 | 248044–264430 | historical v1 |
| Qwen3.5-2B base (`models/Qwen3.5-2B-Base/tokenizer.json`) | `fe000e3ed39ed12b8d2481d527d44f93c65d37e87645d2dcc80d1bf9d50d2927` | 248044 | 22 | 248044–248065 | base, no scientific expansion |
| BioMatrix 1.7B base | `072d8c63700dabfae748c64dd88fdd218cd756a1220a19d60aa1277434fd7c73` | 151643 | 16379 | 151643–168021 | incompatible base family |
| Geo2Seq QA tokenizer | `fc3b8b3b3f71bafc6384a33ae44771717cdbe1f8e58499186c7ae6578138efd5` | 248044 | 32159 | 248044–280202 | incompatible added-token semantics |

The JSON `model.vocab` contains the base BPE map; `added_tokens` are separate records, so total ID capacity is `max(base IDs, added IDs)+1`, not `len(model.vocab)+len(added_tokens)`. The current scinetics smoke tokenizer therefore has ID capacity 248077 despite 248044 base entries.

Known v0 boundary IDs from `models/v0/architecture.md` §4A: `mol_3d_start/end` 264424/264425, `prot_aa_start/end` 264426/264427, `prot_3d_start/end` 264428/264429, `dna_seq_start/end` 264431/264432, `rna_seq_start/end` 264448/264449. These IDs cannot be interpreted against the 248077 smoke family without the corresponding scientific tokenizer artifact.

Compatibility graph: Qwen base → smoke family is append-only for its 33 reserved IDs; Qwen base → scientific 264k families is not interchangeable without the exact append receipt and model embedding alignment; 151k and 248k base families are incompatible. No tokenizer file was modified. Pretokenize-regex comparison remains pending because the v0 reference tokenizer path is not present in the bounded current inventory.
