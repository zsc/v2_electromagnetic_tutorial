from __future__ import annotations

import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, slider


def build() -> dict:
    module_id = "wireless_power"

    intro_html = """
    <p>
      无线充电（耦合谐振）的关键字：<b>耦合系数 k</b>、<b>谐振频率</b>、<b>Q 值</b> 与 <b>失谐</b>。
      两个谐振回路通过互感耦合，只有在频率合适、损耗较小（Q 大）且耦合适中时，能量才能高效传输。
    </p>
    <p>
      本页用“两个串联 RLC + 互感 M”的频域模型计算效率曲线 η(f)（离线交互，前端 O(N) 扫频）。
    </p>
    """

    controls_html = "\n".join(
        [
            slider(cid=f"{module_id}-k", label="耦合系数 k", vmin=0.0, vmax=0.6, step=0.01, value=0.20, unit=""),
            slider(cid=f"{module_id}-Q1", label="发送端 Q1（损耗越小越大）", vmin=10, vmax=400, step=5, value=120, unit=""),
            slider(cid=f"{module_id}-Q2", label="接收端 Q2", vmin=10, vmax=400, step=5, value=120, unit=""),
            slider(cid=f"{module_id}-RL", label="负载电阻 R_L (Ω)", vmin=1, vmax=80, step=1, value=12, unit=" Ω"),
            slider(
                cid=f"{module_id}-detune",
                label="失谐（接收端谐振频率偏差）",
                vmin=-0.25,
                vmax=0.25,
                step=0.01,
                value=0.00,
                unit="×f0",
                help_text="例如 +0.10 表示接收端谐振频率比发送端高约 10%。",
            ),
            buttons([(f"{module_id}-reset", "重置参数", "primary")]),
        ]
    )

    fig0 = go.Figure(
        data=[go.Scatter(x=[0.6, 1.4], y=[0.1, 0.2], mode="lines", line=dict(color="#66d9ef", width=2), name="η(f)")],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="传输效率 η vs 归一化频率 f/f0",
            xaxis_title="f/f0",
            yaxis_title="η",
            yaxis=dict(range=[0, 1.05]),
            showlegend=False,
        ),
    )

    fig1 = go.Figure(
        data=[
            go.Scatter(x=[0.6, 1.4], y=[1, 2], mode="lines", line=dict(color="#a6e22e", width=2), name="|I1|"),
            go.Scatter(x=[0.6, 1.4], y=[0.5, 1.0], mode="lines", line=dict(color="#ff6b6b", width=2), name="|I2|"),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="电流幅值（频域）|I1| 与 |I2|",
            xaxis_title="f/f0",
            yaxis_title="|I| (arb.)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“k 越大效率越高”：不一定。过强耦合会导致频响分裂（双峰）与失配，取决于 Q 与负载。</li>
      <li>“只要调到谐振就行”：失谐会显著降低效率；且系统参数变化（距离、位置、负载）都会改变最佳频率。</li>
      <li>“Q 越大越好”：Q 大意味着损耗小，但带宽变窄，对失谐更敏感。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>引导问题</summary>
      <ol>
        <li><b>预测</b>：把 detune 从 0 改到 +0.15，效率峰值会向哪边移动？峰值会变高还是变低？</li>
        <li><b>验证</b>：在 Q 很大时，曲线会变“尖”还是“宽”？这对无线充电的鲁棒性意味着什么？</li>
        <li><b>解释</b>：为什么耦合过强时会出现“双峰”？（提示：两个耦合振子的正常模）</li>
      </ol>
    </details>
    """

    data_payload = {"defaults": {"k": 0.20, "Q1": 120, "Q2": 120, "RL": 12, "detune": 0.0}}

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);

      const els = {{
        k: root.querySelector("#{module_id}-k"),
        Q1: root.querySelector("#{module_id}-Q1"),
        Q2: root.querySelector("#{module_id}-Q2"),
        RL: root.querySelector("#{module_id}-RL"),
        detune: root.querySelector("#{module_id}-detune"),
        reset: root.querySelector("#{module_id}-reset"),
      }};

      emlabBindValue(root, "{module_id}-k", "", 2);
      emlabBindValue(root, "{module_id}-Q1", "", 0);
      emlabBindValue(root, "{module_id}-Q2", "", 0);
      emlabBindValue(root, "{module_id}-RL", " Ω", 0);
      emlabBindValue(root, "{module_id}-detune", "×f0", 2);

      const figEta = document.getElementById("fig-{module_id}-0");
      const figI = document.getElementById("fig-{module_id}-1");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"η_peak", id:"{module_id}-ro-eta", value:"—"}},
        {{key:"峰值频率", id:"{module_id}-ro-f", value:"—"}},
        {{key:"提示", id:"{module_id}-ro-tip", value:"—"}},
      ]);

      // minimal complex helpers
      function c(re, im){{ return {{re:re, im:im}}; }}
      function csub(a,b){{ return c(a.re-b.re, a.im-b.im); }}
      function cadd(a,b){{ return c(a.re+b.re, a.im+b.im); }}
      function cmul(a,b){{ return c(a.re*b.re - a.im*b.im, a.re*b.im + a.im*b.re); }}
      function cdiv(a,b){{ const d=b.re*b.re+b.im*b.im; return c((a.re*b.re+a.im*b.im)/d, (a.im*b.re-a.re*b.im)/d); }}
      function conj(a){{ return c(a.re, -a.im); }}
      function cabs(a){{ return Math.hypot(a.re, a.im); }}
      function cre(a){{ return a.re; }}

      function update(){{
        const k = Math.max(0, emlabNum(els.k.value));
        const Q1 = Math.max(1, emlabNum(els.Q1.value));
        const Q2 = Math.max(1, emlabNum(els.Q2.value));
        const RL = Math.max(0.1, emlabNum(els.RL.value));
        const det = emlabNum(els.detune.value);

        const f0 = 100e3;
        const w0 = 2*Math.PI*f0;
        const L1 = 100e-6, L2 = 100e-6;
        const C1 = 1/(w0*w0*L1);
        const w02 = w0*(1+det);
        const C2 = 1/(w02*w02*L2);
        const R1 = w0*L1/Q1;
        const R2 = w0*L2/Q2;
        const M = k*Math.sqrt(L1*L2);
        const Vs = 10.0;

        const N = 620;
        const fr = new Array(N);
        const eta = new Array(N);
        const I1m = new Array(N);
        const I2m = new Array(N);

        let best = -1, bestF = 1.0;
        for(let i=0;i<N;i++) {{
          const r = 0.6 + 0.8*i/(N-1);
          fr[i] = r;
          const w = w0*r;

          const Zc1 = c(0, -1/(w*C1));
          const Zc2 = c(0, -1/(w*C2));
          const Z1 = cadd(cadd(c(R1,0), c(0,w*L1)), Zc1);
          const Z2 = cadd(cadd(c(R2+RL,0), c(0,w*L2)), Zc2);
          const jwM = c(0, w*M);

          // solve 2x2:
          // Z1 I1 + jwM I2 = Vs
          // jwM I1 + Z2 I2 = 0
          // => I1 = Vs*Z2 / (Z1*Z2 - (jwM)^2)
          //    I2 = -Vs*jwM / (Z1*Z2 - (jwM)^2)
          const den = csub(cmul(Z1, Z2), cmul(jwM, jwM));
          const I1 = cdiv(cmul(c(Vs,0), Z2), den);
          const I2 = cdiv(cmul(c(-Vs,0), jwM), den); // -Vs*jwM/den

          const I1abs = cabs(I1);
          const I2abs = cabs(I2);
          I1m[i] = I1abs;
          I2m[i] = I2abs;

          const Pin = 0.5 * (Vs * cre(conj(I1)));
          const PL = 0.5 * I2abs*I2abs * RL;
          const et = (Pin>1e-12) ? (PL/Pin) : 0;
          eta[i] = Math.max(0, Math.min(1.0, et));
          if(eta[i] > best) {{ best = eta[i]; bestF = r; }}
        }}

        Plotly.restyle(figEta, {{x:[fr], y:[eta]}}, [0]);
        Plotly.restyle(figI, {{x:[fr, fr], y:[I1m, I2m]}}, [0,1]);

        root.querySelector("#{module_id}-ro-eta").textContent = emlabFmt(best, 3);
        root.querySelector("#{module_id}-ro-f").textContent = "≈"+emlabFmt(bestF,3)+" f0";
        root.querySelector("#{module_id}-ro-tip").textContent = (Math.abs(det)>0.05) ? "明显失谐：峰值降低/偏移" : "接近调谐";
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
        "title": "扩展：无线充电（耦合谐振）",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }
