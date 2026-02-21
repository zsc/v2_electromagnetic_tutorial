from __future__ import annotations

import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, select, slider


def build() -> dict:
    module_id = "ac_motor"

    intro_html = """
    <p>
      交流电机的核心直观：<b>线圈电流 → 磁场</b>；多相电流叠加可形成<b>旋转磁场</b>。
      单相电流只产生往返的“脉动磁场”，起动困难；三相 120° 相位差可形成近恒幅旋转磁场；
      单相 + 电容可人为制造相位差，得到椭圆形“近似旋转”。
    </p>
    <p>
      本页同时给出“相电流波形（电路观点）”与“合成磁场矢量端点轨迹（电磁场观点）”。
    </p>
    """

    controls_html = "\n".join(
        [
            select(
                cid=f"{module_id}-mode",
                label="模式",
                value="three",
                options=[
                    ("single", "单相（脉动磁场）"),
                    ("three", "三相（旋转磁场）"),
                    ("cap", "单相 + 电容相移（近似旋转）"),
                ],
            ),
            slider(
                cid=f"{module_id}-f",
                label="频率 f (Hz)",
                vmin=0.5,
                vmax=100,
                step=0.5,
                value=10,
                unit=" Hz",
                help_text="用于波形与“同步转速”读数：2 极电机近似 n_sync≈60f rpm（教学）。",
            ),
            slider(
                cid=f"{module_id}-I0",
                label="电流幅值 I0 (arb.)",
                vmin=0.0,
                vmax=2.0,
                step=0.02,
                value=1.0,
                unit="",
            ),
            slider(
                cid=f"{module_id}-phi",
                label="相位差 Δφ（仅电容模式）",
                vmin=0,
                vmax=180,
                step=1,
                value=90,
                unit="°",
            ),
            slider(
                cid=f"{module_id}-ratio",
                label="辅助绕组电流比例（仅电容模式）",
                vmin=0.0,
                vmax=1.5,
                step=0.01,
                value=0.7,
                unit="",
            ),
            slider(
                cid=f"{module_id}-t0",
                label="时间位置（相位）",
                vmin=0.0,
                vmax=1.0,
                step=0.001,
                value=0.0,
                unit=" 周期",
                help_text="拖动观察矢量端点随时间旋转/往返。",
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
        data=[
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="端点轨迹", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[0, 0.5], y=[0, 0.2], mode="lines", name="合成磁场矢量", line=dict(color="#a6e22e", width=3)),
            go.Scatter(x=[0.5], y=[0.2], mode="markers", name="当前端点", marker=dict(size=10, color="#ff6b6b")),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=50, r=20, t=40, b=45),
            title="合成磁场矢量：端点轨迹（单相=线段，三相≈圆）",
            xaxis_title="B_x (arb.)",
            yaxis_title="B_y (arb.)",
            xaxis=dict(scaleanchor="y", scaleratio=1),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    fig1 = go.Figure(
        data=[
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="I_a", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=[0, 1], y=[0, 0], mode="lines", name="|B|", line=dict(color="#a6e22e", width=2), yaxis="y2"),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="相电流（电路）与 |B|(电磁场) 随时间",
            xaxis_title="t (ms)",
            yaxis_title="I (arb.)",
            yaxis2=dict(title="|B| (arb.)", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“单相交流一定产生旋转磁场”：不对。单相主要是脉动磁场；要形成旋转需要相位差（两相/三相）。</li>
      <li>“三相电流相加会互相抵消所以没磁场”：电流的空间方向不同，叠加得到的是<strong>旋转矢量</strong>而非恒为零。</li>
      <li>“频率越高转得越快越好”：同步转速随频率增大，但损耗、铁心涡流等也会增加（工程细节此处不展开）。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>引导问题</summary>
      <ol>
        <li><b>预测</b>：单相模式下，端点轨迹会是圆还是线？为什么？</li>
        <li><b>验证</b>：切到三相模式，观察 |B| 是否近似恒定；这对“转矩平稳”意味着什么？</li>
        <li><b>解释</b>：用“相位差”解释电容模式中端点轨迹为什么变成椭圆。</li>
        <li><b>拓展</b>：如果辅助绕组比例太小/太大，会发生什么？如何让椭圆更接近圆？</li>
      </ol>
    </details>
    """

    data_payload = {
        "defaults": {"mode": "three", "f": 10, "I0": 1.0, "phi": 90, "ratio": 0.7, "t0": 0.0}
    }

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);
      const els = {{
        mode: root.querySelector("#{module_id}-mode"),
        f: root.querySelector("#{module_id}-f"),
        I0: root.querySelector("#{module_id}-I0"),
        phi: root.querySelector("#{module_id}-phi"),
        ratio: root.querySelector("#{module_id}-ratio"),
        t0: root.querySelector("#{module_id}-t0"),
        play: root.querySelector("#{module_id}-play"),
        reset: root.querySelector("#{module_id}-reset"),
      }};

      emlabBindValue(root, "{module_id}-f", " Hz", 1);
      emlabBindValue(root, "{module_id}-I0", "", 2);
      emlabBindValue(root, "{module_id}-phi", "°", 0);
      emlabBindValue(root, "{module_id}-ratio", "", 2);
      emlabBindValue(root, "{module_id}-t0", "周期", 3);

      const figVec = document.getElementById("fig-{module_id}-0");
      const figCur = document.getElementById("fig-{module_id}-1");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"同步转速 n_sync（2极）", id:"{module_id}-ro-n", value:"—"}},
        {{key:"旋转质量 min|B|/max|B|", id:"{module_id}-ro-q", value:"—"}},
        {{key:"提示", id:"{module_id}-ro-tip", value:"—"}},
      ]);

      let timer = null;
      function stop(){{ if(timer){{ clearInterval(timer); timer=null; }} }}

      function compute(mode, f, I0, phiDeg, ratio){{
        const N = 420;
        const T = 1/Math.max(1e-6, f);
        const t = new Array(N);
        const ia = new Array(N);
        const ib = new Array(N);
        const ic = new Array(N);
        const bx = new Array(N);
        const by = new Array(N);
        const w = 2*Math.PI*f;
        const phi = phiDeg*Math.PI/180;
        for(let i=0;i<N;i++){{
          const tt = T*i/(N-1);
          t[i] = 1000*tt;
          let Ia=0, Ib=0, Ic=0, Bx=0, By=0;
          if(mode === "single"){{
            Ia = I0*Math.sin(w*tt);
            Bx = Ia; By = 0;
          }} else if(mode === "three"){{
            Ia = I0*Math.sin(w*tt);
            Ib = I0*Math.sin(w*tt - 2*Math.PI/3);
            Ic = I0*Math.sin(w*tt + 2*Math.PI/3);
            // winding axes: 0°, 120°, 240°
            const u0 = [1,0];
            const u1 = [Math.cos(2*Math.PI/3), Math.sin(2*Math.PI/3)];
            const u2 = [Math.cos(4*Math.PI/3), Math.sin(4*Math.PI/3)];
            Bx = Ia*u0[0] + Ib*u1[0] + Ic*u2[0];
            By = Ia*u0[1] + Ib*u1[1] + Ic*u2[1];
          }} else {{
            // cap: two-phase (orthogonal axes) with phase shift
            Ia = I0*Math.sin(w*tt);
            Ib = ratio*I0*Math.sin(w*tt - phi);
            Bx = Ia;
            By = Ib;
          }}
          ia[i]=Ia; ib[i]=Ib; ic[i]=Ic; bx[i]=Bx; by[i]=By;
        }}
        const bmag = bx.map((v,i)=>Math.hypot(v, by[i]));
        const bmin = Math.min(...bmag), bmax = Math.max(...bmag);
        return {{t, ia, ib, ic, bx, by, bmag, bmin, bmax}};
      }}

      function update(){{
        const mode = els.mode.value;
        els.phi.disabled = (mode !== "cap");
        els.ratio.disabled = (mode !== "cap");
        const f = emlabNum(els.f.value);
        const I0 = emlabNum(els.I0.value);
        const phi = emlabNum(els.phi.value);
        const ratio = emlabNum(els.ratio.value);
        const t0 = emlabNum(els.t0.value);

        const s = compute(mode, f, I0, phi, ratio);
        const idx = Math.max(0, Math.min(s.t.length-1, Math.round(t0*(s.t.length-1))));

        // vector plot
        Plotly.restyle(figVec, {{
          x:[s.bx, [0, s.bx[idx]], [s.bx[idx]]],
          y:[s.by, [0, s.by[idx]], [s.by[idx]]]
        }}, [0,1,2]);

        // currents + |B| (use markers + time line to link with vector plot)
        let traces = [];
        let marks = [];
        const tPick = s.t[idx];
        if(mode === "single"){{
          traces = [
            {{x:s.t, y:s.ia, mode:"lines", name:"I_a", line:{{color:"#66d9ef", width:2}}}},
          ];
          marks = [
            {{x:[tPick], y:[s.ia[idx]], mode:"markers", marker:{{size:8, color:"#66d9ef"}}, showlegend:false, hoverinfo:"skip"}},
          ];
          root.querySelector("#{module_id}-ro-tip").textContent = "单相：端点往返，起动困难（定性）。";
        }} else if(mode === "three"){{
          traces = [
            {{x:s.t, y:s.ia, mode:"lines", name:"I_a", line:{{color:"#66d9ef", width:2}}}},
            {{x:s.t, y:s.ib, mode:"lines", name:"I_b", line:{{color:"#a6e22e", width:2}}}},
            {{x:s.t, y:s.ic, mode:"lines", name:"I_c", line:{{color:"#ff6b6b", width:2}}}},
          ];
          marks = [
            {{x:[tPick], y:[s.ia[idx]], mode:"markers", marker:{{size:8, color:"#66d9ef"}}, showlegend:false, hoverinfo:"skip"}},
            {{x:[tPick], y:[s.ib[idx]], mode:"markers", marker:{{size:8, color:"#a6e22e"}}, showlegend:false, hoverinfo:"skip"}},
            {{x:[tPick], y:[s.ic[idx]], mode:"markers", marker:{{size:8, color:"#ff6b6b"}}, showlegend:false, hoverinfo:"skip"}},
          ];
          root.querySelector("#{module_id}-ro-tip").textContent = "三相：端点近圆周，|B| 近恒定。";
        }} else {{
          traces = [
            {{x:s.t, y:s.ia, mode:"lines", name:"I_main", line:{{color:"#66d9ef", width:2}}}},
            {{x:s.t, y:s.ib, mode:"lines", name:"I_aux", line:{{color:"#a6e22e", width:2}}}},
          ];
          marks = [
            {{x:[tPick], y:[s.ia[idx]], mode:"markers", marker:{{size:8, color:"#66d9ef"}}, showlegend:false, hoverinfo:"skip"}},
            {{x:[tPick], y:[s.ib[idx]], mode:"markers", marker:{{size:8, color:"#a6e22e"}}, showlegend:false, hoverinfo:"skip"}},
          ];
          root.querySelector("#{module_id}-ro-tip").textContent = "电容相移：端点椭圆（相位差越接近 90°越接近圆）。";
        }}
        traces.push({{x:s.t, y:s.bmag, mode:"lines", name:"|B|", line:{{color:"rgba(255,255,255,0.85)", width:1.5, dash:"dot"}}, yaxis:"y2"}});
        marks.push({{x:[tPick], y:[s.bmag[idx]], mode:"markers", marker:{{size:8, color:"rgba(255,255,255,0.85)"}}, yaxis:"y2", showlegend:false, hoverinfo:"skip"}});
        const allTraces = traces.concat(marks);

        const layout = {{
          template:"plotly_dark",
          margin:{{l:55,r:20,t:40,b:45}},
          title:"相电流（电路）与 |B|(电磁场) 随时间",
          xaxis:{{title:"t (ms)"}},
          yaxis:{{title:"I (arb.)"}},
          yaxis2:{{title:"|B| (arb.)", overlaying:"y", side:"right", showgrid:false}},
          shapes:[{{
            type:"line",
            x0:tPick, x1:tPick,
            y0:0, y1:1,
            xref:"x", yref:"paper",
            line:{{color:"rgba(255,255,255,0.35)", width:1, dash:"dot"}}
          }}],
          legend:{{orientation:"h", yanchor:"bottom", y:1.02, xanchor:"left", x:0}},
        }};
        Plotly.react(figCur, allTraces, layout, {{displaylogo:false, responsive:true}});
        if(figCur && figCur.on && !figCur.dataset.emlabPick){{
          figCur.dataset.emlabPick = "1";
          figCur.on("plotly_click", (ev) => {{
            if(!ev || !ev.points || !ev.points.length) return;
            const xms = ev.points[0].x;
            if(!isFinite(xms)) return;
            const fNow = Math.max(1e-9, emlabNum(els.f.value));
            let tt = (xms/1000.0) * fNow;
            if(!isFinite(tt)) return;
            tt = Math.max(0.0, Math.min(1.0, tt));
            els.t0.value = tt.toFixed(3);
            const span = root.querySelector("#{module_id}-t0-val");
            if(span) span.textContent = emlabFmt(tt,3) + "周期";
            update();
          }});
        }}

        // readouts
        root.querySelector("#{module_id}-ro-n").textContent = emlabFmt(60*f, 1) + " rpm";
        const q = (s.bmax>1e-9) ? (s.bmin/s.bmax) : 0;
        root.querySelector("#{module_id}-ro-q").textContent = emlabFmt(q, 3);
      }}

      function togglePlay(){{
        if(timer){{ stop(); return; }}
        timer = setInterval(() => {{
          if(!root.classList.contains("active")) {{ stop(); return; }}
          let v = emlabNum(els.t0.value);
          v += 0.005;
          if(v > 1.0) v -= 1.0;
          els.t0.value = v.toFixed(3);
          const span = root.querySelector("#{module_id}-t0-val");
          if(span) span.textContent = emlabFmt(v,3) + "周期";
          update();
        }}, 33);
      }}

      function reset(){{
        stop();
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
        "title": "M04 交流电机：旋转磁场可视化",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }
