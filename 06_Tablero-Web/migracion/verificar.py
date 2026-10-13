#!/usr/bin/env python3
"""Compara el CSV del Sheet (misma regla acortar() de la web) con lo que devuelve
tablero_publico() en Supabase. Debe dar cero diferencias antes del cambio (Fase 4)."""
import csv, io, json, os, re, sys, urllib.request, unicodedata

CSV = sys.argv[1] if len(sys.argv) > 1 else "https://docs.google.com/spreadsheets/d/e/2PACX-1vSDP5V6nI_cacFyy5hmmh_Lqy92K1ioHRhLdib97-tL1m8udoiykjhjN1peCk7ZsQ/pub?gid=540644959&single=true&output=csv"
URL = os.environ.get("SUPABASE_URL", "https://oyvrdwkoorkidoadnzmc.supabase.co")
ANON = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")

def acortar(t):
    t = re.sub(r"\s+", " ", (t or "").strip())
    if re.fullmatch(r"(?i)reservad[oa]", t): return "Reservado"
    if not t or "*" in t: return t
    p = t.split(" ")
    cap = lambda w: w[:1].upper() + w[1:].lower()
    a = cap(p[0][:3])
    b = " " + p[1][:1].upper() + "." if len(p) > 1 else ""
    return a + "***" + b

def leer_csv():
    with urllib.request.urlopen(CSV, timeout=30) as r:
        rows = list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))
    esperado = {}
    for f in rows:
        n = (f.get("NUMERO") or "").strip()
        if not re.fullmatch(r"\d{3}", n): continue
        est = (f.get("ESTADO") or "LIBRE").strip().upper()
        nom = (f.get("NOMBRE_PUBLICO") or "").strip()
        if est == "PAGADO": esperado[n] = ("PAGADO", acortar(nom))
        elif est == "APARTADO": esperado[n] = ("APARTADO", "")
    return esperado

def leer_db():
    req = urllib.request.Request(URL.rstrip("/") + "/rest/v1/rpc/tablero_publico", method="POST",
        data=b"{}", headers={"apikey": ANON, "Authorization": "Bearer " + ANON, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    return {row[0]: (row[1], row[2]) for row in data["v"]}

def main():
    e = leer_csv(); d = leer_db()
    difs = []
    todos = set(e) | set(d)
    for n in sorted(todos):
        if e.get(n, ("LIBRE", "")) != d.get(n, ("LIBRE", "")):
            difs.append((n, e.get(n), d.get(n)))
    print(f"CSV: {sum(1 for v in e.values() if v[0]=='PAGADO')} pagados, {sum(1 for v in e.values() if v[0]=='APARTADO')} apartados")
    print(f"BD : {sum(1 for v in d.values() if v[0]=='PAGADO')} pagados, {sum(1 for v in d.values() if v[0]=='APARTADO')} apartados")
    print(f"Diferencias: {len(difs)}")
    for d_ in difs[:20]: print(" ", d_)
    sys.exit(0 if not difs else 1)

if __name__ == "__main__": main()
