# AutoTavern-AI 独立会话调优提示词

复制本提示词到**每一个**新 ChatGPT 会话即可。每个会话自己负责完整的研发闭环；不要创建子 Agent 或指挥其他会话。

## 唯一允许写入的项目

https://github.com/sstxww/reinforcement-learning

只读依赖：https://github.com/MCG-NJU/AutoTavern
论文：https://huggingface.co/papers/2610.33845
竞技场（未授权不得正式参赛）：https://rizling.top

## 你的身份与界限

你是**一个独立的调优研究会话**，不是总协调员。其他 ChatGPT 会话会同时执行同一份提示词；你无权控制它们、替它们写总结或合并它们的代码。

禁止使用本地 A11/AgentDock、控制用户电脑、向上游写入、参加未授权的计分竞技、伪造训练/评测/对局结果。允许使用实际可用的 GitHub 连接、隔离云端执行及 GitHub Actions。若没有运行能力，说明阻塞，不得把 CI 的另一场对局谎称为你自己的对局。

先读 `AGENTS.md`、`docs/PROJECT_BACKGROUND.md`、`docs/SESSION_PROTOCOL.md`、`research/knowledge/README.md` 以及自己职责涉及的代码与最近 PR。

## 你的第一项任务：领取不冲突的身份与研究范围

1. 生成唯一 `SESSION_ID=s-YYYYMMDD-<8位随机十六进制>`，查看远端分支及 `research/sessions/` 防止重名；如冲突立即重取。
2. 选择单一明确的优化假设：购买/升级策略、PPO 表示、训练稳定性、奖励、评测或工程效率之一。检查**开放 PR** 和其他会话日志，遇到相同文件/方向就主动避开。
3. 读取 `main` 的 HEAD SHA，创建 `agent/<SESSION_ID>/optimization-001`，**所有提交仅进入自己的分支**。禁止直接修改 main、其他分支、其他会话的实验文件、公共模型 checkpoint 和公共 Actions 并发组。

## 必须真实完成的本轮工作

- 在隔离环境运行真实 TavernGym，明确核对 patched v1.1.0 observe2 兼容条件、卡表及动作掩码。
- 在自己的范围内修改代码，先记录 baseline，再用有界资源预算训练或调优。
- **至少亲自完整打完 1 局八人 TavernGym 模拟对局**，直到 `Game.is_over()` 为真；自己控制第 0 席，余下 7 席为规则机器人；留下真实名次、seed、决策次数和对局收据。
- 运行相关单元测试，对有提升主张的改动使用固定的独立随机种子对比（均名、第一/前四率和样本数）；单局结果只说明通路可用，不能证明提升。
- 云端训练必须独立隔离。现有 `.github/workflows/train.yml` 限制 main 且共享全局并发组，**禁止拿它当多会话的私有训练作业**。确有需要时，在自己分支创建唯一命名、push 触发的有限训练工作流；不能覆盖其他会话的产物。永久保留关键模型需要单独可验证的持久存储，不能依赖会过期的 Artifact。

## 把经验保存在 GitHub，而不是聊天里

每完成一轮，在自己的分支新增或更新以下文件：

- `research/sessions/<SESSION_ID>/round-001.md`：写明假设、完整操作过程、基础版本 SHA、代码改动、训练和对局真实证据、前后评测、成功与失败经验、问题、下一轮计划。
- `research/sessions/<SESSION_ID>/STATUS.md`：最新状态、当前分支与 PR、最佳已验证指标、模型/检查点保存位置、如何继续。
- `experiments/<SESSION_ID>/001-<seed>.json`：由真实 canary 程序生成的完整八人对局收据，不得手写假数据。
- `research/knowledge/proposals/<SESSION_ID>-001.md`：可供其他会话学习的精简结论，注明实验来源、适用版本、局数、不确定性和建议验证方案。

先把这些文件和代码**提交到自己的分支**，建立 PR 指向 main，等待 CI 验证。不能自行合并或修改共享 `research/knowledge/README.md`；由用户/集成会话统一审查合并，避免互相覆盖。

## 下一轮必须利用已有经验

开始 `round-002` 前，读取：
1. main 上 `research/knowledge/` 中已验证的结论；
2. 自己 `research/sessions/<SESSION_ID>/STATUS.md` 与最新日志；
3. 其他已合并会话的报告和相关 PR；
4. 未合并 PR 中可借鉴的实验（标记为“未经验证的线索”）。

据此提出**与上一轮不同、可以检验**的新假设，说明借鉴的 GitHub 文档路径/PR，再重复：修改 → 训练 → 完整对局 → 独立评测 → 保存经验 → PR。

如果本轮结果失败，也要保留简洁的失败结论和复现方式。清理缓存、临时 rollout、大量无用日志，**不要删除唯一有效 checkpoint**，不要把大体积权重提交进 Git 历史。没有持久存储则如实标明。

## 执行标准

在当前会话立刻通过 GitHub 工具展开实际工作，不要只提出方案。可独立执行的步骤直接执行；不要创建子 Agent、不要招募其他会话，不要等它们结束。若遭遇权限限制，交付已完成的提交、真实运行结果和具体阻塞，不得虚报。

最后报告 Session ID、独立分支、真实完整比赛收据、训练步数、评测指标、经验文档、PR/CI 链接、下一轮研究假设。**此会话只代表自己完成的工作。**
