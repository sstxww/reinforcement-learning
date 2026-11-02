# V5 R001 — 第八名行为证据复核（跨会话已提交数据，未开展新比赛）

**Session:** `s-20261102-1aff5449`。**证据等级：**从仓库 main 上真实实验记录读取并比对；本会话没有自行运行这些 PPO 比赛或重建因果实验。分析基于 TavernGym 1.1.0 / observe2 / 245 actions 的相同环境指纹 `6d8712c93022ba11`。

## 1. 三个相互独立的故障信号

1. **合法可买但模型不买（观察证实）。** 主分支 `reports/s-20261102-83d91476/001-buy-opportunity-report.json`：V2 1280-step 模型在 seeds 45111、45112 的**两场完整八人游戏**排名 [8,8]；248 个模型动作中，74 次动作时至少存在一个 mask-legal BUY，但 **0 次 BUY**；raw action IDs 1/2 占 222/248。相同 seeds 规则 baseline 排名 [6,7]，购买 33 次（48 次合法 BUY 暴露）。两场无安全强制结束。**注意**：74 次动作级暴露不是 74 个独立购买机会，更不能证明每一次购买都具有正收益。
2. **Hero Power↔Cancel 无进展循环（在有界不完整试验中证实）。** `reports/s-20261102-ba09e2d4/002-action-opportunities.json`，seed 87102 **未完成的诊断**达到 6000 决策上限，卡在 turn 3；动作 Hero Power 2978、Cancel 2977，0 BUY，10 次合法 BUY 决策，未发生安全 fallback。该诊断**不是**完整对局收据，不能赋予排名。它显示具体循环机制，而非仅凭“大量重复动作”猜测。
3. **完成对局仍然没有竞技收益（观察证实）。** `reports/s-20261102-ba09e2d4/005-guarded-evaluation-summary.json`：V2 在 seeds 87102/87103 的**guarded**完成游戏排名 [8,8]、BUY [0,0]；同种子 baseline [5,7]。guard 干预 [4,0] 次；必须与不使用 guard 的原始 PPO 表现分开报告。另一个已提交 draft PR #107 的强制 BUY 消融，在三场中执行 46 次 BUY，名次仍为 [8,8,8]，并记录 Play/Cancel 循环；**“只纠正 BUY 频率”不足以证明竞争力**。

## 2. 根因强度及未证明事项

- **已证实**：V2 策略在多个实测状态里未利用 mask-legal BUY，部分运行出现 Hero Power/Cancel 循环及完整游戏难以推进；多个完整游戏排名第八。保护性强制结束不能当作原生模型策略胜利。
- **未证明**：观测编码、动作掩码实现、奖励函数、优化器状态或学习率是导致这些行为的单一因果根源；合法购买也不必然是正确购买；一次单因素 Buy-override 失败不表示所有经济策略无效。
- **新一轮实验可证伪假设**：对准确恢复的模型以不改变推理动作的记录器收集每回合前后状态、当前金币、商店价格、场上随从/手牌、合法 BUY/PLAY/END 切片、动作族概率、游戏推进度。先检查 Hero Power→Cancel 的状态是否往返、PLAY 后取消是否合法且是否从手牌落地；在这些问题修复后再做少步 checkpoint-resume 烟雾验证。测试训练种子与 heldout 种子隔离，区分“raw”与“guarded”。

## 3. 本会话的执行边界

本会话实际修改现有统一 `tavern_ai/evaluate.py` 的完整对局证据校验，使未来不把受 guard/fallback 的成绩混入原始模型评测。没有重训 PPO、没有下载或另存模型权重、没有自行重复上述诊断，也没有宣布 Champion。只有验证了训练恢复/合法动作/真实完整比赛的独立候选，才能扩大训练预算。

**来源：** main 上的上述三个 report 文件；draft [PR #103](https://github.com/sstxww/reinforcement-learning/pull/103) 与 [PR #107](https://github.com/sstxww/reinforcement-learning/pull/107)（后两者未合并，作为独立重复实验线索；不得当作 main 已验证规范）。
