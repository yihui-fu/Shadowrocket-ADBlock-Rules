# Shadowrocket 去广告与分流规则

本仓库维护一份名为 **customized** 的 Shadowrocket 订阅。它以上游的白名单去广告版为基础，加入个人规则、AdGuard 广告域名和哔哩哔哩专项规则。未匹配的流量默认走代理，代理节点需自行添加。[上游项目](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever)

## 扫码安装与更新

用 **Shadowrocket** 扫描下方二维码，下载后点 **使用配置**，并在首页将「全局路由」设为「配置」。如果正在同一台 iPhone 上阅读，可复制下方订阅地址，在 Shadowrocket 的「配置」页点 `+` 粘贴。

![用 Shadowrocket 扫码添加 customized 配置](figure/customized.png)

**订阅地址**（长期有效）

```text
https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/customized.conf
```

以后在「配置」页点 **customized.conf → 更新配置**，就能一起获取已发布的上游分流、个人规则和 AdGuard 补充列表。首次扫码后可一直沿用这个入口。[查看发布状态](https://github.com/yihui-fu/Shadowrocket-ADBlock-Rules/actions/workflows/customized.yml)

## 添加个人规则

1. 在 `release` 分支编辑 [custom/rules.list](https://github.com/yihui-fu/Shadowrocket-ADBlock-Rules/edit/release/custom/rules.list)，每行写一条 Shadowrocket 分流规则。下例会拦截指定域名及其子域名。

   ```text
   DOMAIN-SUFFIX,ads.example.com,REJECT
   ```

2. 提交后，GitHub Actions 会自动构建。等 **Publish customized.conf** 的 `publish` 步骤成功，再在手机上点「更新配置」。个人规则排在最前面，之后依次匹配 B 站广告域名、AdGuard 补充规则和上游分流。

上游更新时，工作流会重新读取 `custom/`，只写回 `customized.conf` 和 `adguard-dns.list` 两个生成文件。因此，保存在 `custom/` 的个人规则会随下次发布继续生效。

## 验证去广告是否生效

**确认补充列表已下载。** 主配置用一条 `RULE-SET` 引用整份 AdGuard 列表。例如主配置有 54,090 条时，同一次发布的外部列表另有 140,285 条，两处计数会随更新变化。在「配置 → customized.conf → 编辑配置 → 规则集 URL」找到 `adguard-dns.list`，✅ 表示下载成功。若显示 ❎，点该地址重试，再点「使用配置」重新编译。这份列表下载后在本机匹配，日常访问无需向 GitHub 逐次查询。[该次构建记录](https://github.com/yihui-fu/Shadowrocket-ADBlock-Rules/actions/runs/44543731398) · [Shadowrocket 使用手册](https://lowertop.github.io/Shadowrocket/)

**确认 App 请求被拦截。** 在「数据 → 代理」启用日志记录，打开芒果 TV 刷新首页或播放免费节目，再回到最新日志搜索 `da.mgtv.com`。该域名在上述版本的补充列表里。若日志策略显示 `REJECT`，就确认这次请求被拒绝。若 App 当次没有请求该域名，这次测试就没有可供判断的记录。离线仍能显示的开屏画面也不适合用来判断网络规则是否生效。

### AdGuard 规则与 DNS

订阅会自动把 AdGuard 可转换的域名规则补入本地规则集。使用上游默认的阿里 DNS 和 DNSPod 也能拦截这些域名，无需安装 AdGuard App。若还想让 AdGuard 过滤发给它的 DNS 查询，可在「配置 → customized.conf → ⓘ → 通用 → DNS 覆写」中只填 `https://dns.adguard-dns.com/dns-query`。同栏填多个 DNS 会并发查询，较早返回的结果可能来自其他服务商。本机修改订阅配置后，下次更新时请复核这一项。[AdGuard 公共 DNS](https://adguard-dns.io/kb/public-dns/overview/) · [Shadowrocket DNS 设置](https://lowertop.github.io/Shadowrocket/)

### 哔哩哔哩与 HTTPS 解密

B 站的四条广告域名规则可直接生效。开屏、首页推荐、短视频流和动态里的部分广告卡与正常内容共用接口，配置另用 Biliverse 响应脚本处理。要启用这部分，在当前配置的「ⓘ → HTTPS 解密」开启解密及 HTTP/2，在本机生成并安装 CA，然后到 iOS「设置 → 通用 → 关于本机 → 证书信任设置」信任它。[B 站专项配置](custom/bilibili.conf) · [Biliverse ADBlock v0.7.5](https://github.com/Biliverse/ADBlock/releases/tag/v0.7.5) · [广告域来源](https://github.com/letswish/Shadowrocket-Module/blob/main/All-in-One-AdBlock.sgmodule)

开启后，Shadowrocket 能读取匹配主机的 HTTPS 明文。专项规则添加了四个 B 站 API 主机，最终解密清单还包含上游的 `*.google.cn` 和 `*.googlevideo.com`。只需要域名拦截时，可以把 HTTPS 解密保持关闭。

## 其他配置

在 Shadowrocket 的「配置」页点「+」，粘贴下表对应的链接，下载后选用。未命中规则时，黑名单版默认直连，白名单版默认代理。原作者的配置和二维码可在上游文档中找到。[上游使用文档](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/)

| 类型 | 用途 | 下载 |
| --- | --- | --- |
| 黑名单 | 未命中规则时默认直连 | [普通版](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/sr_top500_banlist.conf) · [去广告版](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/sr_top500_banlist_ad.conf) |
| 白名单 | 未命中规则时默认代理 | [普通版](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/sr_top500_whitelist.conf) · [去广告版](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/sr_top500_whitelist_ad.conf) |
| 国内外划分 | 国内直连，国外代理 | [普通版](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/sr_cnip.conf) · [去广告版](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/sr_cnip_ad.conf) |
| 回国规则 | 针对中国站点使用回国代理 | [普通版](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/sr_backcn.conf) · [去广告版](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/sr_backcn_ad.conf) |
| 去广告 | 按需选直连、代理或仅广告规则 | [直连去广告](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/sr_direct_banad.conf) · [代理去广告](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/sr_proxy_banad.conf) · [仅广告规则](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/sr_ad_only.conf) |
| 懒人配置 | 同步自 LOWERTOP，可选带策略组的版本 | [普通版](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/lazy.conf) · [策略组版](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/lazy_group.conf) |

构建还产出 [`sr_adb.conf`](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/sr_adb.conf)，可直接查看。

## 维护手册

**分支职责。** [`build`](https://github.com/yihui-fu/Shadowrocket-ADBlock-Rules/tree/build) 是构建输入，入口是 [`factory/auto_build.sh`](https://github.com/yihui-fu/Shadowrocket-ADBlock-Rules/blob/build/factory/auto_build.sh)，由 [`factory/build_confs.py`](https://github.com/yihui-fu/Shadowrocket-ADBlock-Rules/blob/build/factory/build_confs.py) 结合 [模板及规则源文件](https://github.com/yihui-fu/Shadowrocket-ADBlock-Rules/tree/build/factory) 生成配置。[默认分支 `release`](https://github.com/yihui-fu/Shadowrocket-ADBlock-Rules/tree/release) 既是下载入口，也存放 [发布工作流](.github/workflows/release.yml) 和这份 README。不要直接编辑生成的配置来做长期定制，下次发布会替换它们。

**什么时候发布。** [Release Shadowrocket Rules](https://github.com/yihui-fu/Shadowrocket-ADBlock-Rules/actions/workflows/release.yml) 每天 **北京时间 07:00**（UTC 23:00）计划启动，完成时间以 Actions 为准。可以在 Actions 中选 `release` 后点 **Run workflow** 手动发布。修改并推送工作流文件到 `release` 也会触发。只更新 `build` 或 README 不会立即触发发布，可手动运行或等下一次定时任务。

**发布边界。** `build` 任务只有 `contents: read`，检出后不保留 Git 凭据。它把规则作为同次运行的 `generated-rules` 产物交给 `publish`。只有后者有 `contents: write`，且只写工作流中 `GENERATED_CONFIGS` 的 12 个文件及 `LAZY_CONFIGS` 的 `lazy.conf`、`lazy_group.conf`。工作流、README、图和其他配置不在覆盖名单内。保持构建与发布分离，不启用 `pull_request_target` 发布，不给整个仓库开启默认写权限，不用强推。

**检查和恢复。** 先看 Actions 里 `build` 和 `publish` 都是绿色，再看 [`release` 提交记录](https://github.com/yihui-fu/Shadowrocket-ADBlock-Rules/commits/release/)：有改动时应出现普通提交 `Update generated Shadowrocket rules`，差异只应涉及名单内的规则。`No changes to publish` 也是正常结果。失败先看具体步骤：构建或收集失败，检查依赖、规则源和产出文件。推送失败（如 403），核对发布任务的权限、目标分支及分支限制，不要扩大默认权限。若因分支已更新而不能快进，重新触发一次，让任务基于最新 `release` 发布。需回退时用普通 revert 提交，不改写历史。

**更新上游。** 先对照 [上游 `build`](https://github.com/johnshall/Shadowrocket-ADBlock-Rules-Forever/tree/build) 与本 fork 的 `build`，审查差异后再合入需要的源码和规则输入。特别留意依赖、生成脚本、输出文件名以及以后新增的自定义规则入口。不要用上游 `release` 覆盖本 fork 的 `release`，也不要让上游工作流替换本仓库的发布流程。更新后手动发布并检查提交差异。标准配置从本仓库的 `build` 分支构建，个人订阅会独立拉取上游发布文件。

**个人配置发布。** [Publish customized.conf](.github/workflows/customized.yml) 在北京时间每天 08:37 计划运行。向 `release` 提交 `custom/` 或该工作流的改动也会触发构建，另可在 Actions 手动运行。它下载上游最新的白名单去广告配置和 AdGuard DNS filter，把主配置及其引用的列表放在同一提交发布。输入下载或构建失败时，订阅继续提供上次成功发布的版本。[上游基础配置](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever/blob/release/sr_top500_whitelist_ad.conf) · [AdGuard 过滤器](https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt)

**AdGuard 转换。** 构建时会跳过已有拒绝规则覆盖的域名，把其余可直接匹配的条目写入外部列表，并在引用地址中附上由内容计算的版本号。遇到放行例外时，主配置用条件规则排除相应域名，使其继续走后续分流。构建日志列出补充、已有覆盖、例外及跳过的数量。转换器会跳过无法等价处理的网址、IP 和正则拦截项。若遇到无法识别的放行例外，会停止构建，以免发布会误拦的规则。[转换脚本](custom/adguard.py) · [生成列表](adguard-dns.list) · [过滤器来源](https://github.com/AdguardTeam/AdGuardSDNSFilter) · [补充列表许可证](licenses/AdGuard-DNS-GPL-3.0.txt)

## 来源及许可

感谢 [h2y 原项目](https://github.com/h2y/Shadowrocket-ADBlock-Rules)、[johnshall 的后续维护](https://github.com/johnshall/Shadowrocket-ADBlock-Rules-Forever)、[LOWERTOP 的懒人配置](https://github.com/LOWERTOP/Shadowrocket) 及各规则源维护者。主要来源见 [上游鸣谢](https://github.com/johnshall/Shadowrocket-ADBlock-Rules-Forever#鸣谢)。本仓库保留上游 [CC BY-SA 4.0 许可](LICENSE)。
