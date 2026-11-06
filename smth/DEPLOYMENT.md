# SMTH 官网部署

本目录维护 `smth.qteqpid.xyz` 的静态页面、Android APK，以及共享给
`qteqpid.xyz`、`apps.qteqpid.xyz` 的 Nginx 和 systemd 配置。

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
