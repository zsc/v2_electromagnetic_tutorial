from __future__ import annotations

import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, slider


def build() -> dict:
    module_id = "rlc_oscillation"

    intro_html = """
    <p>
      RLC 振荡把“电路里的能量”可视化：电容能量 <code>E_C=½CV²</code> 与电感磁能 <code>E_L=½LI²</code> 在振荡中来回交换，
      电阻把能量以焦耳热形式耗散。阻尼越大（R 越大），振荡衰减越快，Q 值越小。
    </p>
    """

    controls_html = "\n".join(
        [
            slider(cid=f"{module_id}-V0", label="初始电压 V0 (V)", vmin=1, vmax=50, step=1, value=20, unit=" V"),
            slider(cid=f"{module_id}-R", label="电阻 R (Ω)", vmin=0.0, vmax=50.0, step=0.2, value=4.0, unit=" Ω"),
            slider(cid=f"{module_id}-L", label="电感 L (mH)", vmin=1.0, vmax=200.0, step=1.0, value=40.0, unit=" mH"),
            slider(cid=f"{module_id}-C", label="电容 C (mF)", vmin=0.1, vmax=10.0, step=0.1, value=2.0, unit=" mF"),
            buttons([(f"{module_id}-reset", "重置参数", "primary")]),
        ]
    )

    fig0 = go.Figure(
        data=[
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="I(t)", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="V_C(t)", line=dict(color="#a6e22e", width=2), yaxis="y2"),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="RLC 放电：电流与电容电压",
            xaxis_title="t (ms)",
            yaxis_title="I (A)",
            yaxis2=dict(title="V (V)", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    fig1 = go.Figure(
        data=[
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="E_C", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="E_L", line=dict(color="#a6e22e", width=2)),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="E_R(累积热)", line=dict(color="#ff6b6b", width=2)),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="能量观点：C↔L 交换 + R 耗散",
            xaxis_title="t (ms)",
            yaxis_title="能量 (J)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“电感储能在电阻上消失”：电感能量并不会凭空消失，而是通过电流在电阻上转化为热。</li>
      <li>“振荡频率只由 L 或 C 决定”：理想频率 <code>ω0=1/√(LC)</code>，两者共同决定；R 会影响阻尼与实际频率。</li>
      <li>“Q 值越大越危险”：Q 描述的是“相对损耗大小”，并不直接等同于危险性（仍需结合电压/电流幅值）。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>引导问题</summary>
      <ol>
        <li><b>预测</b>：把 C 加倍，振荡周期会变大还是变小？为什么？</li>
        <li><b>验证</b>：把 R 调到接近 0 与较大值，对比能量曲线：E_R 增长速度有何不同？</li>
        <li><b>解释</b>：能量在 E_C 与 E_L 之间交换时，为什么 I(t) 与 V_C(t) 有相位差？</li>
      </ol>
    </details>
    """

    data_payload = {"defaults": {"V0": 20, "R": 4.0, "L": 40.0, "C": 2.0}}

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);
      const els = {{
        V0: root.querySelector("#{module_id}-V0"),
        R: root.querySelector("#{module_id}-R"),
        L: root.querySelector("#{module_id}-L"),
        C: root.querySelector("#{module_id}-C"),
        reset: root.querySelector("#{module_id}-reset"),
      }};

      emlabBindValue(root, "{module_id}-V0", " V", 0);
      emlabBindValue(root, "{module_id}-R", " Ω", 2);
      emlabBindValue(root, "{module_id}-L", " mH", 0);
      emlabBindValue(root, "{module_id}-C", " mF", 1);

      const figIV = document.getElementById("fig-{module_id}-0");
      const figE = document.getElementById("fig-{module_id}-1");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"ω0, 阻尼 α", id:"{module_id}-ro-w", value:"—"}},
        {{key:"Q（近似）", id:"{module_id}-ro-q", value:"—"}},
        {{key:"阻尼类型", id:"{module_id}-ro-reg", value:"—"}},
      ]);

      function update(){{
        const V0 = emlabNum(els.V0.value);
        const R = Math.max(0, emlabNum(els.R.value));
        const L = 1e-3*Math.max(1e-6, emlabNum(els.L.value));
        const C = 1e-3*Math.max(1e-9, emlabNum(els.C.value));

        const w0 = 1/Math.sqrt(L*C);
        const alpha = R/(2*L);
        const Q = (R>1e-12) ? (1/R)*Math.sqrt(L/C) : 1e9;

        let regime = "欠阻尼";
        if(Math.abs(alpha-w0)/w0 < 1e-3) regime = "临界阻尼";
        else if(alpha > w0) regime = "过阻尼";
        root.querySelector("#{module_id}-ro-w").textContent = "ω0≈"+emlabFmt(w0,1)+" rad/s, α≈"+emlabFmt(alpha,1);
        root.querySelector("#{module_id}-ro-q").textContent = emlabFmt(Q,2);
        root.querySelector("#{module_id}-ro-reg").textContent = regime;

        // time axis: show several periods or decay time
        const T0 = 2*Math.PI/Math.max(1e-9, w0);
        const tMax = Math.min(0.08, Math.max(6*T0, 6/Math.max(1e-9,alpha)));
        const N = 1000;
        const t = new Array(N);
        const Vc = new Array(N);
        const I = new Array(N);

        const dt = tMax/(N-1);
        if(alpha < w0*(1-1e-6)) {{
          const wd = Math.sqrt(w0*w0 - alpha*alpha);
          for(let i=0;i<N;i++) {{
            const tt = i*dt;
            t[i] = 1000*tt;
            const exp = Math.exp(-alpha*tt);
            const vc = V0*exp*(Math.cos(wd*tt) + (alpha/wd)*Math.sin(wd*tt));
            Vc[i] = vc;
            I[i] = (V0/(L*wd))*exp*Math.sin(wd*tt);
          }}
        }} else if(Math.abs(alpha-w0)/w0 < 1e-3) {{
          for(let i=0;i<N;i++) {{
            const tt = i*dt;
            t[i] = 1000*tt;
            const exp = Math.exp(-alpha*tt);
            Vc[i] = V0*exp*(1 + alpha*tt);
            I[i] = (V0/L)*tt*exp;
          }}
        }} else {{
          const beta = Math.sqrt(alpha*alpha - w0*w0);
          const s1 = -alpha + beta;
          const s2 = -alpha - beta;
          for(let i=0;i<N;i++) {{
            const tt = i*dt;
            t[i] = 1000*tt;
            Vc[i] = V0*(s2*Math.exp(s1*tt) - s1*Math.exp(s2*tt))/(s2-s1);
            I[i] = (V0/L)*(Math.exp(s1*tt) - Math.exp(s2*tt))/(s1-s2);
          }}
        }}

        // energies
        const Ec = new Array(N);
        const El = new Array(N);
        const Er = new Array(N);
        Er[0]=0;
        for(let i=0;i<N;i++) {{
          Ec[i] = 0.5*C*Vc[i]*Vc[i];
          El[i] = 0.5*L*I[i]*I[i];
          if(i>0) {{
            const i2a = I[i-1]*I[i-1], i2b = I[i]*I[i];
            Er[i] = Er[i-1] + 0.5*(i2a+i2b)*R*(dt);
          }}
        }}

        Plotly.restyle(figIV, {{x:[t,t], y:[I,Vc]}}, [0,1]);
        Plotly.restyle(figE, {{x:[t,t,t], y:[Ec,El,Er]}}, [0,1,2]);
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
        "title": "扩展：RLC 振荡（能量交换与阻尼）",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }

