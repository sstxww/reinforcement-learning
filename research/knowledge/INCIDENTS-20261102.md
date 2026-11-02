# 2026-11-02：并行实验早期故障观察

**来源**：GitHub Actions 真实运行日志；这些记录是排查线索，不应当代替后续每个会话复核最新状态。

| 症状 | GitHub 证据 | 初步分类 | 下一步验证 |
| --- | --- | --- | --- |
| 初始 PPO 检查点可以加载推理，但完整比赛触发步数上限 | [检查点恢复运行](https://github.com/sstxww/reinforcement-learning/actions/runs/41412807456) | 候选策略无法推进，未完成完整比赛 | 在独立分支采集合法动作序列、回合/状态循环，修复后由候选策略真实完成游戏 |
| GitHub Release 上传返回 403 Resource not accessible by integration | [检查点恢复运行](https://github.com/sstxww/reinforcement-learning/actions/runs/41412807456) | 运行凭证权限/上下文不足 | 核对所需的最小权限和仓库策略；用 Artifact 临时隔离模型，不宣称持久化 |
| 测试预期动作 55，实际 61 | [站位策略失败运行](https://github.com/sstxww/reinforcement-learning/actions/runs/41413065664) | 决策逻辑与回归测试不一致 | 核对 action 46–125 的手牌/站位编码，确定是策略还是测试错误 |
| 多次 CI、实验作业取消或失败 | [仓库 Actions](https://github.com/sstxww/reinforcement-learning/actions) | 分支频繁推送、失败重试和并发资源消耗 | 每会话独立 concurrency；一次原始运行+至多两次真正修复；禁止自动提交触发死循环 |

本观察不表示上述问题在所有最新分支上仍存在。其他会话工作尚在进行中；合并前检查最终 head commit 的 CI、PR 冲突、真实对局与独立评测。未经验证的 PPO 不得晋升为 Best。

**知识库规则**：具体故障总结可被新会话引用，正式共享优化结论仍必须经集成者审查后才进入公共知识库。
