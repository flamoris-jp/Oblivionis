import json, numpy as np
import session as S, sys
from music_field import MusicParams
kw = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
rows=[]
for seed in range(6):
    f, ev, notes, tr = S.run(seed, MusicParams(**kw))
    r = S.analyze(f, ev, notes, tr)
    C = r["C"]["voices_by_n"]
    rows.append(dict(seed=seed,
        A_voices=sorted(int(k) for k,v in r["A"]["voices_by_n"].items() if v>=10),
        B_voices=sorted(int(k) for k,v in r["B"]["voices_by_n"].items() if v>=10),
        C_voices=sorted(int(k) for k,v in C.items() if v>=10),
        C_straight=sum(v for k,v in C.items() if int(k) in (1,2,4,8,16)),
        C_triplet=sum(v for k,v in C.items() if int(k) in (3,6,12)),
        C_per4=r["C_notes_per_4bars"], last_bar=r["last_note_bar"],
        n5_n7_total=sum(r[s]["voices_by_n"].get(k,0) for s in "ABC" for k in (5,7)),
        n16_in_C=C.get(16,0),
        within30=[ (r[s]["straight_voices_vs_16th"] or {}).get("within_30ms") for s in "ABC"] + [ (r[s]["triplet_voices_vs_triplet"] or {}).get("within_30ms") for s in "BC"]))
for r in rows: print(r)
json.dump({"params": kw, "rows": rows}, open("music_seeds.json","w"), ensure_ascii=False, indent=1)
