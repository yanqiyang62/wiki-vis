---
name: wiki-vis
description: 给一个代码项目生成「标准项目 wiki」：系统分析项目→在 docs/ 写多文档（流程图/E-R图/时序图，按模块拆分，讲清多 Agent 如何被 Claude Code 执行）→打包成单文件可视化 wiki.html（紫靛渐变 + Tailwind slate 风格：侧边栏、按标题层级折叠的框体、彩色统计条、Mermaid 同色系主题与图片放大、代码高亮）。也能把现成的 docs/*.md 直接转成 wiki。当用户提到「生成项目 wiki / 项目文档站 / 梳理项目链路流程 / 把 markdown 变 html / 复用这套板式 / 说清楚多 agent 怎么跑 / 给项目写文档让新人看懂」时使用。
---

# wiki-vis — 项目 → 单文件可视化 Wiki

两件事：**①（写作层）系统分析一个代码项目，在 `docs/` 写出一套新人也能读懂的多文档 wiki（大量图）；②（构建层）把 `docs/*.md` 打包成一个自包含的 `wiki.html`**（双击即看，可分发 / 部署到任意静态服务器）。

## 两种用法
- **从零给项目生成 wiki（推荐，完整链路）**：先读 **[`references/authoring-guide.md`](references/authoring-guide.md)**，按其五阶段流程（侦察→信息架构→图优先写作→构建→质检）产出 `docs/` 与 `wiki.html`。这是「标准项目 wiki 方案」，含「多 Agent 如何被 Claude Code 执行」的讲法与所有 Mermaid 图模板。
- **已有 docs，只要 HTML**：直接跳到下面「怎么用」构建即可。

## 能力一览（全部已内置在模板里，无需后端）
- **侧边栏导航** + 紫靛渐变品牌头（Tailwind slate 配色）
- **章节框体**：按 `H2/H3/H4…` 自动套**实色标题栏**（蓝/绿/琥珀/红随层级），**点击折叠**，带「展开/折叠全部」
- **顶部彩色统计条**：章节 / 小节 / 图示 / 表格 计数
- **Mermaid 图**：与页面同色系主题 + 圆角投影；每张图右上角 **🔍 放大浮层**（滚轮缩放、拖拽平移、Esc 关闭）
- **代码高亮**（highlight.js）、表格、引用块统一风格
- **内部 `.md` 链接互跳**、上一页 / 下一页

## 文件结构
```
wiki-vis/
├── SKILL.md
├── build_wiki.py          # 构建：docs/*.md → wiki.html（纯 Python3 标准库，零依赖）
├── lint_mermaid.py        # 图质量闸门：静态扫描 mermaid 雷区，报 file:line
├── check_render.py        # 可选：用 Chrome 真渲染所有图，抓语义级失败
├── template.html          # 模板壳：CSS + JS 引擎 + {{占位符}}
└── references/
    ├── authoring-guide.md       # ⭐ 写作层：读项目→多文档多图 wiki 的完整流程
    └── wiki.config.example.json # 标准 8 篇骨架的配置模板
```

## 怎么用

### 最简（自动扫描）
```bash
python3 build_wiki.py --docs docs --out wiki.html
```
不带参数时默认扫描 `./docs`（不存在则扫当前目录）。自动发现 `*.md`：`README/index` 置顶，其余按文件名排序；导航标题和 id 由文件名推导（`01-项目总览.md` → 「01 · 项目总览」）。

### 推荐（配置文件，可控顺序 / 标题 / 品牌）
新建 `wiki.config.json`（参考 `references/wiki.config.example.json`）：
```json
{
  "title":    "Clef 项目 Wiki",
  "brand":    "🎼 Clef Wiki",
  "subtitle": "多 Agent 作曲技能 · 项目文档",
  "footer":   "由 wiki-vis 生成 · 改 .md 后重跑即可更新",
  "docs":     "docs",
  "out":      "wiki.html",
  "pages": [
    { "file": "README.md",     "id": "home",     "nav": "🏠 首页 / 导航" },
    { "file": "01-项目总览.md", "id": "overview", "nav": "01 · 项目总览" }
  ]
}
```
然后：
```bash
python3 build_wiki.py --config wiki.config.json
```
`pages[].nav` 可含 emoji/⭐ 等；`pages[].id` 用于 URL 锚点与内部 `.md` 链接互跳（缺省自动推导）。CLI 参数（`--title/--brand/--subtitle/--footer/--docs/--out/--theme`）优先级高于配置。

## 主题（亮 / 暗）
每份 wiki **都带运行时切换**（侧边栏品牌头右上角 ☾/☀，状态存 `localStorage`，Mermaid 图随主题重渲）。生成时用 `--theme` 设默认（也可在 config 写 `"theme"`）：
```bash
python3 build_wiki.py --config wiki.config.json --theme dark   # light(默认) / dark / auto(跟随系统)
```
> 给项目生成 wiki 时，**先问用户要哪种默认主题**再构建（见下「执行提示 A」）。暗色下页面变深，但 **Mermaid 图保持浅色面板（深字浅底）**——保证字清晰、也保留图里手写的高亮填充色；代码高亮切到 github-dark。

## 安装到其它项目 / 服务器
整个 `wiki-vis/` 目录拷过去即可，三种放法任选：
1. **作为 Claude Code Skill**：放到目标机的 `~/.claude/skills/wiki-vis/`（个人级，跨项目可用）或项目内 `.claude/skills/wiki-vis/`。
2. **当普通脚本**：拷到项目里任意位置，直接 `python3 路径/build_wiki.py ...`。脚本会自动找同目录的 `template.html`，也可 `--template` 指定。
3. **CI / 服务器**：`python3 build_wiki.py --config wiki.config.json` 接进构建流程，产物 `wiki.html` 丢给任意静态托管。

> 只依赖 Python 3 标准库，无需 pip 安装。

## 给 Claude 的执行提示
**A. 用户要「给项目生成 wiki / 梳理链路 / 让新人看懂」** → 这是主场景，先读 [`references/authoring-guide.md`](references/authoring-guide.md) 按五阶段执行：侦察项目 → 定骨架+写 `wiki.config.json` → 图优先写 `docs/*.md` → `lint`+`build` → 质检。务必满足该文 §0 的 Definition of Done（含「多 Agent 如何被 Claude Code 执行」）。
> 构建前**用 AskUserQuestion 问用户默认主题**：亮色 / 暗色 / 跟随系统，再以 `--theme light|dark|auto` 生成（读者仍可在页面右上角 ☾/☀ 随时切换）。

**B. 已有 docs，只要 HTML** →
1. 定位 Markdown 目录（常见 `docs/`、`doc/`、`wiki/`、仓库根的 `*.md`）。
2. 需要漂亮的导航顺序/标题就先写 `wiki.config.json`；否则自动模式。
3. **先校验再构建**：`python3 <skill>/lint_mermaid.py docs/` → `python3 <skill>/build_wiki.py --config ... --lint`。
4. `open wiki.html`（macOS）/ `xdg-open`（Linux）预览；有 Chrome 可 `python3 <skill>/check_render.py docs/` 深度验图。
5. 改外观编辑 `template.html` 的 `<style>`（设计令牌在 `:root` 的 `--c-*`、`--grad`）。

## 图质量工具链（避免 mermaid `Syntax error`）
- `python3 lint_mermaid.py docs/`：静态扫描所有 ```mermaid 块，报 `file:line` + 修复建议（捕获 `\"` 转义引号、`-.标签.->` 含 `.`/`"` 等真实雷区）。ERROR 退出码 1。
- `python3 build_wiki.py --lint ...`：构建前自动跑上面的检查，发现 ERROR 拒绝产出半成品。
- `python3 check_render.py docs/`：把每张图真渲染一遍（headless Chrome），抓静态规则漏掉的语义级失败；无 Chrome 则跳过。

## 注意
- **联网渲染**：模板用 CDN 加载 `marked / mermaid / highlight.js`，查看页面时需联网。
  离线场景：把这三个库下载到本地，把 `template.html` `<head>` 里的 4 个 CDN `src/href` 改成本地相对路径，与 `wiki.html` 一起分发即可。
- **Mermaid 写法雷区**（避免 `Syntax error`）：
  - 节点文字里要出现 `"` 用 `#34;`，要出现 `#` 用 `#35;`（`\` 转义无效）。
  - 虚线/箭头带标签且标签含 `. / : ( )` 等字符时，用管道写法 `A -.->|标签| B`，别用 `A -.标签.-> B`。
- **`</script>`**：脚本已自动把 Markdown 里的 `</script>` 转义，正文照常出现没问题。

## 自定义外观（template.html → :root）
```css
--c-primary:#667eea; --grad:linear-gradient(135deg,#667eea,#764ba2);  /* 主色 / 渐变 */
--c-bg:#f8f9fb; --c-text:#1e293b; --c-border:#e2e8f0; --radius:8px;    /* 背景/文字/边框/圆角 */
```
章节框体的层级配色在 `.sec-l2/.sec-l3/.sec-l4/.sec-l5 > .sec-head { background:… }`。
