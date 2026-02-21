from __future__ import annotations

import math
from typing import Literal

import numpy as np
import plotly.graph_objects as go

from emlab.common.htmlbits import buttons, select, slider


def _make_phantom(n: int = 64) -> np.ndarray:
    y, x = np.mgrid[-1:1 : complex(n), -1:1 : complex(n)]
    img = np.zeros((n, n), dtype=float)

    def add_ellipse(x0, y0, a, b, angle_deg, value):
        ang = math.radians(angle_deg)
        xr = (x - x0) * math.cos(ang) + (y - y0) * math.sin(ang)
        yr = -(x - x0) * math.sin(ang) + (y - y0) * math.cos(ang)
        mask = (xr / a) ** 2 + (yr / b) ** 2 <= 1.0
        img[mask] += value

    add_ellipse(0.0, 0.0, 0.85, 0.65, 0, 0.9)
    add_ellipse(-0.25, 0.10, 0.25, 0.12, 20, 0.25)
    add_ellipse(0.25, 0.18, 0.20, 0.10, -35, 0.22)
    add_ellipse(0.18, -0.25, 0.18, 0.14, 10, 0.18)
    add_ellipse(-0.15, -0.28, 0.18, 0.10, -10, 0.15)
    img = np.clip(img, 0.0, 1.0)
    return img


def _radon_fallback(img: np.ndarray, angles_deg: np.ndarray) -> np.ndarray:
    from scipy.ndimage import rotate

    n = img.shape[0]
    sino = np.zeros((n, len(angles_deg)), dtype=float)
    for i, ang in enumerate(angles_deg):
        rot = rotate(img, float(ang), reshape=False, order=1, mode="constant", cval=0.0)
        sino[:, i] = rot.sum(axis=0)
    return sino


def _ramp_filter(proj: np.ndarray) -> np.ndarray:
    # proj: (n_det, n_angles)
    n = proj.shape[0]
    freqs = np.fft.rfftfreq(n).reshape(-1, 1)
    filt = np.abs(freqs)
    P = np.fft.rfft(proj, axis=0)
    return np.fft.irfft(P * filt, n=n, axis=0)


def _iradon_fallback(
    sino: np.ndarray, angles_deg: np.ndarray, method: Literal["bp", "fbp"]
) -> np.ndarray:
    from scipy.ndimage import rotate

    n = sino.shape[0]
    proj = sino if method == "bp" else _ramp_filter(sino)
    recon = np.zeros((n, n), dtype=float)
    for i, ang in enumerate(angles_deg):
        back = np.tile(proj[:, i], (n, 1))
        recon += rotate(back, -float(ang), reshape=False, order=1, mode="constant", cval=0.0)
    recon *= math.pi / (2.0 * len(angles_deg))
    recon = np.clip(recon, 0.0, None)
    return recon


def _radon(img: np.ndarray, angles_deg: np.ndarray) -> np.ndarray:
    try:
        from skimage.transform import radon

        return radon(img, theta=angles_deg, circle=False).astype(float)
    except Exception:
        return _radon_fallback(img, angles_deg)


def _iradon(img: np.ndarray, angles_deg: np.ndarray, method: Literal["bp", "fbp"]) -> np.ndarray:
    try:
        from skimage.transform import iradon

        if method == "bp":
            return iradon(img, theta=angles_deg, filter_name=None, circle=False).astype(float)
        return iradon(img, theta=angles_deg, filter_name="ramp", circle=False).astype(float)
    except Exception:
        return _iradon_fallback(img, angles_deg, method=method)


def build() -> dict:
    module_id = "xct_ct"

    intro_html = """
    <p>
      XCT（X-ray CT）把许多角度的“投影”（线积分）组织成 <b>正弦图(sinogram)</b>，再用数学重建得到截面图像。
      直观理解：角度越多，重建越接近原图；角度太少会产生条纹伪影。
    </p>
    <p>
      本页面用简化模型演示：phantom → Radon 投影 → sinogram → 反投影/滤波反投影(FBP) 重建。
      为保证离线交互性能，重建结果在 Python 端对离散参数做了预计算。
    </p>
    """

    n = 64
    phantom = _make_phantom(n)

    angles_opts = [30, 60, 90, 180]
    sigma_opts = [0.0, 0.02, 0.05, 0.10]
    rng = np.random.default_rng(123)

    sinograms: list[list[list[list[float]]]] = []  # [a][s] -> 2d list
    recon_bp: list[list[list[list[float]]]] = []
    recon_fbp: list[list[list[list[float]]]] = []

    for na in angles_opts:
        angles = np.linspace(0, 180, na, endpoint=False)
        sino_clean = _radon(phantom, angles)
        maxv = float(np.max(sino_clean)) if np.max(sino_clean) > 0 else 1.0

        sino_for_na: list[list[list[float]]] = []
        bp_for_na: list[list[list[float]]] = []
        fbp_for_na: list[list[list[float]]] = []
        for sig in sigma_opts:
            noise = rng.normal(0.0, sig * maxv, size=sino_clean.shape)
            sino = sino_clean + noise
            bp = _iradon(sino, angles, method="bp")
            fbp = _iradon(sino, angles, method="fbp")

            sino_for_na.append(sino.astype(float).tolist())
            bp_for_na.append(bp.astype(float).tolist())
            fbp_for_na.append(fbp.astype(float).tolist())

        sinograms.append(sino_for_na)
        recon_bp.append(bp_for_na)
        recon_fbp.append(fbp_for_na)

    controls_html = "\n".join(
        [
            select(
                cid=f"{module_id}-N",
                label="投影角度数 N_angles",
                value="90",
                options=[(str(v), str(v)) for v in angles_opts],
                help_text="角度越多，重建越好，但采集/计算成本也更高。",
            ),
            select(
                cid=f"{module_id}-sigma",
                label="噪声水平 σ（相对）",
                value="0.02",
                options=[(f"{v:.2f}", f"{v:.2f}") for v in sigma_opts],
                help_text="σ 越大，sinogram 越“花”，重建噪声与伪影更明显。",
            ),
            slider(
                cid=f"{module_id}-kVp",
                label="管电压 kVp（简化映射到衰减系数）",
                vmin=60,
                vmax=120,
                step=1,
                value=80,
                unit=" kVp",
                help_text="这里只做“衰减整体缩放”的教学近似：kVp 越高，等效衰减越小。",
            ),
            slider(
                cid=f"{module_id}-py",
                label="剖线位置 y（像素行）",
                vmin=0,
                vmax=n - 1,
                step=1,
                value=n // 2,
                unit="",
                help_text="用于“剖线曲线”：比较 phantom、BP、FBP 在同一行的强度分布。",
            ),
            select(
                cid=f"{module_id}-diff",
                label="差分显示",
                value="signed",
                options=[("signed", "FBP - BP（有符号）"), ("abs", "|FBP - BP|（绝对值）")],
            ),
            buttons([(f"{module_id}-reset", "重置参数", "primary")]),
        ]
    )

    # figures
    fig0 = go.Figure(
        data=[go.Heatmap(z=phantom.tolist(), colorscale="Gray", showscale=False)],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=30, r=10, t=40, b=30),
            title="原图 phantom（截面衰减系数 μ 的简化示意）",
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False, scaleanchor="x"),
        ),
    )

    fig1 = go.Figure(
        data=[go.Heatmap(z=sinograms[2][1], colorscale="Viridis", colorbar=dict(title="∫μds"))],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=50, r=10, t=40, b=45),
            title="Sinogram（投影数据）",
            xaxis_title="角度索引",
            yaxis_title="探测器索引",
        ),
    )

    fig2 = go.Figure(
        data=[go.Heatmap(z=recon_bp[2][1], colorscale="Gray", showscale=False)],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=30, r=10, t=40, b=30),
            title="重建：简单反投影 BP",
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False, scaleanchor="x"),
        ),
    )

    fig3 = go.Figure(
        data=[go.Heatmap(z=recon_fbp[2][1], colorscale="Gray", showscale=False)],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=30, r=10, t=40, b=30),
            title="重建：滤波反投影 FBP",
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False, scaleanchor="x"),
        ),
    )

    # difference (placeholder)
    diff0 = (np.array(recon_fbp[2][1]) - np.array(recon_bp[2][1])).tolist()
    fig4 = go.Figure(
        data=[go.Heatmap(z=diff0, colorscale="RdBu", zmid=0, colorbar=dict(title="Δ"))],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=40, r=10, t=40, b=30),
            title="差分：FBP - BP（突出边缘/伪影差异）",
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False, scaleanchor="x"),
        ),
    )

    x_idx = np.arange(n)
    prof0 = phantom[n // 2, :].astype(float)
    prof_bp0 = np.array(recon_bp[2][1])[n // 2, :].astype(float)
    prof_fbp0 = np.array(recon_fbp[2][1])[n // 2, :].astype(float)
    fig5 = go.Figure(
        data=[
            go.Scatter(x=x_idx.tolist(), y=prof0.tolist(), mode="lines", name="phantom", line=dict(color="#ffffff", width=2)),
            go.Scatter(x=x_idx.tolist(), y=prof_bp0.tolist(), mode="lines", name="BP", line=dict(color="#66d9ef", width=2)),
            go.Scatter(x=x_idx.tolist(), y=prof_fbp0.tolist(), mode="lines", name="FBP", line=dict(color="#a6e22e", width=2)),
        ],
        layout=go.Layout(
            template="plotly_dark",
            margin=dict(l=55, r=20, t=40, b=45),
            title="剖线对比（同一行 y 的强度分布）",
            xaxis_title="像素 x",
            yaxis_title="μ（相对）",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        ),
    )

    pitfalls_html = """
    <ul>
      <li>“CT 就是把很多张照片叠加”：不对。CT 的核心是 <b>投影数据</b> 与 <b>数学重建</b>（Radon 变换思想）。</li>
      <li>“角度越多就一定完全没噪声”：角度多能减小欠采样伪影，但噪声仍会通过重建传播。</li>
      <li>“FBP 是魔法”：FBP 本质是在反投影前对投影做滤波（补偿反投影的低频过强）。</li>
    </ul>
    """

    questions_html = """
    <details open>
      <summary>引导问题</summary>
      <ol>
        <li><b>预测</b>：把 N_angles 从 30 改到 180，sinogram 会变“密”还是“稀”？重建条纹会如何变化？</li>
        <li><b>验证</b>：固定 σ，对比 BP 与 FBP。哪一种边缘更清晰？为什么需要“滤波”？</li>
        <li><b>解释</b>：用“线积分/投影”的语言解释：为什么一个点在 sinogram 上会画出一条正弦样曲线？</li>
        <li><b>拓展</b>：真实 CT 中还有哪些会影响重建质量？（散射、硬化、运动、有限探测器……）</li>
      </ol>
    </details>
    """

    data_payload = {
        "size": n,
        "angles_opts": angles_opts,
        "sigma_opts": sigma_opts,
        "kVp_ref": 80,
        "phantom": phantom.astype(float).tolist(),
        "sinograms": sinograms,  # [a][s] -> 2d
        "recon_bp": recon_bp,
        "recon_fbp": recon_fbp,
        "defaults": {"N": "90", "sigma": "0.02", "kVp": 80, "py": n // 2, "diff": "signed"},
    }

    js = rf"""
    function init_{module_id}(){{
      const id = "{module_id}";
      const root = document.getElementById("section-"+id);
      const data = emlabGetJSON("data-"+id);
      const els = {{
        N: root.querySelector("#{module_id}-N"),
        sigma: root.querySelector("#{module_id}-sigma"),
        kVp: root.querySelector("#{module_id}-kVp"),
        py: root.querySelector("#{module_id}-py"),
        diff: root.querySelector("#{module_id}-diff"),
        reset: root.querySelector("#{module_id}-reset"),
      }};

      emlabBindValue(root, "{module_id}-kVp", " kVp", 0);
      emlabBindValue(root, "{module_id}-py", "", 0);

      const figP = document.getElementById("fig-{module_id}-0");
      const figS = document.getElementById("fig-{module_id}-1");
      const figBP = document.getElementById("fig-{module_id}-2");
      const figFBP = document.getElementById("fig-{module_id}-3");
      const figD = document.getElementById("fig-{module_id}-4");
      const figProf = document.getElementById("fig-{module_id}-5");

      const readouts = root.querySelector("#readouts-"+id);
      emlabMakeReadouts(readouts, [
        {{key:"读数：N_angles", id:"{module_id}-ro-N", value:"—"}},
        {{key:"读数：σ", id:"{module_id}-ro-s", value:"—"}},
        {{key:"读数：kVp 映射", id:"{module_id}-ro-k", value:"—"}},
        {{key:"质量：NRMSE(BP)", id:"{module_id}-ro-bp", value:"—"}},
        {{key:"质量：NRMSE(FBP)", id:"{module_id}-ro-fbp", value:"—"}},
        {{key:"剖线 y", id:"{module_id}-ro-y", value:"—"}},
      ]);

      function scale2d(z, s){{
        const out = new Array(z.length);
        for(let i=0;i<z.length;i++){{
          const row = z[i];
          const r2 = new Array(row.length);
          for(let j=0;j<row.length;j++) r2[j] = row[j]*s;
          out[i]=r2;
        }}
        return out;
      }}

      function diff2d(a, b, mode){{
        const out = new Array(a.length);
        for(let i=0;i<a.length;i++){{
          const ra = a[i], rb = b[i];
          const r2 = new Array(ra.length);
          for(let j=0;j<ra.length;j++) {{
            const d = (rb[j]-ra[j]);
            r2[j] = (mode === "abs") ? Math.abs(d) : d;
          }}
          out[i]=r2;
        }}
        return out;
      }}

      function nrmse(ref, img){{
        let s = 0, sr = 0, n = 0;
        for(let i=0;i<ref.length;i++){{
          const rr = ref[i], ii = img[i];
          for(let j=0;j<rr.length;j++) {{
            const d = (ii[j]-rr[j]);
            s += d*d;
            sr += rr[j]*rr[j];
            n += 1;
          }}
        }}
        const rmse = Math.sqrt(s/Math.max(1,n));
        const r0 = Math.sqrt(sr/Math.max(1,n));
        return rmse / Math.max(1e-12, r0);
      }}

      function update(){{
        const N = parseInt(els.N.value, 10);
        const sigma = parseFloat(els.sigma.value);
        const kVp = emlabNum(els.kVp.value);
        const py = Math.max(0, Math.min((data.size||64)-1, Math.round(emlabNum(els.py.value))));
        const diffMode = els.diff.value;

        const aIdx = (data.angles_opts || []).indexOf(N);
        const sIdx = (data.sigma_opts || []).indexOf(sigma);
        const ref = emlabNum(data.kVp_ref || 80);
        let scale = ref / Math.max(1e-6, kVp);
        scale = Math.max(0.4, Math.min(1.6, Math.pow(scale, 0.8)));

        const phantom = data.phantom || [];
        const sino = (data.sinograms && data.sinograms[aIdx] && data.sinograms[aIdx][sIdx]) ? data.sinograms[aIdx][sIdx] : [];
        const bp = (data.recon_bp && data.recon_bp[aIdx] && data.recon_bp[aIdx][sIdx]) ? data.recon_bp[aIdx][sIdx] : [];
        const fbp = (data.recon_fbp && data.recon_fbp[aIdx] && data.recon_fbp[aIdx][sIdx]) ? data.recon_fbp[aIdx][sIdx] : [];
        const dimg = diff2d(bp, fbp, diffMode);

        Plotly.restyle(figP, {{z:[scale2d(phantom, scale)]}}, [0]);
        Plotly.restyle(figS, {{z:[scale2d(sino, scale)]}}, [0]);
        Plotly.restyle(figBP, {{z:[scale2d(bp, scale)]}}, [0]);
        Plotly.restyle(figFBP, {{z:[scale2d(fbp, scale)]}}, [0]);
        if(diffMode === "abs"){{
          Plotly.restyle(figD, {{z:[scale2d(dimg, scale)], colorscale:["Viridis"], zmid:[null]}}, [0]);
        }} else {{
          Plotly.restyle(figD, {{z:[scale2d(dimg, scale)], colorscale:["RdBu"], zmid:[0]}}, [0]);
        }}

        // profile line at row py
        const npx = (data.size||64);
        const x = Array.from({{length:npx}}, (_,i)=>i);
        const pRow = phantom[py] || [];
        const bpRow = bp[py] || [];
        const fbpRow = fbp[py] || [];
        Plotly.restyle(figProf, {{x:[x,x,x], y:[pRow.map(v=>v*scale), bpRow.map(v=>v*scale), fbpRow.map(v=>v*scale)]}}, [0,1,2]);

        root.querySelector("#{module_id}-ro-N").textContent = N.toString();
        root.querySelector("#{module_id}-ro-s").textContent = sigma.toFixed(2);
        root.querySelector("#{module_id}-ro-k").textContent = "μ×"+emlabFmt(scale, 3)+"（教学近似）";
        root.querySelector("#{module_id}-ro-y").textContent = py.toString();
        if(phantom.length && bp.length) {{
          root.querySelector("#{module_id}-ro-bp").textContent = emlabFmt(nrmse(phantom, bp), 3);
          root.querySelector("#{module_id}-ro-fbp").textContent = emlabFmt(nrmse(phantom, fbp), 3);
        }}
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
        "title": "M03 XCT/CT：投影→正弦图→重建",
        "intro_html": intro_html,
        "controls_html": controls_html,
        "figures": [fig0, fig1, fig2, fig3, fig4, fig5],
        "data_payload": data_payload,
        "js": js,
        "pitfalls_html": pitfalls_html,
        "questions_html": questions_html,
    }
