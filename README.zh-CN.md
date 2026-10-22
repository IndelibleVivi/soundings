# Soundings

[English](README.md)

Soundings 帮助 Codex 查清一个问题、理解一组材料、发展一个创作方向，以及让后果重大的选择变得可判断。它负责把当前 inquiry 做到可用的结果；理解本身、一个完整创作，也可以就是交付。

打开[「见地 · Soundings」官网](https://indeliblevivi.github.io/soundings/)，走近四种独立方法，操作构造示例、阅读公开案例，并复制安装命令。官网提供完整中英界面，源码在 [site/](site/README.md)；[视觉方向](docs/website-design.md)仍可继续打磨。

当一个项目已经存在、但下一件值得追的事并不明确时，Soundings 可以从项目已接受的目标与当前 artifacts 出发，找到后果最大的未解问题，并继续做到解释、实际 probe、完整 candidate、纠正或其他项目能用的结果。Backlog、repo 摘要或与项目脱节的 demonstration 都不算这个结果。

名字来自 taking soundings：对尚且看不清的事物做有意的测深与探测。四个可独立发现的 Skills 提供不同入口：

| Skill | 委托 | 有用的结果 |
| --- | --- | --- |
| `search` | 向外调查事实、选项、机制与 references。 | 有依据的回答或比较，保留结论成立的条件。 |
| `study` | 解释已提供或已收集材料之间的关系。 | 综合解释、机制或有边界的判断，保留真实分歧。 |
| `explore` | 发展粗略或已经清晰的创作目标。 | 足够完整、可实际感受的场景、可玩体验、样本或候选作品。 |
| `shape` | 处理后果重大的解释、选择与纠正。 | 代表性材料或有依据的决定，并继续完成已授权的后续工作。 |

它们是能力，不是阶段。没有 router、规定顺序、访谈或强制报告。清晰的小任务应直接完成；domain methods 保留其证据标准与制作职责，换方法仍然是在继续同一份委托。

> `0.4.0` 源码候选强化了重要开放选择前主动发现、研究返回后继续原任务的方法，并加入运行时可读的完整案例。[有限对照](docs/dogfood-0.4.0.md)中，候选读到了新指导，但仍跳过了外部取材；小修保持直接。尚未证明行为改善，见[当前状态](docs/current-state.md)。[0.3.1 观察](docs/dogfood-0.3.1.md)继续作为历史证据保留。

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

对照[当前状态](docs/current-state.md)确认 installed version 与 enabled 状态，再新开 task。Marketplace snapshot 与 installed cache 是不同层；最新源码候选与最近做过行为观察的安装版本可能不同。

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

从已有项目开始时，可以直接这样委托：

```text
看看这个项目已经接受的目标与当前 artifacts，找出最值得追的未解问题，并把它做到项目能用的结果，不要只给我 backlog。
```

当问题需要从现有材料的关系里长出来时，由 Study 接住发现；真正决定答案的工作可以继续交给 Search、Explore、Shape 或当前 domain method，无须变成强制 pipeline。

## 让参考进入正在做的工作

产品形态、交互、视觉表达、架构或实现仍有重要开放选择时，Search 要求在大量投入前主动接触相关外部可能性。目标清楚不等于做法已定。仍然适用的参考可以复用；明确的小修和已接受方向的忠实实施应直接继续。

阅读深度跟着用途走：介绍可以帮助发现候选；体验判断需要观察实际媒介；机制判断需要相关实现；真正采用还要核对本地条件。点名的 targets 获得与委托相称的直接覆盖。多个结果围绕共同问题比较，辨认前提冲突，以及值得借鉴但不必整体采用的贡献。[运行时完整案例](plugins/soundings/skills/search/references/proactive-inquiry-examples.md)用构造的工作台与交互场景展示这些转化，也保留应直接执行的小改动对照。

材料返回后，原任务的负责人要结合最初目标和本地证据形成判断，再把判断落实到实际解释、候选或实现中。回到启动调查的场景，观察想要的效果是否出现。只要求研究的委托仍然只做研究；发现了下一步，也不等于完成了实施委托。

普通请求可以只是“继续把这个工作台做得更顺手”或“这个页面能用了，但整体还是很弱，帮我改善”。Host 是否选择并使用相应方法仍需观察。[Host 接线说明](plugins/soundings/docs/host-integration.md)解释早期可见性、资源送达与任务接续，不引入强制依赖或新 runtime。

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

## 从未解问题继续一个项目

Soundings 可以从已有项目材料发展值得追究的问题，保留问题来由、结果依赖的证据、未用线索及重开条件。它按问题对已接受目标的影响来选择，然后继续用相应方法做下去，而不是停在发现。Corpus lookup、原始来源阅读、持续研究执行、视觉与交互 reference 的实际观察，仍是可以通过现有工具组合的不同能力。

### 可选的交接 maintenance

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
- [Host 接线与激活边界](plugins/soundings/docs/host-integration.md)
- [0.4.0 候选对照与未通过的主动发现验收](docs/dogfood-0.4.0.md)
- [完整案例](docs/examples/inquiry-in-practice.md)
- [离线研究包、反例与观测工具](evals/README.md)：构造 fixtures 与固定计划，不代表新增在线行为证据。
- [官网开发与发布](site/README.md)、[视觉方向](docs/website-design.md)与[第三方 notices](docs/website-third-party.md)
- [0.3.1 证据](docs/dogfood-0.3.1.md)、[0.3.0 纠正记录](docs/dogfood-0.3.0.md)、[0.2.0 观察](docs/dogfood-0.2.0.md)与 [0.1.0 历史](docs/dogfood-0.1.0.md)

## 验证

在 repo root 使用 operator 已安装的 Codex Skill tooling：

```bash
skill-validate plugins/soundings/skills/search
skill-validate plugins/soundings/skills/study
skill-validate plugins/soundings/skills/explore
skill-validate plugins/soundings/skills/shape
python3 -m json.tool plugins/soundings/.codex-plugin/plugin.json >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s plugins/soundings/skills/search/scripts -p 'test_*.py' -v
python3 evals/check.py
```

`skill-validate` 是开发工具，不是 Soundings 附带的依赖。JSON 检查只建立 manifest 语法成立；一次成功的 marketplace 安装会另行建立当前 host 接受这个 package。结构验证不能证明触发或判断质量；请在 fresh tasks 中运行相关[行为场景](plugins/soundings/docs/behavior-scenarios.md)，并检查实际成果。

可选 `evals/` 工具使用 Python 3.10+ 与标准库。Provider-neutral check 在不启动 target model 的情况下检查构造 fixtures、语义反例与观测边界。另行 materialize 的 Field Lab pack 固定四类任务、四种历史/当前 Soundings 与 Servotab 组合、每格两次重复，共32次计划运行；真正的无 Skill control 可额外生成独立8次计划。生成包留在 Git 外。计划不授予执行权；离线检查不证明研究质量或隐式 Skill 选择。版本固定、私人产物处理与 receipt-bound 语义审查见[研究指南](evals/README.md)。

## 当前状态

- **Source：** `0.4.0` 是主动发现开放选择、按用途阅读多来源材料、接收结果后继续原任务的候选。Package 仍由四个独立 Skills 与可选本地 helpers 构成。
- **Validation 与 behavior：** [0.4.0 对照](docs/dogfood-0.4.0.md)记录通过的源码检查与小修、可运行的产物，以及开放候选任务中未通过的主动发现验收。[当前状态](docs/current-state.md)明确保留未完成的行为条件；[0.3.1](docs/dogfood-0.3.1.md)保留早先 installed-host 观察。
- **Installation 与 activation：** 历史上实际观察过的安装是 enabled `0.3.1`；它不能证明 `0.4.0` 候选已送达或产生行为效果。
- **Publication：** 公开 [marketplace repo](https://github.com/IndelibleVivi/soundings)分发其中的当前 package。源码发布、本地安装、激活与行为接受分别报告；源码版本不代表新增 tagged release。

有限案例成功不证明跨模型一致、因果增益或全部场景覆盖。Skills 很多的 host 可能缩短 description 以满足 context budget；发现能力仍取决于 host 与当前 inventory。

## Privacy、network 与 authority

Soundings 不增加 MCP server、search backend、hooks、固定 worker team 或自动 memory。可选本地 helpers 没有网络调用。显式 `capture` 把来源文本和 metadata 保存在你指定的本地目录，直至你自行移除；它不执行留存策略，不认证 provenance，也不自动更新来源。私人 store 应放在公开 repo 外。

官网是 GitHub Pages 静态站，scripts、画稿和字体从同一 host 加载，不增加 analytics、账号登录、模型调用或访问者资料上传。交互示例在浏览器内运行；安装插件仍需在 Codex 中运行复制的命令。访问请求适用 GitHub 的托管政策。

Inquiry 可能使用 host 已有的 web、browser、repository 或 connector tools；这些工具的网络与数据边界仍然有效。来源材料是数据，不是指令。Skill 的选择不授予安装软件、修改账号、发布、花钱、暴露隐私或执行 destructive action 的权限。远程 corpus 部署、provider adapters 与 Cloudflare 账号实验不属于本版。

## License

Soundings 采用按 path 划分的许可：

- functional marketplace、plugin、Skills、scripts 与 runtime references：[Sustainable Use License 1.0](LICENSE)（`SUL-1.0`）；
- READMEs、项目文档、示例与 diagrams：[CC BY-NC-SA 4.0](LICENSE-DOCUMENTATION.md)。

[LICENSING.md](LICENSING.md) 是精确 path map 的真源。第三方材料仍适用自身条款，必须另行标明。

本轮新增的 `evals/` 未加入上述授权，沿用 map 对未列出材料保留全部权利的规则。

本次发布没有将 `site/` 的原创网站材料加入上述任何一项授权；它们适用 map 对未列出材料的规则。所带字体子集保留 SIL OFL 1.1，UI 模板保留 MIT notices。见[官网 notices](docs/website-third-party.md)。
