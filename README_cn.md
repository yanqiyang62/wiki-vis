# wiki-vis

**标准项目 wiki 方案**：让 [Claude Code](https://claude.com/claude-code) 系统分析一个代码项目，在 `docs/` 写出一套新人也能读懂的多文档、多图 wiki，再打包成 **一个自包含、可视化的 `wiki.html`** —— 双击即看，可拷给别人或部署到任意静态服务器。（也能把现成的 Markdown 直接转换。）

> 紫靛渐变 + Tailwind slate 配色，自带侧边栏导航、按标题层级折叠的章节框体、Mermaid 图与图片放大、代码高亮。既能当命令行工具用，也是一个 Claude Code Skill。

English: [README.md](README.md)。

![wiki-vis — 亮色](assets/screenshot.png)

*亮色主题。也内置暗色主题 —— 点品牌头右上角 ☾/☀ 切换（状态会记住），或构建时用 `--theme dark` 设默认：*

![wiki-vis — 暗色](assets/screenshot-dark.png)

---

## 🧭 两种用法

- **给项目生成 wiki（主场景）** —— 把 Claude Code 指向一个仓库，它按 [`references/authoring-guide.md`](references/authoring-guide.md) 的五阶段执行：侦察 → 信息架构 → 图优先写作 → lint → 构建 → 质检。产出新人友好、图很多（流程图 / E-R / 时序）的 `docs/` 与 HTML，并讲清「**多 Agent 是怎么被 Claude Code 执行的**」。
- **已有 Markdown，只要 HTML** —— 直接看下面的构建命令。

---

## ✨ 特性

- **侧边栏导航** + 紫靛渐变品牌头（Tailwind slate 配色）
- **章节框体**：按 `H2/H3/H4…` 自动套实色标题栏（蓝/绿/琥珀/红随层级），**点击折叠**，带「展开/折叠全部」
- **顶部彩色统计条**：章节 / 小节 / 图示 / 表格 计数
- **Mermaid 图**：与页面同色系主题 + 圆角投影；每张图右上角 **🔍 放大浮层**（滚轮缩放、拖拽平移、Esc 关闭）
- **亮 / 暗主题** —— 每份 wiki 都带 ☾/☀ 切换（状态存 `localStorage`）；用 `--theme light|dark|auto` 设默认。代码高亮跟随（github ↔ github-dark）；Mermaid 图始终用浅色面板，亮/暗下都清晰
- **代码高亮**（highlight.js）、表格、引用块统一风格
- **内部 `.md` 链接互跳**、上一页 / 下一页
- **图质量闸门** —— `lint_mermaid.py` 静态抓出会导致 `Syntax error` 的 Mermaid 雷区；`check_render.py` 用无头 Chrome 真渲染每张图兜底
- **单文件输出**、纯前端、零后端；构建脚本只依赖 Python 3 标准库

---

## 🚀 快速开始

```bash
# 先校验 Mermaid（推荐），再构建
python3 lint_mermaid.py docs/

# 自动模式：扫描 docs/，README/index 置顶，其余按文件名排序
python3 build_wiki.py --docs docs --out wiki.html --lint

# 或用配置文件控制顺序 / 标题 / 品牌
python3 build_wiki.py --config wiki.config.json --lint
```

打开看看：

```bash
open wiki.html        # macOS
xdg-open wiki.html    # Linux
```

仓库自带可运行示例：

```bash
python3 build_wiki.py --docs examples/docs --out examples/wiki.html
```

---

## ⚙️ 配置文件

`wiki.config.json`（全部字段可选，CLI 参数优先级更高，示例见 [`references/wiki.config.example.json`](references/wiki.config.example.json)）：

```json
{
  "title":    "项目 Wiki",
  "brand":    "📚 项目 Wiki",
  "subtitle": "工程文档 · 知识库",
  "footer":   "由 wiki-vis 生成 · 改 .md 后重跑即可更新",
  "docs":     "docs",
  "out":      "wiki.html",
  "pages": [
    { "file": "README.md",     "id": "home",     "nav": "🏠 首页 / 导航" },
    { "file": "01-架构设计.md", "id": "arch",     "nav": "01 · 架构设计 ⭐" }
  ]
}
```

未提供 `pages` 时自动发现 `*.md`；`pages[].nav` 可含 emoji/⭐，`pages[].id` 用于锚点与内部链接互跳（缺省自动推导）。

CLI 参数：`--docs --out --config --template --title --brand --subtitle --footer`。

---

## 🧩 作为 Claude Code Skill 使用

本仓库根目录就是一个完整的 skill。直接克隆到 skills 目录即可：

```bash
# 个人级（跨项目可用）
git clone https://github.com/yanqiyang62/wiki-vis.git ~/.claude/skills/wiki-vis
# 或项目级
git clone https://github.com/yanqiyang62/wiki-vis.git .claude/skills/wiki-vis
```

之后对 Claude 说「把 docs 生成 wiki」即可触发。

---

## 📦 离线使用

模板默认通过 CDN 加载 `marked` / `mermaid` / `highlight.js`，**查看页面时需联网**。
离线场景：把这三个库下载到本地，将 `template.html` `<head>` 里的 4 个 CDN `src/href` 改为本地相对路径，与 `wiki.html` 一起分发即可。

---

## ⚠️ Mermaid 写法雷区（避免 `Syntax error`）

- 节点文字里要出现 `"` 用 `#34;`，要出现 `#` 用 `#35;`（`\` 转义无效）。
- 虚线/箭头带标签且标签含 `. / : ( )` 等字符时，用管道写法 `A -.->|标签| B`，别用 `A -.标签.-> B`。

---

## 🎨 自定义外观

改 `template.html` 的 `<style>`，设计令牌都在 `:root`：

```css
--c-primary:#667eea; --grad:linear-gradient(135deg,#667eea,#764ba2);  /* 主色 / 渐变 */
--c-bg:#f8f9fb; --c-text:#1e293b; --c-border:#e2e8f0; --radius:8px;
```

章节框体的层级配色在 `.sec-l2/.sec-l3/.sec-l4/.sec-l5 > .sec-head { background:… }`。

---

## 📁 结构

```
wiki-vis/
├── build_wiki.py                    # 构建：docs/*.md → wiki.html（纯 Python3 标准库）
├── lint_mermaid.py                  # Mermaid 静态校验（file:line + 修复建议）
├── check_render.py                  # 可选：无头 Chrome 真渲染每张图
├── template.html                    # 模板壳：CSS + JS 引擎 + {{占位符}}
├── SKILL.md                         # Claude Code skill 清单
├── references/
│   ├── authoring-guide.md           # 项目 → 多文档 wiki 工作流（写作层 / the brain）
│   └── wiki.config.example.json
├── examples/docs/                   # 可直接构建的示例文档
└── assets/screenshot.png
```

## License

[MIT](LICENSE)
