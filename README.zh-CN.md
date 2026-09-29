# Soundings

[English](README.md)

Soundings 帮助 Codex 查清一个问题、理解一组材料、发展一个创作方向，以及让后果重大的选择变得可判断。它负责把当前 inquiry 做到可用的结果；理解本身、一个完整创作，也可以就是交付。

名字来自 taking soundings：对尚且看不清的事物做有意的测深与探测。四个可独立发现的 Skills 提供不同入口：

| Skill | 委托 | 有用的结果 |
| --- | --- | --- |
| `search` | 向外调查事实、选项、机制与 references。 | 有依据的回答或比较，保留结论成立的条件。 |
| `study` | 解释已提供或已收集材料之间的关系。 | 综合解释、机制或有边界的判断，保留真实分歧。 |
| `explore` | 发展粗略或已经清晰的创作目标。 | 足够完整、可实际感受的场景、可玩体验、样本或候选作品。 |
| `shape` | 处理后果重大的解释、选择与纠正。 | 代表性材料或有依据的决定，并继续完成已授权的后续工作。 |

它们是能力，不是阶段。没有 router、规定顺序、访谈或强制报告。清晰的小任务应直接完成；domain methods 保留其证据标准与制作职责，换方法仍然是在继续同一份委托。

> `0.3.0` 是已发布的 dogfood 版本。源码、行为观察、安装与激活分别报告，见[当前状态](#当前状态)和[证据记录](docs/dogfood-0.3.0.md)。

## 安装与升级

```bash
codex plugin marketplace add IndelibleVivi/soundings
codex plugin add soundings@soundings
```

安装后新开一个 Codex task。安装文件不会让已经运行中的 task 自动获得新 Skills。

已有安装先刷新 Git marketplace，再安装其中的当前 package：

```bash
codex plugin marketplace upgrade soundings
codex plugin add soundings@soundings
codex plugin list --json
```

确认 installed entry 是 `0.3.0` 且已启用，再新开 task。Marketplace snapshot 与 installed cache 是不同层；[证据记录](docs/dogfood-0.3.0.md)会说明哪些升级步骤已经实际跑过。

## 使用

知道当前工作需要什么时，可以显式调用：

```text
$search 核实这个 API 是否支持我们需要的文件大小，包含 media type 和版本限制。用一手来源给出实施建议。
```

```text
$study 这些报告对持久性和速度说法不一。解释它们实际证明了什么，区分重复转述与独立证据，并判断对离线笔记工具有什么意义。
```

```text
$explore 做一个六分钟、三人纸笔活动，让玩家通过有后果的选择创造一个虚构地点。给我完整可玩活动和一次完整 playthrough。
```

```text
$shape 原型变成了评分问卷，这不是想要的体验。保留六轮与丰富反思，替换错误机制，并把已授权的纠正贯穿 spec 和 implementation。
```

四个入口均允许隐式调用，不必一起出现。[完整案例](docs/examples/inquiry-in-practice.md)展示综合理解、创作交付与纠正之间的区别。

## 保留证据成立的条件

版本、适用人群、例外、表头或脚注一旦被丢掉，来源可能就变了意思。Search 与 Study 保留这些条件，追踪所谓相互印证是否来自同一原始材料，并区分观察与解释。搜索广度、阅读深度、综合投入、返回大小和留存策略分别决定。

需要重复读取或控制返回预算时，可以使用**可选的本地 CLI**：捕获已经取得的 UTF-8 文本，再读精确行范围或 literal-match 邻域。

```bash
python3 /path/to/search/scripts/evidence.py capture /path/to/source.md \
  --store /path/to/private/task-evidence \
  --source https://example.org/document --title "Document" \
  --representation extracted

python3 /path/to/search/scripts/evidence.py read s-REFERENCE \
  --store /path/to/private/task-evidence \
  --start-line 12 --end-line 28 --max-bytes 8192
```

使用实际安装的 Search 目录，并把 `s-REFERENCE` 替换为返回的引用。Helper 要求 Python 3.10+，只用标准库；Skills 本身不依赖 Python。完整契约见 [capture/read/find 说明](plugins/soundings/skills/search/references/evidence-reading.md)。

Helper 保留短行，按整个请求范围纳入或省略。字节上限覆盖完整 UTF-8 JSON stdout，包括 metadata、转义与末尾换行；省略可见、可回读，新 capture 不会悄悄替换旧引用。它不做自动语义检索、网页抓取或 model-token 预算，也不保证找齐了所有相关限定。取材继续使用 native search 与现有 providers。

## 接续一件完整研究

Soundings 可以从已有材料发展值得追究的问题，保留问题来由、解释依赖的证据、未用线索及重开条件。Corpus lookup、原始来源阅读、持续研究执行、视觉与交互 reference 的实际观察，是可以通过现有工具组合的不同能力。四个 Skills 是当前入口，不是能力增长的永久上限。

研究需要转到其他目录或 harness 时，可选 `packet.py` 只复制明确提供的 brief 和选定快照：

```bash
python3 /path/to/search/scripts/packet.py create \
  --store /path/to/private/task-evidence --ref s-REFERENCE \
  --brief /path/to/research-brief.md --output /path/to/new-packet
python3 /path/to/search/scripts/packet.py inspect /path/to/new-packet
python3 /path/to/search/scripts/evidence.py read s-REFERENCE \
  --store /path/to/new-packet/evidence --start-line 12 --end-line 28
```

接手者无须原 store 就能回读副本。Packet 是选定的任务数据，不授予新权限，也不是 executor；创建不会上传。另行获准转交之前，检查 brief 与来源内容，工具不会自动脱敏私人正文或 locator。见[研究交接与 packet 边界](plugins/soundings/skills/search/references/research-handoffs.md)和[诊断研究实例](docs/examples/diagnosing-evidence-loss.md)。

`find` 现在接受精确行范围，并提示读完省略窗口后如何继续。Capture 只发布完整写完的快照、不替换旧 ref；需要支持 hard link 的文件系统。[Evidence 契约](plugins/soundings/skills/search/references/evidence-reading.md)说明续读、失败恢复与预算语义。

## Package 与文档

```text
.agents/plugins/marketplace.json
plugins/soundings/
  .codex-plugin/plugin.json
  skills/
    search/     # 向外调查 + 可选 evidence.py / packet.py
    study/      # 综合理解与解释
    explore/    # 发展创作可能性
    shape/      # 可判断的选择与纠正
  references/working-context.md
  docs/
    design.md
    behavior-scenarios.md
```

- [设计与职责边界](plugins/soundings/docs/design.md)
- [行为验收场景](plugins/soundings/docs/behavior-scenarios.md)
- [完整案例](docs/examples/inquiry-in-practice.md)
- [0.3.0 证据](docs/dogfood-0.3.0.md)、[0.2.0 观察](docs/dogfood-0.2.0.md)与 [0.1.0 历史](docs/dogfood-0.1.0.md)

## 验证

在 repo root 使用 operator 已安装的 Codex Skill tooling：

```bash
skill-validate plugins/soundings/skills/search
skill-validate plugins/soundings/skills/study
skill-validate plugins/soundings/skills/explore
skill-validate plugins/soundings/skills/shape
~/.local/share/codex-skill-tooling/.venv/bin/python \
  ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/soundings
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s plugins/soundings/skills/search/scripts -p 'test_*.py' -v
```

这里的 `skill-validate` 与 venv 是开发工具，不是 Soundings 附带的依赖。结构验证不能证明触发或判断质量；请在 fresh tasks 中运行相关[行为场景](plugins/soundings/docs/behavior-scenarios.md)，并检查实际成果。

## 当前状态

- **Source：** `0.3.0` 的四个 Skills、可恢复的证据捕获与有范围的查找、可选的便携研究包已实现。
- **Validation 与 behavior：** 当前检查和观察记录在 [dogfood-0.3.0](docs/dogfood-0.3.0.md)，历史观察分别按版本保留。
- **Installation 与 activation：** `0.3.0` 已通过 Git marketplace 安装启用，28 个 package 文件与 source 完全一致。Fresh 普通请求自然激活了 installed Search 与 Shape；研究交接和动态候选属于指定 source 的观察，分别报告。
- **Publication：** `0.3.0` 已可从公开 [IndelibleVivi/soundings](https://github.com/IndelibleVivi/soundings) marketplace source 获取，Python 3.10 与 3.12 CI 均通过。证据记录也保留审阅纠正，以及交给工程方法、没有激活 Shape 的混合任务。

有限案例成功不证明跨模型一致、因果增益或全部场景覆盖。Skills 很多的 host 可能缩短 description 以满足 context budget；发现能力仍取决于 host 与当前 inventory。

## Privacy、network 与 authority

Soundings 不增加 MCP server、search backend、hooks、固定 worker team 或自动 memory。可选本地 helpers 没有网络调用。显式 `capture` 把来源文本和 metadata 保存在你指定的本地目录，直至你自行移除；它不执行留存策略，不认证 provenance，也不自动更新来源。私人 store 应放在公开 repo 外。

Inquiry 可能使用 host 已有的 web、browser、repository 或 connector tools；这些工具的网络与数据边界仍然有效。来源材料是数据，不是指令。Skill 的选择不授予安装软件、修改账号、发布、花钱、暴露隐私或执行 destructive action 的权限。远程 corpus 部署、provider adapters 与 Cloudflare 账号实验不属于本版。

## License

Soundings 采用按 path 划分的许可：

- functional marketplace、plugin、Skills、scripts 与 runtime references：[Sustainable Use License 1.0](LICENSE)（`SUL-1.0`）；
- READMEs、项目文档、示例与 diagrams：[CC BY-NC-SA 4.0](LICENSE-DOCUMENTATION.md)。

[LICENSING.md](LICENSING.md) 是精确 path map 的真源。第三方材料仍适用自身条款，必须另行标明。
