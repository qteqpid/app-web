#!/bin/bash
# Usage: ./deploy-infra.sh [--check]
# Deploys Nginx and systemd recovery configuration to the Qteqpid web server.
set -euo pipefail
cd -- "$(dirname -- "$0")"
exec python3 - "$@" <<'PY'
from pathlib import Path
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import uuid

if sys.argv[1:] not in ([], ["--check"]):
    sys.exit("Usage: ./deploy-infra.sh [--check]")

root = Path.cwd()
instance = "i-2zed0unqjrhigvdmif9m"
workbench = shutil.which("workbench") or str(Path.home() / ".local/bin/workbench")
files = {
    "nginx-pending.conf": root / "nginx-pending.conf",
    "nginx-recovery.conf": root / "infra/nginx-recovery.conf",
    "qteqpid-web-healthcheck": root / "infra/qteqpid-web-healthcheck",
    "qteqpid-web-healthcheck.service": root / "infra/qteqpid-web-healthcheck.service",
    "qteqpid-web-healthcheck.timer": root / "infra/qteqpid-web-healthcheck.timer",
}
for name, path in files.items():
    if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
        sys.exit(f"Invalid or empty infrastructure file: {name}")
nginx = files["nginx-pending.conf"].read_text()
required = ["resolver 127.0.0.53", "proxy_pass https://$telemetry_upstream", "server_name smth.qteqpid.xyz"]
if any(marker not in nginx for marker in required):
    sys.exit("Nginx configuration is missing a required resilience marker")
print(f"Validated {len(files)} infrastructure files.", flush=True)
if sys.argv[1:] == ["--check"]:
    sys.exit(0)
if not Path(workbench).is_file():
    sys.exit("Workbench CLI not found; install it and sign in before deploying.")

release = "qteqpid-infra-" + uuid.uuid4().hex
remote = "/root/" + release + ".tar.gz"
with tempfile.TemporaryDirectory(prefix="qteqpid-infra-") as directory:
    archive = Path(directory) / (release + ".tar.gz")
    with tarfile.open(archive, "w:gz", format=tarfile.USTAR_FORMAT) as bundle:
        for name, path in files.items():
            bundle.add(path, arcname=name)
    subprocess.run([workbench, "upload", str(archive), remote, "--instance-id", instance], check=True)

remote_script = r'''
from pathlib import Path
import os, shutil, subprocess, tarfile

archive = Path(ARCHIVE)
release = RELEASE
stage = Path("/root") / (release + "-stage")
backup = Path("/etc/qteqpid-deploy-backups") / release
stage.mkdir(exist_ok=False)
backup.mkdir(parents=True, exist_ok=False)
with tarfile.open(archive) as bundle:
    for member in bundle.getmembers():
        if member.name.startswith("/") or ".." in Path(member.name).parts or not member.isfile():
            raise RuntimeError("Invalid archive entry")
    bundle.extractall(stage)

targets = {
    "nginx-pending.conf": (Path("/etc/nginx/sites-enabled/smth-pending.conf"), 0o644),
    "nginx-recovery.conf": (Path("/etc/systemd/system/nginx.service.d/recovery.conf"), 0o644),
    "qteqpid-web-healthcheck": (Path("/usr/local/sbin/qteqpid-web-healthcheck"), 0o755),
    "qteqpid-web-healthcheck.service": (Path("/etc/systemd/system/qteqpid-web-healthcheck.service"), 0o644),
    "qteqpid-web-healthcheck.timer": (Path("/etc/systemd/system/qteqpid-web-healthcheck.timer"), 0o644),
}
changed = []
try:
    for name, (target, mode) in targets.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.copy2(target, backup / name)
        temporary = target.with_name(target.name + ".new")
        shutil.copyfile(stage / name, temporary)
        os.chmod(temporary, mode)
        os.replace(temporary, target)
        changed.append((name, target))
    subprocess.run(["nginx", "-t"], check=True)
except Exception:
    for name, target in reversed(changed):
        saved = backup / name
        if saved.exists():
            shutil.copy2(saved, target)
        else:
            target.unlink(missing_ok=True)
    raise

subprocess.run(["systemctl", "daemon-reload"], check=True)
subprocess.run(["systemctl", "reload", "nginx"], check=True)
subprocess.run(["systemctl", "enable", "--now", "qteqpid-web-healthcheck.timer"], check=True)
subprocess.run(["systemctl", "start", "qteqpid-web-healthcheck.service"], check=True)
subprocess.run(["systemctl", "is-active", "--quiet", "nginx"], check=True)
print("Published infrastructure. Backup: " + str(backup), flush=True)
'''.replace("ARCHIVE", repr(remote)).replace("RELEASE", repr(release))
command = "python3 - <<'QTEQPID_INFRA_PY'\n" + remote_script + "\nQTEQPID_INFRA_PY"
subprocess.run([workbench, "exec", "--instance-id", instance, "--timeout", "180", "--command", command], check=True)

for url in ("https://qteqpid.xyz/", "https://apps.qteqpid.xyz/", "https://smth.qteqpid.xyz/"):
    subprocess.run(["curl", "--fail", "--silent", "--show-error", "--location", "--retry", "2",
                    "--max-time", "30", url], stdout=subprocess.DEVNULL, check=True)
print("Infrastructure deployed; all public sites verified.", flush=True)
PY
