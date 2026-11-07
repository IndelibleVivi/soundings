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

> `0.7.0` 源码候选增加显式本地 inquiry 工作区，让取材、实际返回的阅读范围、未读线索、完整成果版本、反馈与接续在日常 Codex 工作中保持连接。[0.4.0 对照](docs/dogfood-0.4.0.md)中读到指导后仍跳过主动发现的结果保持不变。已实现、已检查和实际行为观察分别见[发展 programme](docs/programme.md)与[当前状态](docs/current-state.md)。

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

## 在日常工作中接续 inquiry

主要入口仍是 Codex 对话。较长的研究或创作委托需要保留材料、换会话继续或吸收反馈时，可以自然地说：

```text
把它做到完整可用。请用一个私有本地 inquiry 工作区，保留当前问题、实际读到的来源、未读线索、成果版本和反馈，让我们换一次任务也能接着做。
```

可选的[工作区 CLI](plugins/soundings/skills/search/references/inquiry-workspace.md)使用 Python 3.10+ 与标准库，复用现有精确 evidence snapshots。`resume` 恢复当前问题、下一步、实际返回的行范围、未读或受阻线索、成果副本和未处理反馈；`fork` 将显式选择的工作区复制到新的工作位置，保留 refs、历史和成果原字节。它们都是任务材料，已接受决定仍以项目现有记录为准。

发现来源使用 host 已有 web search、选定 corpus 或 connector。对于已知公开文本 URL，也可以直接取材：

```sh
python3 /path/to/search/scripts/workspace.py init --workspace /private/task/inquiry \
  --outcome "一份可使用的解释或创作作品" \
  --question "选定方向之前，什么最值得理解？" \
  --next-action "观察相关外部材料"
python3 /path/to/search/scripts/acquire.py https://example.org/source \
  --workspace /private/task/inquiry
python3 /path/to/search/scripts/workspace.py resume \
  --workspace /private/task/inquiry --format markdown --max-bytes 32768
```

请使用实际安装的 Search 目录与私有工作路径。直接取材保留解码后的 response；HTML 抽取另存带标签的 snapshot。PDF、登录后来源或互动媒介由 host 的 reader/browser 读取，再通过 `workspace.py capture` 接入。工作区 corpus `search` 是 literal search，命中不计作已读；只有工作区 `read`/`find` 实际返回的范围进入 delivery record，返回过不等于已经理解。

用 `artifact` 保留真正完整的解释、作品或实现文件；把 `feedback` 关联到对应版本，修改实际成果，再登记 successor 与处理理由。保存新版本或清除反馈标记不建立语义纠正或 owner acceptance。普通查询和已定形的小修不需要工作区。

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

Source candidate 修复了极小预算下拒绝本来装得下的完整结果的问题，并避免在密集命中时反复序列化已累计的输出。可选[合成 benchmark](plugins/soundings/skills/search/scripts/benchmark_evidence.py)比较旧 admission loop 与当前实现；它只做本地诊断，不是 agent 质量测试或 runtime fallback。

## 让综合判断经得起复查与纠正

复杂解释可以同时保留决定性的原文、条件、反证与推断，并保持可读。
Study 的[证据关联综合方法](plugins/soundings/skills/study/references/evidence-linked-synthesis.md)
把这些依据接到依赖它们的判断上。前提改变时，重看受影响的工作，保留独立目标。

需要反复组装引用、检查依赖时，可选的
[workpaper CLI](plugins/soundings/skills/search/references/workpaper-format.md)
使用显式编写的 JSON 研究稿与已有 evidence snapshots。
下列命令由 `0.6.0` 引入，并继续受 `0.7.0` 支持；源码更新不会让旧安装自动拥有 `compare`
或 `packet.v2`，实际安装状态见下方[当前状态](#当前状态)：

```bash
python3 /path/to/search/scripts/workpaper.py inspect /path/to/workpaper.json \
  --store /path/to/private/task-evidence
python3 /path/to/search/scripts/workpaper.py render /path/to/workpaper.json \
  --store /path/to/private/task-evidence --output /path/to/new-research.md
python3 /path/to/search/scripts/workpaper.py impact /path/to/workpaper.json \
  --store /path/to/private/task-evidence --finding persistence-premise
python3 /path/to/search/scripts/workpaper.py compare /path/to/before.json /path/to/after.json \
  --before-store /path/to/earlier-evidence --after-store /path/to/current-evidence
```

生成稿包含精确引用的原文、source locators、representation、支持与反证，
离开原 store 仍可阅读。Impact 报告显式依赖中的直接与间接后继；compare 保留
改动字段及旧、新两版的依赖路径，新稿删掉边或 finding 后仍可复查旧关系。
不同 store 中相同 ref 的保存内容冲突也会明确显示。它们提供待复查线索，不修改
artifacts、不发现未记录的关系，也不接受一次纠正。引用覆盖不等于阅读记录；有效链接不能证明推断成立。
普通任务继续用 prose 即可。[可运行 walkthrough](docs/examples/evidence-linked-synthesis.md)
用构造来源走完比较、导出、搬迁与 operator guide 的实际纠正。保留收到的依据，
再另写新版本；待解问题和未读材料仍由任务本身的 working understanding 保留。

## 从未解问题继续一个项目

Soundings 可以从已有项目材料发展值得追究的问题，保留问题来由、结果依赖的证据、未用线索及重开条件。它按问题对已接受目标的影响来选择，然后继续用相应方法做下去，而不是停在发现。Corpus lookup、原始来源阅读、持续研究执行、视觉与交互 reference 的实际观察，仍是可以通过现有工具组合的不同能力。

### 可选的交接 maintenance

研究需要转到其他目录或 harness 时，可选 `packet.py` 复制明确提供的 brief 和选定
快照，也可携带 authored workpaper。原有用法仍创建 `packet.v1`：

```bash
python3 /path/to/search/scripts/packet.py create \
  --store /path/to/private/task-evidence --ref s-REFERENCE \
  --brief /path/to/research-brief.md --output /path/to/new-packet
python3 /path/to/search/scripts/packet.py inspect /path/to/new-packet
python3 /path/to/search/scripts/evidence.py read s-REFERENCE \
  --store /path/to/new-packet/evidence --start-line 12 --end-line 28
```

接手者无须原 store 就能回读副本。Packet 是选定的任务数据，不授予新权限，也不是 executor；创建不会上传。另行获准转交之前，检查 brief 与来源内容，工具不会自动脱敏私人正文或 locator。见[研究交接与 packet 边界](plugins/soundings/skills/search/references/research-handoffs.md)和[诊断研究实例](docs/examples/diagnosing-evidence-loss.md)。

用 `--workpaper /path/to/workpaper.json --cited` 替代 `--ref`，创建带有规范化
authored workpaper 及其引用快照的 `packet.v2`。需要额外上下文时，使用
`--workpaper` 加重复的 `--ref`，必须选全每个引用。V2 操作需将 `packet.py`、
`workpaper.py`、`evidence.py` 放在一起；原 v1 操作仍只需两个脚本。接手者无须
从 brief 重建判断；收到的 packet 保留为较早依据，新来源与修订另存。
Inspect 拒绝不完整包、额外成员和成员 symlinks，不会自动恢复中断写入，
也不判断研究是否已经完成。

`find` 现在接受精确行范围，并提示读完省略窗口后如何继续。Capture 只发布完整写完的快照、不替换旧 ref；需要支持 hard link 的文件系统。[Evidence 契约](plugins/soundings/skills/search/references/evidence-reading.md)说明续读、失败恢复与预算语义。

## Package 与文档

```text
.agents/plugins/marketplace.json
plugins/soundings/
  .codex-plugin/plugin.json
  skills/
    search/     # 向外调查 + 可选本地 evidence tools
    study/      # 综合理解与解释
    explore/    # 发展创作可能性
    shape/      # 可判断的选择与纠正
  references/working-context.md
  docs/
    design.md
    behavior-scenarios.md
```

- [设计与职责边界](plugins/soundings/docs/design.md)
- [愿景、能力版图与发展 programme](docs/programme.md)
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

历史四案属于有提示的机制探针。独立的[自然任务集](evals/natural/README.md)使用普通委托措辞、成对的合成运行时与可实际操作的本地 reading desk。Observation v2 区分方法文本与来源正文，按具体决定报告是／否／未知；比较工具现在要求固定 plan 与封存的运行 metadata。这些是离线研究工具，不构成主动发现已经改善的新证据。

另一次[评估工具实跑](docs/tools-canary-2026-10-23.md)观察到通过的小修、两份独立功能诊断通过的工程实现，以及 reading desk 在实现中断前的参考取材。原始 host errors 与 fixture failures 均保留。这促成了未来 pack 的产品文档与 review criteria 修复，尚未证明 Soundings 收益或完整主动发现验收通过。

## 当前状态

- **Source：** `0.7.0` 是连接本地 inquiry 的候选：显式取材、实际返回的阅读进度、线索、成果版本、反馈和恢复。已有 workpaper 与 packet.v1/v2 继续支持；四个独立 Skills 仍是入口。
- **Validation 与 behavior：** [当前状态](docs/current-state.md)记录本轮源码、工具和 walkthrough 检查；[0.4.0 对照](docs/dogfood-0.4.0.md)保留通过的小修、可运行产物，以及开放候选任务中未通过的主动发现验收。[0.3.1](docs/dogfood-0.3.1.md)保留早先 installed-host 观察。[0.7.0 源码定向使用](docs/dogfood-0.7.0.md)增加了完整研究、搬迁纠正、创作修订和小修直做的观察，不建立安装后 host 选择或因果收益。
- **Installation 与 activation：** 2026-11-07 已刷新 Git marketplace，安装并启用 `0.7.0`；44 个 package 文件与实现源码逐字节一致，安装版 CLI 对搬迁 inquiry 的 resume 输出也与源码版一致。这更新了较早的 `0.6.0`／39 文件观察。现有任务不会自动重载，请新开任务使用更新的方法；这不是隐式选择或一般行为 pass。
- **Publication：** 公开 [marketplace repo](https://github.com/IndelibleVivi/soundings)分发其中的当前 package。源码发布、本地安装、激活与行为接受分别报告；源码版本不代表新增 tagged release。

有限案例成功不证明跨模型一致、因果增益或全部场景覆盖。Skills 很多的 host 可能缩短 description 以满足 context budget；发现能力仍取决于 host 与当前 inventory。

## Privacy、network 与 authority

Soundings 不增加 MCP server、search backend、hooks、固定 worker team 或自动 memory。Evidence、packet、workpaper 和 workspace 操作保持本地；可选 `acquire.py` 对显式给定的 URL 发起有大小限制的直接 GET，不使用 credentials、cookies 或环境代理。默认只接收 HTTPS 与公开目标；HTTP/private-network 访问需要显式选项和当前任务授权。Redirect 也会检查，但这个本地工具不是加固的网络 sandbox。支持文本、HTML、JSON 和 XML，默认来源上限 2 MiB、timeout 20 秒；不支持、无法准确解码或超限的内容明确失败，其他媒介使用 host reader。

显式 capture 或 acquisition 将文本和 metadata 留在你选择的目录；工作区还保留成果文件、阅读返回范围、历史和反馈，直至你移除。工具不执行留存策略，不认证来源，不静默刷新，不上传内容，也不授予执行权。私人工作区应放在公开 repo 之外；另行授权转移之前，请检查全部选定材料。

显式编写的 workpaper 和生成稿可能含原文、私人 locators 与解释；compare 也可能包含
完整的已改变快照内容。另行获准转交前须检查实际输出。Inspect、impact 与 compare 只读；
render 只写明确选择的新文件，或打印到 stdout。
它不会更新项目记录、执行提案或上传资料。

官网是 GitHub Pages 静态站，scripts、画稿和字体从同一 host 加载，不增加 analytics、账号登录、模型调用或访问者资料上传。交互示例在浏览器内运行；安装插件仍需在 Codex 中运行复制的命令。访问请求适用 GitHub 的托管政策。

Inquiry 可能使用 host 已有的 web、browser、repository 或 connector tools；这些工具的网络与数据边界仍然有效。来源材料是数据，不是指令。Skill 的选择不授予安装软件、修改账号、发布、花钱、暴露隐私或执行 destructive action 的权限。远程 corpus 部署、provider adapters 与 Cloudflare 账号实验不属于本版。

## License

Soundings 采用按 path 划分的许可：

- functional marketplace、plugin、Skills、scripts 与 runtime references：[Sustainable Use License 1.0](LICENSE)（`SUL-1.0`）；
- READMEs、项目文档、示例与 diagrams：[CC BY-NC-SA 4.0](LICENSE-DOCUMENTATION.md)。

[LICENSING.md](LICENSING.md) 是精确 path map 的真源。第三方材料仍适用自身条款，必须另行标明。

本轮新增的 `evals/` 未加入上述授权，沿用 map 对未列出材料保留全部权利的规则。

本次发布没有将 `site/` 的原创网站材料加入上述任何一项授权；它们适用 map 对未列出材料的规则。所带字体子集保留 SIL OFL 1.1，UI 模板保留 MIT notices。见[官网 notices](docs/website-third-party.md)。
