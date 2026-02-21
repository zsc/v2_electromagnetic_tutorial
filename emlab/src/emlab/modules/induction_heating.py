from __future__ import annotations

import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, slider


def build() -> dict:
    module_id = "induction_heating"

    intro_html = """
    <p>
      电磁感应加热的直观链条：交流磁场 → 金属内部产生感应电场 → 涡流 → 焦耳热。
      高频下会出现<strong>集肤效应</strong>：电流主要集中在表面一层厚度 δ 内，
      近似 <code>δ ≈ √(2ρ/(ωμ))</code>（ρ 为电阻率，μ 为磁导率）。
    </p>
    <p>
      本页用教学近似展示 δ(f) 与“相对加热功率指标”随频率的趋势（不涉及任何装置制造或危险实验指导）。
    </p>
    """

    controls_html = "\n".join(
        [
            slider(cid=f"{module_id}-f", label="频率 f (kHz)", vmin=0.5, vmax=200.0, step=0.5, value=50.0, unit=" kHz"),
            slider(
                cid=f"{module_id}-B",
                label="磁场幅值 B (mT)",
                vmin=0.5,
                vmax=80.0,
                step=0.5,
                value=20.0,
                unit=" mT",
                help_text="功率随 B 增大明显上升（定性：感应电动势 ∝ ωB）。",
            ),
            slider(
                cid=f"{module_id}-rho",
                label="电阻率 ρ (×10⁻⁸ Ω·m)",
                vmin=1.0,
                vmax=200.0,
                step=1.0,
                value=20.0,
                unit="",
                help_text="ρ 越大，电流越小，功率一般下降；但 δ 会变大（更深处参与）。",
            ),
            slider(cid=f"{module_id}-t", label="材料厚度 t (mm)", vmin=0.2, vmax=20.0, step=0.2, value=5.0, unit=" mm"),
            buttons(
                [
                    (f"{module_id}-play", "播放/暂停", "primary"),
                    (f"{module_id}-reset", "重置参数", ""),
                ]
            ),
        ]
    )

    fig0 = go.Figure(
        data=[
            go.Scatter(x=[0.5, 200], y=[10, 2], mode="lines", name="δ(f)", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[50], y=[3], mode="markers", name="当前", marker=dict(size=10, color="#ff6b6b")),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="集肤深度 δ vs 频率（教学近似）",
            xaxis_title="f (kHz)",
            yaxis_title="δ (mm)",
            xaxis=dict(type="log"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    fig1 = go.Figure(
        data=[
            go.Scatter(x=[0.5, 200], y=[0.1, 0.8], mode="lines", name="P_rel(f)", line=dict(color="#a6e22e", width=2)),
            go.Scatter(x=[50], y=[0.5], mode="markers", name="当前", marker=dict(size=10, color="#ff6b6b")),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="相对加热功率指标 P_rel vs 频率（趋势演示）",
            xaxis_title="f (kHz)",
            yaxis_title="P_rel (arb.)",
            xaxis=dict(type="log"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“频率越高 δ 越大”：相反，<code>δ ∝ 1/√f</code>，频率越高集肤越明显。</li>
      <li>“电阻率越大越容易加热”：一般趋势是功率随 1/ρ 降低，但同时 δ 变大、有效体积变化（此处用简化指标）。</li>
      <li>“磁场只要有就会强烈加热”：功率与 ω 与 B 的增长有关，低频/弱磁场下加热很弱。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>引导问题</summary>
      <ol>
        <li><b>预测</b>：把 f 提高 4 倍，δ 会变成原来的多少？（提示：δ∝1/√f）</li>
        <li><b>验证</b>：把厚度 t 从 2mm 增到 10mm，当 t≫δ 时，功率随 t 还会明显增加吗？</li>
        <li><b>解释</b>：用“感应电动势 ∝ dΦ/dt ∝ ωB”解释：为什么功率对频率很敏感？</li>
      </ol>
    </details>
    """

    data_payload = {"defaults": {"f": 50.0, "B": 20.0, "rho": 20.0, "t": 5.0}}

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);
      const els = {{
        f: root.querySelector("#{module_id}-f"),
        B: root.querySelector("#{module_id}-B"),
        rho: root.querySelector("#{module_id}-rho"),
        t: root.querySelector("#{module_id}-t"),
        play: root.querySelector("#{module_id}-play"),
        reset: root.querySelector("#{module_id}-reset"),
      }};

      emlabBindValue(root, "{module_id}-f", " kHz", 1);
      emlabBindValue(root, "{module_id}-B", " mT", 1);
      emlabBindValue(root, "{module_id}-rho", "", 0);
      emlabBindValue(root, "{module_id}-t", " mm", 1);

      const figD = document.getElementById("fig-{module_id}-0");
      const figP = document.getElementById("fig-{module_id}-1");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"当前 δ", id:"{module_id}-ro-d", value:"—"}},
        {{key:"当前 P_rel", id:"{module_id}-ro-p", value:"—"}},
        {{key:"提示", id:"{module_id}-ro-tip", value:"—"}},
      ]);

      const mu0 = 4e-7*Math.PI;

      let timer = null;
      let dir = 1;
      function stopPlay(){{ if(timer){{ clearInterval(timer); timer=null; }} }}
      function tick(){{
        const el = els.f;
        if(!el) return;
        const vmin = emlabNum(el.min);
        const vmax = emlabNum(el.max);
        const step = Math.max(1e-12, emlabNum(el.step || 1));
        let v = emlabNum(el.value);
        const factor = 1.04;
        v = (dir > 0) ? (v*factor) : (v/factor);
        if(v >= vmax){{ v=vmax; dir=-1; }}
        if(v <= vmin){{ v=vmin; dir=1; }}
        v = vmin + Math.round((v-vmin)/step)*step;
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
        }}, 150);
      }}

      function skinDepth(fHz, rho){{
        const w = 2*Math.PI*fHz;
        return Math.sqrt(2*rho/(Math.max(1e-12,w*mu0)));
      }}

      function powerRel(fHz, B, rho, t){{
        // teaching indicator: P ~ (ω^2 B^2 / ρ) * (1 - exp(-t/δ))
        const w = 2*Math.PI*fHz;
        const d = skinDepth(fHz, rho);
        const fill = 1 - Math.exp(-t/Math.max(1e-12,d));
        return (w*w*B*B/Math.max(1e-18,rho)) * fill;
      }}

      function update(){{
        const f = 1e3*Math.max(1e-6, emlabNum(els.f.value)); // Hz
        const B = 1e-3*Math.max(0, emlabNum(els.B.value)); // T
        const rho = 1e-8*Math.max(1e-6, emlabNum(els.rho.value)); // Ω·m
        const t = 1e-3*Math.max(1e-6, emlabNum(els.t.value)); // m

        const d = skinDepth(f, rho);
        const P = powerRel(f, B, rho, t);

        root.querySelector("#{module_id}-ro-d").textContent = emlabFmt(1000*d, 3) + " mm";
        root.querySelector("#{module_id}-ro-p").textContent = emlabFmt(P/1e6, 3) + "×10⁶ (arb.)";
        root.querySelector("#{module_id}-ro-tip").textContent = (t > 3*d) ? "t≫δ：主要表面加热" : "t~δ：体积参与更多";

        // curves
        const fmin = 0.5, fmax = 200.0;
        const N = 240;
        const fk = new Array(N);
        const ds = new Array(N);
        const ps = new Array(N);
        for(let i=0;i<N;i++) {{
          const ffk = fmin*Math.pow(fmax/fmin, i/(N-1));
          fk[i] = ffk;
          const fHz = 1e3*ffk;
          ds[i] = 1000*skinDepth(fHz, rho);
          ps[i] = powerRel(fHz, B, rho, t)/1e6;
        }}
        Plotly.restyle(figD, {{x:[fk, [f/1000]], y:[ds, [1000*d]]}}, [0,1]);
        Plotly.restyle(figP, {{x:[fk, [f/1000]], y:[ps, [P/1e6]]}}, [0,1]);
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
        el.addEventListener("input", update);
      }});
      els.play.addEventListener("click", togglePlay);
      els.reset.addEventListener("click", reset);
      update();
    }}
    """

    return {
        "id": module_id,
        "title": "扩展：电磁感应加热（涡流与集肤效应）",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }
