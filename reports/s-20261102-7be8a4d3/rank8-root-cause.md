# V5 第八名问题：证据分层根因审计（2026-11-02）

> 状态：**行为异常已得到真实对局佐证；原因机制尚未证明**。此报告不能用来晋升 Champion 或启动大规模 PPO。

## 可复核的既有真实结果

- 主候选 V2 发布 [v2-learning-41413557445](https://github.com/sstxww/reinforcement-learning/releases/tag/v2-learning-41413557445)，真实 1280 PPO 步，完整模型控制八人对局 seed 23002 第 **8** 名；相同独立 seeds 24000–24003 上，新 V2 名次 **[8,8,8,8]**，V1 亦为 **[8,8,8,8]**，规则 Baseline 为 **[7,6,8,8]**。后者平均 7.25，新模型平均 8.00；四场样本不足以量化稳定差距，但不能声称 PPO 获得提高。来源：[PR #15](https://github.com/sstxww/reinforcement-learning/pull/15)，成功训练 [41413557445](https://github.com/sstxww/reinforcement-learning/actions/runs/41413557445)。
- 独立低学习率诊断 [PR #60](https://github.com/sstxww/reinforcement-learning/pull/60) 在真实独立 seeds 42174–42176（各三场完整对局）观察到：低 LR 1e-4 候选名次 **[8,8,8]**，共 36 次选择，其中 21 次 END_TURN、**0 次 BUY**、0 安全强制结束；3e-4 对照名次 **[8,8,7]**，875 次选择，其中 20 次 BUY、3 次模型选 END_TURN、21 次强制结束，最多连续相同动作 **40** 次。来源：仓库 `reports/s-20261102-24728f13/002-action-telemetry.json`（PR 分支），成功运行 [41418438337](https://github.com/sstxww/reinforcement-learning/actions/runs/41418438337)。
- [PR #39](https://github.com/sstxww/reinforcement-learning/pull/39) 对未经改动的 **规则 Baseline** 做 6 场真实比赛，已观测 127/127 合法动作、0 同回合相同公开观测重复；这**不能**外推到 PPO。它现已通过 SHA 锁定合并集成。

## 可能机制及可证伪条件

1. **过早结束回合或合法购买机会未被利用。** “36 次动作中 0 BUY”得到观察证实，但尚缺每一步金币、合法 BUY 掩码及剩余商店选择；因此无法证明购买机会被模型主动放弃。必须在同一模型的回合级轨迹中计算 `buy_legal_opportunities`、`buy_chosen_given_legal`、`gold_unspent_on_end`。
2. **有效状态无进展动作循环。** 3e-4 对照最长连续 40 次同类/同编号动作，21 次安全结束；需记录精确的动作编号、状态 SHA、执行前后状态、金币变化，区分不同状态下同类动作与真正无进展循环。
3. **训练/评测契约与奖励。** 主分支 `TavernEnv` 检查 observe2 4017/447、245 掩码，但还没有证明训练对局中的收益/优势信号与完整八人竞技目标一致。检查 Reward、Advantage、Entropy、value loss、动作族覆盖率；不要在证据不足时直接重调奖励。
4. **经济规则 Baseline 本身偏弱。** `BaselinePolicy` 优先 Play/选择并根据固定回合升级和购买，不含卡牌价值、阵容协同或长期经济规划；同种子 baseline 均分 7.25 不代表强教师，也不能把其动作强行复制作为性能证明。

## 下一关门槛

- 首先对恢复验证通过的原模型及续训候选各运行真实完整对局，区分可恢复性和竞技表现（本会话专用 Actions [41428181901](https://github.com/sstxww/reinforcement-learning/actions/runs/41428181901)，开始时未完成）。
- 之后在独立 PR 中加非干预式每回合合法动作和金币跟踪，同时验证观察不改变相同种子的真实比赛结果；与 baseline 在同一席位、独立种子、明确 fallback 标签下比较。
- 在买牌与动作循环根因可证实前，**停止无目的扩大 PPO 步数**。即便恢复训练成功，只能算流程烟雾测试，不是实力提升。

## 证据边界

没有重新下载每一历史 Release 的模型做多种子复测；历史结论仅引用其 GitHub 实验和 PR 原始数据。此文件中的“已证实”仅指上述可核查具体比赛及记录，不等于得出单一因果根因。无正式 Arena 对局。