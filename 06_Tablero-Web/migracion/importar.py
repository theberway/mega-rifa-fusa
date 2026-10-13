#!/usr/bin/env python3
"""Carga el tablero público (CSV del Sheet) en la copia de Supabase, en modo ensayo.

Opcional: si existen `06_Tablero-Web/_privado/compradores.csv` y `pagos.csv`, los lee para
enriquecer los nombres completos y la plata, sin publicar nada de ahí. Los CSV privados
nunca se suben al repositorio (están en `.gitignore`).

Uso:
    python3 importar.py [URL_CSV]        # por defecto, el CSV publicado
    SUPABASE_URL=... SUPABASE_SERVICE_KEY=... python3 importar.py
"""
import csv, io, json, os, re, sys, urllib.request

CSV = (sys.argv[1] if len(sys.argv) > 1 else
       "https://docs.google.com/spreadsheets/d/e/2PACX-1vSDP5V6nI_cacFyy5hmmh_Lqy92K1ioHRhLdib97-tL1m8udoiykjhjN1peCk7ZsQ/pub?gid=540644959&single=true&output=csv")
URL = os.environ.get("SUPABASE_URL", "https://oyvrdwkoorkidoadnzmc.supabase.co")
KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")

PRIV = os.path.join(os.path.dirname(__file__), "..", "_privado")
PRIV_COMPRADORES = os.path.join(PRIV, "compradores.csv")

def leer_csv_url(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))

def normalizar(s):
    # misma regla que rifa.normalizar en SQL
    import unicodedata
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s).strip().upper()

def armar_payload(filas, enriquecer):
    out = []
    for f in filas:
        n = (f.get("NUMERO") or "").strip()
        if not re.fullmatch(r"\d{3}", n): continue
        est = (f.get("ESTADO") or "").strip().upper()
        if est not in ("PAGADO", "APARTADO"): continue
        nombre = (f.get("NOMBRE_PUBLICO") or "").strip()
        hora = (f.get("HORA_APARTADO") or "").strip()
        # «FALTA LA FECHA» / «FALTA LA HORA» no son fechas válidas: se dejan vacío para marcar decisión 51
        if hora.upper().startswith("FALTA"): hora = ""
        if not re.search(r"\d{4}-\d{2}-\d{2}", hora) and not re.search(r"\d{1,2}/\d{1,2}", hora):
            # horas como «12:00» no sirven; se pierden a propósito (decisión 51)
            hora_iso = ""
        else:
            hora_iso = hora  # Postgres acepta varios formatos; si no, pasa a null por el EXCEPTION
        vend = (f.get("VENDEDOR") or "").strip()
        nota = (f.get("NOTA") or "").strip()
        completo = enriquecer.get(n) or nombre  # si tenemos el nombre completo privado, lo usamos
        out.append({"n": n, "estado": est, "hora": hora_iso, "vend": vend, "nombre": completo, "nota": nota})
    return out

def leer_compradores_privado():
    if not os.path.exists(PRIV_COMPRADORES): return {}
    r = {}
    with open(PRIV_COMPRADORES, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            n = (row.get("NUMERO") or "").strip()
            nombre = (row.get("NOMBRE_COMPLETO") or "").strip()
            if re.fullmatch(r"\d{3}", n) and nombre:
                r[n] = nombre
    return r

def rpc(path, payload):
    import urllib.request
    if not KEY:
        print("Falta SUPABASE_SERVICE_KEY. Para la Fase 1 pégalo:\n"
              "  export SUPABASE_SERVICE_KEY=...\n"
              "lo encuentras en Project settings → API → service_role (SECRETA).")
        sys.exit(2)
    req = urllib.request.Request(
        URL.rstrip("/") + "/rest/v1/rpc/" + path, method="POST",
        data=json.dumps(payload).encode("utf-8"),
        headers={"apikey": KEY, "Authorization": "Bearer " + KEY,
                 "Content-Type": "application/json", "Prefer": "params=single-object"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

def main():
    filas = leer_csv_url(CSV)
    enriquecer = leer_compradores_privado()
    pay = armar_payload(filas, enriquecer)
    # cargar_copia vive en el esquema `rifa`, no expuesto por la API: lo llamamos como RPC a través
    # de una función puente pública que crearemos (ver 006). Por ahora se puede llamar manualmente
    # desde el panel SQL de Supabase con:
    #   select rifa.cargar_copia('[...]'::jsonb);
    print(f"Payload listo: {len(pay)} filas no libres de un total de {len(filas)}.")
    print(f"Enriquecidas con nombre completo privado: {sum(1 for p in pay if p['n'] in enriquecer)}")
    salida = os.path.join(os.path.dirname(__file__), "payload.json")
    with open(salida, "w", encoding="utf-8") as f: json.dump(pay, f, ensure_ascii=False, indent=0)
    print(f"Payload guardado en {salida}. Súbelo con: select rifa.cargar_copia(:p);")

if __name__ == "__main__":
    main()
