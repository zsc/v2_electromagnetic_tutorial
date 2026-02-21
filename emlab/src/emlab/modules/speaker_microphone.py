from __future__ import annotations

import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, select, slider


def build() -> dict:
    module_id = "speaker_microphone"

    intro_html = """
    <p>
      动圈扬声器与动圈麦克风体现“互逆性”：
      <ul>
        <li><b>扬声器</b>：线圈电流在磁场中受力 <code>F = B L · I</code>，推动振膜振动。</li>
        <li><b>麦克风</b>：振膜/线圈在磁场中运动，磁通变化产生感应电动势，近似 <code>e ≈ B L · v</code>（v 为速度）。</li>
      </ul>
      电路观点：电流由驱动电压与线圈阻抗决定；麦克风输出电压与负载电阻相关。
    </p>
    <p>本页用“电-机”简化模型展示：机械共振、相位与输出幅值随频率变化。</p>
    """

    controls_html = "\n".join(
        [
            select(
                cid=f"{module_id}-mode",
                label="模式",
                value="spk",
                options=[("spk", "扬声器：电压驱动→位移"), ("mic", "麦克风：外力驱动→感应电压")],
            ),
            slider(
                cid=f"{module_id}-f",
                label="频率 f (Hz)",
                vmin=20,
                vmax=2000,
                step=5,
                value=200,
                unit=" Hz",
            ),
            slider(
                cid=f"{module_id}-BL",
                label="力因子 BL (N/A)（亦是 V·s/m）",
                vmin=1.0,
                vmax=15.0,
                step=0.1,
                value=7.0,
                unit="",
                help_text="同一个 BL 同时决定：扬声器受力 F=BL·I 与麦克风感应 e≈BL·v。",
            ),
            f'<div id="{module_id}-group-spk">',
            slider(cid=f"{module_id}-Vin", label="驱动电压幅值 V_in (V, peak)", vmin=0.0, vmax=20.0, step=0.2, value=6.0, unit=" V"),
            slider(cid=f"{module_id}-Rcoil", label="线圈电阻 R_coil (Ω)", vmin=1.0, vmax=20.0, step=0.2, value=6.0, unit=" Ω"),
            slider(
                cid=f"{module_id}-Lcoil",
                label="线圈电感 L_coil (mH)",
                vmin=0.0,
                vmax=10.0,
                step=0.1,
                value=1.5,
                unit=" mH",
                help_text="电感使电流相位滞后（交流电路观点）。",
            ),
            "</div>",
            f'<div id="{module_id}-group-mic" style="display:none">',
            slider(
                cid=f"{module_id}-Fext",
                label="外界等效力幅值 F_ext (N, peak)",
                vmin=0.0,
                vmax=2.0,
                step=0.02,
                value=0.3,
                unit=" N",
                help_text="把“声压驱动”简化为对振膜的等效正弦外力。",
            ),
            slider(cid=f"{module_id}-Rload", label="负载电阻 R_load (Ω)", vmin=1.0, vmax=500.0, step=1.0, value=50.0, unit=" Ω"),
            "</div>",
            "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.12);margin:12px 0'>",
            slider(cid=f"{module_id}-m", label="振动质量 m (g)", vmin=1.0, vmax=60.0, step=1.0, value=12.0, unit=" g"),
            slider(cid=f"{module_id}-k", label="弹性系数 k (N/m)", vmin=10.0, vmax=2000.0, step=10.0, value=400.0, unit=" N/m"),
            slider(cid=f"{module_id}-b", label="阻尼 b (N·s/m)", vmin=0.0, vmax=2.0, step=0.02, value=0.25, unit=""),
            buttons([(f"{module_id}-reset", "重置参数", "primary")]),
        ]
    )

    fig0 = go.Figure(
        data=[
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="电信号", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="机械位移 x(t)", line=dict(color="#a6e22e", width=2), yaxis="y2"),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="时间波形（两周期）：电 ↔ 机",
            xaxis_title="t (ms)",
            yaxis_title="V 或 I（归一）",
            yaxis2=dict(title="x (mm)", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    fig1 = go.Figure(
        data=[
            go.Scatter(x=[20, 2000], y=[1, 2], mode="lines", name="幅频响应", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[200], y=[1.5], mode="markers", name="当前 f", marker=dict(size=10, color="#ff6b6b")),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="幅频响应（共振）",
            xaxis_title="f (Hz)",
            yaxis_title="输出幅值（mm 或 V）",
            xaxis=dict(type="log"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“扬声器只是电路元件”：它是电-机耦合系统，机械共振会影响电声表现。</li>
      <li>“麦克风输出与频率无关”：振膜/系统有机械共振，输出随频率变化明显。</li>
      <li>“BL 只影响扬声器不影响麦克风”：互逆性表明 BL 同时影响受力与感应电动势。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>引导问题</summary>
      <ol>
        <li><b>预测</b>：把 k 增大（更“硬”），共振频率会升高还是降低？</li>
        <li><b>验证</b>：增大阻尼 b，共振峰会变高还是变矮/变宽？</li>
        <li><b>解释</b>：为什么扬声器的电流相位会因 L_coil 而滞后？这会如何影响力 F(t)=BL·I(t)？</li>
      </ol>
    </details>
    """

    data_payload = {
        "defaults": {
            "mode": "spk",
            "f": 200,
            "BL": 7.0,
            "Vin": 6.0,
            "Rcoil": 6.0,
            "Lcoil": 1.5,
            "Fext": 0.3,
            "Rload": 50.0,
            "m": 12.0,
            "k": 400.0,
            "b": 0.25,
        }
    }

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);
      const els = {{
        mode: root.querySelector("#{module_id}-mode"),
        f: root.querySelector("#{module_id}-f"),
        BL: root.querySelector("#{module_id}-BL"),
        Vin: root.querySelector("#{module_id}-Vin"),
        Rcoil: root.querySelector("#{module_id}-Rcoil"),
        Lcoil: root.querySelector("#{module_id}-Lcoil"),
        Fext: root.querySelector("#{module_id}-Fext"),
        Rload: root.querySelector("#{module_id}-Rload"),
        m: root.querySelector("#{module_id}-m"),
        k: root.querySelector("#{module_id}-k"),
        b: root.querySelector("#{module_id}-b"),
        reset: root.querySelector("#{module_id}-reset"),
      }};

      const gSpk = root.querySelector("#{module_id}-group-spk");
      const gMic = root.querySelector("#{module_id}-group-mic");

      emlabBindValue(root, "{module_id}-f", " Hz", 0);
      emlabBindValue(root, "{module_id}-BL", "", 2);
      emlabBindValue(root, "{module_id}-Vin", " V", 2);
      emlabBindValue(root, "{module_id}-Rcoil", " Ω", 1);
      emlabBindValue(root, "{module_id}-Lcoil", " mH", 2);
      emlabBindValue(root, "{module_id}-Fext", " N", 2);
      emlabBindValue(root, "{module_id}-Rload", " Ω", 0);
      emlabBindValue(root, "{module_id}-m", " g", 0);
      emlabBindValue(root, "{module_id}-k", " N/m", 0);
      emlabBindValue(root, "{module_id}-b", "", 2);

      const figT = document.getElementById("fig-{module_id}-0");
      const figFR = document.getElementById("fig-{module_id}-1");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"共振频率 f0", id:"{module_id}-ro-f0", value:"—"}},
        {{key:"输出幅值", id:"{module_id}-ro-out", value:"—"}},
        {{key:"相位/功率（定性）", id:"{module_id}-ro-ph", value:"—"}},
      ]);

      function showMode(mode){{
        gSpk.style.display = (mode === "spk") ? "" : "none";
        gMic.style.display = (mode === "mic") ? "" : "none";
      }}

      // complex helpers (phasors)
      function c(re, im){{ return {{re:re, im:im}}; }}
      function cadd(a,b){{ return c(a.re+b.re, a.im+b.im); }}
      function csub(a,b){{ return c(a.re-b.re, a.im-b.im); }}
      function cmul(a,b){{ return c(a.re*b.re - a.im*b.im, a.re*b.im + a.im*b.re); }}
      function cdiv(a,b){{ const d=b.re*b.re+b.im*b.im; return c((a.re*b.re+a.im*b.im)/d, (a.im*b.re-a.re*b.im)/d); }}
      function cabs(a){{ return Math.hypot(a.re, a.im); }}
      function carg(a){{ return Math.atan2(a.im, a.re); }}

      function update(){{
        const mode = els.mode.value;
        showMode(mode);
        const f = Math.max(1e-6, emlabNum(els.f.value));
        const w = 2*Math.PI*f;
        const BL = Math.max(0, emlabNum(els.BL.value));

        const m = 1e-3*Math.max(1e-6, emlabNum(els.m.value)); // kg
        const k = Math.max(1e-6, emlabNum(els.k.value)); // N/m
        const b = Math.max(0, emlabNum(els.b.value)); // N*s/m

        const f0 = (1/(2*Math.PI))*Math.sqrt(k/m);
        root.querySelector("#{module_id}-ro-f0").textContent = emlabFmt(f0, 1) + " Hz";

        // mechanical impedance Zm = k - m w^2 + j b w
        const Zm = c(k - m*w*w, b*w);

        let elecSignal = [];
        let mechXmm = [];
        let outAmpText = "";
        let phaseText = "";

        // choose drive
        let X = c(0,0); // displacement phasor (m, peak)
        let markerY = 0;
        let drivePh = 0;
        if(mode === "spk"){{
          const Vin = Math.max(0, emlabNum(els.Vin.value)); // V peak
          const R = Math.max(0.1, emlabNum(els.Rcoil.value));
          const Lc = 1e-3*Math.max(0, emlabNum(els.Lcoil.value));
          const Zc = c(R, w*Lc);
          const I = cdiv(c(Vin,0), Zc); // coil current phasor (A peak)
          const F = cmul(c(BL,0), I);   // force phasor (N peak)
          X = cdiv(F, Zm);
          drivePh = carg(I); // current phase vs voltage
          outAmpText = "|x|≈"+emlabFmt(1000*cabs(X),3)+" mm";
          markerY = 1000*cabs(X);
          phaseText = "I 相位滞后≈"+emlabFmt(-drivePh*180/Math.PI,1)+"°（由 L_coil 引入）";

          // time series: show normalized voltage/current (scaled) and x(t)
          const N = 600;
          const T = 2/f;
          const t = new Array(N);
          const s1 = new Array(N);
          const x = new Array(N);
          for(let i=0;i<N;i++){{
            const tt = T*i/(N-1);
            t[i] = 1000*tt;
            s1[i] = Vin*Math.sin(w*tt); // voltage (for display)
            x[i] = 1000*(X.re*Math.cos(w*tt) - X.im*Math.sin(w*tt)); // mm
          }}
          elecSignal = {{x:t, y:s1}};
          mechXmm = {{x:t, y:x}};
        }} else {{
          const Fext = Math.max(0, emlabNum(els.Fext.value)); // N peak
          const Rload = Math.max(0.1, emlabNum(els.Rload.value));
          const F = c(Fext, 0);
          X = cdiv(F, Zm);
          const Vemf = cmul(c(0, BL*w), X); // e = BL * v = BL * j w X
          const Vout = Vemf; // ignore loading for simplicity
          const P = (cabs(Vout)*cabs(Vout)) / (2*Rload);
          outAmpText = "|e|≈"+emlabFmt(cabs(Vout),3)+" V, P≈"+emlabFmt(P,3)+" W";
          markerY = cabs(Vout);
          phaseText = "e 与 v 同相（e≈BL·v）";

          const N = 600;
          const T = 2/f;
          const t = new Array(N);
          const s1 = new Array(N);
          const x = new Array(N);
          for(let i=0;i<N;i++){{
            const tt = T*i/(N-1);
            t[i] = 1000*tt;
            s1[i] = (Vout.re*Math.cos(w*tt) - Vout.im*Math.sin(w*tt)); // V
            x[i] = 1000*(X.re*Math.cos(w*tt) - X.im*Math.sin(w*tt));
          }}
          elecSignal = {{x:t, y:s1}};
          mechXmm = {{x:t, y:x}};
        }}

        root.querySelector("#{module_id}-ro-out").textContent = outAmpText;
        root.querySelector("#{module_id}-ro-ph").textContent = phaseText;

        // update time plot
        Plotly.restyle(figT, {{x:[elecSignal.x, mechXmm.x], y:[elecSignal.y, mechXmm.y]}}, [0,1]);

        // frequency response (log axis)
        const fmin = 20, fmax = 2000;
        const Nf = 260;
        const fs = new Array(Nf);
        const out = new Array(Nf);
        for(let i=0;i<Nf;i++){{
          const ff = fmin*Math.pow(fmax/fmin, i/(Nf-1));
          fs[i] = ff;
          const ww = 2*Math.PI*ff;
          const Zm2 = c(k - m*ww*ww, b*ww);
          if(mode === "spk"){{
            const Vin = Math.max(0, emlabNum(els.Vin.value));
            const R = Math.max(0.1, emlabNum(els.Rcoil.value));
            const Lc = 1e-3*Math.max(0, emlabNum(els.Lcoil.value));
            const ZcMag = Math.hypot(R, ww*Lc);
            const Iabs = (ZcMag>1e-12) ? (Vin/ZcMag) : 0;
            const F0 = BL*Iabs;
            const Xabs = (cabs(Zm2)>1e-12) ? (F0/cabs(Zm2)) : 0;
            out[i] = 1000*Xabs; // mm (peak)
          }} else {{
            const Fext = Math.max(0, emlabNum(els.Fext.value));
            const Xabs = (cabs(Zm2)>1e-12) ? (Fext/cabs(Zm2)) : 0;
            out[i] = BL*ww*Xabs; // V (peak), e≈BL·v
          }}
        }}
        Plotly.restyle(figFR, {{x:[fs], y:[out]}}, [0]);
        Plotly.restyle(figFR, {{x:[[f]], y:[[markerY]]}}, [1]);

        // enable/disable groups
        els.Vin.disabled = (mode !== "spk");
        els.Rcoil.disabled = (mode !== "spk");
        els.Lcoil.disabled = (mode !== "spk");
        els.Fext.disabled = (mode !== "mic");
        els.Rload.disabled = (mode !== "mic");
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
        "title": "扩展：扬声器/麦克风互逆（BL·I 与 BL·v）",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }
