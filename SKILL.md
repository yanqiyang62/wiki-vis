---
name: wiki-vis
description: 把一个 Markdown 文档目录打包成单文件、可视化的 wiki.html（紫靛渐变 + Tailwind slate 风格）。内置侧边栏导航、按标题层级自动折叠的实色框体、顶部彩色统计条、Mermaid 同色系主题与图片放大浮层、代码高亮、上一页/下一页。当用户想把 docs/ 里的 .md 生成好看的离线可分享 wiki / 项目文档站 / 知识库单页，或提到「生成 wiki、文档站、把 markdown 变成网页、复用这套板式」时使用。
---

# wiki-vis — Markdown → 单文件可视化 Wiki

把一个装着 `.md` 的目录，生成**一个自包含的 `wiki.html`**（双击即可在浏览器看，可拷给别人 / 部署到任意静态服务器）。

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
├── build_wiki.py          # 生成脚本（纯 Python3 标准库，零依赖）
├── template.html          # 模板壳：CSS + JS 引擎 + {{占位符}}
└── references/
    └── wiki.config.example.json
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
`pages[].nav` 可含 emoji/⭐ 等；`pages[].id` 用于 URL 锚点与内部 `.md` 链接互跳（缺省自动推导）。CLI 参数（`--title/--brand/--subtitle/--footer/--docs/--out`）优先级高于配置。

## 安装到其它项目 / 服务器
整个 `wiki-vis/` 目录拷过去即可，三种放法任选：
1. **作为 Claude Code Skill**：放到目标机的 `~/.claude/skills/wiki-vis/`（个人级，跨项目可用）或项目内 `.claude/skills/wiki-vis/`。
2. **当普通脚本**：拷到项目里任意位置，直接 `python3 路径/build_wiki.py ...`。脚本会自动找同目录的 `template.html`，也可 `--template` 指定。
3. **CI / 服务器**：`python3 build_wiki.py --config wiki.config.json` 接进构建流程，产物 `wiki.html` 丢给任意静态托管。

> 只依赖 Python 3 标准库，无需 pip 安装。

## 给 Claude 的执行提示
当用户要「生成 wiki / 文档站」：
1. 定位 Markdown 目录（常见 `docs/`、`doc/`、`wiki/`、仓库根的 `*.md`）。
2. 若需要漂亮的导航顺序与标题，先写 `wiki.config.json`；否则直接自动模式。
3. 跑 `python3 <skill>/build_wiki.py --config ...` 或 `--docs ...`。
4. 用 `open wiki.html`（macOS）/ `xdg-open`（Linux）打开给用户预览。
5. 要改外观，编辑 `template.html` 的 `<style>`（设计令牌在 `:root` 的 `--c-*`、`--grad`）。

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
