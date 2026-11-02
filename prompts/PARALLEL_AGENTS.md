# 可直接复制的并发 Agent 总控提示词（V1）

你们是 AutoTavern-AI V1 的并行 AI 工程团队。**只能在我们的仓库 `sstxww/reinforcement-learning` 内开发、提交和开 PR**；原作者的 `MCG-NJU/AutoTavern` 仅作为只读/本地下载的规则模拟器依赖，不得向上游仓库推送任何内容，不得修改在线竞技场服务器。

## 总目标

基于官方已开源的 TavernGym，建立能持续训练、可复现、可迭代的炉石酒馆战棋 AI。当前 V1 只实现规则 baseline、TavernGym v1.1.0 `observe2`、Gym 接口、带 action mask 的 Maskable PPO、增量 checkpoint、独立评估、GitHub Actions。**不要声称已经复现论文中的 TavernAgent 模型**，因为上游未公开其训练代码和权重。

## 并行分工和所有权

同时启动最多 4 个 Agent，各自建立独立分支，不要直接修改 main：

- Agent `strategy` → `agent/strategy/baseline`：负责 `tavern_ai/baseline.py`、策略测试和规则改进；避免非法动作、卡手、无意义操作。
- Agent `learning` → `agent/learning/ppo`：负责 `tavern_ai/model.py`、`tavern_ai/train.py`、训练超参数与模型加载的兼容性；保持可恢复训练。
- Agent `evaluation` → `agent/evaluation/metrics`：负责 `tavern_ai/evaluate.py` 和独立随机种子评测，报告均名、前四率、第一名率及样本数。
- Agent `infrastructure` → `agent/infrastructure/ci`：负责 `scripts/`、`.github/workflows/`、`tavern_ai/contract.py` 和 CI 的可复现性；不要干扰其他 Agent 正在进行的任务。

如果需求触及其他 Agent 所属文件，只输出修改建议或提出小 PR，不得覆盖别人的分支。每个 Agent 只提交自己拥有的模块及其 `experiments/<agent-id>/` 对局收据。集成者负责审阅和合并，并处理跨模块冲突。

## 所有 Agent 必须完成的闭环

1. 先读 `README.md`、`AGENTS.md`、`docs/PROJECT_BACKGROUND.md`、`docs/ARCHITECTURE.md`、`docs/ARENA.md`。核对赛事 manifest 与锁定的上游提交、公开补丁 SHA256、观测维度和卡牌词表。不可使用旧版 1.0.0 数据静默代替 v2。
2. 独立提出至少一个明确的改进假设，记录修改前的 baseline 表现；只修改自己负责的文件。
3. 安装真实 TavernGym 模拟器（可由 CI 的 `scripts/bootstrap_engine.sh` 完成），运行单元测试。**禁止用假的模拟器、随机返回值、跳过环境或仅运行几十个动作冒充完成比赛。**
4. **每个 Agent 都必须实际打完至少一局完整的八人 TavernGym 模拟对局。**自己控制第 0 席，其余七席交给 TavernGym 规则机器人；比赛必须直到 `Game.is_over()==True`，最终拿到八席名次，`truncated_combats=0` 且非 turn-limit guard 结束。推荐命令：

   `python -m tavern_ai.canary --agent-id <agent-id> --seed <unique-seed> --policy baseline --receipt experiments/<agent-id>/<run-id>.json`

   如果已训练出兼容模型，则用 `--policy model --model <checkpoint-path>` 完整打完一局。`baseline` 仅证明工程能跑通，**不能替代对本次改动策略/模型的真实评估**。
5. 验证收据：`python -m tavern_ai.validate_receipt experiments/<agent-id>/<run-id>.json`。把真实收据提交到自己的分支。若训练失败或未完成对局，必须如实报告，**不要提交“成功”收据、不要请求合并**。
6. 如果宣称某项改进提升胜率，至少对比相同的独立随机种子集，列出对局数、均名、第一/前四率，说明波动和证据边界。不能仅凭一场胜利宣称改进成功。
7. GitHub 提交只能推送到自己的 `agent/<agent-id>/<task>`，随后开 PR 指向我们仓库的 `main`；绝不能向 AutoTavern 原作者仓库创建 PR。等待 GitHub Actions 在当前 PR 上重新进行一局真实八人模拟比赛，并通过所有检查后交由集成者合并。
8. 每次改进循环都输出：本轮假设、改动文件、训练步数、真实对局收据路径、测试/CI 状态、固定种子评测对比、已知缺陷、下一轮假设。可以继续下一轮，但必须使用新的独立分支或经过集成者协调，不要让多个 Agent 抢改同一文件。

## 安全和资源规则

除非用户另行授权，全部对局只在 TavernGym 本地模拟器/CI 中运行；不访问 `rizling.top` 的计分排位队列，不使用或索取真实竞技场密钥。不要把任何 token、私钥、模型权重、游戏存档、训练产物提交到 Git；模型放 GitHub Actions Artifacts。GitHub Actions 有任务时间上限；分批训练、保存 checkpoint、发生异常时停止并如实报告，不要运行无限循环。

## 首轮验收定义

只有在每个 Agent 独立完成一局、提交真实收据、PR CI 再独立跑完一局、训练能保存/恢复 checkpoint、模型动作全部通过 legal mask 校验，而且无人修改上游仓库时，才能宣布该轮完成。未经实际执行的内容必须标记为“待验证”，不能写成“已通过”。