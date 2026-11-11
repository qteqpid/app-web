# Workbench 迁移到个人电脑与水木拾光部署

本文用于在另一台个人电脑上接手 Workbench、官网部署和可选的 Android 签名打包。
执行部署前先完成安装、个人云身份配置和只读验证。官网的日常发布说明见
[SMTH 官网部署](smth/DEPLOYMENT.md)。以下路径默认使用 `~/Projects`，可以换成自己的目录。

## 1. 已确认的信息与待补项

核对日期：2026-11-11。

| 项目 | 已确认的信息 |
| --- | --- |
| 官网项目 | `https://github.com/qteqpid/app-web.git`，部署脚本位于 `smth/` |
| Android 源码 | `https://github.com/qteqpid/smth_android.git` |
| APK 下载仓库 | `https://gitee.com/qsmth/smth.git` |
| Workbench 旧安装位置 | `~/.local/bin/workbench`；此前文件为 macOS ARM64 可执行程序 |
| Workbench 旧配置位置 | `~/.workbench/config.json`；它可能包含凭据，不提交到 Git |
| 部署实例 | `i-2zed0unqjrhigvdmif9m`，写在现有三个部署脚本中 |
| 官网远端目录 | `/var/www/smth/` |
| 官网 | `https://smth.qteqpid.xyz/` |
| Android 签名配置入口 | `~/.config/smth/android-signing/signing.properties` |

还有两项需要从可信的发行方资料补齐，本文不编造安装包名或登录命令：

- **Workbench 安装来源、版本和下载校验值**：旧机器上的可执行程序已不存在，无法从本机进一步核实。先确认这里需要的是支持阿里云实例 `upload`、`exec` 的同一个 CLI，避免安装同名产品。
- **该版本的具体认证命令**：旧 `config.json` 也已不存在。须使用所安装版本的帮助或发行方文档确认登录、profile 和区域配置方式，再创建或登录个人云身份。

这两项完成后，后面的仓库获取、脚本校验和发布命令可以直接使用。

## 2. 准备新电脑与运行依赖

部署官网和上传已签名 APK，只需要 Workbench、Bash、Python 3、Git 和 curl。
不需要先安装 Android Studio，也不需要为了上传 APK 复制签名密钥。

在新电脑检查：

```bash
python3 --version
git --version
curl --version
bash --version
uname -sm
```

macOS 若已安装 Homebrew，可用 `brew install python git` 补齐 Python 和 Git。
Workbench 本身的安装来源仍需单独确认。Apple Silicon 使用 ARM64 发行包；Intel Mac
使用 x86_64 发行包。Linux 需使用对应发行包；Windows 运行仓库的 shell 脚本需准备
WSL 或兼容的 Bash 环境，并确认 Workbench 在该环境可用。

个人设备应启用磁盘加密。公司 Git 身份和 SSH 密钥不随个人部署环境复制。

## 3. 安装 Workbench 并配置 PATH

优先从确认过的可信渠道重新安装，核对发行版本、系统架构和校验值。
如发行方提供独立可执行文件，下面是 macOS/Linux 的放置方式；把占位路径改为
已经下载并验证的文件路径：

```bash
mkdir -p "$HOME/.local/bin"
install -m 755 /absolute/path/to/verified-workbench "$HOME/.local/bin/workbench"
export PATH="$HOME/.local/bin:$PATH"
command -v workbench
workbench --help
```

macOS 的 zsh 可把 `export PATH="$HOME/.local/bin:$PATH"` 加入 `~/.zprofile`，重新打开
终端后再次检查 `command -v workbench`。其他 shell 按其启动文件配置，避免反复添加重复行。

查看帮助，确认下面这些现有部署脚本依赖的能力：

```text
workbench upload LOCAL_FILE REMOTE_FILE --instance-id INSTANCE_ID
workbench exec --instance-id INSTANCE_ID --timeout SECONDS --command COMMAND
```

若新版本语法不同，先适配并检查部署脚本，再发布；不要直接猜测 login、deploy 等命令。

## 4. 配置个人阿里云身份并只读验证

1. 按发行方文档重新登录个人账号，或为个人账号创建权限范围合适的新 AccessKey/profile。
2. 核对账号、区域和目标实例。区域从个人阿里云控制台中该实例的信息确认，不从 APK 文件名或 OSS 区域推断。
3. 使用工具支持的交互式方式配置秘密值，避免将密钥放入命令参数、shell 历史或本文。
4. 若 CLI 使用 `~/.workbench/config.json`，确认目录和配置文件已由工具正确创建，再限制权限：

```bash
chmod 700 "$HOME/.workbench"
chmod 600 "$HOME/.workbench/config.json"
```

如果新版本采用其他存储方式，以该版本文档为准，不要为了套用旧路径创建空配置。
不需要输出配置内容来确认身份，不执行 `cat ~/.workbench/*`，也不复制整个目录。

先使用发行方支持的身份/资源查询命令核对个人云账号，再验证目标实例的只读访问：

```bash
workbench exec --instance-id i-2zed0unqjrhigvdmif9m --timeout 60 \
  --command 'id; ls -ld /var/www/smth /var/www/smth/downloads'
```

这里的 `id` 显示远端系统用户，不代表阿里云账号身份。权限需同时满足云端访问实例，
以及远端写入 `/var/www/smth/`、读取备份等需求。只读检查失败时先修正身份或权限。
首次安装验证不需要修改 Nginx，也不需要向生产网站上传测试文件。

## 5. 获取项目、发布包和本地校验

在新电脑配置个人 Git 访问权限；私有 GitHub 仓库需要个人账号有相应访问权。
迁移前应将需要的源码和文档推送到远程，或通过允许的方式传递已提交的项目副本。
**只在旧电脑本地 commit，新电脑 clone 还拿不到这些提交。**

```bash
mkdir -p "$HOME/Projects"
cd "$HOME/Projects"
git clone https://github.com/qteqpid/app-web.git
git clone https://gitee.com/qsmth/smth.git smth-apk
cd "$HOME/Projects/app-web/smth"
./deploy.sh --check
```

已克隆过的项目先检查 `git status`，确认自己的改动已保存，再更新对应分支。
`deploy.sh --check` 只校验本地静态文件，不调用 Workbench、不修改服务器。

如果需要上传 Android 2.0，先在 APK 仓库核对校验文件：

```bash
cd "$HOME/Projects/smth-apk"
shasum -a 256 -c smth-2.0.apk.sha256
```

Linux 若无 `shasum`，可用 `sha256sum -c smth-2.0.apk.sha256`。核对失败时不要上传。
版本和文件名以当次发布为准，不要把已有 APK 改名来假装新版本。

## 6. 官网与 APK 发布

新版本先上传 APK，再发布包含新下载链接的页面，避免首页先指向不存在的文件。
以 Android 2.0 为例，在个人电脑执行：

```bash
cd "$HOME/Projects/app-web/smth"
./deploy-apk.sh "$HOME/Projects/smth-apk/smth-2.0.apk" 2.0
./deploy.sh --check
./deploy.sh
```

`deploy-apk.sh` 只发布 APK，目标为：

```text
https://smth.qteqpid.xyz/downloads/smth-2.0.apk
```

它会核对上传文件的 SHA-256、备份已有同名包、原子替换，并从公网重新下载验证。
同名旧包备份位于 `/var/www/smth/backups/`。已有文件名尽量保持对应版本内容不变，
新版本使用新文件名。

`deploy.sh` 发布 HTML、资源、隐私政策、robots 和 sitemap，**不上传 APK**。
它会备份旧文件、最后替换首页，并逐个从公网下载核对 SHA-256。
保留脚本输出的备份路径，失败后先检查结果，避免连续重复执行。

发布前核对 `index.html` 的下载链接及结构化数据，并同步 `index.html` 和
`changelog.html` 的更新记录。APK 仓库的 README、CHANGELOG、版本文件和校验文件
也应匹配当次版本。完整操作和基础设施维护见 [DEPLOYMENT.md](smth/DEPLOYMENT.md)。

日常 HTML/APK 发布不需要执行 `deploy-infra.sh`；该脚本还会改动多个站点共享的
Nginx/systemd 配置，只有维护这些配置时才使用。

### 发布后独立校验

```bash
curl --fail --location --head https://smth.qteqpid.xyz/
curl --fail --location --head https://smth.qteqpid.xyz/changelog.html
curl --fail --location --output /tmp/smth-2.0-downloaded.apk \
  https://smth.qteqpid.xyz/downloads/smth-2.0.apk
shasum -a 256 /tmp/smth-2.0-downloaded.apk
cat "$HOME/Projects/smth-apk/smth-2.0.apk.sha256"
```

最后两条输出的 SHA-256 应一致；HTTP 200 本身不能证明 APK 正确。
浏览器确认首页下载地址、版本更新记录和实际下载内容；必要时检查浏览器/CDN 缓存。
保留安装包，不让页面指向尚未上传或已删除的版本。

### 出错与回滚

- **文件校验未通过**：检查日志和远端备份，暂停页面切换；脚本的“备份已保留”不等于自动完成回滚。
- **APK 需要回退**：把官网下载链接恢复到已验证的旧版本，保留旧 APK。若需要覆盖同名文件，先核对备份哈希再恢复；降低 Android `versionCode` 通常不能覆盖安装，客户端修复需另外发更高构建号。
- **静态网页需要回退**：使用上次已发布的 Git 版本在独立目录中运行 `deploy.sh --check`，确认后重新部署，或在服务器按脚本打印的备份清单恢复文件。不要直接还原整个 `/var/www/smth` 目录，以免误删下载包和其他资源。
- **Nginx/systemd 配置需要回退**：按 [DEPLOYMENT.md 的基础设施回滚说明](smth/DEPLOYMENT.md#回滚基础设施) 操作，并先通过 `nginx -t` 再 reload。

## 7. 可选：在新电脑签名打包 Android

仅上传现成签名包可以跳过本节。需要重新构建时才准备 Android Studio、Android SDK、
项目兼容的 JDK 和源码；SDK/JDK 版本以项目 Gradle 配置与工具链设置为准。

```bash
cd "$HOME/Projects"
git clone https://github.com/qteqpid/smth_android.git
cd smth_android
./gradlew --version
```

正式签名配置入口为 `~/.config/smth/android-signing/signing.properties`，项目读取
`storeFile`、`storePassword`、`keyAlias`、`keyPassword`。`storeFile` 引用的实际 keystore
必须一并安全迁移，并改为新电脑上的路径；仅复制 properties 文件不能完成签名迁移。
不要输出 properties 内容、密码或私钥，也不要将其提交到任何源码/下载仓库。

原签名密钥无法靠重新生成替代，否则已安装 App 无法按原签名正常升级。
先确认可靠备份及关联密码，再通过批准的私密传输方式迁移。配置就绪后执行：

```bash
./gradlew :app:testDebugUnitTest :app:assembleRelease
```

输出：`app/build/outputs/apk/release/app-release.apk`。使用 Android SDK 的 `apksigner verify`
验证新 APK 和旧正式 APK，并比较签名证书的 SHA-256；使用 `aapt dump badging` 核对
包名、`versionName` 和 `versionCode`。每次发版提高构建号、更新 CHANGELOG，并核对
R8 构建结果，再进入第 6 节。不要通过打印签名配置来排查构建错误。

## 8. 旧设备凭据撤销与清理

如果旧设备属于公司，按安全团队要求处理；需要导出无法重新生成的签名密钥或个人
配置时，先确认允许的传输方式。仅迁移个人资产，不复制公司代码、账号凭据或受限资料。
新环境没有验证完成时，不发送“全部迁移完成”，也不继续从公司电脑运行个人部署。

新环境验证后，在个人云账号管理界面撤销或轮换旧设备上的 AccessKey/会话。
先核对其他个人系统的依赖；删除本机文件不等于撤销云端凭据。

清理前只检查已知路径的存在、类型和符号链接，不输出秘密内容：

```bash
ls -ld "$HOME/.local/bin/workbench" "$HOME/.workbench" \
  "$HOME/.config/smth/android-signing"
```

以下删除命令**只在旧设备、迁移/备份已验证且确认清理范围后执行**：

```bash
rm -f -- "$HOME/.local/bin/workbench"
rm -rf -- "$HOME/.workbench"
```

如是符号链接，先确认其目标，避免只移除链接却遗漏副本。签名密钥按已经确认的
实际路径单独处理，不能因为 CLI 已移除而省略，也不要仅凭示例路径递归删除。
不删除整个 `~/.local/bin`，不删除公司共用工具、凭据、安全告警或系统日志。

检查相关 shell PATH/alias、个人凭据副本和迁移临时文件。涉及 shell 历史或备份快照
中的秘密值时按安全团队指导处理，不以清空全部历史替代精准处理。

```bash
for item in "$HOME/.local/bin/workbench" "$HOME/.workbench"; do
  if [ -e "$item" ] || [ -L "$item" ]; then
    printf '仍存在：%s\n' "$item"
  else
    printf '已移除：%s\n' "$item"
  fi
done
command -v workbench
```

如仍找到其他 CLI 位置，先确认是否属于个人 Workbench，再按其安装方式移除。
上述删除命令不在新个人电脑执行。

## 9. 完成记录

- [ ] 已核实 Workbench 安装来源、版本与架构，并记录具体认证方式。
- [ ] 新电脑的个人身份、区域和实例只读访问验证通过。
- [ ] 项目、发布包、文档已获取，所需本地提交已推送到远程。
- [ ] 本地脚本校验通过；如已发布，官网下载的 APK 和页面校验通过。
- [ ] 如迁移签名能力，新电脑正式签名与旧版一致，密钥有可靠备份。
- [ ] 旧云凭据已撤销/轮换，或记录不适用原因。
- [ ] 旧设备指定 CLI、配置和签名密钥已清理，并检查相关个人副本。
- [ ] 若其他公司设备也有这些资产，已按相同流程处理。
- [ ] 已向安全团队如实反馈，未完成项单独说明。

不要在本文填写实际密钥、密码或完整配置，也不要提前把未执行的步骤标为完成。

如需回复安全团队，仅在对应项目确实完成后使用下面的模板；部分完成时改写为
实际进展并列出剩余事项，不发送“全部完成”。

> Hi Graham, I’ve moved my personal Workbench setup to my personal device and removed
> `~/.local/bin/workbench` and `~/.workbench/` from my work Mac. I’ve also removed the
> smth signing keys and revoked or rotated the personal cloud credentials that were stored
> on the device. Going forward, I’ll keep personal development on my personal device.
> Please let me know if any additional cleanup is needed.

本节仅提供反馈文本；文档整理不代表迁移、清理或反馈消息已经执行。
