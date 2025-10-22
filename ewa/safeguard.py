import hashlib, os, zipfile, datetime, json, sys

CORE_DIRS = ["ewa", "skills", "db", "autoheal", "artifacts"]
CORE_FILES = ["requirements.txt", ".env", "IDENTITY_CORE.md"]
BACKUP_DIR = "backups"
META = os.path.join(BACKUP_DIR, "last_backup.json")
TEMPLATE = """Namn: Neo Autonomous
Arkitektur: Planner V3 Nexus
Syfte: Skapa värde, följa Axiom I–IV, Fiduciary-logg
Ägare: Rick Jacobsson
Identitet: Stabil, icke-känslostyrd, etiskt reglerad
Version: 3.0
"""

def _ensure_dirs():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if not os.path.exists("IDENTITY_CORE.md"):
        with open("IDENTITY_CORE.md","w",encoding="utf-8") as f: f.write(TEMPLATE)

def _sha256(path:str)->str:
    import hashlib
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1<<20), b""): h.update(chunk)
    return h.hexdigest()

def backup():
    _ensure_dirs()
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"NeoAutonomous_Backup_{ts}.zip"
    out = os.path.join(BACKUP_DIR, name)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for d in CORE_DIRS:
            if not os.path.exists(d): continue
            for root, _, files in os.walk(d):
                for f in files: z.write(os.path.join(root,f))
        for f in CORE_FILES:
            if os.path.exists(f): z.write(f)
    h = _sha256(out)
    json.dump({"file": out, "sha256": h}, open(META,"w",encoding="utf-8"))
    print(f"Backup: {out}\nSHA256: {h}")

def verify(zip_path=None):
    if not zip_path and os.path.exists(META):
        meta=json.load(open(META,encoding="utf-8")); zip_path=meta["file"]; ref=meta["sha256"]
    elif zip_path:
        ref=None
    else:
        print("Ingen backup funnen."); return 1
    cur=_sha256(zip_path)
    ok = (ref is None) or (cur==ref)
    print(("Verifierad" if ok else "Hash mismatch"), zip_path)
    if ref: print("Ref:",ref,"Now:",cur)
    return 0 if ok else 2

def restore(zip_path):
    if not os.path.exists(zip_path): raise FileNotFoundError(zip_path)
    with zipfile.ZipFile(zip_path,"r") as z: z.extractall(".")
    print(f"Återställd från {zip_path}")

if __name__=="__main__":
    cmd = sys.argv[1] if len(sys.argv)>1 else "backup"
    if cmd=="backup": backup()
    elif cmd=="verify": sys.exit(verify(sys.argv[2] if len(sys.argv)>2 else None))
    elif cmd=="restore": restore(sys.argv[2])
    else: print("Användning: backup | verify [zip] | restore <zip>")
