from __future__ import annotations

import math

import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, select, slider


def build() -> dict:
    module_id = "mass_spec"

    intro_html = """
    <p>
      质谱仪用电场加速与磁场偏转把不同 <b>m/q</b> 的粒子分开：
      <code>qV = ½mv²</code>，
      <code>r = mv/(|q|B)</code>。
      因此在固定 V、B 下，半径 r 与 <code>√(m/q)</code> 有关。
      也可以加入<strong>速度选择器</strong>：<code>v = E/B</code>，让进入磁场的粒子速度更一致。
    </p>
    <p>
      本页面用理想化 2D 圆弧轨迹展示“落点分离”，并给出读数 v、r 与分离度（定性）。
    </p>
    """

    species = [
        ("H+", 1.0),
        ("He+", 4.0),
        ("Ne+", 20.0),
        ("Ar+", 40.0),
        ("Kr+", 84.0),
        ("Xe+", 131.0),
    ]  # (label, m_over_q in (u/e))

    controls_html = "\n".join(
        [
            slider(
                cid=f"{module_id}-Vacc",
                label="加速电压 V_acc (V)",
                vmin=200,
                vmax=5000,
                step=10,
                value=1200,
                unit=" V",
            ),
            slider(
                cid=f"{module_id}-B",
                label="磁感应强度 B (T)",
                vmin=0.01,
                vmax=0.20,
                step=0.001,
                value=0.08,
                unit=" T",
            ),
            select(
                cid=f"{module_id}-mode",
                label="模式",
                value="accel",
                options=[("accel", "仅加速后进入磁场"), ("selector", "加入速度选择器 (v=E/B)")],
                help_text="速度选择器是理想化模型：用 E 与 B 选出特定速度。",
            ),
            slider(
                cid=f"{module_id}-E",
                label="速度选择器电场 E (V/m)",
                vmin=0,
                vmax=8000,
                step=50,
                value=2000,
                unit=" V/m",
            ),
            select(
                cid=f"{module_id}-sp1",
                label="粒子 A（单价正离子）",
                value="H+",
                options=[(k, k) for k, _ in species],
            ),
            select(
                cid=f"{module_id}-sp2",
                label="粒子 B（对比，可选）",
                value="Ne+",
                options=[("none", "不显示")] + [(k, k) for k, _ in species],
            ),
            buttons([(f"{module_id}-reset", "重置参数", "primary")]),
        ]
    )

    fig0 = go.Figure(
        data=[
            go.Scatter(x=[0], y=[0], mode="lines", name="轨迹 A", line=dict(color="#66d9ef", width=3)),
            go.Scatter(x=[0], y=[0], mode="markers", name="落点 A", marker=dict(size=10, color="#66d9ef")),
            go.Scatter(x=[0], y=[0], mode="lines", name="轨迹 B", line=dict(color="#a6e22e", width=3)),
            go.Scatter(x=[0], y=[0], mode="markers", name="落点 B", marker=dict(size=10, color="#a6e22e")),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=50, r=20, t=40, b=45),
            title="磁场中圆弧轨迹与探测屏落点（理想化）",
            xaxis_title="x (m)",
            yaxis_title="y (m)",
            xaxis=dict(range=[-0.02, 0.20], showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(range=[-0.02, 0.22], showgrid=True, gridcolor="rgba(255,255,255,0.06)", scaleanchor="x"),
            shapes=[
                dict(type="line", x0=0.15, x1=0.15, y0=-0.02, y1=0.25, line=dict(color="rgba(255,255,255,0.35)", dash="dot")),
            ],
            annotations=[
                dict(x=0.15, y=0.24, text="探测屏", showarrow=False, font=dict(size=11, color="rgba(255,255,255,0.75)")),
            ],
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    fig1 = go.Figure(
        data=[
            go.Scatter(x=[1, 2, 3], y=[0, 1, 2], mode="lines", name="y_hit(m/q)", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[1], y=[0], mode="markers", name="A", marker=dict(size=10, color="#66d9ef")),
            go.Scatter(x=[1], y=[0], mode="markers", name="B", marker=dict(size=10, color="#a6e22e")),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="落点位置 vs m/q（固定屏幕位置）",
            xaxis_title="m/q (u/e)",
            yaxis_title="落点 y (m)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“B 越大半径越大”：不对，<code>r ∝ 1/B</code>，磁场越强弯得越厉害。</li>
      <li>“电压越大弯得越厉害”：对仅加速模式，电压越大速度越大，反而 <code>r ∝ √V</code> 增大。</li>
      <li>“m 越大一定更难偏转”：要看 m/q。带电量不同（q 不同）会显著影响轨迹。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>引导问题</summary>
      <ol>
        <li><b>预测</b>：把 B 加倍，轨迹半径 r 会变成原来的多少？落点会如何移动？</li>
        <li><b>验证</b>：在“仅加速”与“速度选择器”两种模式下，改变 V_acc 对落点的影响是否相同？为什么？</li>
        <li><b>解释</b>：用 <code>qV=½mv²</code> 与 <code>r=mv/(qB)</code> 推导出 r 与 V、B、m/q 的关系。</li>
      </ol>
    </details>
    """

    data_payload = {
        "species": {k: v for k, v in species},
        "x_det": 0.15,
        "u_over_e_kg_per_C": 1.66053906660e-27 / 1.602176634e-19,
        "defaults": {"Vacc": 1200, "B": 0.08, "mode": "accel", "E": 2000, "sp1": "H+", "sp2": "Ne+"},
    }

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);
      const els = {{
        Vacc: root.querySelector("#{module_id}-Vacc"),
        B: root.querySelector("#{module_id}-B"),
        mode: root.querySelector("#{module_id}-mode"),
        E: root.querySelector("#{module_id}-E"),
        sp1: root.querySelector("#{module_id}-sp1"),
        sp2: root.querySelector("#{module_id}-sp2"),
        reset: root.querySelector("#{module_id}-reset"),
      }};

      emlabBindValue(root, "{module_id}-Vacc", " V", 0);
      emlabBindValue(root, "{module_id}-B", " T", 3);
      emlabBindValue(root, "{module_id}-E", " V/m", 0);

      const figTraj = document.getElementById("fig-{module_id}-0");
      const figHit = document.getElementById("fig-{module_id}-1");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"粒子A：v, r", id:"{module_id}-ro-a", value:"—"}},
        {{key:"粒子B：v, r", id:"{module_id}-ro-b", value:"—"}},
        {{key:"分离 Δy", id:"{module_id}-ro-dy", value:"—"}},
      ]);

      const sp = data.species || {{}};
      const xDet = data.x_det || 0.15;
      const uoe = data.u_over_e_kg_per_C || 1.0;

      function moq_kgC(label){{
        const v = sp[label];
        return (v === undefined) ? null : (v * uoe);
      }}

      function kinematics(moq, Vacc, B, mode, E){{
        // moq: kg/C
        let v = 0;
        if(mode === "selector"){{
          v = E / Math.max(1e-9, B);
        }} else {{
          v = Math.sqrt(Math.max(0, 2*Vacc / Math.max(1e-12, moq)));
        }}
        const r = (moq * v) / Math.max(1e-9, B);
        return {{v, r}};
      }}

      function arcToDetector(r){{
        if(r <= xDet) return null;
        const th = Math.asin(xDet / r); // 0..pi/2
        const N = 220;
        const xs = new Array(N);
        const ys = new Array(N);
        for(let i=0;i<N;i++){{
          const a = th * i/(N-1);
          xs[i] = r*Math.sin(a);
          ys[i] = r*(1 - Math.cos(a));
        }}
        const yHit = r*(1 - Math.cos(th));
        return {{xs, ys, yHit}};
      }}

      function update(){{
        const Vacc = emlabNum(els.Vacc.value);
        const B = emlabNum(els.B.value);
        const mode = els.mode.value;
        const E = emlabNum(els.E.value);

        const aLabel = els.sp1.value;
        const bLabel = els.sp2.value;

        const moqA = moq_kgC(aLabel);
        const moqB = (bLabel === "none") ? null : moq_kgC(bLabel);

        const kA = kinematics(moqA, Vacc, B, mode, E);
        const arcA = arcToDetector(kA.r);
        let kB = null, arcB = null;
        if(moqB !== null) {{
          kB = kinematics(moqB, Vacc, B, mode, E);
          arcB = arcToDetector(kB.r);
        }}

        // update trajectory plot
        const xA = arcA ? arcA.xs : [0];
        const yA = arcA ? arcA.ys : [0];
        const hitAx = arcA ? [xDet] : [0];
        const hitAy = arcA ? [arcA.yHit] : [0];

        const xB = (arcB && bLabel !== "none") ? arcB.xs : [0];
        const yB = (arcB && bLabel !== "none") ? arcB.ys : [0];
        const hitBx = (arcB && bLabel !== "none") ? [xDet] : [0];
        const hitBy = (arcB && bLabel !== "none") ? [arcB.yHit] : [0];

        Plotly.restyle(figTraj, {{x:[xA, hitAx, xB, hitBx], y:[yA, hitAy, yB, hitBy]}}, [0,1,2,3]);

        // hit position vs m/q curve (scan)
        const moqList = Object.values(sp);
        const xs = [];
        const ys = [];
        for(let i=0;i<moqList.length;i++) {{
          const moq = moqList[i]*uoe;
          const k = kinematics(moq, Vacc, B, mode, E);
          const arc = arcToDetector(k.r);
          if(!arc) continue;
          xs.push(moqList[i]);
          ys.push(arc.yHit);
        }}
        Plotly.restyle(figHit, {{
          x:[xs, [sp[aLabel]||1], (bLabel==="none")?[0]:[sp[bLabel]||1]],
          y:[ys, [arcA?arcA.yHit:0], (bLabel==="none")?[0]:[arcB?arcB.yHit:0]],
        }}, [0,1,2]);

        // readouts
        const vTxtA = "v≈"+emlabFmt(kA.v,2)+" m/s, r≈"+emlabFmt(kA.r,3)+" m";
        root.querySelector("#{module_id}-ro-a").textContent = vTxtA;
        if(bLabel === "none" || !kB) {{
          root.querySelector("#{module_id}-ro-b").textContent = "—";
          root.querySelector("#{module_id}-ro-dy").textContent = "—";
        }} else {{
          root.querySelector("#{module_id}-ro-b").textContent = "v≈"+emlabFmt(kB.v,2)+" m/s, r≈"+emlabFmt(kB.r,3)+" m";
          const dy = (arcA && arcB) ? Math.abs(arcA.yHit - arcB.yHit) : NaN;
          root.querySelector("#{module_id}-ro-dy").textContent = isFinite(dy) ? (emlabFmt(dy*1000,2)+" mm") : "未击中屏";
        }}

        // enable/disable E by mode
        els.E.disabled = (mode !== "selector");
      }}

      function reset(){{
        const d = data.defaults || {{}};
        Object.keys(d).forEach(k => {{
          const el = root.querySelector("#{module_id}-"+k);
          if(el) el.value = d[k];
        }});
        update();
      }}

      Object.values(els).forEach(el => {{
        if(!el) return;
        const ev = (el.tagName === "SELECT") ? "change" : "input";
        el.addEventListener(ev, update);
      }});
      els.reset.addEventListener("click", reset);
      update();
    }}
    """

    return {
        "id": module_id,
        "title": "M06 质谱仪：V 与 B 决定轨迹半径",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }

