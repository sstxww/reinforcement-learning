# AutoTavern-AI V1 — 项目背景和研究任务

## 1. 项目定位

AutoTavern-AI 是独立于原研究团队的开源 AI 强化学习实验仓库。项目的目标不是
重写《炉石传说》或部署游戏服务器，而是复用 `MCG-NJU/AutoTavern` 公开的
**TavernGym** 规则模拟器，在相同的规则和合法动作约束下训练自己的酒馆战棋策略模型。
后续模型可通过 TavernArena 官方连接器在参赛者自己的环境中推理。

本项目 V1 专注建立 **可复现、可持续训练、允许多个 AI Agent 并行迭代的工程基线**。
游戏模拟、数据采集、策略评测和训练都在隔离环境运行；仅提交自己的实验代码、
配置、文档及不含敏感数据的实验结果到 `sstxww/reinforcement-learning`。

## 2. 上游与限制

- 上游： https://github.com/MCG-NJU/AutoTavern
- 研究文章： https://huggingface.co/papers/2610.33845
- 在线竞技场： https://rizling.top
- 竞赛协议： https://rizling.top/protocol
- 当前环境清单： https://rizling.top/api/v1/manifest

原 AutoTavern 公开 TavernGym 和 TavernBench，但是**不含**论文中 TavernAgent
的权重、训练代码或完整自动科研系统。V1 的模型、训练算法和 Agent 协作方案
是我们自行实现的，不是官方复刻。不得声称达到论文的胜率。

竞技场目前运行 TavernGym 1.1.0 的 `observe2` 契约：
- `features`：float32[4017]
- `cards`：int32[447]
- `action_mask`：bool[245]
- TavernGym 源码指纹：`6d8712c93022ba11`
- 定位与基准固定在 `tavern_ai/contract.py`，使用上游固定提交和已验证公开补丁

**环境变化必须人工核对并创建迁移 PR**。相同维度不代表卡牌索引相同，
旧 checkpoint 不能静默在新词表上继续训练。

## 3. V1 研究目标

第一阶段完成合法且可重复的策略基线。第二阶段以 Maskable PPO 训练一席玩家
对抗 7 个 TavernGym 规则机器人，保存完整训练状态和模型权重。第三阶段让多个
研究 Agent 并行提出可验证改进，各自运行完整对局，带结果和假设回到独立 PR。

V1 核心指标：**完整对局率、非法动作数、单局推理稳定性、平均名次、第一名率、
前四率、每一训练步成本、不同随机种子的泛化表现**。训练奖励和竞技场积分
是不同统计口径，不能混淆。

V1 明确不包括：训练论文中的原始 TavernAgent、真正的八玩家强化学习自博弈训练、
公开服务器常驻托管、GPU 大规模训练、Blizzard 正式客户端自动化、对手隐藏信息访问。
这些可作为 V2 工作提案。

## 4. 多 Agent 协同

建议 4 个并行 Agent：策略与基线、模型与 PPO、评测与统计、工程与兼容。
每个 Agent 领取互不重叠的文件范围，独立分支 `agent/<id>/<task>`，
独立 `experiments/<id>/<run>.json`，禁止互相覆盖。

所有 Agent 均须完成 **至少一局真正的 TavernGym 八人完整模拟比赛**（自己控制
一席，另外七席由模拟器规则机器人驱动）。`Game.is_over()` 为真，
记录最终 `placements` 后才允许提交。每个 PR 的 CI 还会重新执行一局，
没有游戏收据的 PR 不能合并。

不同 Agent 的游戏只是工程冒烟验证。真正的性能比较必须使用固定的独立评测
随机种子、多场对局和样本量，不能把偶然拿到第 1 名当作显著性能改进。

## 5. 训练与持久化

GitHub Actions 的 `train.yml` 是**按周 + 可手动触发的有限时间增量训练**。
它从上次成功训练的 Artifacts 恢复模型和兼容元数据，继续 PPO 训练，
然后进行完整对局和独立评估，并上传新 checkpoint。

> GitHub Actions 不是无限时长 GPU 服务。Artifacts 默认存在保留期限；本项目
> 设置 90 天。若长时间没有成功任务或旧 Artifacts 过期，就无法自动恢复，
> 必须由维护者从其他备份恢复模型。当前版本不是永久耐久的模型数据库。

工作流默认 CPU 小步推进，真实训练效果取决于随机种子、数据、模型结构及
资源。要构建有竞争力的模型，后续需要更多训练预算和更强对手。

## 6. 正式竞技边界

在项目内部通过完整模拟对局和测试之后，才可以在 `rizling.top` 进行练习。
进入会计分的 `arena` / `standard` 匹配之前，需要仓库拥有者明确批准。
私钥只通过本地环境变量或 GitHub Actions Secrets 提供，不应写入任何仓库文件。
Arena 的模型始终在参赛端推理，不上传权重。

## 7. 可验收的 V1 里程碑

- [x] 可安装项目骨架、代码规范和仓库安全边界
- [x] TavernGym pinned 1.1.0 安装脚本及哈希校验
- [x] 合法动作规则 baseline、八人完整对局收据程序
- [x] MaskablePPO 训练、增量 checkpoint、评测 CLI
- [x] CI 全局对局闸门及训练流水线定义
- [ ] 首次 GitHub Actions CI 实跑成功（仓库创建后执行）
- [ ] 第一次实际 PPO 训练 Artifact（仓库创建后执行）
- [ ] 多 Agent 实际并发 PR 及每个 Agent 的独立完整对局（授权并发后执行）
- [ ] 真人参赛账号练习与正式对局（另行授权）