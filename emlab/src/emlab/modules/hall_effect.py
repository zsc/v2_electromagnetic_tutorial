from __future__ import annotations

import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, select, slider


def build() -> dict:
    module_id = "hall_effect"

    intro_html = """
    <p>
      霍尔效应把“看不见的载流子受力”变成可测电压：
      载流子在磁场中受洛伦兹力 <code>F = q v × B</code> 向一侧偏转，形成横向电场 E_H，
      直到电场力与磁力平衡。理想单载流子模型给出
      <code>V_H = I B /(n q t)</code>（t 为样品厚度）。
    </p>
    <p>
      本页展示 V_H 随 I、B、n、t 的变化，并用方向图帮助判断载流子类型（电子/空穴）。
    </p>
    """

    controls_html = "\n".join(
        [
            slider(cid=f"{module_id}-I", label="电流 I (A)", vmin=0.0, vmax=5.0, step=0.05, value=1.0, unit=" A"),
            slider(cid=f"{module_id}-B", label="磁感应强度 B (T)", vmin=0.0, vmax=0.2, step=0.002, value=0.08, unit=" T"),
            slider(
                cid=f"{module_id}-n",
                label="载流子浓度 n (×10²² m⁻³)",
                vmin=0.2,
                vmax=20.0,
                step=0.2,
                value=4.0,
                unit="",
                help_text="n 越大，单位体积载流子越多，霍尔电压越小（定性）。",
            ),
            slider(cid=f"{module_id}-t", label="厚度 t (mm)", vmin=0.1, vmax=5.0, step=0.05, value=1.0, unit=" mm"),
            select(
                cid=f"{module_id}-type",
                label="载流子类型",
                value="electron",
                options=[("electron", "电子（q<0）"), ("hole", "空穴（q>0）")],
                help_text="类型会改变霍尔电压的符号与方向图中的受力方向。",
            ),
            buttons(
                [
                    (f"{module_id}-play", "播放/暂停", "primary"),
                    (f"{module_id}-reset", "重置参数", ""),
                ]
            ),
        ]
    )

    fig0 = go.Figure(
        data=[go.Scatter(x=[0, 0.2], y=[0, 1], mode="lines", line=dict(color="#66d9ef", width=2), name="V_H(B)")],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="霍尔电压 V_H 随磁场 B 变化（其余参数固定）",
            xaxis_title="B (T)",
            yaxis_title="V_H (mV)",
            showlegend=False,
        ),
    )

    fig1 = go.Figure(
        data=[
            go.Scatter(x=[0.0, 1.0], y=[0.0, 0.0], mode="lines+markers", name="I", line=dict(color="#66d9ef", width=4), marker=dict(size=6)),
            go.Scatter(x=[0.5, 0.5], y=[-0.6, 0.6], mode="lines+markers", name="F_L", line=dict(color="#ff6b6b", width=4), marker=dict(size=6)),
            go.Scatter(x=[0.5], y=[0.8], mode="text", text=["B ⊙"], textfont=dict(size=18, color="rgba(255,255,255,0.85)"), name="B"),
            go.Scatter(x=[0.5, 0.5], y=[0.0, 0.55], mode="lines+markers", name="E_H", line=dict(color="#a6e22e", width=4), marker=dict(size=6)),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=40, r=20, t=40, b=40),
            title="方向图：I、B、洛伦兹力与霍尔电场（示意）",
            xaxis=dict(range=[-0.2, 1.2], showgrid=False, zeroline=False, visible=False),
            yaxis=dict(range=[-1.0, 1.0], showgrid=False, zeroline=False, visible=False, scaleanchor="x"),
            showlegend=False,
            shapes=[
                dict(type="rect", x0=0.15, x1=0.85, y0=-0.35, y1=0.35, line=dict(color="rgba(255,255,255,0.18)"), fillcolor="rgba(255,255,255,0.04)"),
            ],
            annotations=[
                dict(x=0.9, y=0.0, text="I →", showarrow=False, font=dict(size=12, color="rgba(255,255,255,0.75)")),
                dict(x=0.55, y=0.95, text="B 出屏幕(⊙)", showarrow=False, font=dict(size=12, color="rgba(255,255,255,0.75)")),
            ],
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“霍尔电压与 B 无关”：不对，理想模型中 <code>V_H ∝ B</code>。</li>
      <li>“n 越大霍尔电压越大”：相反，<code>V_H ∝ 1/n</code>。</li>
      <li>“符号不重要”：霍尔电压的符号可用于判断主要载流子类型（电子/空穴）。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>引导问题</summary>
      <ol>
        <li><b>预测</b>：把 I 加倍，V_H 会如何变化？把 t 加倍呢？</li>
        <li><b>验证</b>：切换载流子类型，方向图中 F_L 与 E_H 的方向发生了什么变化？</li>
        <li><b>解释</b>：用“平衡：qE_H = q vB”推导出 V_H 与 I、B、n、t 的关系。</li>
      </ol>
    </details>
    """

    data_payload = {"defaults": {"I": 1.0, "B": 0.08, "n": 4.0, "t": 1.0, "type": "electron"}}

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);

      const els = {{
        I: root.querySelector("#{module_id}-I"),
        B: root.querySelector("#{module_id}-B"),
        n: root.querySelector("#{module_id}-n"),
        t: root.querySelector("#{module_id}-t"),
        type: root.querySelector("#{module_id}-type"),
        play: root.querySelector("#{module_id}-play"),
        reset: root.querySelector("#{module_id}-reset"),
      }};

      emlabBindValue(root, "{module_id}-I", " A", 2);
      emlabBindValue(root, "{module_id}-B", " T", 3);
      emlabBindValue(root, "{module_id}-n", "", 1);
      emlabBindValue(root, "{module_id}-t", " mm", 2);

      const figVB = document.getElementById("fig-{module_id}-0");
      const figDir = document.getElementById("fig-{module_id}-1");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"当前 V_H", id:"{module_id}-ro-VH", value:"—"}},
        {{key:"霍尔系数 R_H", id:"{module_id}-ro-RH", value:"—"}},
        {{key:"符号/方向", id:"{module_id}-ro-sgn", value:"—"}},
      ]);

      const q = 1.602176634e-19;

      let timer = null;
      let dir = 1;
      function stopPlay(){{ if(timer){{ clearInterval(timer); timer=null; }} }}
      function tick(){{
        const el = els.B;
        if(!el) return;
        const vmin = emlabNum(el.min);
        const vmax = emlabNum(el.max);
        const step = Math.max(1e-12, emlabNum(el.step || 1));
        let v = emlabNum(el.value);
        v += dir*step*5;
        if(v >= vmax){{ v=vmax; dir=-1; }}
        if(v <= vmin){{ v=vmin; dir=1; }}
        const n = Math.round((v-vmin)/step);
        v = vmin + n*step;
        v = Math.max(vmin, Math.min(vmax, v));
        el.value = v.toString();
      }}
      function togglePlay(){{
        if(timer){{ stopPlay(); return; }}
        timer = setInterval(() => {{
          if(!root.classList.contains("active")) {{ stopPlay(); return; }}
          tick();
          emlabRefreshBoundValues(root);
          update();
        }}, 160);
      }}

      function update(){{
        const I = emlabNum(els.I.value);
        const B = emlabNum(els.B.value);
        const n22 = Math.max(1e-6, emlabNum(els.n.value));
        const n = n22*1e22;
        const t = Math.max(1e-6, 1e-3*emlabNum(els.t.value)); // m
        const isElectron = (els.type.value === "electron");
        const sign = isElectron ? -1 : 1;

        const RH = sign/(n*q);
        const VH = (I*B)/(n*q*t) * sign; // V

        root.querySelector("#{module_id}-ro-VH").textContent = emlabFmt(1000*VH, 3) + " mV";
        root.querySelector("#{module_id}-ro-RH").textContent = emlabFmt(RH, 3) + " m³/C";
        root.querySelector("#{module_id}-ro-sgn").textContent = (isElectron ? "电子：V_H<0" : "空穴：V_H>0");

        // V_H vs B curve
        const Bs = [];
        const Vs = [];
        for(let i=0;i<120;i++) {{
          const bb = 0.2*i/119;
          Bs.push(bb);
          Vs.push(1000*(I*bb)/(n*q*t) * sign);
        }}
        Plotly.restyle(figVB, {{x:[Bs], y:[Vs]}}, [0]);

        // direction diagram: Lorentz force direction flips with carrier sign
        // Keep I along +x and B out of page; for v along +x, q(v×B) is -y for q>0; reversed for electrons.
        const Fy = isElectron ? +0.6 : -0.6;
        const Ey = -Fy*0.8; // Hall E opposes force to balance
        Plotly.restyle(figDir, {{
          x:[[0.0,1.0], [0.5,0.5], [0.5], [0.5,0.5]],
          y:[[0.0,0.0], [0.0,Fy], [0.8], [0.0,Ey]]
        }}, [0,1,2,3]);
      }}

      function reset(){{
        stopPlay();
        dir = 1;
        const d = data.defaults || {{}};
        Object.keys(d).forEach(k => {{
          const el = root.querySelector("#{module_id}-"+k);
          if(el) el.value = d[k];
        }});
        emlabRefreshBoundValues(root);
        update();
      }}

      Object.values(els).forEach(el => {{
        if(!el) return;
        const ev = (el.tagName === "SELECT") ? "change" : "input";
        el.addEventListener(ev, update);
      }});
      els.play.addEventListener("click", togglePlay);
      els.reset.addEventListener("click", reset);
      update();
    }}
    """

    return {
        "id": module_id,
        "title": "扩展：霍尔效应（方向判定与 V_H）",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }
