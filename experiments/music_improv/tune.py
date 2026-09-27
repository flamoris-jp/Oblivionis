import sys, json, numpy as np
import session as S
from music_field import MusicParams
def stats(**kw):
    p = MusicParams(**kw)
    f, ev, notes, tr = S.run(0, p)
    r = S.analyze(f, ev, notes, tr)
    out = {k: (r[k]["notes_per_bar"], r[k]["voices_by_n"]) for k in "ABC"}
    return r, out
if __name__ == "__main__":
    kw = json.loads(sys.argv[1])
    r, out = stats(**kw)
    for k,v in out.items(): print(k, v)
    print("C/4bars", r["C_notes_per_4bars"], "last", r["last_note_bar"], "grid16", [r[k]["on_16th_grid"] for k in "ABC"], "grid3", [r[k]["on_triplet_grid"] for k in "ABC"])
    print("S", r["S_end_by_n"]); print("K", r["K_end_top"][:6])
