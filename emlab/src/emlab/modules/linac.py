from __future__ import annotations

import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, select, slider


def build() -> dict:
    module_id = "linac"

    intro_html = """
    <p>
      直线加速器（Linac）的核心直觉：RF 腔隙中有<strong>纵向电场</strong>可以加速；
      漂移管内近似无场（屏蔽），粒子在其中“等待”RF 翻转到合适相位后再进入下一个加速缝隙。
      因此必须考虑<strong>相位同步</strong>与<strong>漂移管长度</strong>随速度增加而变长。
    </p>
    <p>
      本页面用“离散加速缝隙 + 漂移段”的教学模型展示：同步设计 vs 固定长度导致的相位漂移与能量增长差异。
    </p>
    """

    controls_html = "\n".join(
        [
            slider(
                cid=f"{module_id}-f",
                label="RF 频率 f (MHz)",
                vmin=1,
                vmax=200,
                step=1,
                value=50,
                unit=" MHz",
            ),
            slider(
                cid=f"{module_id}-E0",
                label="加速梯度 E0 (MV/m)",
                vmin=0.0,
                vmax=5.0,
                step=0.05,
                value=1.5,
                unit=" MV/m",
                help_text="用 V_gap ≈ E0·g 表示每个缝隙的等效加速电压（g 为固定缝隙长度）。",
            ),
            slider(
                cid=f"{module_id}-K0",
                label="注入能量 K0 (keV)",
                vmin=1,
                vmax=200,
                step=1,
                value=20,
                unit=" keV",
            ),
            slider(
                cid=f"{module_id}-phi",
                label="同步相位 φ (deg)",
                vmin=-90,
                vmax=90,
                step=1,
                value=0,
                unit="°",
                help_text="相位为 0° 时加速最大；接近 ±90° 时加速趋近 0；超过 90° 会减速（此处仅示意）。",
            ),
            select(
                cid=f"{module_id}-design",
                label="漂移管长度设计",
                value="sync",
                options=[("sync", "同步设计：每段≈v·T/2"), ("fixed", "固定长度：易相位漂移")],
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
        data=[go.Scatter(x=[1, 2, 3], y=[0.02, 0.03, 0.05], mode="lines+markers", line=dict(color="#66d9ef", width=2))],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="漂移管长度随速度增长（示意）",
            xaxis_title="级数 n",
            yaxis_title="漂移管长度 L_n (m)",
        ),
    )

    fig1 = go.Figure(
        data=[
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines+markers", name="K (keV)", line=dict(color="#a6e22e", width=2)),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines+markers", name="到达相位/π", line=dict(color="#ff6b6b", width=1.5), yaxis="y2"),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="能量增长与相位同步（示意）",
            xaxis_title="缝隙编号 n",
            yaxis_title="K (keV)",
            yaxis2=dict(title="相位/π", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“只要一直加电场就能一直加速”：不对。RF 电场会随时间反向，必须在合适相位穿过缝隙。</li>
      <li>“漂移管长度无所谓”：不对。速度变大后，若漂移段不变长，会出现相位漂移，甚至在错误相位被减速。</li>
      <li>“相位=0° 永远最佳”：相位选择还涉及束团稳定性等更深入内容（此处不展开）。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>引导问题</summary>
      <ol>
        <li><b>预测</b>：把 f 提高（周期变短），漂移管长度会变长还是变短？为什么？</li>
        <li><b>验证</b>：切换到“固定长度”，观察到达相位是否漂移？能量增长是否变差？</li>
        <li><b>解释</b>：用“漂移时间≈T/2”解释为什么漂移管长度需要随速度增长。</li>
      </ol>
    </details>
    """

    data_payload = {
        "defaults": {"f": 50, "E0": 1.5, "K0": 20, "phi": 0, "design": "sync"},
        "n_stage": 14,
        "gap_m": 0.01,
    }

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);

      const els = {{
        f: root.querySelector("#{module_id}-f"),
        E0: root.querySelector("#{module_id}-E0"),
        K0: root.querySelector("#{module_id}-K0"),
        phi: root.querySelector("#{module_id}-phi"),
        design: root.querySelector("#{module_id}-design"),
        play: root.querySelector("#{module_id}-play"),
        reset: root.querySelector("#{module_id}-reset"),
      }};

      emlabBindValue(root, "{module_id}-f", " MHz", 0);
      emlabBindValue(root, "{module_id}-E0", " MV/m", 2);
      emlabBindValue(root, "{module_id}-K0", " keV", 0);
      emlabBindValue(root, "{module_id}-phi", "°", 0);

      const figL = document.getElementById("fig-{module_id}-0");
      const figK = document.getElementById("fig-{module_id}-1");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"末能量 K_end", id:"{module_id}-ro-K", value:"—"}},
        {{key:"末速度 v_end", id:"{module_id}-ro-v", value:"—"}},
        {{key:"相位漂移范围", id:"{module_id}-ro-ph", value:"—"}},
      ]);

      const e = 1.602176634e-19;
      const mp = 1.67262192369e-27;
      const c = 299792458;
      const nStage = data.n_stage || 14;
      const gap = data.gap_m || 0.01;

      let timer = null;
      let dir = 1;
      function stopPlay(){{ if(timer){{ clearInterval(timer); timer=null; }} }}
      function tick(){{
        const el = els.phi;
        if(!el) return;
        const vmin = emlabNum(el.min);
        const vmax = emlabNum(el.max);
        const step = Math.max(1e-12, emlabNum(el.step || 1));
        let v = emlabNum(el.value);
        v += dir*step*2;
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

      function vFromK(KJ){{
        // non-rel for teaching; clamp below c
        const v = Math.sqrt(Math.max(0, 2*KJ/mp));
        return Math.min(0.6*c, v);
      }}

      function update(){{
        const fMHz = emlabNum(els.f.value);
        const f = fMHz*1e6;
        const T = 1/Math.max(1e-9, f);
        const E0 = 1e6*emlabNum(els.E0.value); // V/m
        const Vgap = E0*gap; // V
        const K0 = 1e3*e*emlabNum(els.K0.value); // J
        const phi0 = emlabNum(els.phi.value) * Math.PI/180;
        const design = els.design.value;

        // arrays per gap crossing
        const K = new Array(nStage+1);
        const v = new Array(nStage+1);
        const phase = new Array(nStage+1);
        const Ld = new Array(nStage+1);
        K[0] = K0;
        v[0] = vFromK(K0);
        phase[0] = phi0;
        Ld[0] = v[0]*T/2;

        // choose drift lengths: sync uses v_n, fixed uses v_0
        const Lfixed = v[0]*T/2;
        let t = 0;
        let phMin = 1e9, phMax = -1e9;
        for(let n=1;n<=nStage;n++) {{
          const L = (design === "sync") ? (v[n-1]*T/2) : Lfixed;
          Ld[n] = L;
          // drift time through tube
          const dt = L / Math.max(1e-9, v[n-1]);
          t += dt;
          const ph = (2*Math.PI*f*t + phi0);
          phase[n] = ((ph % (2*Math.PI)) + 2*Math.PI) % (2*Math.PI);
          // energy gain at gap (use cos phase)
          const dK = e*Vgap*Math.cos(phase[n]);
          K[n] = Math.max(0, K[n-1] + dK);
          v[n] = vFromK(K[n]);

          phMin = Math.min(phMin, phase[n]);
          phMax = Math.max(phMax, phase[n]);
        }}

        // plot drift lengths
        const idx = Array.from({{length:nStage}}, (_,i)=>i+1);
        const Lplot = idx.map(i => Ld[i]);
        Plotly.restyle(figL, {{x:[idx], y:[Lplot]}}, [0]);

        // plot K and phase/pi
        const nIdx = Array.from({{length:nStage+1}}, (_,i)=>i);
        const KkeV = K.map(k => k/(1e3*e));
        const phPi = phase.map(p => p/Math.PI);
        Plotly.restyle(figK, {{x:[nIdx, nIdx], y:[KkeV, phPi]}}, [0,1]);

        root.querySelector("#{module_id}-ro-K").textContent = emlabFmt(KkeV[nStage], 2) + " keV";
        root.querySelector("#{module_id}-ro-v").textContent = emlabFmt(v[nStage]/1e6, 3) + "×10⁶ m/s";
        const dph = (phMax>phMin) ? (phMax-phMin) : 0;
        root.querySelector("#{module_id}-ro-ph").textContent = (design==="sync") ? "≈0（同步）" : ("≈"+emlabFmt(dph/Math.PI,2)+"π");
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
        "title": "M09 直线加速器：相位同步与漂移管",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }
