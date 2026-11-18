# SMTH 官网部署

本目录维护 `smth.qteqpid.xyz` 的静态页面、Android APK，以及共享给
`qteqpid.xyz`、`apps.qteqpid.xyz` 的 Nginx 和 systemd 配置。

新电脑安装、认证、项目获取与迁移清理步骤见
[Workbench 迁移与部署指南](../WORKBENCH_MIGRATION.md)。

## 通过网页版 Workbench 部署（当前方式）

当前仓库提供 `deploy-site.sh`，在云服务器执行。需要 Bash 和 Python 3，
不需要本地 Workbench CLI。默认网站目录为 `/var/www/smth`，备份目录为
`/var/backups/smth`；首次部署前通过 `nginx -T` 核对官网的 `root`。

### 1. 在本地电脑打包

压缩包根目录直接放网页和 `assets/`，不要再套一层 `smth/` 目录。
在 Mac 本地终端执行：

```bash
cd ~/Desktop/ios开发/app-web/smth
COPYFILE_DISABLE=1 tar -czf /tmp/smth-site.tar.gz \
  index.html changelog.html privacy.html robots.txt sitemap.xml llms.txt \
  a395924ca50b4cbb96440bc6b435c8d3.txt assets
```

### 2. 首次安装部署脚本

在网页版 Workbench 连接官网 ECS，使用文件管理将本仓库的 `deploy-site.sh`
上传到服务器 `/tmp/`。以 root 用户执行：

```bash
install -m 755 /tmp/deploy-site.sh /usr/local/bin/deploy-smth-site
```

这一步只需要执行一次。以后脚本有更新时，再上传并执行同一安装命令。

### 3. 每次上传压缩包并部署

使用 Workbench 文件管理把本地压缩包上传至服务器 `/tmp/smth-site.tar.gz`，
然后在服务器终端执行：

```bash
deploy-smth-site /tmp/smth-site.tar.gz
```

也可以不安装，直接执行上传的脚本：

```bash
bash /tmp/deploy-site.sh /tmp/smth-site.tar.gz
```

脚本会先检查压缩包路径和文件类型、解压到独立临时目录，再备份旧站点。
备份排除 `downloads/` 和站点内的 `backups/`，存放在网站目录之外。
部署先更新资源和辅助页面、最后替换首页，每个文件采用临时文件加原子替换，
并核对 SHA-256。脚本只接受约定的网页文件和静态资源，不删除站点的其他文件。
并发部署会被拒绝。部署完成后无需重启 Nginx，浏览器强制刷新官网即可验证。

如命令报错，不要仅凭存在备份文件认为已完成部署。上传包检查失败时站点不会改变；
部署过程中失败时可能已替换部分文件，脚本会返回非零状态并打印备份路径。
需要回滚时，核对脚本打印的备份文件，在服务器执行：

```bash
tar -xzf /var/backups/smth/实际的备份文件名.tar.gz -C /var/www/smth
```

回滚会覆盖备份中的同名文件，新发布中额外新增的静态资源会保留。

脚本可选的第二、第三个参数用于指定网站目录和备份目录，例如本地测试；
备份目录必须在网站目录之外：

```bash
bash deploy-site.sh /tmp/smth-site.tar.gz /tmp/test-site /tmp/test-backups
```

## 旧版 CLI 部署说明

以下为历史 CLI 流程，供迁移和基础设施维护时参考；其中的 `deploy.sh`、
`deploy-apk.sh` 和 `deploy-infra.sh` 当前不在本仓库中。日常部署使用上面的
网页版 Workbench 和 `deploy-site.sh`。

## 前置条件

- 本机已安装并登录 Workbench CLI。
- 当前账号可以操作实例 `i-2zed0unqjrhigvdmif9m`。
- 部署基础设施时，服务器已安装 Nginx、systemd 和 curl。
- 不要把证书、私钥、Token 或 Workbench 凭据提交到仓库。

所有部署脚本都会先校验输入。远端文件采用临时文件加原子替换，已有文件会先备份。

## 部署静态网站

```bash
cd smth
./deploy.sh --check
./deploy.sh
```

脚本部署 HTML、站点资源、隐私政策、robots 和 sitemap。它不会部署 APK、Nginx
配置或脚本自身。发布完成后会从公网逐个下载文件并核对 SHA-256。

远端目录：`/var/www/smth/`。每次发布生成的备份路径会打印在终端中。

## 部署 Android APK

先在 Android 项目中生成并校验正式签名包，再执行：

```bash
cd smth
./deploy-apk.sh /absolute/path/to/app-release.apk 1.1
```

版本参数决定公开文件名，例如 `1.1` 对应：

```text
https://smth.qteqpid.xyz/downloads/smth-1.1.apk
```

脚本会计算本地大小和 SHA-256、上传 APK、备份旧包、原子替换，并从公网重新下载校验。
旧包保存在 `/var/www/smth/backups/`。

发布新版本时，还要同步修改 `index.html` 中的下载地址和结构化数据，再部署静态网站。

## 部署 Nginx 与自愈配置

基础设施文件包括：

- `nginx-pending.conf`：三个站点的 Nginx 配置。
- `infra/nginx-recovery.conf`：Nginx 启动失败自动重试。
- `infra/qteqpid-web-healthcheck`：本机 HTTPS 健康检查和自动恢复。
- `infra/qteqpid-web-healthcheck.service`、`.timer`：每分钟执行健康检查。

先做本地校验：

```bash
cd smth
./deploy-infra.sh --check
```

确认改动后部署：

```bash
./deploy-infra.sh
```

脚本会在服务器创建 `/etc/qteqpid-deploy-backups/<release>/` 备份，原子替换配置，执行
`nginx -t`，失败则恢复原文件；校验成功后 reload Nginx、启用健康检查，并验证三个公网域名。

## 部署后检查

```bash
curl --fail --location --head https://qteqpid.xyz/
curl --fail --location --head https://apps.qteqpid.xyz/
curl --fail --location --head https://smth.qteqpid.xyz/
```

在服务器检查服务状态：

```bash
nginx -t
systemctl status nginx --no-pager
systemctl status qteqpid-web-healthcheck.timer --no-pager
journalctl -u nginx -n 100 --no-pager
journalctl -u qteqpid-web-healthcheck.service -n 100 --no-pager
```

## 回滚基础设施

选择 `deploy-infra.sh` 输出的备份目录，将其中的文件恢复到以下位置：

| 备份文件 | 恢复位置 |
|---|---|
| `nginx-pending.conf` | `/etc/nginx/sites-enabled/smth-pending.conf` |
| `nginx-recovery.conf` | `/etc/systemd/system/nginx.service.d/recovery.conf` |
| `qteqpid-web-healthcheck` | `/usr/local/sbin/qteqpid-web-healthcheck` |
| `qteqpid-web-healthcheck.service` | `/etc/systemd/system/qteqpid-web-healthcheck.service` |
| `qteqpid-web-healthcheck.timer` | `/etc/systemd/system/qteqpid-web-healthcheck.timer` |

恢复后执行：

```bash
nginx -t
systemctl daemon-reload
systemctl reload nginx
systemctl restart qteqpid-web-healthcheck.timer
```

如果 `nginx -t` 失败，不要 reload；继续使用当前运行中的配置并检查错误。
