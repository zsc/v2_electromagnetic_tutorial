from __future__ import annotations

import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, select, slider


def build() -> dict:
    module_id = "cyclotron"

    intro_html = """
    <p>
      回旋加速器（cyclotron）的“高中直觉”可以拆成一句话：
      <b>磁场让粒子绕圈，缝隙里的交变电场每半圈给它“再推一把”</b>。
    </p>
    <p>
      <b>(电磁场)</b> 在近似均匀的磁场 B 中，粒子受洛伦兹力做圆周运动，半径与速度满足
      <code>r = mv/(|q|B)</code>。
      非相对论近似下，回旋角频率与半径无关：
      <code>ω_c = |q|B/m</code>，对应频率 <code>f_c = ω_c/(2π)</code>。
      这就是“可以用固定 RF 频率”的关键原因。
    </p>
    <p>
      <b>(电路)</b> 两个 D 形电极之间由 RF 电源提供正弦电压（可理解成“交流高频电源/谐振腔”）：
      当粒子每次穿过缝隙时，如果恰好遇到“加速相位”，就会获得能量增量（符号由相位决定）：
      <code>ΔK ≈ q·V_gap·sin(相位)</code>（教学近似）。
      频率对准且相位合适时，能量会一圈圈累积，轨迹向外扩展成螺旋。
    </p>
    <p>
      <b>失谐</b>（f_rf ≠ f_c）时，粒子到达缝隙的相位会逐渐漂移：有时推、有时拉，平均加速变差甚至抵消，
      你会看到能量增长减慢、相位曲线“跑掉”、轨迹不再平滑外扩。
      <b>相对论开关</b>打开后，能量升高使 <code>γ</code> 增大，等效回旋频率变为 <code>ω_c=|q|B/(γm)</code>，
      即使最初对准也会逐步失谐（经典回旋加速器的限制之一）。
    </p>
    """

    controls_html = "\n".join(
        [
            select(
                cid=f"{module_id}-particle",
                label="粒子类型（正电）",
                value="p",
                options=[("p", "质子 p⁺"), ("alpha", "α 粒子(He²⁺)")],
            ),
            slider(
                cid=f"{module_id}-B",
                label="磁感应强度 B (T)",
                vmin=0.02,
                vmax=0.20,
                step=0.001,
                value=0.10,
                unit=" T",
            ),
            slider(
                cid=f"{module_id}-Vgap",
                label="缝隙电压幅值 V_gap (V)",
                vmin=0,
                vmax=800,
                step=10,
                value=200,
                unit=" V",
            ),
            slider(
                cid=f"{module_id}-frf",
                label="RF 频率 f_rf (MHz)",
                vmin=0.2,
                vmax=3.0,
                step=0.01,
                value=1.52,
                unit=" MHz",
                help_text="把 f_rf 调到接近理论 f_c，观察轨迹与能量的差异。",
            ),
            select(
                cid=f"{module_id}-rel",
                label="相对论开关（选做）",
                value="off",
                options=[("off", "关闭：ωc=|q|B/m"), ("on", "开启：ωc=|q|B/(γm)")],
                help_text="开启后，能量升高会使 γ 增大，回旋频率下降，产生失谐。",
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
        data=[go.Scatter(x=[0], y=[0], mode="lines", line=dict(color="#66d9ef", width=2), name="轨迹")],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=50, r=20, t=40, b=45),
            title="轨迹（螺旋外扩 / 失谐时变差）",
            xaxis_title="x (m)",
            yaxis_title="y (m)",
            xaxis=dict(scaleanchor="y", scaleratio=1, showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
            showlegend=False,
        ),
    )

    fig1 = go.Figure(
        data=[
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="K (keV)", line=dict(color="#a6e22e", width=2)),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="相位(π)", line=dict(color="#ff6b6b", width=1.5), yaxis="y2"),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="能量增长与相位（共振/失谐对比）",
            xaxis_title="半周次数 n",
            yaxis_title="K (keV)",
            yaxis2=dict(title="相位/π", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“频率越高越好”：不对。必须与回旋频率匹配；失谐会导致加速相位跑偏甚至减速。</li>
      <li>“B 只决定半径不影响共振”：B 同时决定回旋频率 <code>ω_c=|q|B/m</code>。</li>
      <li>“永远不需要考虑相对论”：能量高时 γ 增大，频率下降，经典回旋加速器会失谐。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>引导问题</summary>
      <ol>
        <li><b>预测</b>：把 B 增大，理论 f_c 会如何变化？轨迹半径在同样能量下如何变化？</li>
        <li><b>验证</b>：把 f_rf 调到略高/略低于 f_c，能量曲线会发生什么？相位会漂移吗？</li>
        <li><b>拓展</b>：打开相对论开关后，为什么在能量更高时更容易失谐？</li>
      </ol>
    </details>
    """

    data_payload = {
        "defaults": {"particle": "p", "B": 0.10, "Vgap": 200, "frf": 1.52, "rel": "off"}
    }

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);
      const els = {{
        particle: root.querySelector("#{module_id}-particle"),
        B: root.querySelector("#{module_id}-B"),
        Vgap: root.querySelector("#{module_id}-Vgap"),
        frf: root.querySelector("#{module_id}-frf"),
        rel: root.querySelector("#{module_id}-rel"),
        play: root.querySelector("#{module_id}-play"),
        reset: root.querySelector("#{module_id}-reset"),
      }};

      emlabBindValue(root, "{module_id}-B", " T", 3);
      emlabBindValue(root, "{module_id}-Vgap", " V", 0);
      emlabBindValue(root, "{module_id}-frf", " MHz", 2);

      const figTraj = document.getElementById("fig-{module_id}-0");
      const figK = document.getElementById("fig-{module_id}-1");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"理论回旋频率 f_c", id:"{module_id}-ro-fc", value:"—"}},
        {{key:"失谐 Δf = f_rf - f_c", id:"{module_id}-ro-df", value:"—"}},
        {{key:"末能量 K_end", id:"{module_id}-ro-K", value:"—"}},
      ]);

      const e = 1.602176634e-19;
      const mp = 1.67262192369e-27;
      const c = 299792458;

      function particleQM(kind){{
        if(kind === "alpha") return {{q: 2*e, m: 4*mp}};
        return {{q: 1*e, m: 1*mp}};
      }}

      let timer = null;
      let dir = 1;
      function stopPlay(){{ if(timer){{ clearInterval(timer); timer=null; }} }}
      function tick(){{
        const el = els.frf;
        if(!el) return;
        const vmin = emlabNum(el.min);
        const vmax = emlabNum(el.max);
        const step = Math.max(1e-12, emlabNum(el.step || 1));
        let v = emlabNum(el.value);
        v += dir*step*3;
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
        }}, 170);
      }}

      function simulate(q, m, B, Vgap, frf, relOn){{
        const wRF = 2*Math.PI*frf;
        const nSteps = 140; // half-turns
        let t = 0;
        let K = 0; // J
        let theta = 0;
        const xs = [];
        const ys = [];
        const ks = [];
        const phs = [];

        function gammaFromK(K){{
          return 1 + K/(m*c*c);
        }}
        for(let n=0;n<nSteps;n++) {{
          const gam = relOn ? gammaFromK(K) : 1.0;
          const wC = Math.abs(q)*B/(gam*m);
          const dtHalf = Math.PI/Math.max(1e-9, wC);
          const phase = wRF*t;
          const dK = q*Vgap*Math.sin(phase);
          K = Math.max(0, K + dK);

          // kinematics
          const gam2 = relOn ? gammaFromK(K) : 1.0;
          const v = relOn ? (c*Math.sqrt(1 - 1/(gam2*gam2))) : Math.sqrt(Math.max(0, 2*K/m));
          const r = (gam2*m*v)/(Math.abs(q)*Math.max(1e-9,B));

          // add arc points for this half-turn
          const nSeg = 18;
          for(let i=0;i<=nSeg;i++) {{
            const a = theta + Math.PI*i/nSeg;
            xs.push(r*Math.cos(a));
            ys.push(r*Math.sin(a));
          }}
          theta += Math.PI;
          t += dtHalf;
          ks.push(K/1e3/e); // keV
          phs.push(((phase%(2*Math.PI))+2*Math.PI)%(2*Math.PI)/Math.PI); // phase/pi in [0,2)
        }}
        return {{xs, ys, ks, phs}};
      }}

      function update(){{
        const part = els.particle.value;
        const B = emlabNum(els.B.value);
        const Vgap = emlabNum(els.Vgap.value);
        const frfMHz = emlabNum(els.frf.value);
        const frf = frfMHz*1e6;
        const relOn = (els.rel.value === "on");

        const qm = particleQM(part);
        const fc = Math.abs(qm.q)*B/(2*Math.PI*qm.m); // Hz (non-rel)
        root.querySelector("#{module_id}-ro-fc").textContent = emlabFmt(fc/1e6, 3) + " MHz";
        root.querySelector("#{module_id}-ro-df").textContent = emlabFmt((frf-fc)/1e6, 3) + " MHz";

        const sim = simulate(qm.q, qm.m, B, Vgap, frf, relOn);
        Plotly.restyle(figTraj, {{x:[sim.xs], y:[sim.ys]}}, [0]);

        const n = sim.ks.length;
        const idx = Array.from({{length:n}}, (_,i)=>i);
        Plotly.restyle(figK, {{x:[idx, idx], y:[sim.ks, sim.phs]}}, [0,1]);

        const Kend = sim.ks[n-1];
        root.querySelector("#{module_id}-ro-K").textContent = emlabFmt(Kend, 2) + " keV";
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
        "title": "M08 回旋加速器：共振与失谐",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }
