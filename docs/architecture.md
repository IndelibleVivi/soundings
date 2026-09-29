# Soundings architecture

[简体中文](architecture.zh-CN.md) · [Back to README](../README.md)

**Reading view of the 0.3.1 demo.** These diagrams describe current responsibilities and local data paths. They do not add a service, force a skill sequence or freeze the project's future architecture. Runtime contracts remain in `plugins/soundings/skills/`; the [design rationale](../plugins/soundings/docs/design.md) explains the choices.

There are three views, because method selection, evidence files and installation are different things. Teal identifies Soundings methods; blue identifies the host and its existing capabilities; ochre identifies optional local helpers. Labels carry the meaning without colour. Solid arrows describe the operation written on them. Dashed arrows mark an optional selection; they do not claim that a future adapter exists.

## 1. Who does the work?

![The coordinating agent reads independent Soundings instructions and uses its existing tools.](visuals/01-responsibilities.svg)

Soundings is an instruction package consumed by the host, not a set of four running services. Search investigates outside material; Study develops understanding and can discover a project question; Explore develops concrete possibilities; Shape handles consequential choices and corrections. None requires the other three.

The coordinating agent retains the task, chooses methods, invokes tools within existing authority and delivers the result. Engineering, design and other domain methods keep their own production and evidence standards. The working context is the current understanding, normally in conversation or an existing project record; it is not a Soundings database.

**Source anchors:** [four skill directories](../plugins/soundings/skills/), [shared working context](../plugins/soundings/references/working-context.md), [project-grounded sounding](../plugins/soundings/skills/study/references/project-grounded-sounding.md).

## 2. How can evidence be retained and handed over?

![An explicit capture creates a stable local snapshot; read and find return bounded ranges; a packet copies only selected evidence and a brief.](visuals/02-evidence.svg)

Acquisition stays with existing tools. Capture takes a selected text file and a caller-declared representation: `verbatim`, `extracted` or `generated`. A fresh ref is created each time. Complete JSON is staged before a no-clobber hard link exposes the final snapshot; hard-link support is required, and this is not a power-loss durability guarantee.

Read and find use that snapshot. A window is returned whole or visibly omitted. After handling `first_omitted`, the caller can continue inside the original scope; a null next line means no remainder after that omitted window, not that the window was already read. A byte cap covers stdout, not the host's wrapper or model tokens.

Packet creation copies an explicit brief and selected refs into a new directory. The manifest is written last; a missing or invalid manifest is not a usable packet. Inspection checks membership and readability, not provenance, secrecy or research quality. The receiver reads the copied evidence with the same helper. Transfer and worker execution remain separate, independently authorised actions.

**Source anchors:** [`capture`, `publish`, `read`, `find`, `pack`](../plugins/soundings/skills/search/scripts/evidence.py), [`create`, `inspect`](../plugins/soundings/skills/search/scripts/packet.py), [reading contract](../plugins/soundings/skills/search/references/evidence-reading.md), [handoff contract](../plugins/soundings/skills/search/references/research-handoffs.md).

## 3. What does installation establish?

![Source package, derived marketplace and installation copies, then a fresh task and observed method use.](visuals/03-installation.svg)

The marketplace manifest points to the canonical plugin package. Refresh updates a derived market copy; installation produces another derived package on the operator's machine. A new task is needed to observe discovery and selection. Do not edit an installed cache as if it were source.

Installation success is not useful method use. A task can discover a skill but prefer a domain method; loading a skill does not prove that it improved the result. The current [evidence record](dogfood-0.3.1.md) separates these observations, including negative implicit Study selection in Relata. The drawing is a deployment/observation map, not an automatic release pipeline.

**Source anchors:** [marketplace manifest](../.agents/plugins/marketplace.json), [plugin manifest](../plugins/soundings/.codex-plugin/plugin.json), [repository contract](../AGENTS.md), [installation observations](dogfood-0.3.1.md).

## Extension space, without pretending it is built

An external corpus, sustained research executor or richer media reader can be useful. Today these are distinct needs served through available tools, not implemented Soundings adapters. The existing [source-capability reference](../plugins/soundings/skills/search/references/source-capabilities.md) describes what to preserve: source identity, representation, conditions, actual read coverage and operation-specific limits. A future integration should be drawn here only when its real contract and implementation exist.

## A small vocabulary

A *commission* is the complete result the user asked for, rather than one tool call. A *candidate* is material developed enough to judge. *Working context* is the current shared understanding. A *snapshot* is a retained local representation, not certified original truth. *Implicit selection* means the host chooses a skill without an explicit `$skill` invocation. A *reopening condition* is an observation that would make a previous judgment worth revisiting.

## Editable sources

The SVGs are rendered from the following Mermaid sources, using [the visual configuration](visuals/mermaid-config.json). The code blocks below are the same sources, not a separate architecture. [Rendering and visual rules](visuals/README.md).

### 01-responsibilities

[Mermaid source](visuals/01-responsibilities.mmd) · [SVG](visuals/01-responsibilities.svg)

```mermaid
flowchart LR
  accTitle: Soundings — 谁负责什么 / responsibilities
  accDescr: Soundings is a package of independent instructions read by a coordinating agent, not four sequential agents. Codex coordinates the current task, uses existing domain methods and tools, maintains working understanding and delivers the result. The context is not a new database.
  subgraph S["Soundings 方法"]
    direction TB
    SEARCH["Search / 查证<br/>外部事实与参考"]:::method
    STUDY["Study / 研读<br/>综合材料、发现值得追的问题"]:::method
    EXPLORE["Explore / 创造<br/>发展具体作品或体验"]:::method
    SHAPE["Shape / 判断<br/>关键选择与纠偏"]:::method
    SEARCH ~~~ STUDY
    STUDY ~~~ EXPLORE
    EXPLORE ~~~ SHAPE
  end
  U["用户 / User<br/>目标、材料、当前授权"]:::data
  H["Codex / 协调 agent<br/>选择方法 · 执行 · 整合"]:::host
  S -->|所选方法的指导| H
  U -->|提出委托| H
  subgraph E["宿主已有能力"]
    direction TB
    D["领域方法 / Craft<br/>工程、设计、写作与验证"]:::host
    T["现有工具 / Tools<br/>搜索、文件、浏览器与连接器"]:::host
    D ~~~ T
  end
  H -->|按需使用| E
  C["工作理解 / Context<br/>目标、决定、提议、证据、授权<br/>留在上下文或项目已有记录"]:::data
  H ---|维护| C
  R["可用结果 / Outcome<br/>解释、比较、作品或授权实现"]:::data
  H -->|交付| R
  classDef host fill:#EAF0F7,stroke:#345C8B,color:#183D47,stroke-width:1.6px;
  classDef method fill:#E7F0ED,stroke:#246F70,color:#183D47,stroke-width:1.6px;
  classDef data fill:#FFFFFF,stroke:#8A9FA3,color:#183D47,stroke-width:1.6px;
  classDef optional fill:#F6EDD9,stroke:#805A28,color:#183D47,stroke-width:1.6px;
```

### 02-evidence

[Mermaid source](visuals/02-evidence.mmd) · [SVG](visuals/02-evidence.svg)

```mermaid
flowchart TB
  accTitle: Soundings — 可选证据工具 / optional evidence support
  accDescr: Existing tools acquire material. A selected UTF-8 file is explicitly captured to a stable local snapshot. Read and find return whole ranges with byte budgets and omissions. Packet create copies an explicit brief and selected snapshots into a new directory; manifest is written last. A recipient inspects then rereads the copied evidence. None of these helpers uploads or executes a research task.
  A["现有来源工具<br/>已经取得的材料"]:::host
  F["选定 UTF-8 文件<br/>文本或 Markdown"]:::data
  A -->|保存所需表示| F
  C["evidence.py capture<br/>明确 store、source、representation"]:::optional
  F -->|显式保留| C
  S["本地 snapshot / s-ref<br/>完整暂存 → 不覆盖地发布<br/>旧引用继续读取旧内容"]:::data
  C -->|创建新引用| S
  R["evidence.py read / find<br/>精确行段 / 范围内字面查找"]:::optional
  S -->|读取| R
  J["有界 JSON 输出<br/>整窗返回或说明 omission<br/>处理 first_omitted 后再续读"]:::data
  R -->|计量完整 stdout 字节| J
  B["显式研究 brief<br/>目标、选定材料与范围"]:::data
  P["packet.py create<br/>只复制选定 refs 与 brief"]:::optional
  S -.->|选定快照| P
  B -->|选定 brief| P
  K["新目录 / Portable packet<br/>brief.md + evidence/ + manifest.json<br/>manifest 最后写入"]:::data
  P -->|本地写入；不传输| K
  I["packet.py inspect<br/>检查成员与可读性"]:::optional
  K -->|在接收位置检查| I
  X["接手者 / Recipient<br/>通过 evidence.py 重读副本<br/>不再依赖原 store"]:::host
  I -->|检查后按需重读| X

  classDef host fill:#EAF0F7,stroke:#345C8B,color:#183D47,stroke-width:1.6px;
  classDef method fill:#E7F0ED,stroke:#246F70,color:#183D47,stroke-width:1.6px;
  classDef data fill:#FFFFFF,stroke:#8A9FA3,color:#183D47,stroke-width:1.6px;
  classDef optional fill:#F6EDD9,stroke:#805A28,color:#183D47,stroke-width:1.6px;
```

### 03-installation

[Mermaid source](visuals/03-installation.mmd) · [SVG](visuals/03-installation.svg)

```mermaid
flowchart TB
  accTitle: Soundings — 从源码到实际使用 / source to use
  accDescr: The public marketplace manifest points to plugins/soundings. Marketplace refresh updates a derived marketplace snapshot; installation produces a derived enabled package. A fresh task can discover its skills. Discovery, selection, task result and general effectiveness are separate observations; installing does not hot reload an already-running task.
  subgraph SOURCE["01 · 公开源码"]
    direction LR
    M["marketplace.json<br/>指向插件目录"]:::data
    P["plugins/soundings/<br/>元数据、方法说明、可选工具"]:::method
    M -->|登记路径| P
  end
  subgraph LOCAL["02 · 派生副本"]
    direction LR
    Q["市场副本 / Snapshot<br/>刷新后的市场副本"]:::data
    I["安装的插件 / Installed<br/>安装并启用的包"]:::host
    Q -->|plugin add| I
  end
  SOURCE -->|刷新市场副本| LOCAL
  subgraph TASK["03 · 新任务"]
    direction LR
    F["新任务 / Fresh task<br/>宿主暴露 Skills 描述"]:::host
    S["选择某个 Skill<br/>显式调用或宿主隐式选择"]:::method
    O["实际结果<br/>再核验来源、判断与交付"]:::data
    F -->|按需选择| S
    S -->|方法参与当前工作| O
  end
  LOCAL -->|开始新任务| TASK

  classDef host fill:#EAF0F7,stroke:#345C8B,color:#183D47,stroke-width:1.6px;
  classDef method fill:#E7F0ED,stroke:#246F70,color:#183D47,stroke-width:1.6px;
  classDef data fill:#FFFFFF,stroke:#8A9FA3,color:#183D47,stroke-width:1.6px;
  classDef optional fill:#F6EDD9,stroke:#805A28,color:#183D47,stroke-width:1.6px;
```
