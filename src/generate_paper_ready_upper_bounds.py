"""Solver-free paper-ready upper-bound regeneration."""
import csv,json
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1]; C=R/"experiments/baseline_n11_17/constructive_upper_bounds"; O=R/"experiments/baseline_n11_17/paper_ready_upper_bounds"; D=R/"docs/n11_17/paper_ready_upper_bound_tables.md"; B=O/"backup_20260716T220534Z"
def rd(p):
 with p.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def wr(p,x,fields=None):
 fields=fields or list(x[0]); f=p.open("w",newline="",encoding="utf-8"); w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(x); f.close()
der=json.loads((C/"derivation_trees.json").read_text()); by=defaultdict(list)
for i,d in der.items():by[(d["kind"],int(d["n"]),int(d["t"]),int(d["depth"]))].append((i,d))
rows=[]
for kind in "UV":
 for x in rd(C/f"upper_bounds_{kind}.csv"):
  n,t,u=int(x["n"]),int(x["t"]),int(x["best_upper_bound"]); l=int(x["lower_bound_if_known"]) if x["lower_bound_if_known"] else None; g=None if l is None else u-l
  ds=by[(kind,n,t,u)]; pref=next(((i,d) for i,d in ds if d["rule"]==x["primary_rule"] and d.get("primary_source","")==x["primary_source"]),ds[0] if ds else ("",{})); did,pd=pref
  vf=kind=="V" and t==2 and 2<=n<=17 and u in {1,3,5,6,8}
  exact=g==0
  caveat=("V(2,2^k) formula needs paper-ready citation or included proof" if vf else ("no explicit verified network artifact for primary derivation" if x["network_artifact_available"].lower()!="true" else ""))
  rows.append({"kind":kind,"n":n,"t":t,"best_upper_bound":u,"exact_status":"exact" if exact else "upper_bound_only","lower_bound_if_known":"" if l is None else l,"lower_bound_provenance":x.get("lower_bound_provenance",""),"current_gap_if_known":"" if g is None else g,"primary_rule":x["primary_rule"],"primary_source":x["primary_source"],"primary_provenance_type":x["provenance_type"],"secondary_sources":";".join(i for i,_ in ds if i!=did),"derivation_tree_id":did,"network_artifact_available":x["network_artifact_available"].lower(),"generated_network_verified":str(x["verifier_status"] in {"VERIFIED","VERIFIED_SAT"}).lower(),"verifier_status":x["verifier_status"],"sorting_fallback_used":str(x["primary_rule"]=="SORTING_FALLBACK").lower(),"citation_status":"citation TODO" if vf else ("paper-ready" if exact else "local-note-only"),"caveats":caveat})
F=list(rows[0])
for k in "UV":wr(O/f"paper_ready_upper_bounds_{k}.csv",[x for x in rows if x["kind"]==k],F)
wr(O/"provenance_audit.csv",rows,F); wr(O/"artifact_verified_entries.csv",[x for x in rows if x["network_artifact_available"]=="true"],F); wr(O/"theorem_derived_entries.csv",[x for x in rows if x["primary_provenance_type"]=="THEOREM_DERIVED"],F); wr(O/"sorting_fallback_entries.csv",[x for x in rows if x["sorting_fallback_used"]=="true"],F)
src=[{"source_path":"V(2,2^k) formula","status":"citation TODO","source_kind":"theorem formula","entries_contributed":"V(2,n), n<=17","citation_readiness":"citation TODO","caveats":"needs paper-ready citation or included proof"},{"source_path":"experiments/baseline_n10/decisions/V_t2_n10/depth_05/","status":"exists","source_kind":"computational lower bound","entries_contributed":"VDepth(2,10)>=6 and n-monotonic consequences","citation_readiness":"computational-artifact","caveats":""},{"source_path":"experiments/baseline_n10/decisions/V_t3_n10/depth_06/","status":"exists","source_kind":"verified witness","entries_contributed":"VDepth(2,10)<=6 because V3 implies V2","citation_readiness":"computational-artifact","caveats":""},{"source_path":"docs/n11_17/constructive_upper_bound_closure.md","status":"exists","source_kind":"generated closure","entries_contributed":"all","citation_readiness":"local-note-only","caveats":""}]
wr(O/"source_audit.csv",src)
front=[]
for x in rows:
 n,t,u=int(x["n"]),int(x["t"]),int(x["best_upper_bound"])
 if n<11 or t in {1,n} or x["exact_status"]=="exact":continue
 l=int(x["lower_bound_if_known"]) if x["lower_bound_if_known"]!="" else None; g=None if l is None else u-l; p=R/f"experiments/baseline_n11_17/decisions/{x['kind']}_t{t}_n{n}/depth_{u-1:02d}"
 front.append({"priority_score":100+(20 if g==1 else 0)+(10 if t<=4 else 0),"kind":x["kind"],"n":n,"t":t,"best_upper_bound_D":u,"strongest_known_lower_bound_L":"" if l is None else l,"gap_D_minus_L":"" if g is None else g,"candidate_UNSAT_depth":u-1,"existing_artifact_at_depth_D_minus_1":"exists" if p.exists() else "none","artifact_path":str(p.relative_to(R)) if p.exists() else "","reason_for_priority":f"gap={g if g is not None else 'unknown'}; constructive upper bound","suggested_next_action":"Audit evidence before any solver experiment."})
front.sort(key=lambda x:(-x["priority_score"],x["n"],x["kind"],x["t"])); wr(O/"frontier_for_lower_bounds.csv",front)
def tex(k):
 z=[x for x in rows if x["kind"]==k]; a=["% generated",r"\begin{tabular}{r|l}",r"$n$ & bounds \\ \hline"]
 for n in range(10,18):a.append(f"{n} & "+", ".join(str(x["best_upper_bound"]) for x in z if int(x["n"])==n)+r" \\")
 return "\n".join(a+[r"\end{tabular}",""])
(O/"paper_table_U.tex").write_text(tex("U"));(O/"paper_table_V.tex").write_text(tex("V"));(O/"paper_text_snippets.tex").write_text("% citation TODO\n"+r"$\mathrm{VDepth}(2,n)=6$ for $10\le n\le16$."+"\n")
(O/"paper_ready_upper_bounds_all.json").write_text(json.dumps({"generated_at":datetime.now(timezone.utc).isoformat(),"entries":rows},indent=2)+"\n")
oldv={(int(x["n"]),int(x["t"])):int(x["best_upper_bound"]) for x in rd(B/"paper_ready_upper_bounds_V.csv")}; oldu={(int(x["n"]),int(x["t"])):int(x["best_upper_bound"]) for x in rd(B/"paper_ready_upper_bounds_U.csv")}
chg=[{"kind":"V","n":n,"t":2,"before":oldv[(n,2)],"after":next(int(x["best_upper_bound"]) for x in rows if x["kind"]=="V" and int(x["n"])==n and int(x["t"])==2)} for n in range(11,17)]
uc=[{"n":int(x["n"]),"t":int(x["t"]),"before":oldu[(int(x["n"]),int(x["t"]))],"after":int(x["best_upper_bound"])} for x in rows if x["kind"]=="U" and oldu[(int(x["n"]),int(x["t"]))]!=int(x["best_upper_bound"])]
exact=all(x["exact_status"]=="exact" and int(x["best_upper_bound"])==int(x["lower_bound_if_known"])==6 and x["lower_bound_provenance"] for x in rows if x["kind"]=="V" and int(x["t"])==2 and 10<=int(x["n"])<=16)
removed=all(not(x["kind"]=="V" and int(x["t"])==2 and 11<=int(x["n"])<=16 and int(x["candidate_UNSAT_depth"])==6) for x in front)
audit={"entry_count":len(rows),"frontier_count":len(front),"formula_citation_status":"citation TODO","v2_10_16_exact":exact,"removed_v2_11_16_depth6":removed,"u_table_change_count":len(uc),"derivation_tree_parse":True,"no_u_duality_for_v":all(not(d["kind"]=="V" and d["rule"]=="U_DUALITY") for d in der.values()),"no_v_t_monotonicity_for_u":all(not(d["kind"]=="U" and d["rule"]=="V_T_MONOTONICITY") for d in der.values())}
(O/"audit_summary.json").write_text(json.dumps(audit,indent=2)+"\n"); summary={"formula_added":True,"citation_status":"citation TODO","v2_changes":chg,"v2_n17":next(int(x["best_upper_bound"]) for x in rows if x["kind"]=="V" and int(x["n"])==17 and int(x["t"])==2),"exact_10_16":exact,"frontier_removed":removed,"u_table_changes":uc,"backup_timestamp":"20260716T220534Z"};(O/"v2_formula_regeneration_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
v=[x for x in rows if x["kind"]=="V" and int(x["t"])==2 and 10<=int(x["n"])<=17]
D.write_text("""# Paper-ready upper-bound tables

## Scope

Solver-free regeneration; no clingo or SAT/UNSAT experiment was run.

## V(2,n) formula correction

The previous closure omitted `VDepth(2,2^k)=k+ceil(log2 k)`. Power-of-two facts through n=32 and padding/restriction are now included. Citation status: **citation TODO**.

| n | upper | lower | status |
|---:|---:|---:|---|
"""+"\n".join(f"| {x['n']} | {x['best_upper_bound']} | {x['lower_bound_if_known']} | {x['exact_status']} |" for x in v)+f"""

For 10<=n<=16 the upper provenance is `V2_POWER_OF_TWO_FORMULA` plus `PADDING_RESTRICTION`; the lower provenance is `VDepth(2,10)=6` plus `N_MONOTONICITY_LOWER_FROM_N10`. Thus these entries are exact.

## Updated source audit

- V(2,2^k) formula: citation TODO; a paper-ready citation or proof is required.
- V(2,10) lower bound: saved depth-5 UNSAT.
- V(2,10) upper bound: verified V(3,10) depth-6 witness, also valid for V(2,10).

## Updated frontier

V(2,11..16) candidate depth 6 entries were removed.

## U-table impact

V_IMPLIES_U was recomputed; U changes relative to backup: {len(uc)}.

## Audit and caveats

- exact 10..16: {exact}
- requested removals: {removed}
- no U-duality for V: {audit['no_u_duality_for_v']}
- no V t-monotonicity for U: {audit['no_v_t_monotonicity_for_u']}
- Upper bounds and exact values remain distinct.
- Formula citation remains TODO.
""")
for p in O.glob("*.json"):json.loads(p.read_text())
for p in O.glob("*.csv"):rd(p)
print(json.dumps(summary,indent=2))
