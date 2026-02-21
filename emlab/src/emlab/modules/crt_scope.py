from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, select, slider


def build() -> dict:
    module_id = "crt_scope"

    intro_html = """
    <p>
      <b>CRT</b>（阴极射线管）是“显示器件”；<b>示波器</b>是“测量系统”。老式模拟示波器常用 CRT 显示，
      现代示波器多用 LCD，但测量功能（时基、触发、输入阻抗、采样量化）仍然存在。
    </p>
    <p>
      这个模块用简化模型展示：电子被加速电压 <code>V_acc</code> 加速，进入偏转板后受电场力偏转。
      近似结论：屏上偏转 <code>y ∝ V_def / V_acc</code>（电场偏转灵敏度随加速电压增大而减小）。
    </p>
    """

    # fixed-length noise base so "noise" waveform is stable across updates
    rng = np.random.default_rng(0)
    noise_base = rng.normal(0, 1, size=1400).astype(float)
    noise_base = np.tanh(noise_base)  # compress tails

    controls_html = "\n".join(
        [
            slider(
                cid=f"{module_id}-Vacc",
                label="加速电压 V_acc (V)",
                vmin=500,
                vmax=10000,
                step=50,
                value=3000,
                unit=" V",
                help_text="V_acc 越大，电子速度越大，偏转灵敏度越小（同样偏转电压，屏上位移更小）。",
            ),
            select(
                cid=f"{module_id}-mode",
                label="显示模式",
                value="yt",
                options=[("yt", "Y-T（随时间）"), ("xy", "X-Y（李萨如）")],
            ),
            select(
                cid=f"{module_id}-wave",
                label="Y 输入波形",
                value="sine",
                options=[
                    ("sine", "正弦"),
                    ("square", "方波"),
                    ("tri", "三角波"),
                    ("noise", "噪声(固定样本)"),
                ],
                help_text="波形只影响 V_y(t)；屏幕偏转仍满足 y ∝ V_y/V_acc（近似）。",
            ),
            slider(
                cid=f"{module_id}-Ay",
                label="Y 偏转电压幅值 A_y (V)",
                vmin=0,
                vmax=50,
                step=0.5,
                value=15,
                unit=" V",
            ),
            slider(
                cid=f"{module_id}-fy",
                label="Y 频率 f_y (Hz)",
                vmin=0.5,
                vmax=200,
                step=0.5,
                value=20,
                unit=" Hz",
            ),
            f'<div id="{module_id}-group-yt">',
            slider(
                cid=f"{module_id}-Ts",
                label="时基扫掠周期 T_sweep (s)",
                vmin=0.01,
                vmax=0.50,
                step=0.005,
                value=0.10,
                unit=" s",
                help_text="T_sweep 变小＝扫描更快；同样信号会在屏上“拉伸/压缩”。",
            ),
            select(
                cid=f"{module_id}-trig",
                label="触发（Trigger）",
                value="free",
                options=[("free", "未触发：自由运行"), ("trig", "触发：锁定到阈值")],
                help_text="触发会把每次扫掠的起点对齐到“输入电压跨过阈值”的时刻，使波形稳定。",
            ),
            slider(
                cid=f"{module_id}-Vtrig",
                label="触发电平 V_trig (V)",
                vmin=-50,
                vmax=50,
                step=0.5,
                value=0.0,
                unit=" V",
            ),
            select(
                cid=f"{module_id}-slope",
                label="触发沿",
                value="rise",
                options=[("rise", "上升沿"), ("fall", "下降沿")],
            ),
            buttons([(f"{module_id}-play", "播放/暂停（时基滚动）", "primary")]),
            "</div>",
            f'<div id="{module_id}-group-xy" style="display:none">',
            slider(
                cid=f"{module_id}-Ax",
                label="X 输入幅值 A_x (V)",
                vmin=0,
                vmax=50,
                step=0.5,
                value=15,
                unit=" V",
            ),
            slider(
                cid=f"{module_id}-fx",
                label="X 频率 f_x (Hz)",
                vmin=0.5,
                vmax=200,
                step=0.5,
                value=10,
                unit=" Hz",
                help_text="当 f_x : f_y 是简单整数比时，李萨如图形更稳定。",
            ),
            slider(
                cid=f"{module_id}-phi",
                label="相位差 φ（Y 相对 X）(deg)",
                vmin=0,
                vmax=180,
                step=1,
                value=60,
                unit="°",
            ),
            "</div>",
            "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.12);margin:12px 0'>",
            slider(
                cid=f"{module_id}-fs",
                label="数字示波器采样率 f_s (Hz)",
                vmin=20,
                vmax=5000,
                step=10,
                value=400,
                unit=" Hz",
                help_text="采样率不足会出现混叠：观察数字采样曲线与模拟曲线的差异。",
            ),
            select(
                cid=f"{module_id}-nbits",
                label="量化位数 Nbits",
                value="8",
                options=[("4", "4 bits"), ("6", "6 bits"), ("8", "8 bits"), ("10", "10 bits")],
                help_text="位数越少，波形越“台阶化”。",
            ),
            buttons([(f"{module_id}-reset", "重置参数", "primary")]),
        ]
    )

    # figures
    fig0 = go.Figure(
        data=[
            go.Scatter(x=[0, 0.25], y=[0, 0], mode="lines", name="+A", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[0, 0.25], y=[0, 0], mode="lines", name="-A", line=dict(color="#a6e22e", width=2)),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=40, r=20, t=40, b=40),
            title="CRT 电子轨迹示意（偏转板内抛物线 + 漂移段直线，近似）",
            xaxis_title="x (m, schematic)",
            yaxis_title="y (m, schematic)",
            xaxis=dict(range=[0, 0.25], showgrid=False, zeroline=False),
            yaxis=dict(range=[-0.04, 0.04], showgrid=False, zeroline=False),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            shapes=[
                dict(type="rect", x0=0.06, x1=0.11, y0=-0.01, y1=0.01, line=dict(color="rgba(255,255,255,0.25)")),
                dict(type="line", x0=0.25, x1=0.25, y0=-0.04, y1=0.04, line=dict(color="rgba(255,255,255,0.25)", dash="dot")),
            ],
            annotations=[
                dict(x=0.085, y=0.012, text="偏转板", showarrow=False, font=dict(size=11, color="rgba(255,255,255,0.75)")),
                dict(x=0.25, y=0.042, text="屏幕", showarrow=False, font=dict(size=11, color="rgba(255,255,255,0.75)")),
            ],
        ),
    )

    fig1 = go.Figure(
        data=[
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="模拟(连续)", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines+markers", name="数字(采样/量化)", line=dict(color="#ff6b6b", width=1), marker=dict(size=5)),
            go.Scatter(
                x=[0, 1],
                y=[0, 0],
                mode="lines",
                name="触发电平",
                line=dict(color="rgba(255,255,255,0.55)", width=1, dash="dot"),
            ),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="屏幕显示：Y-T（模拟 vs 数字采样）",
            xaxis_title="t (ms)",
            yaxis_title="y (mm, relative)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    fig2 = go.Figure(
        data=[
            go.Scatter(x=[0], y=[0], mode="lines", name="模拟(连续)", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[0], y=[0], mode="lines+markers", name="数字(采样/量化)", line=dict(color="#ff6b6b", width=1), marker=dict(size=4)),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="屏幕显示：X-Y（李萨如）",
            xaxis_title="x (mm, relative)",
            yaxis_title="y (mm, relative)",
            xaxis=dict(scaleanchor="y", scaleratio=1),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“示波器=CRT”：不对。CRT 只是显示器件；示波器还包含输入衰减/耦合、时基、触发、放大等测量系统。</li>
      <li>“V_acc 越大偏转越大”：在电场偏转模型中相反，<code>y ∝ V_def / V_acc</code>，V_acc 越大电子越“硬”。</li>
      <li>“采样率只要比信号频率大就行”：需要满足奈奎斯特条件 <code>f_s ≥ 2 f</code> 才能避免混叠（理想情况）。</li>
      <li>“位数越低只是更粗糙”：低位数会引入量化噪声/台阶，影响幅值与细节判断。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>引导问题（3~5 分钟）</summary>
      <ol>
        <li><b>预测</b>：把 V_acc 加倍，屏幕上同样 A_y 的正弦波高度会怎样变化？</li>
        <li><b>验证</b>：分别把 f_s 调到 1.2 f_y 和 10 f_y，数字波形出现了什么差异？</li>
        <li><b>解释</b>：用“电子速度变大 → 在偏转板内停留时间变短”解释 <code>y ∝ 1/V_acc</code> 的趋势。</li>
        <li><b>拓展</b>：为什么真实示波器需要触发？如果没有触发，屏幕图形会发生什么？</li>
      </ol>
    </details>
    """

    data_payload = {
        "noise": noise_base.tolist(),
        "defaults": {
            "Vacc": 3000,
            "mode": "yt",
            "wave": "sine",
            "Ay": 15,
            "fy": 20,
            "Ts": 0.10,
            "trig": "free",
            "Vtrig": 0.0,
            "slope": "rise",
            "Ax": 15,
            "fx": 10,
            "phi": 60,
            "fs": 400,
            "nbits": "8",
        },
    }

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);

      const els = {{
        Vacc: root.querySelector("#{module_id}-Vacc"),
        mode: root.querySelector("#{module_id}-mode"),
        wave: root.querySelector("#{module_id}-wave"),
        Ay: root.querySelector("#{module_id}-Ay"),
        fy: root.querySelector("#{module_id}-fy"),
        Ts: root.querySelector("#{module_id}-Ts"),
        trig: root.querySelector("#{module_id}-trig"),
        Vtrig: root.querySelector("#{module_id}-Vtrig"),
        slope: root.querySelector("#{module_id}-slope"),
        play: root.querySelector("#{module_id}-play"),
        Ax: root.querySelector("#{module_id}-Ax"),
        fx: root.querySelector("#{module_id}-fx"),
        phi: root.querySelector("#{module_id}-phi"),
        fs: root.querySelector("#{module_id}-fs"),
        nbits: root.querySelector("#{module_id}-nbits"),
        reset: root.querySelector("#{module_id}-reset"),
      }};
      const gYT = root.querySelector("#{module_id}-group-yt");
      const gXY = root.querySelector("#{module_id}-group-xy");

      emlabBindValue(root, "{module_id}-Vacc", " V", 0);
      emlabBindValue(root, "{module_id}-Ay", " V", 1);
      emlabBindValue(root, "{module_id}-fy", " Hz", 1);
      emlabBindValue(root, "{module_id}-Ts", " s", 3);
      emlabBindValue(root, "{module_id}-Vtrig", " V", 1);
      emlabBindValue(root, "{module_id}-Ax", " V", 1);
      emlabBindValue(root, "{module_id}-fx", " Hz", 1);
      emlabBindValue(root, "{module_id}-phi", "°", 0);
      emlabBindValue(root, "{module_id}-fs", " Hz", 0);

      const fig0 = document.getElementById("fig-{module_id}-0");
      const figYT = document.getElementById("fig-{module_id}-1");
      const figXY = document.getElementById("fig-{module_id}-2");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"电子速度 v_e", id:"{module_id}-ro-ve", value:"—"}},
        {{key:"偏转灵敏度 (mm/V)", id:"{module_id}-ro-sens", value:"—"}},
        {{key:"测量：f（模拟）", id:"{module_id}-ro-fa", value:"—"}},
        {{key:"测量：f（数字）", id:"{module_id}-ro-fd", value:"—"}},
        {{key:"测量：y_pp", id:"{module_id}-ro-ypp", value:"—"}},
        {{key:"混叠/触发提示", id:"{module_id}-ro-alias", value:"—"}},
      ]);

      // constants
      const e = 1.602176634e-19;
      const me = 9.1093837015e-31;

      // geometry (meters, schematic)
      const x0 = 0.0;
      const x1 = 0.06;   // plate start
      const x2 = 0.11;   // plate end
      const xs = 0.25;   // screen
      const dPlate = 0.010; // plate gap

      let timer = null;
      let tOffset = 0.0; // seconds, used for "free-run rolling"
      function stopRolling(){{
        if(timer){{ clearInterval(timer); timer = null; }}
      }}

      function showMode(mode){{
        gYT.style.display = (mode === "yt") ? "" : "none";
        gXY.style.display = (mode === "xy") ? "" : "none";
        if(mode !== "yt") stopRolling();
      }}

      function waveY(t, A, f, kind){{
        const w = 2*Math.PI*f;
        if(kind === "sine") return A*Math.sin(w*t);
        if(kind === "square") return A*(Math.sin(w*t) >= 0 ? 1 : -1);
        if(kind === "tri") return (2*A/Math.PI)*Math.asin(Math.sin(w*t));
        return 0;
      }}

      function noiseAt(t){{
        const nb = data.noise || [];
        if(nb.length < 2) return 0;
        const fsn = 2500; // Hz (teaching)
        const idx = Math.floor((t*fsn) % nb.length);
        return nb[(idx + nb.length) % nb.length] || 0;
      }}

      function vyAt(t, Ay, fy, wave){{
        if(wave === "noise") return Ay * noiseAt(t);
        return waveY(t, Ay, fy, wave);
      }}

      function findTriggerStart(baseStart, Ts, Ay, fy, wave, level, slope){{
        const total = 2*Ts;
        const N = 2400;
        const dt = total/(N-1);
        let prev = vyAt(baseStart, Ay, fy, wave) - level;
        for(let i=1;i<N;i++) {{
          const tt = baseStart + i*dt;
          const curr = vyAt(tt, Ay, fy, wave) - level;
          if(slope === "rise") {{
            if(prev < 0 && curr >= 0) return tt;
          }} else {{
            if(prev > 0 && curr <= 0) return tt;
          }}
          prev = curr;
        }}
        return baseStart;
      }}

      function estimateFreq(tSec, y){{
        if(y.length < 10) return null;
        let mean = 0;
        for(let i=0;i<y.length;i++) mean += y[i];
        mean /= y.length;
        let last = null;
        const periods = [];
        let prev = y[0] - mean;
        for(let i=1;i<y.length;i++) {{
          const curr = y[i] - mean;
          if(prev < 0 && curr >= 0) {{
            const t0 = tSec[i-1], t1 = tSec[i];
            const tc = t0 + (t1-t0) * (-prev) / Math.max(1e-12, (curr-prev));
            if(last !== null) periods.push(tc - last);
            last = tc;
          }}
          prev = curr;
        }}
        if(periods.length < 2) return null;
        periods.sort((a,b)=>a-b);
        const med = periods[Math.floor(periods.length/2)];
        return (med > 1e-9) ? (1.0/med) : null;
      }}

      function deflectionScale(Vacc){{
        // y_screen for Vdef=1V (meters per volt)
        const v = Math.sqrt(Math.max(0, 2*e*Vacc/me));
        const Lp = (x2-x1);
        const tp = Lp / Math.max(1e-9, v);
        const td = (xs-x2) / Math.max(1e-9, v);
        const ay_per_V = (-e/(me*dPlate)); // electron charge negative
        return ay_per_V * (0.5*tp*tp + tp*td);
      }}

      function beamTrajectory(Vacc, Vdef){{
        const v = Math.sqrt(Math.max(0, 2*e*Vacc/me));
        const ay = (-e * (Vdef/dPlate) / me);
        const xsamp = [];
        const ysamp = [];
        const N = 240;
        for(let i=0;i<N;i++){{
          const x = xs * i/(N-1);
          let y = 0;
          if(x < x1) {{
            y = 0;
          }} else if(x <= x2) {{
            const t = (x-x1) / Math.max(1e-9, v);
            y = 0.5 * ay * t*t;
          }} else {{
            const tp = (x2-x1) / Math.max(1e-9, v);
            const y2 = 0.5*ay*tp*tp;
            const vy2 = ay*tp;
            const t = (x-x2) / Math.max(1e-9, v);
            y = y2 + vy2*t;
          }}
          xsamp.push(x);
          ysamp.push(y);
        }}
        return {{x: xsamp, y: ysamp}};
      }}

      function update(){{
        const Vacc = emlabNum(els.Vacc.value);
        const mode = els.mode.value;
        showMode(mode);

        const v = Math.sqrt(Math.max(0, 2*e*Vacc/me));
        root.querySelector("#{module_id}-ro-ve").textContent = emlabFmt(v/1e6, 3) + "×10⁶ m/s";

        const yPerV = deflectionScale(Vacc); // m/V
        root.querySelector("#{module_id}-ro-sens").textContent = emlabFmt(1000*yPerV, 4) + " mm/V";

        // trajectory uses +/-Ay as representative
        const Ay = emlabNum(els.Ay.value);
        const trP = beamTrajectory(Vacc, +Ay);
        const trN = beamTrajectory(Vacc, -Ay);
        Plotly.restyle(fig0, {{x:[trP.x, trN.x], y:[trP.y, trN.y]}}, [0,1]);

        // digital settings
        const fs = Math.max(1, emlabNum(els.fs.value));
        const nbits = parseInt(els.nbits.value, 10);

        // Y-T mode
        const wave = els.wave.value;
        const fy = emlabNum(els.fy.value);
        const Ts = Math.max(1e-3, emlabNum(els.Ts.value));
        const trigMode = els.trig.value;
        const Vtrig = emlabNum(els.Vtrig.value);
        const slope = els.slope.value;

        let start = tOffset;
        if(mode === "yt" && trigMode === "trig") {{
          start = findTriggerStart(tOffset, Ts, Ay, fy, wave, Vtrig, slope);
        }}

        const N = 1400;
        const t = new Array(N);
        const y = new Array(N);
        const tSec = new Array(N);
        let yMin = 1e18, yMax = -1e18;
        for(let i=0;i<N;i++){{
          const tt = Ts * i/(N-1);
          t[i] = 1000*tt;
          tSec[i] = tt;
          const Vy = vyAt(start + tt, Ay, fy, wave);
          const yy = 1000 * (yPerV * Vy); // mm
          y[i] = yy;
          if(yy < yMin) yMin = yy;
          if(yy > yMax) yMax = yy;
        }}

        // sampled + quantized
        const range = Math.max(1e-6, 1.1*Ay);
        const qLevels = Math.pow(2, nbits);
        const qStep = 2*range / qLevels;
        const tS = [];
        const yS = [];
        for(let k=0;;k++){{
          const tt = k / fs;
          if(tt > Ts + 1e-12) break;
          const Vy = vyAt(start + tt, Ay, fy, wave);
          const q = Math.round((Vy + range)/qStep)*qStep - range;
          tS.push(1000*tt);
          yS.push(1000*(yPerV*q));
        }}

        const yTrig = 1000*(yPerV*Vtrig);
        Plotly.restyle(figYT, {{x:[t, tS, [0, 1000*Ts]], y:[y, yS, [yTrig, yTrig]]}}, [0,1,2]);

        // measurements
        const ypp = yMax - yMin;
        root.querySelector("#{module_id}-ro-ypp").textContent = emlabFmt(ypp, 2) + " mm";
        const fA = (wave === "noise") ? null : estimateFreq(tSec, y);
        root.querySelector("#{module_id}-ro-fa").textContent = (fA && isFinite(fA)) ? (emlabFmt(fA, 2) + " Hz") : "—";
        const tSd = tS.map(v=>v/1000.0);
        const fD = (wave === "noise") ? null : estimateFreq(tSd, yS);
        root.querySelector("#{module_id}-ro-fd").textContent = (fD && isFinite(fD)) ? (emlabFmt(fD, 2) + " Hz") : "—";

        // alias hint for sine case
        let aliasText = "—";
        if(wave === "sine" && fs > 0){{
          const n = Math.round(fy/fs);
          const fAlias = Math.abs(fy - n*fs);
          aliasText = (fs < 2*fy) ? ("可能混叠：f_alias≈"+emlabFmt(fAlias,2)+" Hz") : "满足 f_s≥2f（理想）";
        }} else if(wave !== "sine") {{
          aliasText = "非正弦含高频分量，更易混叠";
        }}
        if(mode === "yt") {{
          aliasText = (trigMode === "trig") ? ("触发锁定｜" + aliasText) : ("自由运行｜" + aliasText);
        }}
        root.querySelector("#{module_id}-ro-alias").textContent = aliasText;

        // X-Y mode (always update; not expensive)
        const Ax = emlabNum(els.Ax.value);
        const fx = emlabNum(els.fx.value);
        const phi = emlabNum(els.phi.value) * Math.PI/180; // phase of Y relative to X
        const T0 = 1/Math.max(1e-6, Math.min(fx, fy));
        const Twin = Math.min(0.8, 6*T0);
        const Nxy = 2000;
        const xsArr = new Array(Nxy);
        const ysArr = new Array(Nxy);
        const dty = (fy > 1e-9) ? (phi/(2*Math.PI*fy)) : 0; // phase -> time shift for general waveforms
        const baseXY = tOffset;
        for(let i=0;i<Nxy;i++){{
          const tt = Twin * i/(Nxy-1);
          const Vx = Ax*Math.sin(2*Math.PI*fx*(baseXY + tt));
          const Vy = vyAt(baseXY + tt + dty, Ay, fy, wave);
          xsArr[i] = 1000*(yPerV * Vx);
          ysArr[i] = 1000*(yPerV * Vy);
        }}

        // digital XY
        const rangeX = Math.max(1e-6, 1.1*Ax);
        const qStepX = 2*rangeX / qLevels;
        const xSd = [];
        const ySd = [];
        for(let k=0;;k++){{
          const tt = k / fs;
          if(tt > Twin + 1e-12) break;
          const Vx = Ax*Math.sin(2*Math.PI*fx*(baseXY + tt));
          const Vy = vyAt(baseXY + tt + dty, Ay, fy, wave);
          const qx = Math.round((Vx + rangeX)/qStepX)*qStepX - rangeX;
          const qy = Math.round((Vy + range)/qStep)*qStep - range;
          xSd.push(1000*(yPerV*qx));
          ySd.push(1000*(yPerV*qy));
        }}
        Plotly.restyle(figXY, {{x:[xsArr, xSd], y:[ysArr, ySd]}}, [0,1]);
      }}

      function toggleRolling(){{
        const mode = els.mode.value;
        if(mode !== "yt") return;
        if(timer){{ stopRolling(); return; }}
        timer = setInterval(() => {{
          if(!root.classList.contains("active")) {{ stopRolling(); return; }}
          const Ts = Math.max(1e-3, emlabNum(els.Ts.value));
          tOffset = (tOffset + Ts/40) % 1000.0;
          update();
        }}, 60);
      }}

      function reset(){{
        stopRolling();
        tOffset = 0.0;
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
      els.play.addEventListener("click", toggleRolling);
      els.reset.addEventListener("click", reset);
      update();
    }}
    """

    return {
        "id": module_id,
        "title": "M02 示波器 vs CRT：偏转、时基、采样",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1, fig2],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }
