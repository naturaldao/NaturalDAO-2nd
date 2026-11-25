<div align="center">

# 🌿 NaturalDAO-2nd · 自然道

**爱2证明的研究与复现**<br>
**Research and reproducibility for Proof of Love2**

[![Research index](https://img.shields.io/badge/Research-Index-2F855A?style=flat-square)](Research/README.md)
[![POL2 Steward developer preview](https://img.shields.io/badge/POL2%20Steward-Developer%20preview-3768A3?style=flat-square)](POL2-Steward/README.md)
[![Hugging Face: NaturalDAO](https://img.shields.io/badge/Hugging%20Face-NaturalDAO-E4AD32?style=flat-square)](https://huggingface.co/NaturalDAO)
[![License: Proof of Love2](https://img.shields.io/badge/License-Proof%20of%20Love2-64748B?style=flat-square)](LICENSE)

[简介](#-简介--about) · [仓库结构](#-仓库结构--repository-layout) · [研究与复现](#-研究与复现--research-and-replication) · [参与协作](#-参与协作--contribute) · [最近更新](#-最近更新--recent-activity) · [相关资源](#-相关资源--resources)

</div>

---

## 📖 简介 · About

自然道的研究报告、治理评测、实验复现材料在这里协作和发布。爱2证明理论与开发规划见 [NaturalDAO 主仓](https://github.com/naturaldao/NaturalDAO)。

This repository brings together NaturalDAO’s research, governance evaluations, and replication materials. The foundational theory and development plans live in the [main repository](https://github.com/naturaldao/NaturalDAO).

---

## 📂 仓库结构 · Repository Layout

| 入口 · Entry point | 可以在这里找到 · What you’ll find |
| :--- | :--- |
| 📚 [研究总索引 · Research](Research/README.md) | 研究问题、报告、论文与复现入口 |
| 🧪 [运行评测 · Run evaluations](PoL-Governance/benchmark/README.md) | [治理评测项目](PoL-Governance/README.md)的评测工具、[结果索引](PoL-Governance/results/README.md)、数据和模型 |
| 🛠 [安装 POL2 Steward · Set up Steward](POL2-Steward/pol2-service/README.md) | [治理服务开发者预览](POL2-Steward/README.md)、安装和 Agent 接入 |
| 🤝 [参与协作 · Contribute](CONTRIBUTING.md) | [任务看板](PoL-Governance/TASKS.md)与研究提交清单 |
| 🎞 [项目媒体 · Media](media/README.md) | 图片、演示和对外材料 |
| [合作交流 · Partnerships](BD/README.md) | 公开合作入口与通用邀约模板 |

---

## 📚 研究与复现 · Research and Replication

| 研究方向 · Topic | 阅读 · Read | 复现或核查 · Reproduce or verify |
| :--- | :--- | :--- |
| **具身治理** | [授权、撤权与恢复研究](Research/Embodied/README.md) | [具身评测代码与运行说明](PoL-Governance/benchmark/embodied_reasoning/README.md) |
| **神经状态与动态治理** | [目标记忆撤销与恢复实验](Research/Brain/README.md) | [连接模板、冻结协议与复算](PoL-Governance/benchmark/fly_brain/README.md) |
| **存储与数据基础设施** | [V2 方案与证据边界](Research/Storage/README.md) | [容量复算与假设](Research/Storage/03-复算与支撑/README.md) |
| **DAO 治理机制** | [投票、资源分配与申诉实验](PoL-Governance/research/PoL2-DAO-Governance-Lab/README.md#结果) | [运行示例与测试](PoL-Governance/research/PoL2-DAO-Governance-Lab/README.md#快速开始) |
| **类型化决策模型** | [PoL2 × Jev 正文](PoL-Governance/research/PoL2-Jev-Typed-Literature-Survey/paper/main.pdf) · [在线附录](PoL-Governance/research/PoL2-Jev-Typed-Literature-Survey/paper/online_appendix.pdf) | [文献编码与构建方法](PoL-Governance/research/PoL2-Jev-Typed-Literature-Survey/README.md#复现) |

智能体记忆与工程设计见[工程研究索引](Research/Engineering/README.md)。

---

## 🤝 参与协作 · Contribute

1. **查任务。** 从[副仓任务看板](PoL-Governance/TASKS.md)查看任务、进展和交付入口。
2. **做研究。** 按 [Agent 协作指南](PoL-Governance/AGENTS.md)使用任务分支，在任务页记录证据与下一步。
3. **交付成果。** 按[研究提交清单](CONTRIBUTING.md#提交研究--submit-research)更新主题索引，并把 PR 提交到本仓。

---

## 🪾 最近更新 · Recent Activity

主分支最近 7 天的更新按人、按日汇总（UTC+8），最多 15 行。每行显示最新两项，其余见「其他更新」。点击文件名打开对应版本，点击「详情」查看完整变更。

Main branch updates from the past seven days, grouped by contributor and day (UTC+8), up to 15 rows. Each row shows the two latest updates. File names open the changed version, and “Details” opens the full change.

<!-- readme-activity:start -->

| 序号<br>No. | 时间（UTC+8）<br>Time (UTC+8) | 更新人<br>Contributor | 更新详情<br>Update details |
| ---: | --- | --- | --- |
| 1 | 11-25 11:57–12:05 | [@w609641894](https://github.com/w609641894) | <strong>12:05 · Mark GOV-02 task as published</strong><br>　　[GOV-02-kev-pol2-governance-hybrid.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/2f654dd659cc2a35026d393a737bc0aeb41165e7/PoL-Governance/tasks/GOV-02-kev-pol2-governance-hybrid.md)<br><br><strong>11:57 · Add POL2 governance hybrid v2+v4 unknown-gate model &#40;GOV-02&#41;</strong><br>　　[full-release.json](https://github.com/naturaldao/NaturalDAO-2nd/blob/2dd301c9297e5e406fb26fd9dd32553717a8cbe1/PoL-Governance/datasets/pol2/governance-v2/manifests/full-release.json) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/2dd301c9297e5e406fb26fd9dd32553717a8cbe1) |
| 2 | 11-24 01:35–16:14 | [@Aranna-0572](https://github.com/Aranna-0572) | <strong>16:14 · docs&#40;BD&#41;&#58; link outreach status log</strong><br>　　[README.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/0f4bcf95135c2acb97a1ccad775d82b0a4d919c2/BD/README.md)<br><br><strong>16:14 · docs&#40;BD&#41;&#58; record first outreach status</strong><br>　　[OUTREACH-STATUS.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/4f52bf6e5c3c998f96f6398c806e74ccff3c9317/BD/OUTREACH-STATUS.md)<details><summary>其他更新 · Other updates (2)</summary><strong>01:44 · Pol/eval 05/blind replay</strong><br>　　[SCHEMA.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/c206612531394760c2bdb93495d8c4b7ce0b5e2d/PoL-Governance/benchmark/love_hate_behavior/SCHEMA.md) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/c206612531394760c2bdb93495d8c4b7ce0b5e2d)<br><br><strong>01:35 · Claim EVAL-05 offline JSONL validation</strong><br>　　[SCHEMA.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/1c2bd34c83bfcaed7427aa0f90cf133eb9704a43/PoL-Governance/benchmark/love_hate_behavior/SCHEMA.md) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/1c2bd34c83bfcaed7427aa0f90cf133eb9704a43)</details> |
| 3 | 11-24 14:33 | [@shentonyan](https://github.com/shentonyan) | <strong>14:33 · EVAL-05：arXiv 论文行文方案与首轮配对试标设计</strong><br>　　[ARXIV-PAPER-PLAN.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/34953670b2aaba1d9577018c2e71157866b2044a/PoL-Governance/research/PoL2-Love-Hate-Behavior-Evaluation/ARXIV-PAPER-PLAN.md) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/34953670b2aaba1d9577018c2e71157866b2044a) |
| 4 | 11-24 01:49 | [@codex](https://github.com/codex) | <strong>01:49 · Revert "Merge pull request &#35;29 from naturaldao/pol/EVAL-05/blind-replay"</strong><br>　　[SCHEMA.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/f2437d1b0c23ae3f203c53baa5f325b9347260b4/PoL-Governance/benchmark/love_hate_behavior/SCHEMA.md) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/f2437d1b0c23ae3f203c53baa5f325b9347260b4) |
| 5 | 11-22 22:45 | [@shentonyan](https://github.com/shentonyan) | <strong>22:45 · docs&#58; organize governance research reading and evidence navigation</strong><br>　　[LITERATURE.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/a92332c2c8f0e84a28706b2be0a715e281b1bb02/PoL-Governance/research/LITERATURE.md) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/a92332c2c8f0e84a28706b2be0a715e281b1bb02) |
| 6 | 11-19 14:08–16:49 | [@Aranna-0572](https://github.com/Aranna-0572) | <strong>16:49 · docs&#58; index Nov 18 PoL weekly meeting notes</strong><br>　　[README.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/012e0790a74108fd6ed2e8ea82a2952784707e84/PoL-Governance/meetings/README.md)<br><br><strong>16:49 · docs&#58; add Nov 18 PoL weekly meeting notes</strong><br>　　[2026-11-18-pol-weekly-meeting.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/579b919825544a5cb876ebd12bc937c7071130a5/PoL-Governance/meetings/2026-11-18-pol-weekly-meeting.md)<details><summary>其他更新 · Other updates (3)</summary><strong>16:43 · docs&#58; index Nov 19 PoL weekly meeting notes</strong><br>　　[README.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/ffea17a91c01c402fe19800e7846fa3cc80f0e01/PoL-Governance/meetings/README.md)<br><br><strong>16:43 · docs&#58; add Nov 19 PoL weekly meeting notes</strong><br>　　[2026-11-19-pol-weekly-meeting.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/e2b41726e18187c6716316d632292b2925773e01/PoL-Governance/meetings/2026-11-19-pol-weekly-meeting.md)<br><br><strong>14:08 · EVAL-05&#58; prepare PDF-aligned pilot review</strong><br>　　[SCHEMA.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/411fa45719d65d9de5e4e2a37237849d8798f1bb/PoL-Governance/benchmark/love_hate_behavior/SCHEMA.md) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/411fa45719d65d9de5e4e2a37237849d8798f1bb)</details> |
| 7 | 11-19 14:10–15:11 | [@shentonyan](https://github.com/shentonyan) | <strong>15:11 · Define reference facts, experimental variables and paired comparisons</strong><br>　　[README.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/d6f0f2e954f241b8c8cd926a23f538bc94e6dfea/Research/Engineering/PrologMCP/comparison/README.md)<br><br><strong>15:05 · Explain comparison decisions and replay each path from raw responses</strong><br>　　[trace&#95;case.py](https://github.com/naturaldao/NaturalDAO-2nd/blob/8f9e84f20268f0f640e2aed3f79114e8d09d30c5/Research/Engineering/PrologMCP/comparison/trace_case.py) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/8f9e84f20268f0f640e2aed3f79114e8d09d30c5)<details><summary>其他更新 · Other updates (3)</summary><strong>14:55 · Report paired PoL experiment and decision trace in engineering README</strong><br>　　[README.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/6b7ca8f0e84f242341427d2989afe73534fef8f6/Research/Engineering/PrologMCP/README.md)<br><br><strong>14:42 · Compare two Prolog MCP servers with direct and typed model judgments</strong><br>　　[prolog.json](https://github.com/naturaldao/NaturalDAO-2nd/blob/d44e608435c728d570dcfae74289a70b2102999c/Research/Engineering/PrologMCP/comparison/paper-five/raw/prolog.json) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/d44e608435c728d570dcfae74289a70b2102999c)<br><br><strong>14:10 · Document PrologMCP and verify a PoL rule through MCP</strong><br>　　[README.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/52f853232ba441cf8ea8944ae2952425ce3428f7/Research/Engineering/PrologMCP/README.md) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/52f853232ba441cf8ea8944ae2952425ce3428f7)</details> |

<!-- readme-activity:end -->

[查看完整提交历史 · View full commit history](https://github.com/naturaldao/NaturalDAO-2nd/commits/main/)

---

## 🔗 相关资源 · Resources

- **数据与模型 · Data and models** · [数据卡](PoL-Governance/datasets/README.md) · [模型目录](PoL-Governance/models/README.md) · [Hugging Face](https://huggingface.co/NaturalDAO) · [POL2 Score-v2 研究预发布](https://github.com/naturaldao/NaturalDAO/releases/tag/pol2-score-v2-v1.0.0)
- **理论与规划 · Theory and planning** · [中文理论](https://github.com/naturaldao/NaturalDAO/blob/main/PoL/Readme.md) · [English theory](https://github.com/naturaldao/NaturalDAO/blob/main/PoLEn/Readme.md) · [中文开发规划](https://github.com/naturaldao/NaturalDAO/blob/main/docs/development-plan.zh.md) · [English plan](https://github.com/naturaldao/NaturalDAO/blob/main/docs/development-plan.en.md)

---

## ⚖️ 许可证 · License

本项目遵循共识机制 [Proof of Love2](LICENSE)。<br>
This project is released under the consensus of [Proof of Love2](LICENSE).
