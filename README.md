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
| 1 | 11-17 01:42–01:52 | [@shentonyan](https://github.com/shentonyan) | <strong>01:52 · 实验：动态撤权执行协议与连接模板目标记忆干预</strong><br>　　[fly-brain.yml](https://github.com/naturaldao/NaturalDAO-2nd/blob/ad2df3a9a95d77239090f95c0d7629708c00dcb3/.github/workflows/fly-brain.yml) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/ad2df3a9a95d77239090f95c0d7629708c00dcb3)<br><br><strong>01:42 · Pol/gov readme/active management 20261110</strong><br>　　[README.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/3f073bf7407931a372024e56a1015c03ac706ac9/PoL-Governance/research/PoL2-DAO-Governance-Lab/README.md) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/3f073bf7407931a372024e56a1015c03ac706ac9) |
| 2 | 11-17 01:42 | [@Aranna-0572](https://github.com/Aranna-0572) | <strong>01:42 · Pol/eval 05/love hate behavior</strong><br>　　[TASKS.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/44b0959f2c5cbf31daa851c28a17b69b96e5b9f6/PoL-Governance/TASKS.md) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/44b0959f2c5cbf31daa851c28a17b69b96e5b9f6) |
| 3 | 11-13 00:55 | [@Aranna-0572](https://github.com/Aranna-0572) | <strong>00:55 · docs&#58; add Nov 12 PoL2 governance meeting notes</strong><br>　　[2026-11-12-pol-weekly-meeting.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/b3509e917d896f9d22cc67d513714b39d76a9178/PoL-Governance/meetings/2026-11-12-pol-weekly-meeting.md) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/b3509e917d896f9d22cc67d513714b39d76a9178) |
| 4 | 11-12 22:19 | [@QUEENATUNG](https://github.com/QUEENATUNG) | <strong>22:19 · 更新文件 / Updated files：My Fluffy Winter.mp4</strong><br>　　[My Fluffy Winter.mp4](https://github.com/naturaldao/NaturalDAO-2nd/blob/b95fde594d714ac461d5caaff889c328eaaeaf54/media/%E6%AD%8C%E6%9B%B2Song/My%20Fluffy%20Winter.mp4) |
| 5 | 11-12 03:28 | [@shentonyan](https://github.com/shentonyan) | <strong>03:28 · Create 乐鑫科技（ESP32）调研报告</strong><br>　　[乐鑫科技（ESP32）调研报告](https://github.com/naturaldao/NaturalDAO-2nd/blob/d8c17c3fc628a7b2d325752ca363df0904e98a12/Research/Storage/04-%E8%B0%83%E7%A0%94%E7%AC%94%E8%AE%B0/%E4%B9%90%E9%91%AB%E7%A7%91%E6%8A%80%EF%BC%88ESP32%EF%BC%89%E8%B0%83%E7%A0%94%E6%8A%A5%E5%91%8A) |
| 6 | 11-10 03:47–17:21 | [@shentonyan](https://github.com/shentonyan) | <strong>17:21 · Update README.md</strong><br>　　[README.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/194e3136b8533f7fc53c532ac6697bc4df0ca144/PoL-Governance/research/PoL2-DAO-Governance-Lab/README.md)<br><br><strong>17:07 · Update README.md</strong><br>　　[README.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/ccab2d9122fd7e83ae43ff5f64c2e8d808d6fa59/PoL-Governance/research/PoL2-DAO-Governance-Lab/README.md)<details><summary>其他更新 · Other updates (3)</summary><strong>15:24 · Deepen PoL2 publicization analysis and sensitivity figures</strong><br>　　[build&#95;readme&#95;figures&#95;zh.py](https://github.com/naturaldao/NaturalDAO-2nd/blob/6aa2a9952ee042b736ec9bb062e6d9c0d4e31d08/PoL-Governance/research/PoL2-DAO-Governance-Lab/scripts/build_readme_figures_zh.py) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/6aa2a9952ee042b736ec9bb062e6d9c0d4e31d08)<br><br><strong>15:09 · Reframe governance lab README around PoL2 publicization</strong><br>　　[README.md](https://github.com/naturaldao/NaturalDAO-2nd/blob/6bb68cb2ef1be6b3acfa38373c0a7e55e05eb99d/PoL-Governance/research/PoL2-DAO-Governance-Lab/README.md) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/6bb68cb2ef1be6b3acfa38373c0a7e55e05eb99d)<br><br><strong>03:47 · 添加 Major and 益丽的微信头像与手机壁纸</strong><br>　　[微信头像-Major and 益丽.png](https://github.com/naturaldao/NaturalDAO-2nd/blob/0e98548ade702f9706c1e3e8a277f9ff54d248f7/media/%E5%9B%BE%E7%89%87images/%E5%BE%AE%E4%BF%A1%E5%A4%B4%E5%83%8F-Major%20and%20%E7%9B%8A%E4%B8%BD.png) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/0e98548ade702f9706c1e3e8a277f9ff54d248f7)</details> |
| 7 | 11-10 15:08 | [@Wenbobobo](https://github.com/Wenbobobo) | <strong>15:08 · docs&#40;research&#41;&#58; 补回 MemT-1.0 复现材料（拆仓迁移遗漏）</strong><br>　　[memt-1.0-explainer.html](https://github.com/naturaldao/NaturalDAO-2nd/blob/a27d35cf71592459972894bfd4e6b9ae0a0d9d5f/Research/Engineering/MemT-1.0-%E5%A4%8D%E7%8E%B0/memt-1.0-explainer.html) · [详情 / Details](https://github.com/naturaldao/NaturalDAO-2nd/commit/a27d35cf71592459972894bfd4e6b9ae0a0d9d5f) |

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
