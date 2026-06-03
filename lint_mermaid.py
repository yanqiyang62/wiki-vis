#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lint_mermaid — 静态扫描 Markdown 里的 ```mermaid 代码块，提前发现会导致
mermaid `Syntax error` 的写法，报出 file:line + 修复建议。纯 Python3 标准库。

捕获的雷区（均为真实踩过的坑）：
  · 标签里用反斜杠转义引号   \"Em\"            → 用 #34;Em#34;
  · 虚线边内联标签含 . 或 "  A -.确认点2.5.-> B → 用管道写法 A -.->|确认点2.5| B
  · 实线/粗线内联标签含特殊字符（警告）         → 同样建议管道写法
  · 正文里出现 </script>（信息）               → build_wiki.py 已自动转义，仅提示

用法：
  python3 lint_mermaid.py docs/                 # 扫目录下所有 .md
  python3 lint_mermaid.py a.md b.md             # 扫指定文件
  # 退出码：有 ERROR → 1，仅 WARN/INFO → 0

也可被 build_wiki.py 复用：from lint_mermaid import lint_paths
"""
import re
import sys
from pathlib import Path

# 内联标签边：dotted `-.LABEL.->`、solid `--LABEL-->`、thick `==LABEL==>`
# 首字符用否定类排除纯箭头（-.-> / --> / ==>）和管道写法（-->|x|）
RE_ESCQUOTE = re.compile(r'\\"')
RE_DOTTED = re.compile(r'-\.([^->\n][^\n]*?)\.->')
RE_SOLID = re.compile(r'--([^->\n][^\n]*?)-->')
RE_THICK = re.compile(r'==([^=>\n][^\n]*?)==>')

ERR = "ERROR"
WARN = "WARN"
INFO = "INFO"


def _scan_block(lines, base_lineno, fpath, findings):
    """lines: 该 mermaid 块的内容行；base_lineno: 块内第一行在文件中的行号(1-based)"""
    for i, line in enumerate(lines):
        ln = base_lineno + i
        s = line.strip()
        if s.startswith("%%"):                       # mermaid 注释
            continue

        if RE_ESCQUOTE.search(line):
            findings.append((fpath, ln, ERR,
                             '标签里的 \\" 无效（mermaid 不认 \\ 转义）。'
                             '把 \\"X\\" 改成 #34;X#34;', line.strip()))

        for m in RE_DOTTED.finditer(line):
            label = m.group(1).strip()
            if any(c in label for c in '."'):
                findings.append((fpath, ln, ERR,
                                 f'虚线标签 "{label}" 含 . 或 "，会破坏 .-> 结束符。'
                                 f'改用管道写法： -.->|{label}|', line.strip()))
            elif any(c in label for c in '():'):
                findings.append((fpath, ln, WARN,
                                 f'虚线标签 "{label}" 含特殊字符，建议管道写法 -.->|{label}|',
                                 line.strip()))

        for rx, kind in ((RE_SOLID, "实线"), (RE_THICK, "粗线")):
            for m in rx.finditer(line):
                label = m.group(1).strip()
                if any(c in label for c in '.():"'):
                    findings.append((fpath, ln, WARN,
                                     f'{kind}标签 "{label}" 含特殊字符，建议管道写法 -->|{label}|',
                                     line.strip()))

        if "</script>" in line:
            findings.append((fpath, ln, INFO,
                             '出现 </script>（build_wiki.py 会自动转义，通常无需处理）',
                             line.strip()))


def lint_text(text, fpath, findings):
    """扫描单个文件文本，把发现追加进 findings。"""
    lines = text.splitlines()
    in_block, block, start = False, [], 0
    fence = re.compile(r'^\s*```')
    for idx, line in enumerate(lines):
        if not in_block:
            if re.match(r'^\s*```mermaid\b', line):
                in_block, block, start = True, [], idx + 2  # 内容从下一行起(1-based)
        else:
            if fence.match(line):
                _scan_block(block, start, fpath, findings)
                in_block = False
            else:
                block.append(line)
    if in_block:                                     # 未闭合也扫一遍
        _scan_block(block, start, fpath, findings)


def collect_md(paths):
    files = []
    for p in paths:
        pp = Path(p)
        if pp.is_dir():
            files += sorted(pp.rglob("*.md"))
        elif pp.suffix.lower() in (".md", ".markdown", ".html"):
            files.append(pp)
    return files


def lint_paths(paths):
    """返回 findings 列表：[(file, line, severity, message, snippet), ...]"""
    findings = []
    for fp in collect_md(paths):
        try:
            lint_text(fp.read_text(encoding="utf-8"), str(fp), findings)
        except Exception as e:                       # noqa: BLE001
            findings.append((str(fp), 0, WARN, f"读取失败：{e}", ""))
    return findings


def main():
    paths = sys.argv[1:] or ["docs"]
    findings = lint_paths(paths)
    icon = {ERR: "✗", WARN: "⚠", INFO: "ℹ"}
    n_err = n_warn = 0
    for fpath, ln, sev, msg, snip in findings:
        if sev == ERR:
            n_err += 1
        elif sev == WARN:
            n_warn += 1
        loc = f"{fpath}:{ln}" if ln else fpath
        print(f"{icon[sev]} {sev}  {loc}\n    {msg}")
        if snip:
            print(f"    | {snip}")
    total = len(collect_md(paths))
    print(f"\n扫描 {total} 个文件：{n_err} error, {n_warn} warning"
          + ("，全部通过 ✓" if not findings else ""))
    sys.exit(1 if n_err else 0)


if __name__ == "__main__":
    main()
