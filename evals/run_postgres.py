"""Run examples against a new private Unix-socket PostgreSQL cluster."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlencode

for executable in ("initdb", "pg_ctl", "createdb"):
    if not shutil.which(executable):
        raise SystemExit(f"Missing {executable}; install PostgreSQL to run these examples")

with tempfile.TemporaryDirectory(prefix="skill-pg-", dir="/tmp") as temporary:
    root = Path(temporary)
    data = root / "data"
    socket = root / "socket"
    socket.mkdir(mode=0o700)
    (root / "owned-eval-cluster").touch()
    subprocess.run(["initdb", "-D", str(data), "-A", "trust", "-U", "skill_eval"], check=True, stdout=subprocess.DEVNULL)
    started = False
    try:
        subprocess.run(["pg_ctl", "-D", str(data), "-l", str(root / "server.log"), "-o", f"-F -k {socket} -p 55439 -c listen_addresses=''", "-w", "start"], check=True)
        started = True
        subprocess.run(["createdb", "-h", str(socket), "-p", "55439", "-U", "skill_eval", "skill_eval"], check=True)
        environment = os.environ.copy()
        environment["SKILL_EVAL_OWNED_DIR"] = str(root)
        environment["SKILL_EVAL_DATABASE_URL"] = "postgresql+asyncpg://skill_eval@/skill_eval?" + urlencode({"host": str(socket), "port": "55439"})
        result = subprocess.run([sys.executable, "-m", "pytest", "-q", "test_examples.py"], cwd=Path(__file__).parent, env=environment)
    finally:
        if started:
            subprocess.run(["pg_ctl", "-D", str(data), "-m", "fast", "-w", "stop"], check=True)
    raise SystemExit(result.returncode)
