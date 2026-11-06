#!/bin/bash
# Usage: ./deploy-apk.sh /absolute/path/to/app-release.apk 1.1
set -euo pipefail
cd -- "$(dirname -- "$0")"
exec python3 - "$@" <<'PY'
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import sys
import uuid

if len(sys.argv) != 3:
    sys.exit("Usage: ./deploy-apk.sh /absolute/path/to/app-release.apk VERSION")
apk = Path(sys.argv[1]).expanduser().resolve()
version = sys.argv[2]
if not apk.is_file() or apk.suffix.lower() != ".apk" or apk.stat().st_size == 0:
    sys.exit(f"Invalid APK: {apk}")
if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", version):
    sys.exit("VERSION must contain only dot-separated numbers, for example 1.1")

instance = "i-2zed0unqjrhigvdmif9m"
site = "https://smth.qteqpid.xyz/"
workbench = shutil.which("workbench") or str(Path.home() / ".local/bin/workbench")
if not Path(workbench).is_file():
    sys.exit("Workbench CLI not found; install it and sign in before deploying.")
digest = hashlib.sha256(apk.read_bytes()).hexdigest()
size = apk.stat().st_size
release = f"smth-{version}-{uuid.uuid4().hex}"
remote = f"/root/{release}.apk"
target = f"/var/www/smth/downloads/smth-{version}.apk"

print(f"Uploading signed APK: {size} bytes, sha256={digest}", flush=True)
subprocess.run([workbench, "upload", str(apk), remote, "--instance-id", instance], check=True)
remote_script = f'''
from pathlib import Path
import hashlib, os, shutil
source = Path({remote!r})
target = Path({target!r})
expected = {digest!r}
if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
    raise RuntimeError("Uploaded APK hash mismatch")
backup = Path("/var/www/smth/backups")
backup.mkdir(parents=True, exist_ok=True)
if target.exists():
    shutil.copy2(target, backup / (target.name + ".before-" + expected[:12]))
temporary = target.with_name(target.name + ".new")
shutil.copyfile(source, temporary)
os.chmod(temporary, 0o644)
os.replace(temporary, target)
print("Published " + str(target))
'''
command = "python3 - <<'SMTH_APK_DEPLOY_PY'\n" + remote_script + "\nSMTH_APK_DEPLOY_PY"
subprocess.run([workbench, "exec", "--instance-id", instance, "--timeout", "180", "--command", command], check=True)
url = f"{site}downloads/smth-{version}.apk?release={release}"
downloaded = subprocess.check_output(["curl", "--fail", "--silent", "--show-error", "--location",
                                      "--retry", "2", "--max-time", "90", url])
if len(downloaded) != size or hashlib.sha256(downloaded).hexdigest() != digest:
    sys.exit("Public APK verification failed; the server backup was retained")
print(f"Verified {url}: {size} bytes, sha256={digest}", flush=True)
PY
