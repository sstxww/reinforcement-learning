# 独立 ChatGPT 会话并行实验协议（V1）

**本协议的 Agent 指一个独立开启的 ChatGPT 会话，而不是子 Agent。** 用户可将同一提示词发给多场新会话。每场会话自己训练、自己完整打完至少一局、自己记录经验；共享 GitHub 仓库，但不共享工作目录、分支或可变模型文件。

## 单会话身份（必须唯一）

每个新会话首次启动时生成不重复的 `SESSION_ID`（如 `s-20261102-7f3a2d91`），先查询远端是否存在对应分支与实验目录；发生重名就重新生成。后续轮次沿用自己的 Session ID，轮次号递增。

- 工作分支：`agent/<SESSION_ID>/optimization-<NNN>`
- 真实八人对局收据：`experiments/<SESSION_ID>/<NNN>-<seed>.json`
- 自己的研究日志：`research/sessions/<SESSION_ID>/round-<NNN>.md`
- 自己的最新进度：`research/sessions/<SESSION_ID>/STATUS.md`（只由这个会话修改）
- 可供集成者审阅的经验建议：`research/knowledge/proposals/<SESSION_ID>-<NNN>.md`
- PR 标题：`[<SESSION_ID> R<NNN>] <hypothesis>`

**同一份提示词可以复制到多个会话；不允许共用固定的 `strategy`、`learning` 等分支或 `agent_id`。**

## 并发隔离

1. 只允许写 `sstxww/reinforcement-learning`；上游 AutoTavern 是只读模拟器。不得使用用户本地 A11 或操作用户电脑。
2. 基于 `main` 的某个明确 commit SHA 创建自己的分支，记录 base SHA。所有研发提交只推自己的分支；禁止直接推 `main`、强推、删除或修改其他会话的分支、PR、日志、成果与模型。
3. 开始前查询开放 PR、最近的 session 日志/经验提案，查看有没有正在研究同一文件和假设的会话。发现重叠就改研究方向，或在自己的 PR 中给出替代建议；绝不抢占或覆盖。
4. 共享的 `README.md`、`AGENTS.md`、`.github/workflows/train.yml`、`research/knowledge/README.md` 等仅由用户或最终集成会话合并更新。独立调优会话只提出建议。
5. 需要云端训练时使用独立工作流/运行标识及私有检查点，不能从其他会话的“latest”检查点恢复，不能覆盖公共的 `v1-model` Artifact。现有 `train.yml` 只在 `main` 运行且有全局并发组，**不适合作为独立会话的并行训练入口**。可在各自分支新增唯一命名的 `.github/workflows/experiment-<SESSION_ID>.yml`（push 触发，有限时限、只读默认权限、不自动合并）；或使用真正可用的隔离云端执行环境。不得假称 GitHub 已运行任务。
6. 每个 PR 必须包含此会话亲自运行的完整八人 TavernGym 对局收据。CI 会独立执行另一场；CI 的公共 canary 不能代替自己的对局收据。
7. 任何正式竞技场比赛需要用户单独授权。默认只使用本地/Actions 中的开源 TavernGym。

## 一轮研究必须留下什么

在 `research/sessions/<SESSION_ID>/round-<NNN>.md` 中记录：

- Session ID、轮次、研究假设、所属文件、起始 main commit SHA、自己的 commit、PR 链接
- TavernGym 上游 commit、补丁 SHA256、版本、特征/卡牌/动作维度；模型及训练配置哈希
- 可复现训练命令、步数、运行 ID、检查点位置与 SHA256；若没有持久检查点须直言
- **本会话真实完整八人对局**的运行 URL、seed、Agent ID、对局收据路径、本人最终名次、动作数、是否完成及引擎保护状态
- 固定种子的前后对比：局数、平均名次、前四率、第一名率、变异/不确定性；不足以确认提升时明确“不确定”
- 成功经验、失败原因、可泛化的游戏策略/模型技巧、下一轮假设
- 被清理的临时文件；保留数据清单；恢复训练的具体方式

训练日志不需要全量入库：保留精简指标和必要证据。大型权重和 rollout 不得直接提交 Git；Artifacts 会过期，**模型只有在经验证的持久存储可读取时才算已固化**。不能清理唯一可恢复的 checkpoint。

## 经验共享与后续学习

- 会话完成本轮后：提交自己的 `round-<NNN>.md`、`STATUS.md`、必要的收据和 `research/knowledge/proposals/<SESSION_ID>-<NNN>.md` 到独立分支，并创建 PR；禁止把草稿当作 main 中已通过验证的经验。
- 用户/最终集成会话负责审核 PR、CI、数据证据和冲突，合并通过的 PR，并将已证实的可复用结论整理进 `research/knowledge/`（集中知识库），这一步不是调优会话竞争写同一文件。
- **开始下一轮前先读取** `main` 上的 `research/knowledge/`、自己的 `STATUS.md` 和最近轮次日志、其他已合并 session 报告；再看未合并 PR 的经验作为未经验证的线索。要写明本轮借鉴了哪份记录、如何验证、为什么继续调整。
- 如果当前轮的 PR 未合并：继续在自己的隔离分支上研究，或创建以自己的上轮 commit 为基础的新分支；不得把别人的未合并工作当作 main 的既定事实。
- 永远不要因为共用仓库就共用模型权重文件名、远端 Artifact 名或同一研究日志路径。

## 启动与退出验收

启动：核对可写仓库 → 生成唯一 Session ID → 记录 base SHA → 查并发 PR 避冲突 → 选择研究假设 → 独立分支。
退出：完成真实模拟对局 → 验证收据 → 训练/评测 → 独立代码提交 → 会话日志/经验提案 → PR/CI → 向用户交付 GitHub 链接。不允许伪造训练或比赛结果。
