from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, select, slider


def build() -> dict:
    module_id = "pendulum"

    intro_html = """
    <p>
      这个页面把“单摆”放进电场/磁场与线圈电路中，用可调参数把不可见的力、阻尼与能量转化变成可观察的曲线。
      你可以在 4 个变体之间切换：
    </p>
    <ol>
      <li><b>带电小球 + 匀强电场</b>：<code>F=qE</code> 与 <code>mg</code> 合成，平衡角 <code>θ_eq</code> 改变，周期随“等效重力”改变。</li>
      <li><b>金属摆片穿过磁场（涡流制动）</b>：运动导致磁通变化 → 感应电流 → 楞次定律产生阻尼，机械能转为热。</li>
      <li><b>磁铁单摆 + 线圈（负载电阻可调）</b>：<code>I=ε/R</code>，电阻越小电流越大，阻尼越强。</li>
      <li><b>电磁驱动（共振）</b>：外加周期力矩，出现共振曲线；阻尼越大峰越低越宽。</li>
    </ol>
    """

    controls_html = "\n".join(
        [
            select(
                cid=f"{module_id}-variant",
                label="变体选择",
                value="charged_E",
                options=[
                    ("charged_E", "变体1：带电小球 + 匀强电场"),
                    ("eddy", "变体2：涡流阻尼（摆片过磁场）"),
                    ("coil", "变体3：线圈负载阻尼（磁铁 + 线圈）"),
                    ("drive", "变体4：电磁驱动（共振）"),
                ],
                help_text="切换后会显示该变体对应的参数与图像。",
            ),
            f'<div id="{module_id}-controls-charged_E">',
            slider(
                cid=f"{module_id}-V",
                label="板间电压 V (V)",
                vmin=0,
                vmax=5000,
                step=10,
                value=1500,
                unit=" V",
                help_text="近似匀强电场：E≈V/d（忽略边缘效应）。",
            ),
            slider(
                cid=f"{module_id}-d",
                label="板距 d (m)",
                vmin=0.01,
                vmax=0.20,
                step=0.005,
                value=0.05,
                unit=" m",
            ),
            slider(
                cid=f"{module_id}-qom",
                label="电荷质量比 q/m (C/kg)",
                vmin=-0.005,
                vmax=0.005,
                step=0.0001,
                value=0.0015,
                unit=" C/kg",
                help_text="正值表示电场力与 +x 方向同向；负值反向。",
            ),
            slider(
                cid=f"{module_id}-L1",
                label="摆长 L (m)",
                vmin=0.2,
                vmax=2.0,
                step=0.01,
                value=0.8,
                unit=" m",
            ),
            slider(
                cid=f"{module_id}-theta0_1",
                label="初始角 θ0 (deg)",
                vmin=-30,
                vmax=30,
                step=0.5,
                value=12,
                unit="°",
            ),
            "</div>",
            f'<div id="{module_id}-controls-eddy" style="display:none">',
            slider(
                cid=f"{module_id}-B2",
                label="磁感应强度 B (T)",
                vmin=0.0,
                vmax=0.5,
                step=0.005,
                value=0.20,
                unit=" T",
            ),
            slider(
                cid=f"{module_id}-Req2",
                label="等效电阻 R_eq (Ω)",
                vmin=0.2,
                vmax=10.0,
                step=0.1,
                value=2.0,
                unit=" Ω",
                help_text="电阻越小 → 感应电流越大 → 阻尼越强（定性）。",
            ),
            slider(
                cid=f"{module_id}-m2",
                label="摆锤质量 m (kg)",
                vmin=0.05,
                vmax=0.50,
                step=0.01,
                value=0.20,
                unit=" kg",
            ),
            slider(
                cid=f"{module_id}-L2",
                label="摆长 L (m)",
                vmin=0.2,
                vmax=2.0,
                step=0.01,
                value=0.9,
                unit=" m",
            ),
            slider(
                cid=f"{module_id}-theta0_2",
                label="初始角 θ0 (deg)",
                vmin=0,
                vmax=30,
                step=0.5,
                value=15,
                unit="°",
            ),
            "</div>",
            f'<div id="{module_id}-controls-coil" style="display:none">',
            slider(
                cid=f"{module_id}-Rload3",
                label="负载电阻 R_load (Ω)",
                vmin=0.2,
                vmax=50.0,
                step=0.2,
                value=4.0,
                unit=" Ω",
                help_text="对比“开路(很大R)”与“接负载(较小R)”的阻尼差异。",
            ),
            slider(
                cid=f"{module_id}-B3",
                label="磁场强度指标 B0 (arb.)",
                vmin=0.0,
                vmax=1.0,
                step=0.01,
                value=0.55,
                unit="",
            ),
            slider(
                cid=f"{module_id}-L3",
                label="摆长 L (m)",
                vmin=0.2,
                vmax=2.0,
                step=0.01,
                value=0.9,
                unit=" m",
            ),
            slider(
                cid=f"{module_id}-theta0_3",
                label="初始角 θ0 (deg)",
                vmin=0,
                vmax=30,
                step=0.5,
                value=18,
                unit="°",
            ),
            "</div>",
            f'<div id="{module_id}-controls-drive" style="display:none">',
            slider(
                cid=f"{module_id}-f4",
                label="驱动频率 f_drive (Hz)",
                vmin=0.1,
                vmax=3.0,
                step=0.01,
                value=1.0,
                unit=" Hz",
            ),
            slider(
                cid=f"{module_id}-A4",
                label="驱动强度 A (arb.)",
                vmin=0.0,
                vmax=2.0,
                step=0.02,
                value=0.8,
                unit="",
            ),
            slider(
                cid=f"{module_id}-duty4",
                label="脉冲占空比 duty",
                vmin=0.05,
                vmax=0.95,
                step=0.01,
                value=0.50,
                unit="",
                help_text="用“矩形脉冲的一次谐波”近似驱动效果（教学用）。",
            ),
            slider(
                cid=f"{module_id}-gamma4",
                label="阻尼系数 γ (1/s)",
                vmin=0.00,
                vmax=0.60,
                step=0.01,
                value=0.08,
                unit=" 1/s",
            ),
            slider(
                cid=f"{module_id}-L4",
                label="摆长 L (m)",
                vmin=0.2,
                vmax=2.0,
                step=0.01,
                value=1.0,
                unit=" m",
            ),
            "</div>",
            buttons(
                [
                    (f"{module_id}-reset", "重置参数", "primary"),
                ]
            ),
        ]
    )

    # Placeholder figures (JS will Plotly.react on init)
    fig0 = go.Figure(
        data=[
            go.Scatter(x=[0, 0], y=[0, -1], mode="lines", name="摆线", line=dict(color="#66d9ef", width=3)),
            go.Scatter(x=[0], y=[-1], mode="markers", name="摆球", marker=dict(size=10, color="#a6e22e")),
        ],
        layout=go.Layout(
            margin=dict(l=40, r=20, t=40, b=40),
            template="plotly_dark",
            title="单摆示意（平衡/初始）",
            xaxis=dict(range=[-1.2, 1.2], zeroline=False, showgrid=False),
            yaxis=dict(range=[-1.3, 0.2], scaleanchor="x", zeroline=False, showgrid=False),
            showlegend=False,
        ),
    )

    fig1 = go.Figure(
        data=[
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="θ(t)", line=dict(color="#66d9ef", width=2)),
        ],
        layout=go.Layout(
            margin=dict(l=50, r=20, t=40, b=40),
            template="plotly_dark",
            title="角度随时间变化 θ(t)",
            xaxis_title="t (s)",
            yaxis_title="θ (deg)",
        ),
    )

    fig2 = go.Figure(
        data=[
            go.Scatter(x=[0, 1], y=[1, 0.7], mode="lines", name="机械能(归一)", line=dict(color="#a6e22e", width=2)),
            go.Scatter(x=[0, 1], y=[0, 0.3], mode="lines", name="耗散/热(归一)", line=dict(color="#ff6b6b", width=2)),
        ],
        layout=go.Layout(
            margin=dict(l=50, r=20, t=40, b=40),
            template="plotly_dark",
            title="能量观点（归一化）",
            xaxis_title="t (s)",
            yaxis_title="能量(相对)",
            yaxis=dict(range=[0, 1.05]),
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“电场直接改变摆长 L”：不对。周期变化主要来自 <b>合加速度</b>（等效重力大小）变化。</li>
      <li>“磁场力做功让摆变慢”：磁力本身通常不做功；阻尼来自 <b>感应电流的焦耳热</b>（能量转化）。</li>
      <li>“电阻越大阻尼越大”：线圈感应中常见相反趋势：<code>I=ε/R</code>，R 小电流大 → 阻尼强（定性）。</li>
      <li>“共振=无限大振幅”：真实系统有阻尼/非线性，振幅会饱和；阻尼越大，共振峰越低越宽。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>预测-验证-解释（建议课堂提问）</summary>
      <ol>
        <li><b>预测</b>：把变体1中 V 加倍，平衡角 <code>θ_eq</code> 会怎样变化？周期 T 会变大还是变小？</li>
        <li><b>验证</b>：拖动 V 与 q/m，观察 <code>θ_eq</code> 与 T 的读数是否符合你的预测。</li>
        <li><b>解释</b>：用 <code>F=qE</code> 与能量观点解释：为什么“峰值角度”衰减时，热能在增加？</li>
        <li><b>拓展</b>：在变体4中，提高阻尼 γ 会让共振曲线发生什么变化？这对应现实中哪些损耗？</li>
      </ol>
    </details>
    """

    data_payload = {
        "g": 9.80665,
        "defaults": {
            "variant": "charged_E",
            "V": 1500,
            "d": 0.05,
            "qom": 0.0015,
            "L1": 0.8,
            "theta0_1": 12,
            "B2": 0.2,
            "Req2": 2.0,
            "m2": 0.2,
            "L2": 0.9,
            "theta0_2": 15,
            "Rload3": 4.0,
            "B3": 0.55,
            "L3": 0.9,
            "theta0_3": 18,
            "f4": 1.0,
            "A4": 0.8,
            "duty4": 0.5,
            "gamma4": 0.08,
            "L4": 1.0,
        },
    }

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);
      const g = data.g || 9.80665;

      const els = {{
        variant: root.querySelector("#{module_id}-variant"),
        V: root.querySelector("#{module_id}-V"),
        d: root.querySelector("#{module_id}-d"),
        qom: root.querySelector("#{module_id}-qom"),
        L1: root.querySelector("#{module_id}-L1"),
        th1: root.querySelector("#{module_id}-theta0_1"),
        B2: root.querySelector("#{module_id}-B2"),
        Req2: root.querySelector("#{module_id}-Req2"),
        m2: root.querySelector("#{module_id}-m2"),
        L2: root.querySelector("#{module_id}-L2"),
        th2: root.querySelector("#{module_id}-theta0_2"),
        R3: root.querySelector("#{module_id}-Rload3"),
        B3: root.querySelector("#{module_id}-B3"),
        L3: root.querySelector("#{module_id}-L3"),
        th3: root.querySelector("#{module_id}-theta0_3"),
        f4: root.querySelector("#{module_id}-f4"),
        A4: root.querySelector("#{module_id}-A4"),
        duty4: root.querySelector("#{module_id}-duty4"),
        gamma4: root.querySelector("#{module_id}-gamma4"),
        L4: root.querySelector("#{module_id}-L4"),
        reset: root.querySelector("#{module_id}-reset"),
      }};

      // bind value labels
      ["V","d","qom","L1","theta0_1","B2","Req2","m2","L2","theta0_2","Rload3","B3","L3","theta0_3","f4","A4","duty4","gamma4","L4"].forEach(k => {{
        const el = root.querySelector("#{module_id}-"+k);
      }});
      emlabBindValue(root, "{module_id}-V", " V", 0);
      emlabBindValue(root, "{module_id}-d", " m", 3);
      emlabBindValue(root, "{module_id}-qom", " C/kg", 4);
      emlabBindValue(root, "{module_id}-L1", " m", 2);
      emlabBindValue(root, "{module_id}-theta0_1", "°", 1);

      emlabBindValue(root, "{module_id}-B2", " T", 3);
      emlabBindValue(root, "{module_id}-Req2", " Ω", 2);
      emlabBindValue(root, "{module_id}-m2", " kg", 2);
      emlabBindValue(root, "{module_id}-L2", " m", 2);
      emlabBindValue(root, "{module_id}-theta0_2", "°", 1);

      emlabBindValue(root, "{module_id}-Rload3", " Ω", 2);
      emlabBindValue(root, "{module_id}-B3", "", 2);
      emlabBindValue(root, "{module_id}-L3", " m", 2);
      emlabBindValue(root, "{module_id}-theta0_3", "°", 1);

      emlabBindValue(root, "{module_id}-f4", " Hz", 2);
      emlabBindValue(root, "{module_id}-A4", "", 2);
      emlabBindValue(root, "{module_id}-duty4", "", 2);
      emlabBindValue(root, "{module_id}-gamma4", " 1/s", 2);
      emlabBindValue(root, "{module_id}-L4", " m", 2);

      const ctrlBoxes = {{
        charged_E: root.querySelector("#{module_id}-controls-charged_E"),
        eddy: root.querySelector("#{module_id}-controls-eddy"),
        coil: root.querySelector("#{module_id}-controls-coil"),
        drive: root.querySelector("#{module_id}-controls-drive"),
      }};

      const fig0 = document.getElementById("fig-{module_id}-0");
      const fig1 = document.getElementById("fig-{module_id}-1");
      const fig2 = document.getElementById("fig-{module_id}-2");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"读数：θ_eq", id:"{module_id}-ro-thetaeq", value:"—"}},
        {{key:"读数：周期 T", id:"{module_id}-ro-T", value:"—"}},
        {{key:"读数：阻尼/共振", id:"{module_id}-ro-extra", value:"—"}},
      ]);

      function showVariant(v){{
        Object.keys(ctrlBoxes).forEach(k => {{
          ctrlBoxes[k].style.display = (k === v) ? "" : "none";
        }});
      }}

      function rad(deg){{ return deg * Math.PI / 180; }}
      function deg(rad){{ return rad * 180 / Math.PI; }}

      function update(){{
        const variant = els.variant.value;
        showVariant(variant);

        const N = 900;
        const tMax = 12.0;
        const t = new Array(N);
        for(let i=0;i<N;i++) t[i] = tMax * i / (N-1);

        if(variant === "charged_E"){{
          const V = emlabNum(els.V.value);
          const d = emlabNum(els.d.value);
          const qom = emlabNum(els.qom.value);
          const L = emlabNum(els.L1.value);
          const th0 = rad(emlabNum(els.th1.value));

          const E = (d > 0) ? (V / d) : 0;
          const a = qom * E;
          const geff = Math.sqrt(g*g + a*a);
          const thetaEq = Math.atan2(a, g);
          const w = Math.sqrt(Math.max(1e-9, geff / Math.max(0.05, L)));
          const T = 2*Math.PI / w;

          const th = t.map(tt => thetaEq + (th0 - thetaEq)*Math.cos(w*tt));

          const xEq = Math.sin(thetaEq), yEq = -Math.cos(thetaEq);
          const x0 = Math.sin(th0), y0 = -Math.cos(th0);
          const xNow = Math.sin(th[0]), yNow = -Math.cos(th[0]);

          const schemData = [
            {{x:[0, xEq], y:[0, yEq], mode:"lines", line:{{color:"#66d9ef", width:3}}, hoverinfo:"skip"}},
            {{x:[xEq], y:[yEq], mode:"markers", marker:{{size:10, color:"#66d9ef"}}, hoverinfo:"skip"}},
            {{x:[0, x0], y:[0, y0], mode:"lines", line:{{color:"#a6e22e", width:2, dash:"dot"}}, hoverinfo:"skip"}},
            {{x:[x0], y:[y0], mode:"markers", marker:{{size:10, color:"#a6e22e"}}, hoverinfo:"skip"}},
            {{x:[0, xNow], y:[0, yNow], mode:"lines", line:{{color:"#ffffff", width:2}}, hoverinfo:"skip"}},
          ];
          const schemLayout = {{
            template:"plotly_dark",
            margin:{{l:40,r:20,t:40,b:40}},
            title:"示意：平衡(蓝) 与 初始(绿)",
            xaxis:{{range:[-1.2,1.2], showgrid:false, zeroline:false}},
            yaxis:{{range:[-1.3,0.2], scaleanchor:"x", showgrid:false, zeroline:false}},
            showlegend:false
          }};

          const thDeg = th.map(v => deg(v));
          const fig1Data = [
            {{x:t, y:thDeg, mode:"lines", name:"θ(t)", line:{{color:"#66d9ef", width:2}}}},
            {{x:[0,tMax], y:[deg(thetaEq), deg(thetaEq)], mode:"lines", name:"θ_eq", line:{{color:"#a6e22e", width:1, dash:"dash"}}}},
          ];
          const fig1Layout = {{
            template:"plotly_dark",
            margin:{{l:50,r:20,t:40,b:40}},
            title:"θ(t)：小角近似（绕平衡位置振动）",
            xaxis:{{title:"t (s)"}},
            yaxis:{{title:"θ (deg)"}},
            legend:{{orientation:"h"}}
          }};

          // show period vs V by scanning V (for learning)
          const Vs = [];
          const Ts = [];
          for(let vv=0; vv<=5000; vv+=100){{
            const E2 = (d>0) ? (vv/d) : 0;
            const a2 = qom*E2;
            const ge2 = Math.sqrt(g*g + a2*a2);
            const w2 = Math.sqrt(Math.max(1e-9, ge2/Math.max(0.05,L)));
            Vs.push(vv);
            Ts.push(2*Math.PI/w2);
          }}
          const fig2Data = [
            {{x:Vs, y:Ts, mode:"lines", name:"T(V)", line:{{color:"#a6e22e", width:2}}}},
            {{x:[V,V], y:[Math.min(...Ts), Math.max(...Ts)], mode:"lines", name:"当前V", line:{{color:"#ff6b6b", width:1, dash:"dot"}}}},
          ];
          const fig2Layout = {{
            template:"plotly_dark",
            margin:{{l:60,r:20,t:40,b:40}},
            title:"周期随电压变化 T(V)（保持 d、q/m、L 不变）",
            xaxis:{{title:"V (V)"}},
            yaxis:{{title:"T (s)"}},
            showlegend:false
          }};

          Plotly.react(fig0, schemData, schemLayout, {{displaylogo:false, responsive:true}});
          Plotly.react(fig1, fig1Data, fig1Layout, {{displaylogo:false, responsive:true}});
          Plotly.react(fig2, fig2Data, fig2Layout, {{displaylogo:false, responsive:true}});

          root.querySelector("#{module_id}-ro-thetaeq").textContent = emlabFmt(deg(thetaEq), 2) + "°";
          root.querySelector("#{module_id}-ro-T").textContent = emlabFmt(T, 3) + " s";
          root.querySelector("#{module_id}-ro-extra").textContent = "E≈V/d,  g_eff=√(g²+a²)";
          return;
        }}

        if(variant === "eddy"){{
          const B = emlabNum(els.B2.value);
          const R = Math.max(0.05, emlabNum(els.Req2.value));
          const m = Math.max(0.02, emlabNum(els.m2.value));
          const L = Math.max(0.1, emlabNum(els.L2.value));
          const th0 = rad(emlabNum(els.th2.value));
          const w0 = Math.sqrt(g / L);
          const gamma = 0.22 * (B/0.2)*(B/0.2) * (1.0/R) * (0.2/m); // 1/s (teaching-scale)
          const wd = Math.sqrt(Math.max(0.0, w0*w0 - gamma*gamma));
          const th = t.map(tt => th0 * Math.exp(-gamma*tt) * Math.cos(wd*tt));
          const thDeg = th.map(v => deg(v));

          // schematic at t=0
          const x0 = Math.sin(th0), y0 = -Math.cos(th0);
          const schemData = [
            {{x:[0, x0], y:[0, y0], mode:"lines", line:{{color:"#66d9ef", width:3}}, hoverinfo:"skip"}},
            {{x:[x0], y:[y0], mode:"markers", marker:{{size:10, color:"#a6e22e"}}, hoverinfo:"skip"}},
          ];
          const schemLayout = {{
            template:"plotly_dark",
            margin:{{l:40,r:20,t:40,b:40}},
            title:"示意：涡流阻尼（能量→热）",
            xaxis:{{range:[-1.2,1.2], showgrid:false, zeroline:false}},
            yaxis:{{range:[-1.3,0.2], scaleanchor:"x", showgrid:false, zeroline:false}},
            showlegend:false
          }};

          const fig1Data = [
            {{x:t, y:thDeg, mode:"lines", name:"θ(t)", line:{{color:"#66d9ef", width:2}}}},
            {{x:t, y:thDeg.map(v=>Math.abs(v)), mode:"lines", name:"|θ|", line:{{color:"#a6e22e", width:1, dash:"dot"}}}},
          ];
          const fig1Layout = {{
            template:"plotly_dark",
            margin:{{l:50,r:20,t:40,b:40}},
            title:"θ(t)：阻尼振动（定性模型）",
            xaxis:{{title:"t (s)"}},
            yaxis:{{title:"θ (deg)"}},
            legend:{{orientation:"h"}}
          }};

          // energy (normalized)
          const dt = tMax/(N-1);
          const thdot = new Array(N);
          for(let i=0;i<N;i++){{
            const im1 = Math.max(0, i-1), ip1 = Math.min(N-1, i+1);
            thdot[i] = (th[ip1]-th[im1]) / ((ip1-im1)*dt);
          }}
          const E = th.map((v,i)=>0.5*(thdot[i]*thdot[i] + w0*w0*v*v));
          const E0 = Math.max(1e-9, E[0]);
          const Em = E.map(v=>Math.max(0, v/E0));
          const Eh = Em.map(v=>Math.max(0, 1-v));
          const fig2Data = [
            {{x:t, y:Em, mode:"lines", name:"机械能(归一)", line:{{color:"#a6e22e", width:2}}}},
            {{x:t, y:Eh, mode:"lines", name:"热(归一)", line:{{color:"#ff6b6b", width:2}}}},
          ];
          const fig2Layout = {{
            template:"plotly_dark",
            margin:{{l:55,r:20,t:40,b:40}},
            title:"能量观点：机械能衰减 → 热增加（定性）",
            xaxis:{{title:"t (s)"}},
            yaxis:{{title:"相对能量", range:[0,1.05]}},
            legend:{{orientation:"h"}}
          }};

          Plotly.react(fig0, schemData, schemLayout, {{displaylogo:false, responsive:true}});
          Plotly.react(fig1, fig1Data, fig1Layout, {{displaylogo:false, responsive:true}});
          Plotly.react(fig2, fig2Data, fig2Layout, {{displaylogo:false, responsive:true}});

          const T = 2*Math.PI / Math.max(1e-9, w0);
          root.querySelector("#{module_id}-ro-thetaeq").textContent = "0° (无平衡偏移)";
          root.querySelector("#{module_id}-ro-T").textContent = emlabFmt(T, 3) + " s";
          root.querySelector("#{module_id}-ro-extra").textContent = "γ≈0.22·(B/0.2)²·(1/R)·(0.2/m)";
          return;
        }}

        if(variant === "coil"){{
          const R = Math.max(0.05, emlabNum(els.R3.value));
          const B = emlabNum(els.B3.value);
          const L = Math.max(0.1, emlabNum(els.L3.value));
          const th0 = rad(emlabNum(els.th3.value));
          const w0 = Math.sqrt(g / L);
          const gammaLoad = 0.20 * (B*B) * (1.0/R);
          const gammaOpen = 0.20 * (B*B) * (1.0/1e6);
          const wdL = Math.sqrt(Math.max(0.0, w0*w0 - gammaLoad*gammaLoad));
          const wdO = Math.sqrt(Math.max(0.0, w0*w0 - gammaOpen*gammaOpen));
          const thL = t.map(tt => th0*Math.exp(-gammaLoad*tt)*Math.cos(wdL*tt));
          const thO = t.map(tt => th0*Math.exp(-gammaOpen*tt)*Math.cos(wdO*tt));

          const schemData = [
            {{x:[0, Math.sin(th0)], y:[0, -Math.cos(th0)], mode:"lines", line:{{color:"#66d9ef", width:3}}, hoverinfo:"skip"}},
            {{x:[Math.sin(th0)], y:[-Math.cos(th0)], mode:"markers", marker:{{size:10, color:"#a6e22e"}}, hoverinfo:"skip"}},
          ];
          const schemLayout = {{
            template:"plotly_dark",
            margin:{{l:40,r:20,t:40,b:40}},
            title:"示意：磁铁单摆 + 线圈（负载改变阻尼）",
            xaxis:{{range:[-1.2,1.2], showgrid:false, zeroline:false}},
            yaxis:{{range:[-1.3,0.2], scaleanchor:"x", showgrid:false, zeroline:false}},
            showlegend:false
          }};

          const fig1Data = [
            {{x:t, y:thO.map(v=>deg(v)), mode:"lines", name:"开路(几乎无阻尼)", line:{{color:"#a6e22e", width:2}}}},
            {{x:t, y:thL.map(v=>deg(v)), mode:"lines", name:"接负载(有阻尼)", line:{{color:"#66d9ef", width:2}}}},
          ];
          const fig1Layout = {{
            template:"plotly_dark",
            margin:{{l:50,r:20,t:40,b:40}},
            title:"θ(t)：R_load 变小 → 阻尼增强（定性）",
            xaxis:{{title:"t (s)"}},
            yaxis:{{title:"θ (deg)"}},
            legend:{{orientation:"h"}}
          }};

          // "电路输出"：感应电流指标 ~ θ'(t)/R
          const dt = tMax/(N-1);
          const dth = new Array(N);
          for(let i=0;i<N;i++) {{
            const im1 = Math.max(0,i-1), ip1 = Math.min(N-1,i+1);
            dth[i] = (thL[ip1]-thL[im1]) / ((ip1-im1)*dt);
          }}
          const iInd = dth.map(v => (B*B)*v / R);
          const fig2Data = [
            {{x:t, y:iInd, mode:"lines", name:"感应电流指标 ~ θ'(t)/R", line:{{color:"#ff6b6b", width:2}}}},
          ];
          const fig2Layout = {{
            template:"plotly_dark",
            margin:{{l:55,r:20,t:40,b:40}},
            title:"电路观点：R 变小 → 电流变大 → 焦耳热增加（定性）",
            xaxis:{{title:"t (s)"}},
            yaxis:{{title:"I_ind (arb.)"}},
            showlegend:false
          }};

          Plotly.react(fig0, schemData, schemLayout, {{displaylogo:false, responsive:true}});
          Plotly.react(fig1, fig1Data, fig1Layout, {{displaylogo:false, responsive:true}});
          Plotly.react(fig2, fig2Data, fig2Layout, {{displaylogo:false, responsive:true}});

          const T = 2*Math.PI / Math.max(1e-9, w0);
          root.querySelector("#{module_id}-ro-thetaeq").textContent = "0°";
          root.querySelector("#{module_id}-ro-T").textContent = emlabFmt(T, 3) + " s";
          root.querySelector("#{module_id}-ro-extra").textContent = "阻尼 ~ 1/R_load";
          return;
        }}

        // drive
        const f = emlabNum(els.f4.value);
        const A = emlabNum(els.A4.value);
        const duty = emlabNum(els.duty4.value);
        const gamma = Math.max(0.0, emlabNum(els.gamma4.value));
        const L = Math.max(0.1, emlabNum(els.L4.value));
        const w0 = Math.sqrt(g / L);
        const w = 2*Math.PI*f;
        const f1 = (2/Math.PI) * Math.sin(Math.PI*duty); // fundamental amplitude factor
        const f0 = A * f1 * w0*w0 * 0.25; // scale into angle-equation
        const denom = Math.sqrt((w0*w0 - w*w)**2 + (2*gamma*w)**2);
        const Amp = (denom>1e-9) ? (f0/denom) : 0;
        const phi = Math.atan2(2*gamma*w, (w0*w0 - w*w));

        const th = t.map(tt => Amp * Math.sin(w*tt - phi));
        const schemData = [
          {{x:[0, Math.sin(th[0])], y:[0, -Math.cos(th[0])], mode:"lines", line:{{color:"#66d9ef", width:3}}, hoverinfo:"skip"}},
          {{x:[Math.sin(th[0])], y:[-Math.cos(th[0])], mode:"markers", marker:{{size:10, color:"#a6e22e"}}, hoverinfo:"skip"}},
        ];
        const schemLayout = {{
          template:"plotly_dark",
          margin:{{l:40,r:20,t:40,b:40}},
          title:"示意：电磁驱动（稳态响应近似）",
          xaxis:{{range:[-1.2,1.2], showgrid:false, zeroline:false}},
          yaxis:{{range:[-1.3,0.2], scaleanchor:"x", showgrid:false, zeroline:false}},
          showlegend:false
        }};

        const fig1Data = [
          {{x:t, y:th.map(v=>deg(v)), mode:"lines", name:"θ(t) 稳态", line:{{color:"#66d9ef", width:2}}}},
        ];
        const fig1Layout = {{
          template:"plotly_dark",
          margin:{{l:50,r:20,t:40,b:40}},
          title:"θ(t)：受迫振动（稳态）",
          xaxis:{{title:"t (s)"}},
          yaxis:{{title:"θ (deg)"}},
          showlegend:false
        }};

        // resonance curve
        const fScan = [];
        const AScan = [];
        const fmin = 0.2*w0/(2*Math.PI);
        const fmax = 2.0*w0/(2*Math.PI);
        for(let i=0;i<180;i++){{
          const ff = fmin + (fmax-fmin)*i/179;
          const ww = 2*Math.PI*ff;
          const den = Math.sqrt((w0*w0 - ww*ww)**2 + (2*gamma*ww)**2);
          const amp = (den>1e-9) ? (f0/den) : 0;
          fScan.push(ff);
          AScan.push(deg(Math.abs(amp)));
        }}
        const fig2Data = [
          {{x:fScan, y:AScan, mode:"lines", name:"稳态振幅", line:{{color:"#a6e22e", width:2}}}},
          {{x:[f,f], y:[0, Math.max(...AScan)], mode:"lines", name:"当前 f", line:{{color:"#ff6b6b", width:1, dash:"dot"}}}},
        ];
        const fig2Layout = {{
          template:"plotly_dark",
          margin:{{l:60,r:20,t:40,b:40}},
          title:"共振曲线：稳态振幅 vs 驱动频率",
          xaxis:{{title:"f (Hz)"}},
          yaxis:{{title:"振幅 (deg)"}},
          showlegend:false
        }};

        Plotly.react(fig0, schemData, schemLayout, {{displaylogo:false, responsive:true}});
        Plotly.react(fig1, fig1Data, fig1Layout, {{displaylogo:false, responsive:true}});
        Plotly.react(fig2, fig2Data, fig2Layout, {{displaylogo:false, responsive:true}});

        root.querySelector("#{module_id}-ro-thetaeq").textContent = "0°";
        root.querySelector("#{module_id}-ro-T").textContent = emlabFmt(2*Math.PI/w0, 3) + " s (固有)";
        root.querySelector("#{module_id}-ro-extra").textContent = "稳态振幅≈" + emlabFmt(deg(Amp), 2) + "°";
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
        "title": "M01 单摆 × 电磁作用（4 变体）",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1, fig2],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }
