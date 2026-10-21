---
name: paogen-wendi
version: 1.0.0
display_name: 刨根问底
display_name_en: Deep-Dive Research
description: 刨根问底深度研究报告生成器。对任意主题/领域/问题按 11 个深度研究角度（反常识洞察、顶尖精通、未来二十年、千年文明、思维逆向工程、古代智慧、后人类视角、前提拆解、最强反方、失败者研究、极端约束）做深度分析，产出日式极简杂志风排版的美观 HTML 与 PDF 报告（黑白双色调、中国红点缀、宋体下沉首字）。内容要求机制解释、定量证据与边界条件，禁止空泛立场文。凡是用户要求"刨根问底""深挖某主题""多角度深度分析某领域并出报告""研究透某个问题""11个角度分析"之类任务，必须使用本 skill。
description_zh: 刨根问底深度研究报告生成器。对任意主题/领域/问题按 11 个深度研究角度（反常识洞察、顶尖精通、未来二十年、千年文明、思维逆向工程、古代智慧、后人类视角、前提拆解、最强反方、失败者研究、极端约束）做深度分析，产出日式极简杂志风排版的美观 HTML 与 PDF 报告（黑白双色调、中国红点缀、宋体下沉首字）。内容要求机制解释、定量证据与边界条件，禁止空泛立场文。凡是用户要求"刨根问底""深挖某主题""多角度深度分析某领域并出报告""研究透某个问题""11个角度分析"之类任务，必须使用本 skill。
description_en: An in-depth research report generator. Analyzes any topic, field, or question through 11 deep-research perspectives (counter-intuitive insights, top-tier mastery, the next twenty years, a thousand-year civilization, reverse engineering of thinking, ancient wisdom, post-human perspective, premise deconstruction, strongest opposition, loser studies, extreme constraints), and produces beautifully typeset HTML and PDF reports in Japanese minimalist magazine style (black-and-white duotone, Chinese red accents, Song-typeface drop caps). Content must include mechanism explanations, quantitative evidence, and boundary conditions; vague position pieces are forbidden. Use this skill whenever the user asks to get to the bottom of a topic, dig deep into a subject, produce a multi-perspective deep-analysis report, thoroughly research a question, or analyze from 11 angles.
---

# 刨根问底

对用户给定的主题，按 11 个深度研究角度完成分析，产出一本杂志级排版的研究报告（HTML + PDF）。

## 工作流

### 1. 确认输入

从用户消息中确定三件事，信息不足时按默认处理、不追问：

- **主题**：研究的领域/概念/问题。主题过大时（如"整个AI行业"），先收窄到一个可分析的层面并在报告副题中注明。
- **角度范围**：默认全部 11 个角度；用户点名几个就只做几个，顺序不变。
- **色调**：`white`（白纸黑字）或 `midnight`（黑底白字），默认 `white`；用户没说就两个都出。

**质量优先原则**：报告的竞争力在内容深度与排版质量，不在速度。宁可多一轮联网核查与自查重写，不可交付表面完整、内里空转的报告。用户催时间时，优先砍分析点数量（每章 3 个），不砍单点深度。

### 2. 研究

通读 `references/angles.md`，逐角度执行其中的「研究动作」，遵守「证据纪律」与「深挖指令」：

- 涉及最新事实、数据、人物、案例的，先联网核查，官方原始来源＞论文/报告＞权威媒体＞二手内容。关键论文要确认作者、年份、出处与核心数字。
- 每个分析点标注证据等级：事实 / 推断 / 思想实验。查不到证据就降级为推断或写明「尚无公开证据」，禁止编造。
- 每个分析点过「深度三问」：有可验证细节？有机制解释？有边界条件？三问不达即重写，不达标的内容不进入 JSON。
- 思想实验框架（未来、千年文明、后人类）的产出必须保持假想属性，同时按各角度要求拉回现实可行性。

### 3. 写内容 JSON

按 `references/angles.md` 末尾的 JSON 结构与质量门槛写入工作目录（默认项目文件夹，禁止 C 盘/系统目录）：

- 文件名：`content-{主题}-{日期}.json`。
- 全 11 章报告 12000～18000 字，为防单次输出截断，**拆成两个 JSON**：`content-*-a.json`（元信息 + 第 1～6 章）、`content-*-b.json`（第 7～11 章），脚本自动合并。
- 写作纪律见 angles.md：全角标点、信息密度、编辑式章标题、lead 首句直接进入内容（首字会被做成下沉首字）、判断给适用条件。
- **写完自查**（对照 angles.md「质量门槛」与「去AI味门槛」）：事实层占比≥40%、每章 3～4 个分析点且形成推进链、分析点无连续同种论证方式、无「研究表明」式无出处指代、无「显然/众所周知」；去AI味硬标准：全文破折号 0、分号≤3、无 50 字以上长句、禁用清单零命中（自查命令见 angles.md）。自查不通过就重写，不许带病进入下一步。

### 4. 生成 HTML 与 PDF（最短路径，一条命令）

```bash
python "<本skill目录>/scripts/build_report.py" \
  content-主题-a.json content-主题-b.json \
  -o "刨根问底-主题-20261019.html" --theme white --pdf
```

- `--pdf` 会在 HTML 生成后立即调 `make_pdf.py`（Edge 无头打印，自动处理中文路径与字体加载）出同名 PDF。
- `midnight` 版只需换 `--theme midnight` 与输出文件名再跑一次（内容 JSON 不动）。
- 脚本会校验 JSON：`ev` 字段只允许 事实/推断/思想实验，报错按提示修正后重跑。

### 5. 交付前检查（hallmark 质量门）

生成后用浏览器或截图检查一遍成品，对照以下各条，全部通过才交付：

1. **排版无碰撞**：封面无元素重叠；每章换页正确；长标题不溢出。
2. **纹理与色彩**：网点纹理正常铺满；红色只出现在锚点（章号、首字、规线、标签、编号），无第四种颜色。
3. **字体加载**：PDF 中宋体/黑体正确渲染（Google Fonts 加载由脚本保证；若离线生成需人工确认回退字体可用）。
4. **内容质量**：事实层分析点均带具体出处；每章有推进链；综合判断回收了至少五个角度。
5. **去AI味抽检**：随机抽三章连读。句子是否一句一件事？有没有绕口的翻译腔？有没有连续排比？念出来像人话还是像通稿？不达标回到第 3 步重写对应章节。
6. **无元描述**：成品中不出现生成过程、提示词、AI 参与的任何痕迹。

发现问题回到对应步骤修正后重新生成，不许带问题交付。

### 6. 交付

HTML 与 PDF 一起交付，并说明：主题与角度范围、证据等级分布（事实/推断/思想实验各几条）、哪个角度结论最反直觉。报告为对外成品，内容中不得出现任何关于生成过程、提示词、AI 参与的元描述。

## 目录结构

```
paogen-wendi/
├── SKILL.md                 # 本文件
├── scripts/
│   ├── build_report.py      # JSON -> HTML（--pdf 连动转 PDF）
│   └── make_pdf.py          # HTML -> PDF（Edge 无头）
├── assets/
│   ├── template.html        # 全部样式与版式（双主题，改样式只改这里）
│   └── sample-content.json  # 示例输入（间隔重复记忆）
└── references/
    ├── angles.md            # 11 角度方法论 + 深挖指令 + 质量门槛（写内容前必读）
    └── design-system.md     # 排版设计规范（维护模板时读）
```

## 边界

- 只做深度分析与报告产出。用户只要简单问答、不要报告时，不触发本 skill 的生成链路。
- 样式与版式已全部固化在模板中，不要在生成时另写 CSS 或内联样式；对样式的修改只发生在 `assets/template.html`。
- 报告默认中文。用户要求其他语言时，排版体系不变，文字语言跟随用户。
