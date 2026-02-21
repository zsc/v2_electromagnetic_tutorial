from __future__ import annotations

import math

import numpy as np
import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, select, slider


def _rlc_normalized_waveforms(
    *,
    t: np.ndarray,
    R: float,
    L: float,
    C: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Normalized series RLC discharge waveforms for V0=1:
    - i_n(t): current (A per V)
    - q_n(t): cumulative charge transferred = ∫i dt (C per V)
    - j1_n(t): cumulative ∫ i^2 dt (A^2*s per V^2)
    - j2_n(t): cumulative ∫ (∫ i^2 dt) dt  (A^2*s^2 per V^2)
    """
    alpha = R / (2.0 * L)
    w0 = 1.0 / math.sqrt(L * C)

    # capacitor voltage normalized: vc(0)=1, dvc/dt(0)=0
    vc = np.zeros_like(t, dtype=float)
    if alpha < w0 * (1 - 1e-6):
        wd = math.sqrt(w0 * w0 - alpha * alpha)
        vc = np.exp(-alpha * t) * (np.cos(wd * t) + (alpha / wd) * np.sin(wd * t))
        i = (1.0 / (L * wd)) * np.exp(-alpha * t) * np.sin(wd * t)
    elif abs(alpha - w0) / w0 <= 1e-6:
        # critical
        vc = np.exp(-alpha * t) * (1.0 + alpha * t)
        i = (t / L) * np.exp(-alpha * t)
    else:
        # over-damped
        beta = math.sqrt(alpha * alpha - w0 * w0)
        s1 = -alpha + beta
        s2 = -alpha - beta
        vc = (s2 * np.exp(s1 * t) - s1 * np.exp(s2 * t)) / (s2 - s1)
        i = (1.0 / L) * (np.exp(s1 * t) - np.exp(s2 * t)) / (s1 - s2)

    # cumulative charge transferred: q = C*(1 - vc)  (for V0=1)
    q = C * (1.0 - vc)

    # integrals for force/kinematics
    dt = float(t[1] - t[0])
    i2 = i * i
    j1 = np.zeros_like(t, dtype=float)
    j2 = np.zeros_like(t, dtype=float)
    for k in range(1, len(t)):
        j1[k] = j1[k - 1] + 0.5 * (i2[k - 1] + i2[k]) * dt
        j2[k] = j2[k - 1] + 0.5 * (j1[k - 1] + j1[k]) * dt
    return i.astype(float), q.astype(float), j1.astype(float), j2.astype(float)


def build() -> dict:
    module_id = "rail_launcher"

    intro_html = """
    <p style="border-left:3px solid rgba(255,107,107,0.55);padding-left:10px">
      <b>安全边界：</b>本模块仅用于课堂讨论的<b>理想化物理与电路仿真</b>（RLC 放电波形 + 能量观点 + I² 力近似）。
      不提供任何现实可执行的制造、材料选型、加工、装配或危险操作指导。
    </p>
    <p>
      理想化模型：
      电容初能量 <code>E0=½CV0²</code>；
      放电电流由串联 RLC 决定；
      采用能量法的常见近似 <code>F ≈ ½·L'·I²</code>（L' 为“电感梯度”参数，仅作为给定常数）。
      通过积分可以得到速度/位移，并用能量条展示“电容能 → 动能/热/剩余”。
    </p>
    """

    # precompute (normalized V0=1) on a (R,C) grid for multiple L options
    t_max = 0.020  # 20 ms
    n_t = 520
    t = np.linspace(0.0, t_max, n_t)

    L_opts = [10e-6, 30e-6, 60e-6]  # H
    R_grid = np.linspace(2e-3, 30e-3, 12)  # ohm
    C_grid = np.linspace(0.5e-3, 5.0e-3, 12)  # F

    wave_L: list[dict] = []
    for L in L_opts:
        I_grid = []
        Q_grid = []
        J1_grid = []
        J2_grid = []
        for R in R_grid:
            I_row = []
            Q_row = []
            J1_row = []
            J2_row = []
            for C in C_grid:
                i_n, q_n, j1_n, j2_n = _rlc_normalized_waveforms(t=t, R=float(R), L=float(L), C=float(C))
                I_row.append(i_n.tolist())
                Q_row.append(q_n.tolist())
                J1_row.append(j1_n.tolist())
                J2_row.append(j2_n.tolist())
            I_grid.append(I_row)
            Q_grid.append(Q_row)
            J1_grid.append(J1_row)
            J2_grid.append(J2_row)
        wave_L.append({"I": I_grid, "Q": Q_grid, "J1": J1_grid, "J2": J2_grid})

    controls_html = "\n".join(
        [
            slider(
                cid=f"{module_id}-V0",
                label="初始电压 V0 (V)",
                vmin=500,
                vmax=5000,
                step=50,
                value=2000,
                unit=" V",
            ),
            slider(
                cid=f"{module_id}-R_mOhm",
                label="回路电阻 R (mΩ)",
                vmin=2,
                vmax=30,
                step=0.5,
                value=8,
                unit=" mΩ",
                help_text="R 越大，峰值电流降低，能量更多变成焦耳热，动能更少（定性）。",
            ),
            slider(
                cid=f"{module_id}-C_mF",
                label="电容 C (mF)",
                vmin=0.5,
                vmax=5.0,
                step=0.05,
                value=2.0,
                unit=" mF",
            ),
            select(
                cid=f"{module_id}-L_uH",
                label="电感 L (µH)",
                value="30",
                options=[("10", "10"), ("30", "30"), ("60", "60")],
                help_text="这里把 L 作为离散选项，以便用预计算网格保证离线交互性能。",
            ),
            slider(
                cid=f"{module_id}-Lprime_uHpm",
                label="电感梯度 L' (µH/m)",
                vmin=0.2,
                vmax=5.0,
                step=0.05,
                value=1.2,
                unit=" µH/m",
                help_text="L' 仅作为给定参数，不讨论结构来源；F≈½·L'·I²。",
            ),
            slider(
                cid=f"{module_id}-m",
                label="质量 m (kg)",
                vmin=0.02,
                vmax=0.50,
                step=0.01,
                value=0.10,
                unit=" kg",
            ),
            slider(
                cid=f"{module_id}-mu",
                label="摩擦系数 μ（可选）",
                vmin=0.0,
                vmax=0.30,
                step=0.01,
                value=0.05,
                unit="",
            ),
            slider(
                cid=f"{module_id}-len",
                label="轨道长度 (m)",
                vmin=0.2,
                vmax=2.0,
                step=0.05,
                value=0.8,
                unit=" m",
            ),
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
            title="RLC 放电：电流 I(t) 与电容电压 Vc(t)",
            xaxis_title="t (ms)",
            yaxis_title="I (kA)",
            yaxis2=dict(title="Vc (kV)", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    fig1 = go.Figure(
        data=[
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="x(t)", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="v(t)", line=dict(color="#a6e22e", width=2), yaxis="y2"),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="运动学：位移 x(t) 与速度 v(t)（理想化）",
            xaxis_title="t (ms)",
            yaxis_title="x (m)",
            yaxis2=dict(title="v (m/s)", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    fig2 = go.Figure(
        data=[
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="E_C", stackgroup="one", line=dict(width=0.5), fillcolor="rgba(102,217,239,0.35)"),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="E_L", stackgroup="one", line=dict(width=0.5), fillcolor="rgba(166,226,46,0.35)"),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="E_R(热)", stackgroup="one", line=dict(width=0.5), fillcolor="rgba(255,107,107,0.35)"),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="E_K(动能)", stackgroup="one", line=dict(width=0.5), fillcolor="rgba(255,255,255,0.25)"),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="摩擦损失", stackgroup="one", line=dict(width=0.5), fillcolor="rgba(255,255,255,0.12)"),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="能量条（随时间累加，理想化）",
            xaxis_title="t (ms)",
            yaxis_title="能量 (J)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“峰值电流越大末速度一定越大”：不对。末速度取决于<strong>能量转化</strong>，与波形、R 损耗、摩擦等有关。</li>
      <li>“电磁力凭空产生能量”：不对。能量主要来自电容初始能量 <code>½CV0²</code>，并在电路/运动之间分配。</li>
      <li>“只要提高 V0 就无限提升”：理想模型里 v 随 V0² 增长很快，但真实系统会受到击穿、发热、结构强度等限制（此处不展开工程细节）。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>引导问题</summary>
      <ol>
        <li><b>预测</b>：把 V0 加倍，I(t) 的峰值会怎样变化？x(t)、v(t) 的量级变化更像“×2”还是“×4”？</li>
        <li><b>验证</b>：固定 C、L，分别把 R 调大/调小，比较能量条中“热”与“动能”的占比。</li>
        <li><b>解释</b>：为什么 I(t) 是一个先上升后衰减（甚至振荡）的波形？用 RLC 的能量交换解释。</li>
        <li><b>拓展</b>：如果轨道长度有限，为什么“更大的峰值电流”不一定转化为更大的出口速度？</li>
      </ol>
    </details>
    """

    data_payload = {
        "t": t.astype(float).tolist(),
        "t_max": t_max,
        "R_grid": R_grid.astype(float).tolist(),
        "C_grid": C_grid.astype(float).tolist(),
        "L_opts_uH": [int(round(v * 1e6)) for v in L_opts],
        "wave": wave_L,
        "defaults": {
            "V0": 2000,
            "R_mOhm": 8,
            "C_mF": 2.0,
            "L_uH": "30",
            "Lprime_uHpm": 1.2,
            "m": 0.10,
            "mu": 0.05,
            "len": 0.8,
        },
    }

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);

      const els = {{
        V0: root.querySelector("#{module_id}-V0"),
        Rm: root.querySelector("#{module_id}-R_mOhm"),
        Cm: root.querySelector("#{module_id}-C_mF"),
        Lu: root.querySelector("#{module_id}-L_uH"),
        Lp: root.querySelector("#{module_id}-Lprime_uHpm"),
        m: root.querySelector("#{module_id}-m"),
        mu: root.querySelector("#{module_id}-mu"),
        len: root.querySelector("#{module_id}-len"),
        reset: root.querySelector("#{module_id}-reset"),
      }};

      emlabBindValue(root, "{module_id}-V0", " V", 0);
      emlabBindValue(root, "{module_id}-R_mOhm", " mΩ", 1);
      emlabBindValue(root, "{module_id}-C_mF", " mF", 2);
      emlabBindValue(root, "{module_id}-Lprime_uHpm", " µH/m", 2);
      emlabBindValue(root, "{module_id}-m", " kg", 2);
      emlabBindValue(root, "{module_id}-mu", "", 2);
      emlabBindValue(root, "{module_id}-len", " m", 2);

      const figI = document.getElementById("fig-{module_id}-0");
      const figXV = document.getElementById("fig-{module_id}-1");
      const figE = document.getElementById("fig-{module_id}-2");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"峰值电流 I_peak", id:"{module_id}-ro-Ipk", value:"—"}},
        {{key:"出口速度 v_exit", id:"{module_id}-ro-v", value:"—"}},
        {{key:"能量分配（末端）", id:"{module_id}-ro-eff", value:"—"}},
      ]);

      const g = 9.80665;

      function pickLIndex(LuH){{
        const Ls = data.L_opts_uH || [];
        const idx = Ls.indexOf(parseInt(LuH,10));
        return Math.max(0, idx);
      }}

      function scale1d(arr, s){{
        const out = new Array(arr.length);
        for(let i=0;i<arr.length;i++) out[i] = arr[i]*s;
        return out;
      }}

      function update(){{
        const V0 = emlabNum(els.V0.value);
        const R = 1e-3 * emlabNum(els.Rm.value);
        const C = 1e-3 * emlabNum(els.Cm.value);
        const L_uH = els.Lu.value;
        const Lidx = pickLIndex(L_uH);
        const L = (parseInt(L_uH,10))*1e-6;
        const Lp = 1e-6 * emlabNum(els.Lp.value); // H/m
        const m = Math.max(1e-6, emlabNum(els.m.value));
        const mu = Math.max(0, emlabNum(els.mu.value));
        const xMax = Math.max(0.05, emlabNum(els.len.value));

        // interpolate normalized series from grid (R,C are continuous)
        const wave = (data.wave && data.wave[Lidx]) ? data.wave[Lidx] : null;
        const Rg = data.R_grid || [];
        const Cg = data.C_grid || [];
        if(!wave) return;

        const In = emlabBilinearSeries(wave.I, Rg, Cg, R, C);
        const Qn = emlabBilinearSeries(wave.Q, Rg, Cg, R, C);
        const J1n = emlabBilinearSeries(wave.J1, Rg, Cg, R, C);
        const J2n = emlabBilinearSeries(wave.J2, Rg, Cg, R, C);

        const t = data.t || [];
        const N = t.length;
        if(N < 2) return;
        const dt = t[1]-t[0];

        // scale to actual V0 (linear system)
        const I = scale1d(In, V0);
        const Q = scale1d(Qn, V0);

        // capacitor voltage
        const Vc = new Array(N);
        for(let i=0;i<N;i++){{
          Vc[i] = V0 - Q[i]/Math.max(1e-12, C);
        }}

        // kinematics from I^2 integrals (with simple friction clamp)
        const v = new Array(N);
        const x = new Array(N);
        v[0]=0; x[0]=0;
        const aFac = 0.5*Lp/m;
        for(let i=1;i<N;i++){{
          // raw v from cumulative I^2 integral
          const vraw = aFac*(V0*V0*J1n[i]) - mu*g*t[i];
          v[i] = Math.max(0, vraw);
          x[i] = x[i-1] + 0.5*(v[i-1]+v[i])*dt;
          if(x[i] >= xMax){{
            x[i] = xMax;
            // freeze after exit
            for(let k=i+1;k<N;k++){{ x[k]=xMax; v[k]=v[i]; }}
            break;
          }}
        }}

        // energy components
        const E0 = 0.5*C*V0*V0;
        const Ec = new Array(N);
        const El = new Array(N);
        const Er = new Array(N);
        const Ek = new Array(N);
        const Ef = new Array(N);
        for(let i=0;i<N;i++){{
          Ec[i] = 0.5*C*Vc[i]*Vc[i];
          El[i] = 0.5*L*I[i]*I[i];
          Er[i] = R*(V0*V0*J1n[i]);
          Ek[i] = 0.5*m*v[i]*v[i];
          Ef[i] = mu*m*g*x[i];
        }}

        // update plots
        const tms = t.map(tt => 1000*tt);
        Plotly.restyle(figI, {{
          x:[tms, tms],
          y:[I.map(ii=>ii/1000.0), Vc.map(vv=>vv/1000.0)]
        }}, [0,1]);

        Plotly.restyle(figXV, {{
          x:[tms, tms],
          y:[x, v]
        }}, [0,1]);

        Plotly.restyle(figE, {{
          x:[tms,tms,tms,tms,tms],
          y:[Ec, El, Er, Ek, Ef]
        }}, [0,1,2,3,4]);

        // readouts at end (exit if reached)
        const Ipk = Math.max(...I.map(vv=>Math.abs(vv)));
        const vExit = v[v.length-1];
        const EkEnd = Ek[Ek.length-1];
        const ErEnd = Er[Er.length-1] + Ef[Ef.length-1];
        const fracK = (E0>1e-9) ? (EkEnd/E0) : 0;
        root.querySelector("#{module_id}-ro-Ipk").textContent = emlabFmt(Ipk/1000.0, 2) + " kA";
        root.querySelector("#{module_id}-ro-v").textContent = emlabFmt(vExit, 2) + " m/s";
        root.querySelector("#{module_id}-ro-eff").textContent = "动能 " + emlabFmt(100*fracK,1) + "%，损耗/热 " + emlabFmt(100*ErEnd/Math.max(1e-9,E0),1) + "%";
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
        "title": "M05 理想化导轨：RLC 放电 + I² 力 + 能量条",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1, fig2],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }

