from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import plotly.io as pio
from jinja2 import Template
from plotly.offline import get_plotlyjs

from emlab.modules import (
    ac_motor,
    crt_scope,
    cyclotron,
    electron_microscope,
    hall_effect,
    induction_heating,
    linac,
    mass_spec,
    rail_launcher,
    rlc_oscillation,
    speaker_microphone,
    transformer,
    wireless_power,
    xct_ct,
)


def _json_default(obj: Any) -> Any:
    try:
        import numpy as np

        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
    except Exception:
        pass
    raise TypeError(f"Not JSON serializable: {type(obj)}")


def _dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"), default=_json_default)


def _split_md_sections(md: str) -> dict[str, str]:
    """
    Split a markdown document into sections keyed by `## <key>` headings.
    The text before the first `##` is ignored.
    """
    sections: dict[str, str] = {}
    cur: str | None = None
    buf: list[str] = []
    for raw in md.splitlines():
        line = raw.rstrip("\n")
        m = re.match(r"^##\s+(\S+)\s*$", line)
        if m:
            if cur is not None:
                sections[cur] = "\n".join(buf).strip("\n")
            cur = m.group(1).strip()
            buf = []
            continue
        if cur is None:
            continue
        buf.append(line)
    if cur is not None:
        sections[cur] = "\n".join(buf).strip("\n")
    return sections


def _md_inline(text: str) -> str:
    """
    Minimal inline markdown:
    - `code`
    - **bold**
    Everything else is HTML-escaped.
    """
    parts = text.split("`")
    out: list[str] = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(f"<code>{html.escape(part)}</code>")
            continue
        s = html.escape(part)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        out.append(s)
    return "".join(out)


def _md_to_html(md: str) -> str:
    """
    Minimal markdown renderer for offline packaging (no extra deps).

    Supported:
    - ### headings (rendered as <h4>) and deeper
    - unordered / ordered lists
    - paragraphs
    - fenced code blocks
    - horizontal rule: ---
    - blockquote lines starting with >
    """
    out: list[str] = []
    para: list[str] = []
    in_code = False
    code_lines: list[str] = []
    list_root: dict[str, Any] | None = None
    list_stack: list[tuple[int, dict[str, Any]]] = []  # (indent_level, node)

    def flush_para() -> None:
        nonlocal para
        if not para:
            return
        text = " ".join(s.strip() for s in para).strip()
        if text:
            out.append(f"<p>{_md_inline(text)}</p>")
        para = []

    def flush_list() -> None:
        nonlocal list_root, list_stack
        if not list_root:
            return

        def render_list(node: dict[str, Any]) -> str:
            tag = node["kind"]
            items = node.get("items", [])
            inner = "".join(render_item(it) for it in items)
            return f"<{tag}>{inner}</{tag}>"

        def render_item(it: dict[str, Any]) -> str:
            s = f"<li>{it['html']}"
            child = it.get("child")
            if child:
                s += render_list(child)
            s += "</li>"
            return s

        out.append(render_list(list_root))
        list_root = None
        list_stack = []

    def list_add(kind: str, indent_level: int, content: str) -> None:
        nonlocal list_root, list_stack

        def new_list(k: str) -> dict[str, Any]:
            return {"kind": k, "items": []}

        if list_root is None:
            list_root = new_list(kind)
            list_stack = [(0, list_root)]
            indent_level = 0

        # climb up if needed
        while list_stack and indent_level < list_stack[-1][0]:
            list_stack.pop()
        if not list_stack:
            list_root = new_list(kind)
            list_stack = [(0, list_root)]
            indent_level = 0

        # descend if needed: attach nested list to last item of current list
        while indent_level > list_stack[-1][0]:
            parent = list_stack[-1][1]
            if not parent["items"]:
                # malformed indentation; treat as same level
                indent_level = list_stack[-1][0]
                break
            last_item = parent["items"][-1]
            child = last_item.get("child")
            if not child or child.get("kind") != kind:
                child = new_list(kind)
                last_item["child"] = child
            list_stack.append((list_stack[-1][0] + 1, child))

        node = list_stack[-1][1]
        if node.get("kind") != kind:
            # if list kind changes at same indent, start a new list block
            flush_list()
            list_root = new_list(kind)
            list_stack = [(0, list_root)]
            node = list_root
        node["items"].append({"html": _md_inline(content.strip()), "child": None})

    for raw in md.splitlines():
        line = raw.rstrip("\n")
        stripped = line.strip()

        if in_code:
            if stripped.startswith("```"):
                out.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                in_code = False
                code_lines = []
            else:
                code_lines.append(line)
            continue

        if stripped.startswith("```"):
            flush_para()
            flush_list()
            in_code = True
            code_lines = []
            continue

        if re.match(r"^---\s*$", stripped):
            flush_para()
            flush_list()
            out.append("<hr/>")
            continue

        m = re.match(r"^(#{3,6})\s+(.*)$", stripped)
        if m:
            flush_para()
            flush_list()
            lvl = len(m.group(1))
            # map ### -> h4, #### -> h5, #####/###### -> h6
            html_lvl = {3: 4, 4: 5, 5: 6, 6: 6}.get(lvl, 4)
            out.append(f"<h{html_lvl}>{_md_inline(m.group(2).strip())}</h{html_lvl}>")
            continue

        m = re.match(r"^>\s?(.*)$", stripped)
        if m:
            flush_para()
            flush_list()
            out.append(f'<p class="quote">{_md_inline(m.group(1).strip())}</p>')
            continue

        m = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        if m:
            flush_para()
            list_add("ul", len(m.group(1)) // 2, m.group(2))
            continue

        m = re.match(r"^(\s*)(\d+)\.\s+(.*)$", line)
        if m:
            flush_para()
            list_add("ol", len(m.group(1)) // 2, m.group(3))
            continue

        # continuation line within a list item (simple, indentation-based)
        if list_root is not None and stripped != "":
            lead = len(line) - len(line.lstrip(" "))
            if lead >= 2:
                cont_level = lead // 2
                target_level = max(0, cont_level - 1)
                target_node: dict[str, Any] | None = None
                for lvl, node in reversed(list_stack):
                    if lvl == target_level:
                        target_node = node
                        break
                if target_node is None:
                    target_node = list_stack[0][1] if list_stack else list_root
                if target_node.get("items"):
                    target_node["items"][-1]["html"] += "<br/>" + _md_inline(stripped)
                    continue

        if stripped == "":
            flush_para()
            flush_list()
            continue

        para.append(line)

    flush_para()
    flush_list()
    if in_code:
        out.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")

    return "\n".join(out)


def _load_formulas_html() -> dict[str, str]:
    repo_root = Path(__file__).resolve().parents[3]
    path = repo_root / "formulas.md"
    if not path.exists():
        return {}
    sections = _split_md_sections(path.read_text(encoding="utf-8"))
    return {k: _md_to_html(v) for k, v in sections.items()}


@dataclass(frozen=True)
class ModuleBundle:
    id: str
    title: str
    intro_html: str
    controls_html: str
    figures_html: list[str]
    data_json: str
    js: str
    pitfalls_html: str
    questions_html: str


def _render_figures(module_id: str, figures: list[Any], *, config: dict[str, Any]) -> list[str]:
    html_parts: list[str] = []
    for i, fig in enumerate(figures):
        div_id = f"fig-{module_id}-{i}"
        html_parts.append(
            pio.to_html(
                fig,
                full_html=False,
                include_plotlyjs=False,
                config=config,
                div_id=div_id,
                default_width="100%",
                default_height="100%",
                auto_play=False,
            )
        )
    return html_parts


def _bundle(module_dict: dict[str, Any], *, config: dict[str, Any]) -> ModuleBundle:
    figures = module_dict["figures"]
    module_id = module_dict["id"]
    return ModuleBundle(
        id=module_id,
        title=module_dict["title"],
        intro_html=module_dict["intro_html"],
        controls_html=module_dict["controls_html"],
        figures_html=_render_figures(module_id, figures, config=config),
        data_json=_dumps(module_dict.get("data_payload", {})),
        js=module_dict.get("js", ""),
        pitfalls_html=module_dict.get("pitfalls_html", ""),
        questions_html=module_dict.get("questions_html", ""),
    )


TEMPLATE = Template(
    r"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>EMLab｜电磁场与电路 交互可视化实验室</title>
    <style>
      :root{
        --bg: #0b1020;
        --panel: rgba(255,255,255,0.06);
        --panel2: rgba(255,255,255,0.09);
        --text: rgba(255,255,255,0.92);
        --muted: rgba(255,255,255,0.72);
        --accent: #66d9ef;
        --accent2: #a6e22e;
        --danger: #ff6b6b;
        --border: rgba(255,255,255,0.14);
        --shadow: rgba(0,0,0,0.35);
        --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        --sans: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
      }
      *{ box-sizing:border-box; }
      body{
        margin:0;
        font-family: var(--sans);
        background: radial-gradient(1200px 800px at 20% 0%, rgba(102,217,239,0.12), transparent 55%),
                    radial-gradient(900px 700px at 80% 20%, rgba(166,226,46,0.10), transparent 55%),
                    var(--bg);
        color: var(--text);
      }
      a{ color: var(--accent); text-decoration: none; }
      a:hover{ text-decoration: underline; }
      .app{
        display:flex;
        min-height:100vh;
      }
      nav{
        width: 260px;
        padding: 14px 12px;
        border-right: 1px solid var(--border);
        background: rgba(0,0,0,0.20);
        backdrop-filter: blur(6px);
        position: sticky;
        top:0;
        align-self: flex-start;
        height: 100vh;
        overflow:auto;
      }
      .brand{
        padding: 10px 10px 12px;
        border: 1px solid var(--border);
        border-radius: 12px;
        background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.05));
        box-shadow: 0 10px 30px var(--shadow);
        margin-bottom: 12px;
      }
      .brand h1{ font-size: 16px; margin: 0 0 6px; letter-spacing: 0.3px; }
      .brand .sub{ font-size: 12px; color: var(--muted); line-height: 1.35; }
      .navbtn{
        width:100%;
        display:block;
        text-align:left;
        padding: 10px 10px;
        margin: 6px 0;
        border-radius: 10px;
        border: 1px solid var(--border);
        background: rgba(255,255,255,0.05);
        color: var(--text);
        cursor: pointer;
        transition: transform 0.05s ease, background 0.15s ease, border-color 0.15s ease;
      }
      .navbtn:hover{ background: rgba(255,255,255,0.08); }
      .navbtn:active{ transform: translateY(1px); }
      .navbtn.active{
        background: rgba(102,217,239,0.12);
        border-color: rgba(102,217,239,0.35);
      }
      main{
        flex:1;
        padding: 18px 18px 28px;
      }
      .module{
        display:none;
        max-width: 1200px;
        margin: 0 auto;
      }
      .module.active{ display:block; }
      .module h2{
        margin: 4px 0 10px;
        font-size: 22px;
        letter-spacing: 0.2px;
      }
      .intro{
        border: 1px solid var(--border);
        background: rgba(255,255,255,0.05);
        border-radius: 14px;
        padding: 12px 14px;
        box-shadow: 0 10px 30px var(--shadow);
        line-height: 1.55;
        color: var(--muted);
      }
      .intro details.formula{ margin-top: 10px; }
      .intro details.formula > summary{
        font-size: 13px;
        color: rgba(255,255,255,0.86);
      }
      .intro .formula-global, .intro .formula-body{
        margin-top: 8px;
        color: rgba(255,255,255,0.78);
      }
      .intro .formula-global h4, .intro .formula-body h4,
      .intro .formula-global h5, .intro .formula-body h5,
      .intro .formula-global h6, .intro .formula-body h6{
        margin: 12px 0 6px;
        font-size: 13px;
        color: rgba(255,255,255,0.88);
      }
      .intro .formula-global p, .intro .formula-body p{ margin: 8px 0; }
      .intro .formula-global ul, .intro .formula-body ul,
      .intro .formula-global ol, .intro .formula-body ol{
        margin: 6px 0 10px 18px;
        padding-left: 16px;
      }
      .intro .formula-global li, .intro .formula-body li{ margin: 4px 0; }
      .intro .formula-global code, .intro .formula-body code{
        font-family: var(--mono);
        font-size: 12px;
        padding: 0.15em 0.35em;
        border-radius: 6px;
        border: 1px solid rgba(255,255,255,0.14);
        background: rgba(0,0,0,0.25);
      }
      .intro .formula-global pre, .intro .formula-body pre{
        margin: 10px 0;
        padding: 10px 12px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.14);
        background: rgba(0,0,0,0.22);
        overflow:auto;
      }
      .intro .formula-global pre code, .intro .formula-body pre code{
        display:block;
        padding: 0;
        border: none;
        background: transparent;
        white-space: pre-wrap;
      }
      .intro .quote{
        margin: 8px 0;
        padding-left: 10px;
        border-left: 3px solid rgba(255,255,255,0.18);
        color: rgba(255,255,255,0.72);
      }
      .grid{
        display:grid;
        grid-template-columns: 340px 1fr;
        gap: 14px;
        margin-top: 14px;
      }
      .card{
        border: 1px solid var(--border);
        background: rgba(255,255,255,0.05);
        border-radius: 14px;
        padding: 12px;
        box-shadow: 0 10px 30px var(--shadow);
      }
      .card h3{
        font-size: 13px;
        color: rgba(255,255,255,0.84);
        margin: 0 0 10px;
        letter-spacing: 0.25px;
      }
      .controls .control{
        margin: 10px 0 12px;
        padding-bottom: 10px;
        border-bottom: 1px dashed rgba(255,255,255,0.14);
      }
      .controls .control:last-child{ border-bottom: none; padding-bottom: 0; }
      label{
        display:block;
        font-size: 12px;
        color: rgba(255,255,255,0.85);
        margin-bottom: 8px;
      }
      .control-row{
        display:flex;
        align-items:center;
        gap: 10px;
      }
      input[type="range"]{ width: 100%; }
      input[type="number"], select{
        width: 100%;
        padding: 8px 10px;
        border-radius: 10px;
        border: 1px solid var(--border);
        background: rgba(0,0,0,0.25);
        color: var(--text);
      }
      .value{
        font-family: var(--mono);
        font-size: 12px;
        color: rgba(255,255,255,0.86);
        min-width: 80px;
        text-align: right;
      }
      .help{
        margin-top: 6px;
        font-size: 11px;
        color: rgba(255,255,255,0.65);
        line-height: 1.35;
      }
      .btnrow{
        display:flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 10px;
      }
      button.btn{
        border-radius: 12px;
        border: 1px solid var(--border);
        background: rgba(255,255,255,0.06);
        color: var(--text);
        padding: 9px 10px;
        cursor:pointer;
      }
      button.btn.primary{ border-color: rgba(102,217,239,0.35); background: rgba(102,217,239,0.10); }
      button.btn.danger{ border-color: rgba(255,107,107,0.35); background: rgba(255,107,107,0.10); }
      button.btn:active{ transform: translateY(1px); }
      .figgrid{
        display:grid;
        grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
        gap: 12px;
      }
      .figcard{
        border: 1px solid var(--border);
        background: rgba(255,255,255,0.05);
        border-radius: 14px;
        overflow:hidden;
      }
      .fighead{
        padding: 10px 12px;
        border-bottom: 1px solid rgba(255,255,255,0.10);
        font-size: 12px;
        color: rgba(255,255,255,0.80);
      }
      .figbody{
        height: 380px;
      }
      .readouts{
        margin-top: 12px;
        display:grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
      }
      .readout{
        border: 1px solid rgba(255,255,255,0.10);
        background: rgba(0,0,0,0.18);
        border-radius: 12px;
        padding: 10px 10px;
      }
      .readout .k{ font-size: 11px; color: rgba(255,255,255,0.70); margin-bottom: 6px; }
      .readout .v{ font-family: var(--mono); font-size: 13px; color: rgba(255,255,255,0.90); }
      .below{
        margin-top: 14px;
        display:grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
      }
      details{
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 10px 12px;
      }
      details summary{
        cursor:pointer;
        color: rgba(255,255,255,0.86);
        font-size: 13px;
      }
      @media (max-width: 980px){
        nav{ position: static; height: auto; width: 100%; }
        .app{ flex-direction: column; }
        main{ padding: 14px; }
        .grid{ grid-template-columns: 1fr; }
        .below{ grid-template-columns: 1fr; }
        .readouts{ grid-template-columns: 1fr; }
      }
    </style>
    {% if plotly_inline %}
    <script>{{ plotly_inline|safe }}</script>
    {% else %}
    <script src="{{ plotly_cdn_src }}"></script>
    {% endif %}
  </head>
  <body>
    <div class="app">
      <nav>
        <div class="brand">
          <h1>EMLab｜电磁场与电路</h1>
          <div class="sub">
            单文件离线交互实验室（Plotly + 原生 JS）<br/>
            生成时间：{{ build_time }}
          </div>
        </div>
        {% for m in modules %}
          <button class="navbtn" id="nav-{{m.id}}" data-module="{{m.id}}">{{ m.title }}</button>
        {% endfor %}
      </nav>
      <main>
        {% for m in modules %}
        <section class="module" id="section-{{m.id}}">
          <h2>{{ m.title }}</h2>
          <div class="intro">{{ m.intro_html|safe }}</div>
          <div class="grid">
            <div class="card controls">
              <h3>参数</h3>
              {{ m.controls_html|safe }}
              <div class="btnrow">
                <button class="btn" id="snap-{{m.id}}" type="button">导出主图 PNG</button>
              </div>
            </div>
            <div class="card">
              <h3>图表</h3>
              <div class="figgrid">
                {% for fig_html in m.figures_html %}
                <div class="figcard">
                  <div class="figbody">{{ fig_html|safe }}</div>
                </div>
                {% endfor %}
              </div>
              <div class="readouts" id="readouts-{{m.id}}"></div>
            </div>
          </div>
          <div class="below">
            <div class="card">
              <h3>常见误区</h3>
              {{ m.pitfalls_html|safe }}
            </div>
            <div class="card">
              <h3>引导问题</h3>
              {{ m.questions_html|safe }}
            </div>
          </div>

          <script type="application/json" id="data-{{m.id}}">{{ m.data_json }}</script>
        </section>
        {% endfor %}
      </main>
    </div>

    <script>
      // ------- Common helpers -------
      function emlabGetJSON(id){
        const el = document.getElementById(id);
        if(!el) return {};
        return JSON.parse(el.textContent);
      }
      function emlabNum(x){ return (typeof x === "number") ? x : parseFloat(x); }
      function emlabFmt(x, digits){
        const d = (digits === undefined) ? 3 : digits;
        if(!isFinite(x)) return "—";
        const ax = Math.abs(x);
        if(ax >= 1000 || (ax > 0 && ax < 1e-3)) return x.toExponential(2);
        return x.toFixed(d);
      }
      function emlabBindValue(root, inputId, unit, digits){
        const input = root.querySelector("#"+inputId);
        const span = root.querySelector("#"+inputId+"-val");
        if(!input || !span) return;
        input.dataset.emlabBound = "1";
        input.dataset.emlabUnit = unit || "";
        input.dataset.emlabDigits = (digits === undefined) ? "" : String(digits);
        const update = () => { span.textContent = emlabFmt(emlabNum(input.value), digits) + (unit || ""); };
        input.addEventListener("input", update);
        update();
      }
      function emlabRefreshBoundValues(root){
        if(!root) return;
        const inputs = root.querySelectorAll('input[data-emlab-bound="1"]');
        inputs.forEach(input => {
          if(!input.id) return;
          const span = root.querySelector("#"+input.id+"-val");
          if(!span) return;
          const unit = input.dataset.emlabUnit || "";
          const dr = input.dataset.emlabDigits;
          const digits = (dr === undefined || dr === "") ? undefined : parseFloat(dr);
          span.textContent = emlabFmt(emlabNum(input.value), digits) + unit;
        });
      }
      function emlabFindBracket(arr, x){
        // arr: increasing numeric list
        const n = arr.length;
        if(n < 2) return {i0:0, i1:0, t:0};
        if(x <= arr[0]) return {i0:0, i1:0, t:0};
        if(x >= arr[n-1]) return {i0:n-2, i1:n-1, t:1};
        let lo = 0, hi = n-1;
        while(hi - lo > 1){
          const mid = (lo + hi) >> 1;
          if(arr[mid] <= x) lo = mid; else hi = mid;
        }
        const a = arr[lo], b = arr[hi];
        const t = (x - a) / (b - a);
        return {i0: lo, i1: hi, t: t};
      }
      function emlabBilinearInterp4(a00, a01, a10, a11, tx, ty){
        const a0 = a00*(1-ty) + a01*ty;
        const a1 = a10*(1-ty) + a11*ty;
        return a0*(1-tx) + a1*tx;
      }
      function emlabBilinearSeries(grid, xs, ys, x, y){
        // grid: [nx][ny][n] numeric arrays
        const bx = emlabFindBracket(xs, x);
        const by = emlabFindBracket(ys, y);
        const g00 = grid[bx.i0][by.i0];
        const g01 = grid[bx.i0][by.i1];
        const g10 = grid[bx.i1][by.i0];
        const g11 = grid[bx.i1][by.i1];
        const n = g00.length;
        const out = new Array(n);
        for(let k=0;k<n;k++){
          out[k] = emlabBilinearInterp4(g00[k], g01[k], g10[k], g11[k], bx.t, by.t);
        }
        return out;
      }
      function emlabMakeReadouts(rootEl, items){
        // items: [{key, id, value}]
        rootEl.innerHTML = items.map(it => (
          '<div class="readout"><div class="k">'+it.key+'</div><div class="v" id="'+it.id+'">'+it.value+'</div></div>'
        )).join('');
      }
      function emlabResizeActive(){
        const active = document.querySelector("section.module.active");
        if(!active) return;
        const divs = active.querySelectorAll(".js-plotly-plot");
        divs.forEach(d => { try{ Plotly.Plots.resize(d); }catch(e){} });
      }

      // ------- Module JS -------
      {{ modules_js|safe }}

      // ------- Navigation + init -------
      const emlabModules = {{ module_ids|safe }};
      function emlabShow(moduleId){
        emlabModules.forEach(id => {
          const sec = document.getElementById("section-"+id);
          const btn = document.getElementById("nav-"+id);
          if(sec) sec.classList.toggle("active", id === moduleId);
          if(btn) btn.classList.toggle("active", id === moduleId);
        });
        setTimeout(emlabResizeActive, 80);
      }
      document.addEventListener("DOMContentLoaded", () => {
        // attach nav
        emlabModules.forEach(id => {
          const btn = document.getElementById("nav-"+id);
          if(btn){
            btn.addEventListener("click", () => emlabShow(id));
          }
        });
        // snapshot buttons (export first figure)
        emlabModules.forEach(id => {
          const btn = document.getElementById("snap-"+id);
          if(!btn) return;
          btn.addEventListener("click", () => {
            const fig = document.getElementById("fig-"+id+"-0");
            if(!fig || typeof Plotly === "undefined") return;
            const ts = new Date().toISOString().slice(0,19).replace(/[:T]/g,"-");
            Plotly.downloadImage(fig, {format:"png", filename:"emlab_"+id+"_"+ts, width: 1100, height: 700});
          });
        });
        // init modules
        emlabModules.forEach(id => {
          const fn = window["init_"+id];
          if(typeof fn === "function") fn();
        });
        // show first
        if(emlabModules.length) emlabShow(emlabModules[0]);
        window.addEventListener("resize", () => setTimeout(emlabResizeActive, 100));
      });
    </script>
  </body>
</html>"""
)


def build_site(*, mode: str = "release", no_ct: bool = False) -> str:
    config = {
        "responsive": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    }

    module_builders: list[Callable[[], dict[str, Any]]] = [
        crt_scope.build,
        xct_ct.build,
        ac_motor.build,
        rail_launcher.build,
        mass_spec.build,
        electron_microscope.build,
        cyclotron.build,
        linac.build,
        transformer.build,
        rlc_oscillation.build,
        wireless_power.build,
        hall_effect.build,
        speaker_microphone.build,
        induction_heating.build,
    ]
    if no_ct:
        module_builders = [b for b in module_builders if getattr(b, "__module__", "") != xct_ct.__name__]

    module_dicts = [b() for b in module_builders if b is not None]
    formulas_html = _load_formulas_html()
    global_html = (formulas_html.get("_global") or "").strip()
    if formulas_html:
        for md in module_dicts:
            mid = md.get("id", "")
            body_html = (formulas_html.get(mid) or "").strip()
            if not (global_html or body_html):
                continue
            parts: list[str] = ['<details class="formula">', "<summary>公式推演（展开）</summary>"]
            if global_html:
                parts.append(f'<div class="formula-global">{global_html}</div>')
            if body_html:
                parts.append(f'<div class="formula-body">{body_html}</div>')
            parts.append("</details>")
            md["intro_html"] = (md.get("intro_html", "") or "") + "\n" + "\n".join(parts)
    modules = [_bundle(md, config=config) for md in module_dicts]

    modules_js = "\n\n".join(m.js for m in modules if m.js)
    module_ids = [m.id for m in modules]

    plotly_inline = get_plotlyjs() if mode == "release" else None
    plotly_cdn_src = None
    if mode != "release":
        # Keep debug small by using CDN, but match the bundled plotly.js version.
        js_head = get_plotlyjs()[:120]
        m = re.search(r"plotly\.js v(\d+\.\d+\.\d+)", js_head)
        ver = m.group(1) if m else "latest"
        plotly_cdn_src = f"https://cdn.plot.ly/plotly-{ver}.min.js"
    return TEMPLATE.render(
        modules=modules,
        module_ids=_dumps(module_ids),
        modules_js=modules_js,
        plotly_inline=plotly_inline,
        plotly_cdn_src=plotly_cdn_src,
        build_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
