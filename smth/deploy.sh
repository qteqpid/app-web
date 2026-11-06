#!/bin/bash
# Usage: ./deploy.sh [--check]
# Requires an authenticated Workbench CLI. No credentials are stored here.
set -euo pipefail
cd -- "$(dirname -- "$0")"
exec python3 - "$@" <<'PY'
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import uuid
import xml.etree.ElementTree as ET

if sys.argv[1:] not in ([], ['--check']):
    sys.exit('Usage: ./deploy.sh [--check]')
root = Path.cwd()
instance = 'i-2zed0unqjrhigvdmif9m'
site = 'https://smth.qteqpid.xyz/'
workbench = shutil.which('workbench') or str(Path.home() / '.local/bin/workbench')
files = sorted(set(['index.html', 'changelog.html', 'privacy.html', 'robots.txt',
                    'sitemap.xml', 'llms.txt'] +
                   [p.relative_to(root).as_posix() for p in (root / 'assets').rglob('*') if p.is_file()] +
                   [p.name for p in root.glob('*.txt')]))
for name in files:
    path = root / name
    if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
        sys.exit(f'Invalid or empty deployment file: {name}')
ET.parse(root / 'sitemap.xml')
if 'Sitemap: https://smth.qteqpid.xyz/sitemap.xml' not in (root / 'robots.txt').read_text():
    sys.exit('robots.txt is missing the sitemap declaration')
print(f'Validated {len(files)} public files. Nginx configuration, scripts and APKs are excluded.', flush=True)
if sys.argv[1:] == ['--check']:
    sys.exit(0)
if not Path(workbench).is_file():
    sys.exit('Workbench CLI not found; install it and sign in before deploying.')

def run(*args):
    subprocess.run(args, check=True)

release = 'smth-web-' + uuid.uuid4().hex
remote = '/root/' + release + '.tar.gz'
with tempfile.TemporaryDirectory(prefix='smth-deploy-') as tmp:
    tmp = Path(tmp)
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files}
    manifest = tmp / 'manifest.json'
    manifest.write_text(json.dumps(hashes))
    archive = tmp / (release + '.tar.gz')
    with tarfile.open(archive, 'w:gz', format=tarfile.USTAR_FORMAT) as tar:
        for name in files:
            tar.add(root / name, arcname=name)
        tar.add(manifest, arcname='manifest.json')
    print('Uploading release...', flush=True)
    run(workbench, 'upload', str(archive), remote, '--instance-id', instance)
    # Hash verification happens before any live file changes. index.html is replaced last.
    remote_script = '''
import hashlib, json, os
from pathlib import Path
import shutil, tarfile
archive = Path(ARCHIVE)
stage = archive.with_suffix('').with_suffix('')
stage.mkdir(exist_ok=False)
with tarfile.open(archive) as tar:
    for member in tar.getmembers():
        if member.name.startswith('/') or '..' in Path(member.name).parts or not member.isfile():
            raise RuntimeError('Invalid archive entry')
    tar.extractall(stage)
hashes = json.loads((stage / 'manifest.json').read_text())
for name, expected in hashes.items():
    if hashlib.sha256((stage / name).read_bytes()).hexdigest() != expected:
        raise RuntimeError('Upload hash mismatch: ' + name)
site = Path('/var/www/smth')
backup = Path(str(stage) + '-backup')
backup.mkdir()
existing = []
for name in hashes:
    target = site / name
    if target.exists():
        saved = backup / name
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved)
        existing.append(name)
(backup / 'manifest.json').write_text(json.dumps({'files': list(hashes), 'previouslyExisting': existing}))
changed = []
try:
    for name in sorted(hashes, key=lambda name: (name == 'index.html', name)):
        target = site / name
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + '.new')
        shutil.copyfile(stage / name, temporary)
        temporary.chmod(0o644)
        os.replace(temporary, target)
        changed.append(name)
except Exception:
    for name in reversed(changed):
        target = site / name
        if name in existing:
            shutil.copy2(backup / name, target)
        else:
            target.unlink()
    raise
print('Published. Backup: ' + str(backup), flush=True)
'''.replace('ARCHIVE', repr(remote))
    command = 'python3 - <<\'SMTH_DEPLOY_PY\'\n' + remote_script + '\nSMTH_DEPLOY_PY'
    print('Backing up and publishing...', flush=True)
    run(workbench, 'exec', '--instance-id', instance, '--timeout', '180', '--command', command)
    print('Verifying public files...', flush=True)
    # curl uses the system trust store; certificate verification remains enabled.
    for name, expected in hashes.items():
        url = site + ('' if name == 'index.html' else name) + '?release=' + release
        data = subprocess.check_output(['curl', '--fail', '--silent', '--show-error',
                                        '--location', '--retry', '2', '--max-time', '30', url])
        if hashlib.sha256(data).hexdigest() != expected:
            sys.exit(f'Public verification failed: {name}. Remote backup retained; inspect before retrying.')
    print(f'Deployed and verified {len(files)} files: {site}', flush=True)
PY
