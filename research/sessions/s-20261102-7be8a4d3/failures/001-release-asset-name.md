# 001 — GitHub Release 文件资产名称错误（已定位，待修复验收）

- 初始工作流：[41428181901](https://github.com/sstxww/reinforcement-learning/actions/runs/41428181901)，本会话独立分支。
- 全部单测、引擎安装、原 V2 1280-step Release 的下载及原 SHA256 校验、真正 128-step MaskablePPO 续训（1408 总步数）、模型和 Baseline 3 场真实完整八人比赛均成功。
- 发布 `gh release create` **成功**，tag `v5-recovery-s-20261102-7be8a4d3-41428181901`，上传模型 SHA256 `250be6159508fdd1ef91abb6c7277efe32fa49c726ea347923f18f6a4765e0f0`，但校验重下载阶段失败 `no assets match the file pattern`。
- 已直接检查 GitHub Release API：存在实际资产文件名 `resumed.zip`、`resumed.metadata.json`、`001-results.json`；`gh release create path#label` 的 `#model.zip` 是展示标签，**不是文件名重命名**。重下载错误地匹配 `model.zip` 和 `model.metadata.json`，因此没有命中。
- `continue-on-error: true` 导致发布步骤的真实 outcome=failure，但工作流最终结论=success；不能仅凭整个工作流绿色就宣称已独立重新下载验证。原始收据 `reports/s-20261102-7be8a4d3/001-results.json` 如实记录 `release_redownload_verified:false`，不可直接改为 true。
- 根因：文件命名约定误用，不是模型保存失败；GitHub API 上确实列出了持久模型资产和相同 SHA256，但需要另一独立运行真正下载。
- 修复：新增专用 `.github/workflows/v5-release-verify-s-20261102-7be8a4d3.yml`，先下载现有 `resumed.zip` 并校验 SHA/步数，再以真正文件名 `model.zip`、`model.metadata.json` 上传同一 Release，独立下载这两个资产并比对字节；成功才生成 `001-release-reverified.json`。
- 边界：此修复不再训练 PPO，不改主分支权重、不晋升 Champion、不触发 Arena；失败时保留现有 Release 资产并给出受阻原因。