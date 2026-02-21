# SPEC：高中物理《电磁场与电路》交互可视化实验室（Python 生成交互图 → 合成单文件 HTML）

> 目标：把“电磁场 + 电路原理”用**可调参数的交互图**讲清楚，面向高中课堂演示 / 学生探究。  
> 交付：`dist/emlab.html`（一个大 HTML，双击即可打开，不依赖后端服务）。

---

## 0. 术语与范围约定

- **XCT**：按 *X-ray computed tomography*（X 射线计算机断层成像 / CT）理解。
- **安全边界（重要）**：涉及“电磁弹射导轨（rail launcher/railgun 类）”仅做**理想化物理与电路仿真**和课堂讨论；不提供现实可执行的制造、材料选型、加工、装配、危险操作指导或“提高威力/效率”的实操建议。

---

## 1. 学习目标（面向高中）

每个模块必须同时覆盖：

1) **电磁场核心**：电场/磁场来源与方向、随时间变化、洛伦兹力、法拉第电磁感应、能量观点。  
2) **电路核心**：电源模型、R/L/C 动态、波形与相位、功率与能量、测量与仪表。  
3) **可见化**：把“看不见的场/电流/相位/轨迹”变成**拖动参数立即看到变化**。

---

## 2. 交付物与交互体验

### 2.1 单文件 HTML（强制）
- 输出：`dist/emlab.html`
- **不启用任何 server**（无 Dash、无 Flask、无后端）。
- 打开 HTML 后：
  - 模块切换（Tabs 或侧边栏导航）
  - 每个模块左侧参数控件、右侧图表区域（主图+辅图）
  - “重置参数”“播放/暂停（需要动画时）”“导出截图（可选）”

### 2.2 交互控件方式（两条路线，二选一或混用）
- **路线 A（推荐）**：原生 HTML `<input type="range"> / <select>` + 原生 JS 回调 + Plotly 更新图
- **路线 B（补充）**：Plotly figure 内置 slider / updatemenus（适合参数维度少、可预计算的情况）

> 约束：无后端情况下，复杂数值仿真应采用**预计算网格 + 前端查表/插值**，避免把大规模 ODE 求解搬到浏览器。

---

## 3. 技术栈与依赖（不包含 Bokeh）

### 3.1 Python 依赖（建议）
- Python 3.10+
- `numpy`, `scipy`
- `plotly>=5`（图表与动画，最终写入 HTML）
- `scikit-image`（CT 的 radon/iradon，推荐；无则降级）
- `jinja2`（HTML 模板拼装，推荐）

### 3.2 前端依赖策略（必须满足“单文件”）
- Plotly.js 必须 **内联**：
  - `plotly.io.to_html(fig, include_plotlyjs="inline", full_html=False)` 或
  - `fig.write_html(..., include_plotlyjs="inline")`（不推荐直接写 full_html，多模块更适合片段拼装）
- 其余 JS/CSS 全部写进 `<script>` / `<style>`，不依赖 CDN（release 模式）。

---

## 4. 代码组织（强制）

```

emlab/
README.md
requirements.txt
build.py
src/emlab/
**init**.py
site.py              # 汇总模块、拼装 HTML（Jinja2）
common/
units.py           # 常量、单位转换、符号约定
physics.py         # 通用公式：洛伦兹力、能量、相量、RLC 等
grids.py           # 预计算参数网格与插值工具
htmlbits.py        # 生成控件 HTML、通用 UI 片段、通用 JS
modules/
pendulum.py
crt_scope.py
xct_ct.py
ac_motor.py
rail_launcher.py
mass_spec.py
electron_microscope.py
cyclotron.py
linac.py
transformer.py
rlc_oscillation.py
wireless_power.py
hall_effect.py
speaker_microphone.py
induction_heating.py

````

---

## 5. 模块统一接口（强制）

每个模块文件必须实现：

```python
def build() -> dict:
    """
    返回一个 dict，包含：
    - id: 模块唯一字符串（用于 DOM id）
    - title: 标签标题
    - intro_html: 原理速览（HTML 字符串）
    - controls_html: 左侧控件（HTML 字符串）
    - figures: list[plotly.graph_objects.Figure]  # 初始图
    - data_payload: dict  # 预计算数据/参数网格（将被 json dump 到 HTML）
    - js: str  # 该模块专属的前端更新逻辑（绑定事件、Plotly.restyle/relayout/update）
    - pitfalls_html: 常见误区（HTML）
    - questions_html: 引导问题（HTML <details>）
    """
````

在 `site.py` 中注册：

```python
MODULES = [
  pendulum.build,
  crt_scope.build,
  xct_ct.build,
  ac_motor.build,
  rail_launcher.build,
  mass_spec.build,
  electron_microscope.build,
  cyclotron.build,
  linac.build,
  transformer.build,
  rlc_oscillation.build,
  wireless_power.build,
  hall_effect.build,
  speaker_microphone.build,
  induction_heating.build,
]
```

---

## 6. HTML 拼装规范（强制）

### 6.1 模板结构（建议）

* `<style>`：统一布局（左右栏、图表卡片、读数面板、Tabs）
* `<nav>`：模块导航（点击切换显示/隐藏 section）
* 每个模块 section：

  * `intro`（原理速览）
  * `controls`（参数区）
  * `figures`（Plotly div 容器）
  * `readouts`（数值读数，JS 更新 innerText）
  * `pitfalls`、`questions`

### 6.2 Plotly 图嵌入要求

* 每个 figure 用 `to_html(..., full_html=False, include_plotlyjs=False)` 生成片段
* 仅在整页顶部插入一次 plotly.js（inline）：

  * 第一个 figure 的 `include_plotlyjs="inline"` 输出中提取 plotly.js
  * 或者单独从 plotly 离线包生成并内联（实现者自行选择）

### 6.3 数据注入（强制）

* 每模块一个 `<script type="application/json" id="data-{module_id}">...</script>`
* JS 通过 `JSON.parse(document.getElementById(...).textContent)` 取数据

---

## 7. 性能与数值策略（强制）

* 前端实时计算必须是 **O(1)~O(N)**，N ≤ 2000（单条曲线点数）
* 需要 ODE/卷积/重建等重计算的模块：

  * Python 端对参数做**离散取样预计算**（每个 slider ≤ 25 档为宜）
  * 前端根据 slider 取最近档或双线性插值（参数 ≤ 2 维时）
* 图更新使用：

  * `Plotly.restyle(div, {...}, traceIndices)`
  * `Plotly.react(div, newData, newLayout)`（必要时）
* 动画采用：

  * 预生成 frames + `Plotly.animate`
  * 或定时器更新 trace（点数小、帧率 ≤ 30fps）

---

## 8. 模块规格（核心清单 + 交互设计）

每个模块必须包含：

* (A) 电磁场原理
* (B) 电路原理
* (C) 交互图与控件（≥3 个可调参数，≥2 个可观测输出）
* (D) 常见误区（至少 3 条）
* (E) 引导问题（至少 3 题）

---

# M01 电磁场中的单摆（至少 4 个变体）

## 变体 1：带电小球单摆 + 匀强电场（平行板）

(A) `F=qE` 与 `mg` 合成；平衡偏角 `θ_eq = arctan(qE/mg)`
(B) `E≈V/d`（定性边缘效应）
(C) 控件：

* `V`（板间电压）、`d`（板距）、`q/m`、`L`、`θ0`
  图：

1. 平衡位置示意（摆线+偏移）
2. `θ(t)` 或 `y(t)` 曲线（小角近似）
3. `T(V)` 或实时周期读数
   (D) 误区：电场改变周期的原因是合加速度大小变化；不是“电场直接改变 L”。

## 变体 2：金属摆片穿过磁场的电磁阻尼（涡流制动）

(A) 运动→磁通变化→感应电流→楞次定律阻碍运动
(B) 等效 `ε ∝ -dΦ/dt`，`P=I^2R` 耗散
(C) 控件：`B`、`R_eq`、`m`、`L`
图：振幅包络衰减、能量条（机械→热）
(D) 误区：磁力本身不做功，能量来自机械能损耗。

## 变体 3：磁铁单摆 + 线圈（阻尼随电阻可调）

(A) 磁通来自磁铁运动
(B) `I=ε/R`，阻尼随 `1/R` 增强（定性）
(C) 控件：`R_load`（短路/开路对比）、`B0`、`θ0`
图：`θ(t)` 对比（R 大小）

## 变体 4：电磁驱动单摆（脉冲驱动/共振）

(A) 线圈磁场对磁铁/铁芯产生力矩（定性）
(B) 脉冲电路（用理想方波源）
(C) 控件：驱动频率、占空比、幅值
图：稳态振幅随频率（共振曲线）

---

# M02 示波器 与 CRT（是否“一回事”）

页面必须明确：

* CRT 是显示器件；示波器是测量系统（老式模拟示波器常用 CRT；现代多 LCD）。

(A) 洛伦兹力，重点电场偏转：`y_screen ∝ V_def / V_acc`（定性+近似推导）
(B) 时基锯齿、触发、输入阻抗（高中层级）
(C) **必须交互：调电压→轨迹变化**
控件：

* `V_acc`（加速电压）
* `V_y`：波形类型（正弦/方波/三角/噪声）、幅值、频率
* `V_x`：时基周期/扫描速度
* 模式：Y-T / X-Y（李萨如）
* 数字示波器对比：采样率 `f_s`、量化位数 `Nbits`（演示混叠/台阶）
  图：

1. CRT 电子轨迹示意（分段解析）
2. 屏幕波形（Y-T）
3. 李萨如（X-Y）
   读数：`v_e`、偏转灵敏度、周期/频率测量
   (D) 误区：示波器≠CRT；采样不足会出现混叠。

---

# M03 XCT（X-ray CT）：投影 → 正弦图 → 重建

(A) 电子高压加速撞靶产生 X 射线（定性）
(B) 高压电源、探测器读出（功能块）
(C) 交互重点：为何能成像
控件：

* `N_angles`（30/60/90/180 离散选项）
* 噪声 `σ`
* `kVp`（用简化映射到衰减系数 µ）
  图：

1. phantom 原图
2. sinogram（Radon）
3. 重建：简单反投影 vs FBP
   实现：

* 优先 `skimage.transform.radon/iradon`
* 无 skimage：降级为低分辨率线积分近似 + 简单反投影
  (D) 误区：CT 不是“多张照片叠加”，而是投影数据的数学重建。

---

# M04 交流电机（单相/三相）：旋转磁场可视化

(A) 线圈电流→磁场；多相叠加→旋转磁场
(B) 单相脉动磁场起动差；三相 120° 相位差形成近恒幅旋转；单相电容起动定性
(C) 控件：

* 模式：单相/三相/单相+电容相移
* `f`、`I0`、相位差 `Δφ`
  图：

1. 三相磁场矢量随时间动画
2. 合成磁场端点轨迹：单相往返 vs 三相圆周
3. 定性“转矩指标”随时间
   (D) 误区：单相并不等于旋转磁场；必须有相位差。

---

# M05 电磁弹射导轨（理想化）：RLC 放电 + I² 力

(A) 力的简化：`F ≈ 0.5 * L' * I^2`（能量法近似）
(B) `E_C=0.5CV0^2`，RLC 放电波形，能量去向（动能/热/残余）
(C) **必须交互：调 V0 看 I(t) 与 x(t)/v(t)**
控件：

* `V0, C, R, L`
* `L'`（给定参数，不讨论结构）
* `m`、摩擦 `μ`（可选）、轨道长度
  图：

1. `I(t)`（RLC）
2. `F(t)`、`v(t)`、`x(t)`（可分多图）
3. 能量条：电容能→动能/热
   实现要求：

* 使用参数网格预计算（例如 V0×R×C 三维中选两维交互，其余固定）
* 前端查表/插值更新曲线
  (D) 误区：峰值电流大不代表末速度一定大；波形与损耗决定能量转化效率。

---

# M06 质谱仪：V 与 B 决定轨迹半径

(A) `qV=0.5mv^2`，`r = mv/(|q|B)`；速度选择器可选 `v=E/B`
(B) 加速电源、磁铁励磁电流（定性 I→B）
(C) 控件：

* `V_acc`、`B`、（可选）`E`
* 粒子：H⁺、He⁺、Ne⁺…或输入 `m/q`
* 双同位素对比
  图：

1. 轨迹（圆弧）+ 探测屏落点
2. 落点位置 vs `m/q`
3. 读数：`v`、`r`、分辨率指标（定性）
   (D) 误区：B 越大半径越小；注意 `r∝1/B`。

---

# M07 电子显微镜：电压→波长，磁透镜→聚焦（定性为主）

(A) 电场加速；磁透镜聚焦（定性洛伦兹力）；德布罗意 `λ = h/sqrt(2meV)`（拓展）
(B) 枪电压、透镜线圈电流（I→B→焦距），扫描线圈（SEM 定性）
(C) 控件：

* `V`（加速电压）
* `I_lens`（用经验关系 `1/f ∝ I^2` 或 `B∝I`）
* 初始发散角/束斑质量参数
  图：

1. “光线追迹式”束线收敛/发散（多条轨迹）
2. `λ(V)` 曲线 + 当前读数
3. 定性像差提示（可选）
   (D) 误区：电压越高不等于无限清晰；存在像差/材料限制（不展开工程细节）。

---

# M08 回旋加速器：共振条件与失谐可视化

(A) `ω=|q|B/m`，缝隙电场加速 `ΔK=qV_gap`
(B) RF 电源频率匹配回旋频率（非相对论）
(C) 控件：

* `B`、`V_gap`
* `f_rf` 与理论 `f_c` 对比
* 粒子类型（q,m）
* 相对论开关（选做：速度高时失谐）
  图：

1. 螺旋外扩轨迹
2. `K(t)` 或 `r(t)`
3. 失谐时“加速抵消/轨迹变差”
   (D) 误区：频率越高不一定越好；必须匹配共振。

---

# M09 直线加速器 Linac：相位同步与漂移管长度

(A) RF 腔纵向电场加速；漂移管内近似无场（屏蔽）
(B) RF 源与腔体谐振（定性），强调同步相位
(C) 控件：

* `f`、`E0`（加速梯度）
* 注入能量 `K0`
* 同步相位 `φ`
  图：

1. 位置-时间与 RF 相位
2. 漂移管长度随速度增长示意
3. 末能量随参数
   (D) 误区：不是“一直加电场就能加速”；相位不同会减速或抵消。

---

## 9. 扩展模块（至少实现 6 个）

从下列选 ≥6 个做成 Tab：

1. **变压器（互感）**：匝数比、负载变化、电压电流、理想功率守恒
2. **RLC 振荡**：能量在 C 与 L 间交换，阻尼与 Q
3. **无线充电（耦合谐振）**：耦合系数 k、失谐导致效率下降
4. **霍尔效应**：`V_H ∝ IB/(nqt)`，方向判定与载流子类型（拓展）
5. **扬声器/动圈麦克风互逆**：`F=BL I` 与 `ε=-dΦ/dt`
6. **电磁感应加热（涡流）**：频率/电阻率/厚度对损耗的定性影响
7. **RL 开关瞬态**：反电动势与能量释放（只做安全提示，不教危险实验）
8. **继电器/电磁铁**：I→B→机械运动，响应时间定性

---

## 10. 参数范围与稳定性（强制建议）

* 电子类：

  * `V_acc`：0.5 kV ~ 10 kV（演示级）
  * 偏转电压：-50 V ~ 50 V
  * `B`：0 ~ 0.2 T（演示级）
* 电机类：`f` 0.5~100 Hz（便于动画）
* RLC：选择可视化稳定范围（避免数值发散）
* CT：phantom 128×128 或 256×256；角度数用离散选项避免数据爆炸

---

## 11. build.py 行为要求（强制）

* `python build.py` 生成 `dist/emlab.html`
* 可选参数：

  * `--out dist/emlab.html`
  * `--mode release|debug`
  * `--no-ct`（无 scikit-image 时跳过 CT 或降级）
* 产物必须可离线打开交互（release 模式不依赖网络）。

---

## 12. 验收标准（Acceptance Criteria）

1. `dist/emlab.html` 双击打开即可交互（无 server）。
2. 每个核心模块满足：

   * ≥3 个可调参数
   * ≥2 个输出（例如轨迹+波形 / 能量+读数）
   * 有“电磁场 + 电路”解释文本、误区与引导题
3. CRT/示波器模块必须做到：

   * 调 `V_acc` 与偏转电压时，电子轨迹与屏幕图形同步变化
4. 理想化导轨模块必须做到：

   * 调 `V0` 同时影响 `I(t)` 与 `x(t), v(t)`，能量条一致
5. CT 模块必须做到：

   * 改 `N_angles` 时 sinogram 与重建同步变化，角度越多重建越好

---

## 13. 教学脚本（每模块必须附 3~5 个引导问题）

模板（模块底部 `<details>`）：

* 预测：把某参数加倍会怎样？为什么？
* 验证：拖动观察，与预测一致吗？
* 解释：用哪条定律（洛伦兹力/法拉第/欧姆/能量守恒）解释？
* 拓展：现实装置为什么不能无限增大参数？（击穿/发热/失谐等定性）

---

## 14. 实现提示（给 gemini-cli/codex）

* 优先用解析关系：前端 JS 直接算曲线点列（N≤2000）并 `Plotly.restyle`
* 必须重计算的（ODE/CT 重建）：

  * Python 预计算参数网格
  * 前端查表/插值更新（不在前端做 heavy compute）
* 单位与符号统一在 `common/units.py`
* 数据注入用 JSON script 标签（避免全局变量污染）
* 各模块 JS 只绑定自己模块的 DOM（避免互相干扰）

---
