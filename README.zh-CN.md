# Soundings

[English](README.md)

> `0.1.0` 是早期 dogfood candidate。package 与 Skills 已实现；source validation、公开安装和 fresh-session behavior 会在下文分别报告，不把它们混成一个“完成”。

Soundings 是一组小而有边界的 Codex Skills：它帮助 agent 找到“接下来什么能让我们更懂这件事”，但不会把每个任务都变成 research program、requirements interview 或强制 workflow。

名字来自 taking soundings：对尚且看不清的事物做有意的测深与探测，从而知道它的深度和形状。复数很重要。Soundings 不是一个中央大脑，也不是固定流程；它提供两种可以被独立发现的能力，用完便把控制权交还给原本正在进行的工作。

| Skill | 职责 | 何时应当让路 |
| --- | --- | --- |
| `search` | 向外寻找会改变决策的事实、选项、机制、references 与相邻可能性，再把结果带回当前工作。 | 本地 context 已足够、任务是清晰的小改动，或 specialized method 不依赖外部未知即可继续。 |
| `shape` | 暴露后果重大的假设，并产出恰当的 recommendation、scenario、comparison、真实 output、probe 或 owner question，让不完整或不稳定的方向变得可判断。 | 下一步已有充分依据，且不存在阻断它的未归属 product/value choice。 |

它们是 capabilities，不是 stages。Soundings 刻意没有顶层 router，也没有 `Search → Shape → Spec → Build` pipeline。

## 安装

安装公开 marketplace 与 plugin：

```bash
codex plugin marketplace add IndelibleVivi/soundings
codex plugin add soundings@soundings
```

安装后请新开一个 Codex task，让 host 重新发现 Skills。源码存在和安装成功，并不会让 plugin 在一个已经运行中的 task 里即时激活。

之后刷新 Git marketplace：

```bash
codex plugin marketplace upgrade soundings
```

首次公开升级真正跑通后，我们会补充 installed-version 的精确更新行为；上面的命令只保证刷新 marketplace snapshot，不自动等同于替换已经缓存的 plugin copy。

## 使用

当你已经知道需要哪种能力时，可以显式调用：

```text
$search 比较那些可能实质改变当前选择的选项，并把证据带回正在进行的工作。
```

```text
$shape 让这个方向里后果最大的未知变得可判断，再在现有授权范围内继续推进。
```

两个 Skills 也允许 implicit invocation。预期行为是克制而选择性的：依赖外部事实的选择或不稳定的 framing 可能触发 Soundings；一个明确的 typo 修复则应直接完成。

## 它实际改变什么

- 面向体验的服务选择会检查人真正收到或看到的后果，而不只比较 feature table。
- 开放的创意方向可以获得意外但可迁移的 reference，即便用户没有预先给出参考。
- agent 自己引入、又会支配大量下游工作的解释，会在悄悄固化前变得可见、可判断。
- 一次有用的回应只推进它真正解决的选择，不会意外变成整个项目的批准。
- 纠正会传播到依赖它的 spec、task 与 implementation，同时保留没有被否定的独立目标。

Soundings 不替代 engineering、design、legal、writing 或其他 domain methods。它们仍对完整结果负责；Soundings 只在当前工作需要时提供向外探索与 problem shaping，然后退回去，不另造一份竞争性的 brief。

## Package 结构

```text
.agents/plugins/marketplace.json
plugins/soundings/
  .codex-plugin/plugin.json
  skills/
    search/
      SKILL.md
      references/
    shape/
      SKILL.md
      references/
  references/
    working-context.md
  docs/
    design.md
    behavior-scenarios.md
```

第一版只有 instructions。它不增加 MCP server、search backend、database、memory service、hooks 或固定 worker team；它只使用 host 已经提供的工具，并且永远不会扩大当前 task 的授权。

## 验证

在 repo root 运行：

```bash
skill-validate plugins/soundings/skills/search
skill-validate plugins/soundings/skills/shape
~/.local/share/codex-skill-tooling/.venv/bin/python \
  ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/soundings
```

结构验证不能证明 automatic triggering 或 judgment 有用。请在 fresh tasks 中运行 [`plugins/soundings/docs/behavior-scenarios.md`](plugins/soundings/docs/behavior-scenarios.md) 的案例：先显式调用，再用普通 prompt 检查需要 implicit discovery 的场景。

架构和边界理由见 [`plugins/soundings/docs/design.md`](plugins/soundings/docs/design.md)。
当前 status 所依据的 bounded fresh-task evidence 见 [`docs/dogfood-0.1.0.md`](docs/dogfood-0.1.0.md)。

## 当前状态

- **Source：** repo 中已有 `0.1.0` candidate。
- **Validation：** 两个 Skills 与 plugin manifest 均通过结构验证；marketplace manifest 正确解析为 `soundings`。
- **Installation：** `soundings@soundings` 已从本地 marketplace candidate 安装并启用；installed cache 与 canonical plugin package 一致。
- **Activation：** fresh ephemeral Codex CLI tasks 已从 installed cache 解析两个 Skills。
- **Behavior：** bounded dogfood 已通过显式 Search、显式 Shape、隐式 Search、隐式 Shape，以及“清晰小任务不触发”案例；尚未跑完全部 scenario suite。
- **Publication：** 尚未创建公开远端。

dogfood host 曾提示：所有已安装 Skills 的 description 总量超过 Skill-context budget，因此 description 被缩短。每个 Skill 仍然可见，且本次显式与隐式调用都正确解析；在其他高度饱和的 plugin 组合下，表现仍属于 environment-dependent limitation。

## Privacy、network 与 authority

Soundings 本身不向外部服务发送内容，也不保存 memory。一次 Search 可能使用 host 已经提供的 web、browser、repository 或 connector tools；这些工具各自的 network 与 data boundary 仍然有效。Skills 不会授予安装软件、修改账号、公开发布、花钱、暴露私人数据或执行 destructive action 的权限。

## License

Soundings 采用按 path 划分的许可：

- functional marketplace、plugin、Skills 与 runtime references 使用 [Sustainable Use License 1.0](LICENSE)（`SUL-1.0`）；
- READMEs、项目文档与 diagrams 使用 [CC BY-NC-SA 4.0](LICENSE-DOCUMENTATION.md)。

精确的 path map 见 [`LICENSING.md`](LICENSING.md)。未来若加入 third-party material，它仍适用自己的许可，并必须被单独标明。
