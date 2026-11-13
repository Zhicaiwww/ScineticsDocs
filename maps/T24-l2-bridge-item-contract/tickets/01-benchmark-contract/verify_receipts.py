#!/usr/bin/env python3
"""Read only existing receipts; write this ticket's verification, never source data."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
checks = []
sources = []

def check(name, condition):
    checks.append({"name": name, "pass": bool(condition)})

def load(relative):
    p = ROOT / relative
    raw = p.read_bytes()
    sources.append({"path": relative, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
    return json.loads(raw)

with (HERE / "bridge-contract.csv").open(newline="") as f:
    rows = list(csv.DictReader(f))
check("nine_unique_contract_rows", len(rows) == 9 and len({r["contract_id"] for r in rows}) == 9)
check("six_modalities", {r["modality"] for r in rows} == {"protein", "dna", "rna", "molecule", "cell", "materials"})
check("three_bridge_paths", sum(r["contract_id"].startswith("B-") for r in rows) == 3)
check("three_routes", {r["route"] for r in rows} == {"l1_direct", "existing_l2", "local_join"})
check("all_contract_cells_nonempty", all(all(v for v in r.values()) for r in rows))
check("evidence_files_exist", all((ROOT / r["evidence_path"]).is_file() for r in rows))
base = "maps/T9-item-card/tickets/"
go = load(base + "10-protein-bridge-facets/results/bridge_check.json")["family-full-v1/prot_go__uniprot_reference"]
check("GO_receipt_count_conservation", go["sample"] == sum(go["counts"].values()))
check("GO_unique_and_isoform_hold", go["counts"].get("unique:same_anchor") == 198867 and go["counts"].get("HOLD_ISOFORM_REFERENCE_NOT_RESOLVED:ISO") == 1133)
prot = load(base + "10-protein-bridge-facets/results/replay_swissprot.json")
check("protein_receipt_100_and_fragments", prot["sampled"] == prot["ok"] == 100 and not prot["bad"] and prot["frag_checked"] == 2468 and prot["frag_bad"] == 0)
rna = load(base + "17-gene-rna-real-merging/results/verify_links_f.json")
check("RNA_receipt_400_equal", rna["precision_rows_sampled"] == rna["precision_sequences_equal"] == 400 and not rna["precision_failures"])
check("RNA_held_difference", rna["hit_pairs_spill"] - rna["link_pairs"] == rna["hit_pairs_not_in_links_total"] == 16 and rna["hit_pairs_not_in_links_and_not_held"] == 0 and rna["link_pairs_not_in_spill_hits"] == 0)
gene = load(base + "17-gene-rna-real-merging/results/replay_gene3.json")
check("gene_receipt_520_equal", gene["n"] == gene["equal"] == 520 and gene["unequal"] == gene["errors"] == 0)
rel = load(base + "19-relation-measurement-facets/results/replay_released_n400_zeroledger.json")
check("BDB_receipt_400_items_3667_lines", rel["bdb_measure"]["n"] == 400 and rel["bdb_measure"]["lines"] == 3667 and rel["bdb_measure"]["mismatches"] == 0)
check("empty_aseq_not_claimed_as_replay", rel["aseq"]["n"] == rel["aseq"]["population"] == 0 and bool(rel["aseq"]["status"]))
# Policy probes are metadata-only rule tests, NOT fabricated scientific records.
def usage(states, match_status):
    if any(s in {"test", "eval_reserved", "HOLD", "REJECT"} for s in states):
        return "withheld"
    if not states or any(s in {"unknown", "dev"} for s in states):
        return "inspection_only"
    if match_status in {"ambiguous", "conflict", "unmatched", "connectivity_only"}:
        return "candidate_context_only"
    return "source_attributed_research_only"
check("protection_candidate_union", usage(["train", "test"], "ambiguous") == "withheld")
check("unknown_never_train", usage(["unknown"], "exact_key_unique") == "inspection_only")
check("ambiguity_no_unique_answer", usage(["train"], "ambiguous") == "candidate_context_only")
check("exact_key_not_production", usage(["train"], "exact_key_unique") == "source_attributed_research_only")
check("existing_denial_preserved", usage(["train", "REJECT"], "exact_key_unique") == "withheld")
# Pin implementation/design evidence without importing or executing upstream scripts.
for relative in [
    "data/v1/02-scientific-evidence/l2.md",
    "data/v1/layers.md",
    "data/v1/03-tasks-samples/training-item.md",
    "data/v1/reports/20261108-bridge-expansion.md",
    base + "19-relation-measurement-facets/code/r3_resolve.py",
    base + "19-relation-measurement-facets/code/relib.py",
    base + "17-gene-rna-real-merging/code/verify_links.py",
]:
    raw = (ROOT / relative).read_bytes()
    sources.append({"path": relative, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
artifacts = []
for name in ["report.md", "bridge-contract.csv", "brief-draft.md", "verify_receipts.py"]:
    raw = (HERE / name).read_bytes()
    artifacts.append({"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
result = {"status": "PASS" if all(x["pass"] for x in checks) else "FAIL", "checked_at": datetime.now(timezone.utc).isoformat(), "scope": "existing_local_receipts_and_contract_only", "checks": checks, "sources": sources, "artifacts": artifacts, "counts": {"contract_rows": len(rows), "modalities": len({r["modality"] for r in rows}), "receipt_bridge_paths": 3, "checks": len(checks), "new_items": 0}, "limits": ["No new L1 replay or scientific identity validation", "Metadata policy probes are not source samples", "No source writes, training, full scans or publication", "No production admission; ticket remains open"]}
(HERE / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"status": result["status"], "counts": result["counts"], "failed": [x["name"] for x in checks if not x["pass"]]}, ensure_ascii=False))
raise SystemExit(0 if result["status"] == "PASS" else 1)
