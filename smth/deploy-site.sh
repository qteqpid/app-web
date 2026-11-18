#!/usr/bin/env bash
# Run on the cloud server after uploading a website archive.
set -euo pipefail

if [[ ${1:-} == "--help" || $# -lt 1 || $# -gt 3 ]]; then
  echo "用法：bash deploy-site.sh 压缩包.tar.gz [网站目录] [备份目录]"
  echo "默认网站目录：/var/www/smth；默认备份目录：/var/backups/smth"
  if [[ ${1:-} == "--help" ]]; then exit 0; else exit 2; fi
fi

command -v python3 >/dev/null || { echo "需要 Python 3，请先安装 python3。" >&2; exit 1; }

python3 - "$1" "${2:-/var/www/smth}" "${3:-/var/backups/smth}" <<'PY'
import fcntl
import hashlib
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import tarfile
import tempfile
from datetime import datetime

archive = Path(sys.argv[1]).resolve()
site = Path(sys.argv[2]).resolve()
backups = Path(sys.argv[3]).resolve()
backup = None
pages = {
    'index.html', 'changelog.html', 'privacy.html', 'robots.txt',
    'sitemap.xml', 'llms.txt', 'a395924ca50b4cbb96440bc6b435c8d3.txt',
}
asset_extensions = {
    '.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.ico', '.avif',
    '.js', '.css', '.json', '.woff', '.woff2', '.ttf', '.otf',
}

def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()

def safe_destination(name):
    destination = site / name
    for current in (destination, *destination.parents):
        if current == site:
            break
        if current.is_symlink():
            raise ValueError('目标路径含符号链接：' + str(current))
    if destination.exists() and not destination.is_file():
        raise ValueError('目标文件类型不正确：' + str(destination))
    return destination

try:
    if not archive.is_file():
        raise ValueError('找不到压缩包：' + str(archive))
    if not site.is_dir():
        raise ValueError('网站目录不存在，请确认 Nginx root：' + str(site))
    if backups == site or site in backups.parents:
        raise ValueError('备份目录必须放在网站目录之外。')

    # Validate and stage every file before writing to the live website.
    with tempfile.TemporaryDirectory(prefix='smth-site-') as staging:
        stage = Path(staging)
        files = []
        seen = set()
        with tarfile.open(archive, 'r:gz') as package:
            for member in package:
                path = PurePosixPath(member.name)
                if path.is_absolute() or not path.parts or '..' in path.parts:
                    raise ValueError('压缩包路径不合法：' + member.name)
                name = str(path)
                if name in seen:
                    raise ValueError('压缩包存在重复路径：' + name)
                seen.add(name)
                if not (member.isfile() or member.isdir()):
                    raise ValueError('压缩包不能包含链接或特殊文件：' + name)
                if name not in pages and path.parts[0] != 'assets':
                    raise ValueError('压缩包包含非官网文件：' + name)
                if member.isdir():
                    if path.parts[0] != 'assets':
                        raise ValueError('目录不合法：' + name)
                    continue
                if path.parts[0] == 'assets' and (len(path.parts) < 2 or path.suffix.lower() not in asset_extensions):
                    raise ValueError('资源文件类型不支持：' + name)
                safe_destination(name)
                target = stage / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with package.extractfile(member) as source, target.open('wb') as output:
                    shutil.copyfileobj(source, output)
                os.chmod(target, 0o644)
                files.append(name)
        if 'index.html' not in files or not (stage / 'index.html').stat().st_size:
            raise ValueError('压缩包必须包含非空的 index.html。')

        backups.mkdir(parents=True, exist_ok=True)
        with (backups / '.deploy.lock').open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValueError('另一个部署正在执行，请稍后重试。')
            for name in files:
                safe_destination(name)
            stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            fd, backup_name = tempfile.mkstemp(prefix='site-' + stamp + '-', suffix='.tar.gz', dir=backups)
            os.close(fd)
            backup = Path(backup_name)
            def skip_downloads(info):
                if PurePosixPath(info.name).parts[:1] in [('downloads',), ('backups',)]:
                    return None
                return info
            with tarfile.open(backup, 'w:gz') as saved:
                saved.add(site, arcname='.', filter=skip_downloads)
            # Also detect a damaged backup before changing the website.
            with tarfile.open(backup, 'r:gz') as saved:
                for member in saved:
                    if member.isfile():
                        with saved.extractfile(member) as stream:
                            while stream.read(1024 * 1024):
                                pass
            print('备份完成：' + str(backup), flush=True)

            # Assets and supporting pages go first; replace the homepage last.
            files.sort(key=lambda name: (name == 'index.html', name))
            for name in files:
                destination = safe_destination(name)
                destination.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
                temporary = None
                try:
                    fd, temporary = tempfile.mkstemp(prefix='.' + destination.name + '.', dir=destination.parent)
                    with os.fdopen(fd, 'wb') as output, (stage / name).open('rb') as source:
                        shutil.copyfileobj(source, output)
                        output.flush()
                        os.fsync(output.fileno())
                    os.chmod(temporary, 0o644)
                    os.replace(temporary, destination)
                    temporary = None
                    if digest(destination) != digest(stage / name):
                        raise ValueError('部署后的文件校验失败：' + name)
                finally:
                    if temporary:
                        Path(temporary).unlink(missing_ok=True)
            print('部署完成，已校验 ' + str(len(files)) + ' 个文件：' + str(site))
            print('静态网页已更新，无需重启 Nginx。')
except Exception as error:
    print('部署失败：' + str(error), file=sys.stderr)
    if backup and backup.is_file():
        print('备份文件：' + str(backup), file=sys.stderr)
    sys.exit(1)
PY
