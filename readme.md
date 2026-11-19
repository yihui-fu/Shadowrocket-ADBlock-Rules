# Shadowrocket 去广告与分流规则

这是 [johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 fork。规则是 Shadowrocket 配置，不提供代理节点。下面的下载链接来自**这个 fork** 的 `release` 分支；[上游使用文档](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/)里列的链接和二维码来自上游。

## customized 个人配置

用 Shadowrocket 扫描下方二维码，下载后选择「使用配置」。以后在「配置」页点 `customized.conf` →「更新配置」，即可获取已发布的上游规则和个人规则。

![扫描以添加 customized.conf](figure/customized.png)

[配置下载地址](https://raw.githubusercontent.com/yihui-fu/Shadowrocket-ADBlock-Rules/release/customized.conf) · [编辑个人规则](https://github.com/yihui-fu/Shadowrocket-ADBlock-Rules/edit/release/custom/rules.list) · [查看发布状态](https://github.com/yihui-fu/Shadowrocket-ADBlock-Rules/actions/workflows/customized.yml)

基础配置采用 [Johnshall 白名单＋去广告版](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever/blob/release/sr_top500_whitelist_ad.conf)。在 `release` 分支的 `custom/rules.list` 中每行填写一条规则，生成时会插入上游 `[Rule]` 段的开头。例如，只拦截某个域名可写 `DOMAIN,ads.example.com,REJECT`。个人文件中只有注释或空行时，订阅内容与上游原文件完全一致。

## 选择并导入

在 Shadowrocket 的「配置」页点「+」，粘贴下表对应的链接，下载后选用。黑名单与白名单最关键的区别是**没有命中规则时怎么走**：黑名单默认直连，白名单默认代理。

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

**什么时候发布。** [Release Shadowrocket Rules](https://github.com/yihui-fu/Shadowrocket-ADBlock-Rules/actions/workflows/release.yml) 每天 **北京时间 07:00**（UTC 23:00）计划启动，完成时间以 Actions 为准。可以在 Actions 中选 `release` 后点 **Run workflow** 手动发布；修改并推送工作流文件到 `release` 也会触发。只更新 `build` 或 README 不会立即触发发布，可手动运行或等下一次定时任务。

**发布边界。** `build` 任务只有 `contents: read`，检出后不保留 Git 凭据。它把规则作为同次运行的 `generated-rules` 产物交给 `publish`；只有后者有 `contents: write`，且只写工作流中 `GENERATED_CONFIGS` 的 12 个文件及 `LAZY_CONFIGS` 的 `lazy.conf`、`lazy_group.conf`。工作流、README、图和其他配置不在覆盖名单内。保持构建与发布分离，不启用 `pull_request_target` 发布，不给整个仓库开启默认写权限，不用强推。

**检查和恢复。** 先看 Actions 里 `build` 和 `publish` 都是绿色，再看 [`release` 提交记录](https://github.com/yihui-fu/Shadowrocket-ADBlock-Rules/commits/release/)：有改动时应出现普通提交 `Update generated Shadowrocket rules`，差异只应涉及名单内的规则；`No changes to publish` 也是正常结果。失败先看具体步骤：构建或收集失败，检查依赖、规则源和产出文件；推送失败（如 403），核对发布任务的权限、目标分支及分支限制，不要扩大默认权限。若因分支已更新而不能快进，重新触发一次，让任务基于最新 `release` 发布。需回退时用普通 revert 提交，不改写历史。

**更新上游。** 先对照 [上游 `build`](https://github.com/johnshall/Shadowrocket-ADBlock-Rules-Forever/tree/build) 与本 fork 的 `build`，审查差异后再合入需要的源码和规则输入；特别留意依赖、生成脚本、输出文件名以及以后新增的自定义规则入口。不要用上游 `release` 覆盖本 fork 的 `release`，也不要让上游工作流替换本仓库的发布流程。更新后手动发布并检查提交差异。这里的定时任务只读取本 fork 的 `build`，并不会自动同步上游分支。

**个人配置发布。** [Publish customized.conf](.github/workflows/customized.yml) 独立下载上游已发布的白名单去广告配置。向 `release` 提交 `custom/` 或该工作流的改动后会触发构建，每天北京时间 08:37 也会检查上游，可在 Actions 中手动运行。构建成功后只发布仓库根目录的 `customized.conf`。上游下载或合并失败时继续提供上次成功发布的版本。订阅地址和二维码都可以长期使用。

## 来源及许可

感谢 [h2y 原项目](https://github.com/h2y/Shadowrocket-ADBlock-Rules)、[johnshall 的后续维护](https://github.com/johnshall/Shadowrocket-ADBlock-Rules-Forever)、[LOWERTOP 的懒人配置](https://github.com/LOWERTOP/Shadowrocket) 及各规则源维护者。主要来源见 [上游鸣谢](https://github.com/johnshall/Shadowrocket-ADBlock-Rules-Forever#鸣谢)。本仓库保留上游 [CC BY-SA 4.0 许可](LICENSE)。
