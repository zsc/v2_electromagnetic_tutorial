from __future__ import annotations

import math

import numpy as np
import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, slider
from emlab.common.units import e, h, m_e


def _lambda_pm(v: np.ndarray) -> np.ndarray:
    # Non-relativistic: λ = h / sqrt(2 m e V)
    p = np.sqrt(2.0 * m_e * e * np.maximum(v, 1e-9))
    lam = h / p
    return lam * 1e12  # pm


def build() -> dict:
    module_id = "electron_microscope"

    intro_html = """
    <p>
      电子显微镜的两个“高中层级”抓手：
    </p>
    <ul>
      <li><b>电压 → 电子波长</b>：德布罗意关系 <code>λ = h/√(2meV)</code>（此处用非相对论近似）。</li>
      <li><b>磁透镜 → 聚焦</b>：线圈电流产生磁场，对运动电子施加洛伦兹力，使电子束像“光线”一样会聚/发散（定性）。</li>
    </ul>
    <p>
      本页用“薄透镜近似”的光线追迹展示聚焦效果，并给出 λ(V) 曲线与当前读数。
    </p>
    """

    v_curve = np.linspace(500, 10000, 120)
    lam_curve = _lambda_pm(v_curve)

    controls_html = "\n".join(
        [
            slider(
                cid=f"{module_id}-V",
                label="加速电压 V (V)",
                vmin=500,
                vmax=10000,
                step=50,
                value=5000,
                unit=" V",
                help_text="V 越大，电子动量越大，德布罗意波长越短（分辨本领提高，但仍受像差等限制）。",
            ),
            slider(
                cid=f"{module_id}-I",
                label="透镜线圈电流 I_lens (A)",
                vmin=0.0,
                vmax=3.0,
                step=0.02,
                value=1.2,
                unit=" A",
                help_text="用经验关系 1/f ∝ I²（教学近似），I 越大聚焦越强（焦距更短）。",
            ),
            slider(
                cid=f"{module_id}-div",
                label="初始发散角（mrad）",
                vmin=0.0,
                vmax=30.0,
                step=0.5,
                value=12.0,
                unit=" mrad",
                help_text="越大发散越强，屏上束斑更大；透镜可减小束斑但会出现最佳值。",
            ),
            slider(
                cid=f"{module_id}-quality",
                label="束质/像差指标（定性）",
                vmin=0.5,
                vmax=2.0,
                step=0.01,
                value=1.0,
                unit="×",
                help_text=">1 表示像差/不完美更明显（仅用于教学展示）。",
            ),
            buttons([(f"{module_id}-reset", "重置参数", "primary")]),
        ]
    )

    fig0 = go.Figure(
        data=[
            go.Scatter(x=[0, 0.2], y=[0, 0], mode="lines", name="束线", line=dict(color="#66d9ef", width=2)),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="束线追迹（薄透镜近似）：z 方向传播，y 方向偏离",
            xaxis_title="z (m)",
            yaxis_title="y (mm)",
            xaxis=dict(range=[0, 0.22]),
            yaxis=dict(range=[-18, 18]),
            shapes=[
                dict(type="line", x0=0.08, x1=0.08, y0=-20, y1=20, line=dict(color="rgba(255,255,255,0.25)", dash="dot")),
                dict(type="line", x0=0.20, x1=0.20, y0=-20, y1=20, line=dict(color="rgba(255,255,255,0.25)", dash="dot")),
            ],
            annotations=[
                dict(x=0.08, y=17, text="磁透镜", showarrow=False, font=dict(size=11, color="rgba(255,255,255,0.75)")),
                dict(x=0.20, y=17, text="屏/像平面", showarrow=False, font=dict(size=11, color="rgba(255,255,255,0.75)")),
            ],
            showlegend=False,
        ),
    )

    fig1 = go.Figure(
        data=[
            go.Scatter(x=v_curve.tolist(), y=lam_curve.tolist(), mode="lines", name="λ(V)", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[5000], y=[float(_lambda_pm(np.array([5000]))[0])], mode="markers", name="当前", marker=dict(size=10, color="#a6e22e")),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="德布罗意波长 λ(V)（非相对论近似）",
            xaxis_title="V (V)",
            yaxis_title="λ (pm)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“电压越高就一定无限清晰”：不对。分辨率还受像差、稳定性、样品与探测等限制（工程细节不展开）。</li>
      <li>“磁力把电子吸向某点”：更合理的说法是：磁场对运动电荷产生洛伦兹力，改变其横向动量，使束线会聚。</li>
      <li>“λ 很小就意味着能看到任意小”：波长只是一个因素；成像系统的像差与噪声也很关键。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>引导问题</summary>
      <ol>
        <li><b>预测</b>：把 V 从 2 kV 提到 8 kV，λ 会变成原来的多少？（观察曲线）</li>
        <li><b>验证</b>：固定发散角，调 I_lens，束斑半径会出现“最小值”吗？为什么？</li>
        <li><b>解释</b>：用“薄透镜：θ_out = θ_in - y/f”解释：为什么焦距变短会更强烈地改变束线斜率？</li>
      </ol>
    </details>
    """

    data_payload = {
        "v_curve": v_curve.astype(float).tolist(),
        "lam_curve": lam_curve.astype(float).tolist(),
        "defaults": {"V": 5000, "I": 1.2, "div": 12.0, "quality": 1.0},
    }

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);

      const els = {{
        V: root.querySelector("#{module_id}-V"),
        I: root.querySelector("#{module_id}-I"),
        div: root.querySelector("#{module_id}-div"),
        quality: root.querySelector("#{module_id}-quality"),
        reset: root.querySelector("#{module_id}-reset"),
      }};

      emlabBindValue(root, "{module_id}-V", " V", 0);
      emlabBindValue(root, "{module_id}-I", " A", 2);
      emlabBindValue(root, "{module_id}-div", " mrad", 1);
      emlabBindValue(root, "{module_id}-quality", "×", 2);

      const figRay = document.getElementById("fig-{module_id}-0");
      const figLam = document.getElementById("fig-{module_id}-1");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"λ（当前）", id:"{module_id}-ro-lam", value:"—"}},
        {{key:"束斑半径（屏上，mm）", id:"{module_id}-ro-spot", value:"—"}},
        {{key:"焦距 f（教学量）", id:"{module_id}-ro-f", value:"—"}},
      ]);

      function lambdaPm(V){{
        const e = 1.602176634e-19;
        const me = 9.1093837015e-31;
        const h = 6.62607015e-34;
        const p = Math.sqrt(Math.max(1e-12, 2*me*e*V));
        return (h/p)*1e12;
      }}

      function update(){{
        const V = emlabNum(els.V.value);
        const I = emlabNum(els.I.value);
        const div = 1e-3 * emlabNum(els.div.value); // rad
        const q = emlabNum(els.quality.value);

        const lam = lambdaPm(V);
        root.querySelector("#{module_id}-ro-lam").textContent = emlabFmt(lam, 2) + " pm";

        // thin-lens ray tracing in (z,y). Lens at zL, screen at zS.
        const z0 = 0.0, zL = 0.08, zS = 0.20;
        // empirical f: 1/f ∝ I^2 ; clamp
        const invf = 8.0 * (I*I); // 1/m (teaching scale)
        const f = (invf > 1e-6) ? (1.0/invf) : 1e6;
        root.querySelector("#{module_id}-ro-f").textContent = (f > 5) ? "很弱(>5m)" : emlabFmt(f,3) + " m";

        // multiple rays from point source y=0 with different angles
        const nRays = 9;
        const xs = [];
        const ys = [];
        const yEnd = [];
        for(let i=0;i<nRays;i++){{
          const a = (-div + 2*div*i/(nRays-1));
          // segment 1: 0 -> zL
          const yL = a*(zL-z0);
          const thIn = a;
          // lens kick: thOut = thIn - y/f
          const thOut = thIn - (yL / f);
          // segment 2: zL -> zS
          const yS = yL + thOut*(zS - zL);
          yEnd.push(yS*q);

          xs.push(z0, zL, zS, null);
          ys.push(0, 1000*yL*q, 1000*yS*q, null); // mm
        }}
        Plotly.restyle(figRay, {{x:[xs], y:[ys]}}, [0]);

        const rms = Math.sqrt(yEnd.reduce((s,v)=>s+v*v,0)/Math.max(1,nRays));
        root.querySelector("#{module_id}-ro-spot").textContent = emlabFmt(1000*rms,2);

        // marker on lambda curve
        Plotly.restyle(figLam, {{x:[[V]], y:[[lam]]}}, [1]);
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
        el.addEventListener("input", update);
      }});
      els.reset.addEventListener("click", reset);
      update();
    }}
    """

    return {
        "id": module_id,
        "title": "M07 电子显微镜：电压→波长，磁透镜→聚焦",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }

