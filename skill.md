# EMLab 实现经验总结（Skill）

面向本仓库：用 **Python 生成 Plotly 图 + 原生 JS 控件回调**，最终合成 **离线单文件** `dist/emlab.html`。

## 目标与硬约束（先统一认知）

- 交付物：`dist/emlab.html`（双击打开可用，不依赖服务端/不依赖网络，release 模式 Plotly.js 必须内联）。
- 模块接口：每个模块实现 `build() -> dict`（`id/title/intro_html/controls_html/figures/data_payload/js/pitfalls_html/questions_html`）。
- 性能：浏览器端更新尽量 `O(N)`（单曲线点数建议 ≤ 2000）；重计算（ODE/重建/卷积）必须 **Python 端预计算**，前端查表/插值。
- 安全边界：涉及“导轨电磁弹射/rail launcher”仅限理想化仿真与课堂讨论，避免任何现实可执行的制造/装配/危险操作细节。

## 代码结构与职责分离（最省心）

- `emlab/src/emlab/site.py`：拼装整页 HTML（模板、导航、通用 JS helpers、模块注册）。
- `emlab/src/emlab/common/htmlbits.py`：控件 HTML 生成（slider/select/buttons/number）。
- `emlab/src/emlab/modules/*.py`：模块本体（生成初始图 + data payload + 前端更新 js）。
- `build.py` / `emlab/build.py`：构建入口（release 内联 plotly.js；debug 可用 CDN）。

经验：**不要**让模块之间互相引用 DOM；模块 JS 只操作自己 section 内的元素，避免联动串台。

## 模块开发清单（从 0 到可交互）

1) **先写“看懂的 intro”**：高中层级能跟上，短句 + 关键公式 + 解释变量含义。
2) **控件 ≥3 个**：用 `slider/select/buttons` 生成；给 slider 配好 `step`（太大会“对不准共振”）。
3) **输出 ≥2 个**：主图 + 辅图/读数（`emlabMakeReadouts`）。
4) **data_payload**：
   - 小计算：可不预计算，直接前端算点列。
   - 大计算：Python 端离散档（每 slider ≤25 档，2D 网格可插值）。
5) **JS update()**：
   - 从控件读值（`emlabNum(...)`）
   - 计算/查表得到新数据
   - `Plotly.restyle(...)`（优先）或 `Plotly.react(...)`（trace 数量/结构会变时）
   - 更新 readouts 文本
6) **误区 ≥3 条 + 引导题 ≥3 条**：用 `<ul>`/`<details>`，是验收必需项。

## Plotly 更新套路（稳定、快、少踩坑）

- **数据不变形**（trace 数量固定）：
  - 用 `Plotly.restyle(div, {x:[...], y:[...], z:[...]}, [traceIdx...])`
- **trace 数量/类型会变**（例如不同模式显示不同曲线/marker）：
  - 用 `Plotly.react(div, traces, layout, config)`，但注意：
    - 点击事件要做“一次性绑定”保护：`if(div.on && !div.dataset.emlabPick){...}`
    - `Plotly.react` 会重建图，但事件绑定仍可保留；仍建议用 dataset guard 防重复绑定。
- **只改标线/游标**（角度线、时间线）：
  - 用 `Plotly.relayout(div, {shapes:[...]})`（比重画快很多）

## “两图联动”的通用做法（已经验证好用）

目标：A 图选中某个参数位置（t/角度/索引），B 图显示对应点，并能反向点击 B 图驱动 A 图。

- 状态变量：`pickIdx`（或 `t0`、`scanIdx`）放在模块闭包内。
- A 图：
  - 用 marker 显示当前位置（`[pickIdx]`）。
- B 图：
  - 加一条 `shapes` 竖线/横线作为游标。
  - 同步 marker（当前点）帮助视觉定位。
  - `plotly_click`：读 `ev.points[0].x` 或 `.y` → 映射回状态变量 → `update()`.

例子：
- M04：矢量端点 ↔ 电流波形（时间游标 + marker + 点击波形设置相位）。
- M03：phantom 旋转采集角度线 ↔ sinogram 列游标（播放角度、点击 sinogram 跳角度）。

## 动画（Play/Pause）建议模板

- 统一按钮：`播放/暂停`（或更明确的 “旋转采集/暂停”）。
- `timer = setInterval(..., 33~120ms)`，每 tick 只更新“必要的小量数据/游标”：
  - 大图像/重建结果不要每帧全量 restyle（会卡）。
  - 用 `relayout(shapes)` + 小曲线 `restyle`（例如投影 `p(s)`）。
- 隐藏模块时必须停表：tick 内检查 `root.classList.contains("active")`，不 active 就 `stop()`。

## 参数与 UI 体验（来自实际反馈）

- slider step：
  - 共振/频率相关：`step` 要小（例如 `1Hz` 或更小），否则“对不准”。
  - 角度/离散档：用 `select`（30/60/90/180）比 range 更稳。
- legend：
  - 默认隐藏“只起标注作用的点”（`showlegend=False`），避免图例爆炸。
- 读数：
  - 不命中/不适用的情况给明确文字（例如“未击中屏”），别留空。

## release 构建与提交前检查（减少返工）

1) `python -m py_compile $(git ls-files '*.py')`
2) `python build.py --mode release`
3) 打开 `dist/emlab.html` 快速人工点检：
   - 切换 tabs 后旧模块动画是否停止
   - play/pause 是否真的让“图动起来”
   - 多图联动是否一致（游标/marker 对齐）
4) 提交时带上 `dist/emlab.html`（保证交付物一致）。

## 常见坑（踩过的就别再踩）

- 只更新了一张图，另一张图看起来“没联动”：通常是缺游标/marker 或缺反向点击映射。
- `Plotly.react` 传错 traces 变量：新增 markers 但没 concat 进去，会导致“看起来没生效”。
- 动画“播放了但图不动”：每 tick 只改了状态变量没触发 restyle/relayout，或被模块隐藏停表逻辑拦截。
- 过多 trace / 过多点数：浏览器交互明显卡顿，尤其在单文件离线环境。

