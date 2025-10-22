#!/bin/bash
ZIP="${1:-backups/$(ls -1 backups/NeoAutonomous_Backup_*.zip 2>/dev/null | tail -n1)}"
echo "Verifying..."; python ewa/safeguard.py verify "$ZIP" || true
if [ -n "$ZIP" ]; then echo "Restoring..."; python ewa/safeguard.py restore "$ZIP"; fi
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
uvicorn ewa.server:app --host 127.0.0.1 --port 8123

