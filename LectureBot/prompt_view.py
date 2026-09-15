"""Animated replay of what one ollama.chat() call sent to the model."""

from html import escape

import ollama
from IPython.display import HTML, display

CSS = """
<style>
.pv { font-size: 13px; line-height: 1.45; max-width: 46rem; }
.pv-block, .pv-model, .pv-bar {
  opacity: 0; animation: pv-in .5s ease forwards;
}
@keyframes pv-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
.pv-block {
  margin: 0 0 6px; padding: 6px 10px; border-left: 4px solid; border-radius: 4px;
}
.pv-block summary { cursor: pointer; }
.pv-block pre {
  white-space: pre-wrap; word-break: break-word; max-height: 16em; overflow: auto;
  margin: 6px 0 2px; font-size: 12px;
}
.pv-meta { opacity: .65; font-size: 12px; }
.pv-instructions { border-color: #8e6bd8; background: rgba(142, 107, 216, .10); }
.pv-context      { border-color: #3b82c4; background: rgba(59, 130, 196, .10); }
.pv-history      { border-color: #9a9a9a; background: rgba(154, 154, 154, .10); }
.pv-question     { border-color: #3a9a5b; background: rgba(58, 154, 91, .12); }
.pv-answer       { border-color: #e07b2a; background: rgba(224, 123, 42, .12); }
.pv-model { margin: 12px 0 4px; font-weight: 600; }
.pv-bar { height: 10px; border-radius: 5px; background: rgba(154, 154, 154, .25); margin: 0 0 12px; overflow: hidden; }
.pv-fill { height: 100%; width: 0; background: #3b82c4; animation: pv-fill 1.2s ease forwards; }
@keyframes pv-fill { to { width: var(--pv-width); } }
@media (prefers-reduced-motion: reduce) {
  .pv-block, .pv-model, .pv-bar, .pv-fill { animation-duration: 1ms; animation-delay: 0s !important; }
}
</style>
"""


def _block(kind, title, meta, text, delay):
    return (
        f'<details class="pv-block pv-{kind}" style="animation-delay:{delay:.2f}s">'
        f"<summary><b>{escape(title)}</b> <span class=\"pv-meta\">{escape(meta)}</span></summary>"
        f"<pre>{escape(text)}</pre></details>"
    )


def show_prompt(last):
    """Replay the call stored in `last`, block by block, in the order the model read it."""
    info = ollama.show(last["model"]).modelinfo
    num_ctx = next(v for k, v in info.items() if k.endswith("context_length"))
    system, *turns = last["messages"]
    instructions = system["content"].split("\n\n=== ", 1)[0]
    rag = last["mode"] == "rag"

    parts, step = [], 0.35
    parts.append(("instructions", "System: instructions", f"~{len(instructions) // 4} tokens", instructions))
    for name, text, score in last["sources"]:
        meta = f"similarity {score:.2f}" if rag else "whole document"
        parts.append(("context", f"System: {name}", f"{meta}, ~{len(text) // 4} tokens", text))
    for msg in turns[:-1]:
        preview = msg["content"][:50] + ("..." if len(msg["content"]) > 50 else "")
        parts.append(("history", f"Earlier {msg['role']}", preview, msg["content"]))
    parts.append(("question", "User: your question", "", turns[-1]["content"]))

    html = [CSS, '<div class="pv">']
    for i, (kind, title, meta, text) in enumerate(parts):
        html.append(_block(kind, title, meta, text, i * step))

    t = len(parts) * step
    used = last["tokens"]
    html.append(
        f'<div class="pv-model" style="animation-delay:{t:.2f}s">'
        f"&darr; {escape(last['model'])} reads {used} tokens "
        f"({len(last['sources'])} {'retrieved chunks' if rag else 'whole documents'}), "
        f"its maximum is {num_ctx}</div>"
    )
    html.append(
        f'<div class="pv-bar" style="animation-delay:{t:.2f}s">'
        f'<div class="pv-fill" style="--pv-width:{min(100, 100 * used / num_ctx):.1f}%;'
        f'animation-delay:{t + .3:.2f}s"></div></div>'
    )
    html.append(_block("answer", "Assistant: answer", "", last["answer"], t + 1.5))
    html.append("</div>")
    display(HTML("".join(html)))
