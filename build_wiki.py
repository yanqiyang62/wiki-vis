#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki-vis — 把一个 Markdown 目录打包成单文件、可视化的 wiki.html。

特性（全部内置在模板里，无需任何后端）：
  · 侧边栏导航 + 紫靛渐变品牌头（Tailwind slate 风格）
  · 章节按 H2/H3/H4… 自动套实色标题栏框体，可点击折叠
  · 顶部彩色统计条（章节 / 小节 / 图示 / 表格 计数）
  · marked 渲染 Markdown，highlight.js 高亮代码
  · Mermaid 图（同色系主题）+ 右上角 🔍 放大浮层（滚轮缩放 / 拖拽平移）
  · 上一页 / 下一页、内部 .md 链接互跳

依赖：仅 Python 3 标准库。运行时页面通过 CDN 加载 marked/mermaid/highlight.js
（即查看 wiki 时需联网；离线场景见 SKILL.md 的“离线”说明）。

用法：
  python3 build_wiki.py --docs docs --out wiki.html
  python3 build_wiki.py --config wiki.config.json
  python3 build_wiki.py            # 默认扫描 ./docs（不存在则扫当前目录）

配置文件 wiki.config.json（全部可选，CLI 参数优先级更高）：
  {
    "title":    "Clef 项目 Wiki",
    "brand":    "🎼 Clef Wiki",
    "subtitle": "多 Agent 作曲技能 · 项目文档",
    "footer":   "由 wiki-vis 生成 · 改 .md 后重跑即可更新",
    "docs":     "docs",
    "out":      "wiki.html",
    "pages": [
      { "file": "README.md",       "id": "home",     "nav": "🏠 首页 / 导航" },
      { "file": "01-项目总览.md",   "id": "overview", "nav": "01 · 项目总览" }
    ]
  }
未提供 "pages" 时，自动扫描 docs 目录下的 *.md（README/index 置顶，其余按文件名排序），
导航标题与 id 由文件名推导。
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


# ---------- 推导导航标题 / id ----------
def derive_nav(stem: str) -> str:
    if stem.lower() in ("readme", "index", "home"):
        return "🏠 首页 / 导航"
    m = re.match(r"^(\d+)[.\-_ ]+(.*)$", stem)
    if m:
        rest = m.group(2).replace("-", " ").replace("_", " ").strip()
        return f"{m.group(1)} · {rest}"
    return stem.replace("-", " ").replace("_", " ").strip() or stem


def derive_id(stem: str, used: set) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", stem).strip("-").lower() or "page"
    base, n, out = s, 1, s
    while out in used:
        n += 1
        out = f"{base}-{n}"
    used.add(out)
    return out


# ---------- 收集页面 ----------
def collect_pages(docs_dir: Path, cfg: dict):
    used = set()
    pages = []

    if cfg.get("pages"):
        for i, p in enumerate(cfg["pages"]):
            fp = docs_dir / p["file"]
            if not fp.exists():
                print(f"  ⚠ 跳过（找不到）：{fp}", file=sys.stderr)
                continue
            stem = fp.stem
            pid = p.get("id") or derive_id(stem, used)
            used.add(pid)
            pages.append({
                "file": p["file"],
                "id": pid,
                "nav": p.get("nav") or derive_nav(stem),
                "md": fp.read_text(encoding="utf-8"),
            })
        return pages

    # 自动发现
    files = sorted(docs_dir.glob("*.md"), key=lambda x: x.name.lower())
    front = [f for f in files if f.stem.lower() in ("readme", "index", "home")]
    rest = [f for f in files if f not in front]
    for fp in front + rest:
        stem = fp.stem
        pages.append({
            "file": fp.name,
            "id": derive_id(stem, used),
            "nav": derive_nav(stem),
            "md": fp.read_text(encoding="utf-8"),
        })
    return pages


# ---------- 生成 HTML 片段 ----------
def build_nav(pages) -> str:
    return "".join(
        f'\n      <li><a href="#{p["id"]}" data-target="{p["id"]}">{p["nav"]}</a></li>'
        for p in pages
    ) + "\n    "


def build_pages(pages) -> str:
    blocks = []
    for p in pages:
        # 防止 markdown 中的 </script> 提前关闭脚本块
        md = p["md"].replace("</script>", "<\\/script>")
        blocks.append(
            f'<script type="text/markdown" data-id="{p["id"]}">\n{md}\n</script>'
        )
    return "\n".join(blocks)


def build_file_map(pages) -> str:
    return json.dumps({p["file"]: p["id"] for p in pages}, ensure_ascii=False)


# ---------- 主流程 ----------
def main():
    ap = argparse.ArgumentParser(description="把 Markdown 目录打包成单文件可视化 wiki.html")
    ap.add_argument("--docs", help="Markdown 目录（默认 ./docs，不存在则用当前目录）")
    ap.add_argument("--out", help="输出文件（默认 wiki.html）")
    ap.add_argument("--config", help="JSON 配置文件路径")
    ap.add_argument("--template", help="模板路径（默认与本脚本同目录的 template.html）")
    ap.add_argument("--title", help="页面 <title>")
    ap.add_argument("--brand", help="侧边栏品牌名")
    ap.add_argument("--subtitle", help="品牌副标题")
    ap.add_argument("--footer", help="侧边栏页脚")
    ap.add_argument("--theme", choices=["light", "dark", "auto"],
                    help="默认主题：light(默认) / dark / auto(跟随系统)。读者仍可在页面右上角切换")
    ap.add_argument("--lint", action="store_true",
                    help="构建前用 lint_mermaid 静态检查所有 mermaid 图，发现 ERROR 则中止")
    args = ap.parse_args()

    cfg = {}
    if args.config:
        cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))

    # 解析路径（CLI > config > 默认）
    docs_dir = Path(args.docs or cfg.get("docs") or "docs")
    if not docs_dir.exists():
        docs_dir = Path(".")
    out_path = Path(args.out or cfg.get("out") or "wiki.html")
    tpl_path = Path(args.template) if args.template else (HERE / "template.html")

    template = tpl_path.read_text(encoding="utf-8")

    pages = collect_pages(docs_dir, cfg)
    if not pages:
        print(f"✗ 在 {docs_dir} 下没找到任何 .md 文件。", file=sys.stderr)
        sys.exit(1)

    # 可选：构建前做 mermaid 静态检查，发现 ERROR 即中止（不产出半成品）
    if args.lint:
        try:
            from lint_mermaid import lint_paths, ERR
        except ImportError:
            print("⚠ 找不到 lint_mermaid.py，跳过 --lint。", file=sys.stderr)
        else:
            findings = lint_paths([docs_dir / p["file"] for p in pages])
            errs = [f for f in findings if f[2] == ERR]
            for fpath, ln, sev, msg, snip in findings:
                print(f"  [{sev}] {fpath}:{ln}  {msg}", file=sys.stderr)
            if errs:
                print(f"✗ mermaid 检查发现 {len(errs)} 个 ERROR，已中止构建。"
                      f"修复后重试，或去掉 --lint。", file=sys.stderr)
                sys.exit(2)

    brand = args.brand or cfg.get("brand") or "📚 Wiki"
    subtitle = args.subtitle or cfg.get("subtitle") or ""
    title = args.title or cfg.get("title") or re.sub(r"<[^>]+>", "", brand).strip()
    footer = args.footer or cfg.get("footer") or "由 wiki-vis 生成 · 改 .md 后重跑即可更新"
    theme = args.theme or cfg.get("theme") or "light"

    replacements = {
        "{{TITLE}}": title,
        "{{BRAND}}": brand,
        "{{SUBTITLE}}": subtitle,
        "{{FOOT}}": footer,
        "{{THEME}}": theme,
        "{{NAV}}": build_nav(pages),
        "{{PAGES}}": build_pages(pages),
        "{{FILE_TO_ID}}": build_file_map(pages),
    }
    html = template
    for k, v in replacements.items():
        html = html.replace(k, v)

    out_path.write_text(html, encoding="utf-8")
    print(f"✓ 已生成 {out_path}  （{len(pages)} 页, {out_path.stat().st_size // 1024} KB, 默认主题 {theme}）")
    for p in pages:
        print(f"    · {p['nav']}  ←  {p['file']}")


if __name__ == "__main__":
    main()
