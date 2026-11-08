# 贡献指南 · Contributing

感谢你愿意参与自然道（NaturalDAO）。请按改动范围查阅对应的说明和检查步骤。

Thanks for contributing to NaturalDAO. Find the workflow and checks for the area you want to change.

| 你要改的内容 | 位置 | 流程 |
| :--- | :--- | :--- |
| AI 治理层协作（数据、评测、模型、任务） | `PoL-Governance/` | 见 [AGENTS.md](PoL-Governance/AGENTS.md) 和 [README](PoL-Governance/README.md) |
| 治理服务与 Agent 接入 · Runtime and Agent integration | [POL2-Steward/](POL2-Steward/README.md) | 从[服务说明](POL2-Steward/pol2-service/README.md)查找测试和接入步骤 |
| 研究报告与图件 · Research reports and figures | [Research/](Research/README.md) | 按主题归档并更新索引。可复现实验按其项目说明提交 |

## 提交改动 · Submit changes

从最新的 `main` 开分支并提交 PR。Agent 的试验请使用任务分支。涉及引用或复用时，在改动中注明来源。

理论、翻译与开发规划改动请提交到 [NaturalDAO](https://github.com/naturaldao/NaturalDAO)，参阅其[贡献指南](https://github.com/naturaldao/NaturalDAO/blob/main/CONTRIBUTING.md)。

## PoL-Governance

任务领取、分支命名（`pol/<任务ID>/<短名>`）、任务页、数据边界和交付检查都写在 [PoL-Governance/AGENTS.md](PoL-Governance/AGENTS.md)，以那里为准。两条最重要的：

- **私有保留集、凭据、私有真实对话不进入任何公开分支、fork、PR、日志或截图。** 误提交时立即停止传播并通知维护者；删除最新文件不能清除 Git 历史，含凭据时还需撤销凭据。
- 交付前在 `PoL-Governance/` 目录运行 `uv run --no-project --offline python tools/check.py`，并检查 `git diff --cached`。

## 许可与署名 · License and credit

本仓库当前的许可声明为 [Proof of Love2](LICENSE)。提交前请确认你有权按该许可声明提交内容，并标明引用来源。此前版本如已按 CC0 或其他许可发布，既有授权不因本次更新而撤销；第三方材料仍遵循各自许可。

## AI 辅助 · AI assistance

可以使用 AI 辅助撰写或整理，但请在 PR 中说明，并由提交者本人核对内容和引用。

## 提问与讨论 · Questions

- 治理评测、数据、服务与复现问题：在本仓开 Issue，选择对应模板。
- 例会：见 [主仓首页](https://github.com/naturaldao/NaturalDAO)中的例会信息。
- 安全与敏感内容：见 [SECURITY.md](SECURITY.md)，不要公开发 Issue。

---

**English summary.** Branch from the latest `main` and open a PR here for governance, Steward, or research changes. Use a task branch for agent experiments. Follow [the agent guide](PoL-Governance/AGENTS.md) for governance work. Submit theory, translation, and planning changes to [NaturalDAO](https://github.com/naturaldao/NaturalDAO). Credit reused material and disclose AI assistance. Earlier releases and third-party materials keep their existing grants and licenses.
