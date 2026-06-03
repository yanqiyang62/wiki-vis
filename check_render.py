#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_render — 深度校验：把 docs 里所有 ```mermaid 块抽出来，真用 mermaid 渲染一遍，
报出**实际渲染失败**的图属于哪个文件。是 lint_mermaid.py 的补充（静态规则之外，
还能抓住语义级错误）。需要本机有 Chrome / Chromium；没有则优雅跳过。

用法：
  python3 check_render.py docs/
  python3 check_render.py a.md b.md
  # 退出码：有渲染失败 → 1；无 Chrome 或全部通过 → 0
"""
import html as htmllib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome-stable", "google-chrome", "chromium", "chromium-browser",
]
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"


def find_chrome():
    import shutil
    for c in CHROME_CANDIDATES:
        if c.startswith("/"):
            if Path(c).exists():
                return c
        elif shutil.which(c):
            return shutil.which(c)
    return None


def extract_blocks(paths):
    """返回 [{'src': 'file:line', 'code': '...'}]"""
    blocks = []
    files = []
    for p in paths:
        pp = Path(p)
        files += sorted(pp.rglob("*.md")) if pp.is_dir() else [pp]
    for fp in files:
        try:
            lines = fp.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        i = 0
        while i < len(lines):
            if re.match(r'^\s*```mermaid\b', lines[i]):
                start = i + 1
                body = []
                i += 1
                while i < len(lines) and not re.match(r'^\s*```', lines[i]):
                    body.append(lines[i])
                    i += 1
                blocks.append({"src": f"{fp}:{start}", "code": "\n".join(body)})
            i += 1
    return blocks


def build_diag_html(blocks):
    data = json.dumps(blocks, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="{MERMAID_CDN}"></script></head><body>
<pre id="out">PENDING</pre>
<div id="sandbox" style="position:absolute;left:-99999px"></div>
<script>
const BLOCKS = {data};
mermaid.initialize({{ startOnLoad:false, securityLevel:'loose' }});
(async () => {{
  const results = [];
  for (let i=0;i<BLOCKS.length;i++) {{
    try {{ await mermaid.render('g'+i, BLOCKS[i].code, document.getElementById('sandbox'));
          results.push({{src:BLOCKS[i].src, ok:true}}); }}
    catch (e) {{ results.push({{src:BLOCKS[i].src, ok:false, err:String((e&&e.message)||e)}}); }}
  }}
  document.getElementById('out').textContent = JSON.stringify(results);
}})();
</script></body></html>"""


def main():
    paths = sys.argv[1:] or ["docs"]
    blocks = extract_blocks(paths)
    if not blocks:
        print("没有发现 mermaid 图，跳过。")
        return 0
    chrome = find_chrome()
    if not chrome:
        print("⚠ 未找到 Chrome / Chromium，跳过渲染检查（静态检查请用 lint_mermaid.py）。")
        return 0

    tmp = Path(tempfile.mkdtemp()) / "diag.html"
    tmp.write_text(build_diag_html(blocks), encoding="utf-8")
    try:
        proc = subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--dump-dom",
             "--virtual-time-budget=20000", f"file://{tmp}"],
            capture_output=True, text=True, timeout=90)
    except Exception as e:                            # noqa: BLE001
        print(f"⚠ 调用 Chrome 失败，跳过：{e}")
        return 0

    m = re.search(r'<pre id="out">(.*?)</pre>', proc.stdout, re.S)
    if not m or m.group(1).strip() in ("", "PENDING"):
        print("⚠ 未取到渲染结果（可能渲染超时或离线无法加载 mermaid CDN），跳过。")
        return 0
    try:
        results = json.loads(htmllib.unescape(m.group(1)))
    except Exception:
        print("⚠ 渲染结果解析失败，跳过。")
        return 0

    failed = [r for r in results if not r.get("ok")]
    for r in failed:
        print(f"✗ 渲染失败  {r['src']}\n    {r.get('err','')}")
    print(f"\n渲染 {len(results)} 张图：{len(failed)} 失败"
          + ("，全部通过 ✓" if not failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
