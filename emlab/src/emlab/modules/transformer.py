from __future__ import annotations

import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, select, slider


def build() -> dict:
    module_id = "transformer"

    intro_html = """
    <p>
      变压器用<strong>互感</strong>把交流电能从原边“磁耦合”到副边。理想模型给出：
      <code>V_s/V_p = N_s/N_p</code>，
      <code>I_s/I_p = N_p/N_s</code>，
      并满足功率近似守恒 <code>P_p ≈ P_s</code>（忽略损耗）。
    </p>
    <p>
      本页用正弦稳态的相量/波形思想：负载从纯电阻变为 RL 时，电流会滞后电压，功率因数改变。
    </p>
    """

    controls_html = "\n".join(
        [
            slider(cid=f"{module_id}-Np", label="原边匝数 Np", vmin=50, vmax=500, step=1, value=200, unit=""),
            slider(cid=f"{module_id}-Ns", label="副边匝数 Ns", vmin=10, vmax=500, step=1, value=100, unit=""),
            slider(
                cid=f"{module_id}-Vp",
                label="原边电压 Vp_rms (V)",
                vmin=5,
                vmax=240,
                step=1,
                value=24,
                unit=" V",
            ),
            slider(cid=f"{module_id}-f", label="频率 f (Hz)", vmin=10, vmax=200, step=1, value=50, unit=" Hz"),
            select(
                cid=f"{module_id}-load",
                label="负载类型",
                value="R",
                options=[("R", "纯电阻 R"), ("RL", "电阻 + 电感 (RL)")],
            ),
            slider(
                cid=f"{module_id}-R",
                label="负载电阻 R_load (Ω)",
                vmin=1,
                vmax=200,
                step=1,
                value=20,
                unit=" Ω",
            ),
            slider(
                cid=f"{module_id}-L",
                label="负载电感 L_load (H)",
                vmin=0.0,
                vmax=0.5,
                step=0.005,
                value=0.10,
                unit=" H",
                help_text="仅 RL 模式生效；L 越大，电流滞后越明显，功率因数越小。",
            ),
            buttons([(f"{module_id}-reset", "重置参数", "primary")]),
        ]
    )

    fig0 = go.Figure(
        data=[
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="v_p(t)", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="v_s(t)", line=dict(color="#a6e22e", width=2)),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="电压波形：原边 vs 副边（理想变压器）",
            xaxis_title="t (ms)",
            yaxis_title="V (V)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    fig1 = go.Figure(
        data=[
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="i_p(t)", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="i_s(t)", line=dict(color="#a6e22e", width=2)),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="电流波形：原边 vs 副边（相位/功率因数）",
            xaxis_title="t (ms)",
            yaxis_title="I (A)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    fig2 = go.Figure(
        data=[
            go.Scatter(
                x=[0, 1],
                y=[0, 0],
                mode="lines+markers",
                name="V ∠0°",
                line=dict(color="#66d9ef", width=3),
                marker=dict(size=6),
            ),
            go.Scatter(
                x=[0, 0.8],
                y=[0, -0.3],
                mode="lines+markers",
                name="I ∠-φ",
                line=dict(color="#a6e22e", width=3),
                marker=dict(size=6),
            ),
            go.Scatter(
                x=[0, 0.8],
                y=[0, 0],
                mode="lines",
                name="I·cosφ（投影）",
                line=dict(color="rgba(255,255,255,0.6)", width=2, dash="dot"),
            ),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="相量图：V 与 I（功率因数 cosφ = 投影/长度）",
            xaxis=dict(title="Re（相对）", range=[-1.2, 1.2], zeroline=False),
            yaxis=dict(title="Im（相对）", range=[-1.2, 1.2], scaleanchor="x", zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“变压器能把直流电压变高/变低”：理想变压器需要交变磁通，因此不能直接变换纯直流（除非用开关电路先变成交流）。</li>
      <li>“匝数比只影响电压不影响电流”：理想模型中电流也按匝数比反比变化，近似功率守恒。</li>
      <li>“电感负载只会让电流变小”：还会引入相位滞后，使有功功率下降（功率因数变小）。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>引导问题</summary>
      <ol>
        <li><b>预测</b>：把 Ns 加倍，Vs_rms 变成多少？Is_rms 又会怎样变化？</li>
        <li><b>验证</b>：切到 RL 负载，增大 L，电流相位滞后会变大还是变小？有功功率会怎样？</li>
        <li><b>解释</b>：用“相量/阻抗”解释：为什么 RL 负载下电流不与电压同相？</li>
      </ol>
    </details>
    """

    data_payload = {
        "defaults": {"Np": 200, "Ns": 100, "Vp": 24, "f": 50, "load": "R", "R": 20, "L": 0.10}
    }

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);

      const els = {{
        Np: root.querySelector("#{module_id}-Np"),
        Ns: root.querySelector("#{module_id}-Ns"),
        Vp: root.querySelector("#{module_id}-Vp"),
        f: root.querySelector("#{module_id}-f"),
        load: root.querySelector("#{module_id}-load"),
        R: root.querySelector("#{module_id}-R"),
        L: root.querySelector("#{module_id}-L"),
        reset: root.querySelector("#{module_id}-reset"),
      }};

      emlabBindValue(root, "{module_id}-Np", "", 0);
      emlabBindValue(root, "{module_id}-Ns", "", 0);
      emlabBindValue(root, "{module_id}-Vp", " V", 0);
      emlabBindValue(root, "{module_id}-f", " Hz", 0);
      emlabBindValue(root, "{module_id}-R", " Ω", 0);
      emlabBindValue(root, "{module_id}-L", " H", 3);

      const figV = document.getElementById("fig-{module_id}-0");
      const figI = document.getElementById("fig-{module_id}-1");
      const figPh = document.getElementById("fig-{module_id}-2");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"Vs_rms / Is_rms", id:"{module_id}-ro-s", value:"—"}},
        {{key:"功率 P_load", id:"{module_id}-ro-p", value:"—"}},
        {{key:"功率因数 cosφ", id:"{module_id}-ro-pf", value:"—"}},
        {{key:"相位滞后 φ", id:"{module_id}-ro-phi", value:"—"}},
        {{key:"视在功率 S", id:"{module_id}-ro-S", value:"—"}},
        {{key:"无功功率 Q", id:"{module_id}-ro-Q", value:"—"}},
      ]);

      function update(){{
        const Np = Math.max(1, Math.round(emlabNum(els.Np.value)));
        const Ns = Math.max(1, Math.round(emlabNum(els.Ns.value)));
        const Vp = Math.max(0, emlabNum(els.Vp.value));
        const f = Math.max(0.1, emlabNum(els.f.value));
        const kind = els.load.value;
        const R = Math.max(0.1, emlabNum(els.R.value));
        const L = Math.max(0.0, emlabNum(els.L.value));

        const n = Ns/Np;
        const Vs = Vp*n;
        const w = 2*Math.PI*f;

        // load impedance
        const Xl = (kind === "RL") ? (w*L) : 0;
        const Zmag = Math.hypot(R, Xl);
        const phi = Math.atan2(Xl, R); // current lags by phi
        const Is = (Zmag>1e-9) ? (Vs/Zmag) : 0;
        const Ip = Is*n; // ideal current ratio
        const pf = Math.cos(phi);
        const P = Vs*Is*pf;
        const S = Vs*Is;
        const Q = Vs*Is*Math.sin(phi);

        root.querySelector("#{module_id}-ro-s").textContent = "Vs≈"+emlabFmt(Vs,2)+"V, Is≈"+emlabFmt(Is,2)+"A";
        root.querySelector("#{module_id}-ro-p").textContent = emlabFmt(P,2)+" W";
        root.querySelector("#{module_id}-ro-pf").textContent = emlabFmt(pf,3);
        root.querySelector("#{module_id}-ro-phi").textContent = emlabFmt(phi*180/Math.PI,1) + "°";
        root.querySelector("#{module_id}-ro-S").textContent = emlabFmt(S,2) + " VA";
        root.querySelector("#{module_id}-ro-Q").textContent = emlabFmt(Q,2) + " var";

        // waveforms (one period)
        const T = 1/f;
        const N = 600;
        const t = new Array(N);
        const vp = new Array(N);
        const vs = new Array(N);
        const ip = new Array(N);
        const is = new Array(N);
        const VpPk = Math.SQRT2*Vp;
        const VsPk = Math.SQRT2*Vs;
        const IpPk = Math.SQRT2*Ip;
        const IsPk = Math.SQRT2*Is;
        for(let i=0;i<N;i++){{
          const tt = T*i/(N-1);
          t[i] = 1000*tt;
          const a = w*tt;
          vp[i] = VpPk*Math.sin(a);
          vs[i] = VsPk*Math.sin(a);
          is[i] = IsPk*Math.sin(a - phi);
          ip[i] = IpPk*Math.sin(a - phi);
        }}

        Plotly.restyle(figV, {{x:[t,t], y:[vp,vs]}}, [0,1]);
        Plotly.restyle(figI, {{x:[t,t], y:[ip,is]}}, [0,1]);

        // phasor (normalized to unit magnitude)
        const cx = Math.cos(phi);
        const sx = Math.sin(phi);
        Plotly.restyle(figPh, {{
          x:[[0,1], [0,cx], [0,cx]],
          y:[[0,0], [0,-sx], [0,0]]
        }}, [0,1,2]);

        // enable/disable L slider by kind
        els.L.disabled = (kind !== "RL");
      }}

      function reset(){{
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
      els.reset.addEventListener("click", reset);
      update();
    }}
    """

    return {
        "id": module_id,
        "title": "扩展：变压器（互感与匝数比）",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1, fig2],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }
