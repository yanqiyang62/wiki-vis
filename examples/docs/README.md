# 示例 Wiki

> **wiki-vis 演示**：这一份 `examples/docs/` 用来展示生成效果。运行
> `python3 build_wiki.py --docs examples/docs --out examples/wiki.html` 即可重建本页。

本示例覆盖了常见元素：多级标题折叠框体、Mermaid 流程图、表格、代码块、内部链接。

---

## 1 它能做什么

把若干 `.md` 文件变成**一个**好看的 `wiki.html`：左侧导航、章节可折叠、图可放大。

```mermaid
flowchart LR
    A[Markdown 目录] --> B[build_wiki.py]
    B --> C[单文件 wiki.html]
    C --> D[浏览器查看 / 分发]
    style B fill:#dbeafe
    style C fill:#dcfce7
```

### 1.1 一句话

> 写文档只管写 Markdown，样式与交互交给模板。

---

## 2 元素速览

| 元素 | 支持 | 说明 |
|---|---|---|
| 标题层级框体 | ✅ | H2/H3/H4… 按层级上色、点击折叠 |
| Mermaid 图 | ✅ | 同色系主题 + 🔍 放大 |
| 代码高亮 | ✅ | highlight.js |
| 内部链接 | ✅ | 见 [架构示例](01-架构示例.md) |

```python
# 代码块会被高亮
def hello(name: str) -> str:
    return f"hi, {name}"
```
