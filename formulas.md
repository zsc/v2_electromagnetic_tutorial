# EMLab｜公式推演（LaTeX 版，统一符号）

> 本文只写“公式推演”，不写代码实现。  
> HTML 中用 `\(...\)`（行内）与 `\[...\]`（行间）写 LaTeX，浏览器端用 **MathJax（离线内联）**渲染。

## _global

### 统一符号与约定（全模块通用）

- 时间：\(t\)（s），频率：\(f\)（Hz），角频率：\(\omega = 2\pi f\)（rad/s）
- 电路量：电压 \(V\)（V），电流 \(I\)（A），电阻 \(R\)（\(\Omega\)），电感 \(L\)（H），电容 \(C\)（F）
- 电磁量：电场 \(\mathbf{E}\)（V/m），磁感应强度 \(\mathbf{B}\)（T），磁通 \(\Phi\)（Wb），电动势/感应电压 \(\varepsilon\)（V）
- 质点量：电荷 \(q\)（C），质量 \(m\)（kg），速度 \(\mathbf{v}\)（m/s），力 \(\mathbf{F}\)（N）
- 洛伦兹力（统一方向判断公式）：
  \[
  \mathbf{F} = q\left(\mathbf{E} + \mathbf{v}\times\mathbf{B}\right).
  \]
  当 \(q<0\)（电子）时，方向相对“右手定则”反向。
- 正弦量（峰值/有效值）：
  - 若 \(x(t) = \hat X\sin(\omega t+\varphi)\)，则 \(X_{\mathrm{rms}}=\hat X/\sqrt 2\)。
  - 相量写法：\(x(t)=\Re\{\tilde X\,e^{j\omega t}\}\)，并约定 \(j^2=-1\)。
- 教学近似边界（所有模块默认）：
  - 忽略边缘场、空间非均匀、材料非线性、温升导致的参数漂移。
  - “等效电压/等效力/等效模型”只保证趋势与量纲正确，不追求工程精度。

---

## crt_scope

### 目标：推导并记住 \(y \propto \dfrac{V_{\mathrm{def}}}{V_{\mathrm{acc}}}\)

### 1) 加速段：\(V_{\mathrm{acc}}\rightarrow v\)

非相对论近似（动能来自电势能）：
\[
eV_{\mathrm{acc}}=\frac12 m_e v^2
\quad\Rightarrow\quad
v=\sqrt{\frac{2eV_{\mathrm{acc}}}{m_e}}.
\]

### 2) 偏转板内：\(V_{\mathrm{def}}\rightarrow E_y\rightarrow a_y\rightarrow y_1\)

偏转板间距 \(d\)，电场近似均匀：
\[
E_y \approx \frac{V_{\mathrm{def}}}{d}.
\]
电场力与加速度：
\[
F_y=eE_y,\qquad
a_y=\frac{F_y}{m_e}=\frac{e}{m_e}\frac{V_{\mathrm{def}}}{d}.
\]
偏转板长度 \(l\)，板内飞行时间 \(t_1=l/v\)。板内位移（初始 \(v_y=0\)）：
\[
y_1=\frac12 a_y t_1^2
 = \frac12\frac{e}{m_e}\frac{V_{\mathrm{def}}}{d}\cdot\frac{l^2}{v^2}.
\]

### 3) 漂移段：\(v_y\rightarrow y_2\)

出板获得横向速度：
\[
v_y=a_y t_1=\frac{e}{m_e}\frac{V_{\mathrm{def}}}{d}\cdot\frac{l}{v}.
\]
漂移段长度 \(L_d\)，漂移时间 \(t_2=L_d/v\)，漂移位移：
\[
y_2=v_y t_2=\frac{e}{m_e}\frac{V_{\mathrm{def}}}{d}\cdot\frac{lL_d}{v^2}.
\]

### 4) 合并得到比例关系（最重要的“记忆式”）

\[
\begin{aligned}
y &= y_1+y_2
  = \frac{e}{m_e}\frac{V_{\mathrm{def}}}{d}\cdot\frac{l^2/2+lL_d}{v^2},\\
v^2&=\frac{2eV_{\mathrm{acc}}}{m_e}
\end{aligned}
\quad\Rightarrow\quad
y=\frac{V_{\mathrm{def}}}{V_{\mathrm{acc}}}\cdot\frac{l^2/2+lL_d}{2d}.
\]
因此（几何量固定时）：
\[
y \propto \frac{V_{\mathrm{def}}}{V_{\mathrm{acc}}}.
\]

> 记忆法：\(V_{\mathrm{acc}}\) 越大 \(\Rightarrow v\) 越大 \(\Rightarrow\) 在偏转区“停留时间”更短 \(\Rightarrow\) 同样 \(V_{\mathrm{def}}\) 偏转更小。

### 5) 数字示波器：采样与量化（两条必会公式）

- 采样时刻：\(\;t_n = n/f_s\)（采样率 \(f_s\)）
- 量化台阶（满量程 \(\pm A\)，位数 \(N_{\mathrm{bits}}\)）：
  \[
  \Delta \approx \frac{2A}{2^{N_{\mathrm{bits}}}},\qquad
  e_q\in\left[-\frac{\Delta}{2},\frac{\Delta}{2}\right]
  \quad(\text{理想均匀量化}).
  \]
- 混叠（定性记忆）：当信号频率接近/超过 \(f_s/2\)，会折叠为低频；常用写法：
  \[
  f_{\mathrm{alias}}=\lvert f-kf_s\rvert
  \quad(\text{取整数 }k\text{ 使 }f_{\mathrm{alias}}\in[0,f_s/2]).
  \]

---

## xct_ct

### 目标：从 Beer–Lambert \(\rightarrow\) Radon \(\rightarrow\) BP/FBP

### 1) 透射与“投影数据”

设截面衰减系数为 \(\mu(x,y)\)（单位 \( \mathrm{m^{-1}}\)）。沿一条射线 \(L(\theta,s)\)：
\[
I_{\mathrm{out}} = I_{\mathrm{in}}\exp\!\left(-\int_{L(\theta,s)} \mu\,ds\right).
\]
取对数得到更“线性”的投影量：
\[
p(\theta,s):=-\ln\!\left(\frac{I_{\mathrm{out}}}{I_{\mathrm{in}}}\right)
 = \int_{L(\theta,s)} \mu\,ds.
\]
这一步说明：CT 的核心数据不是照片，而是“线积分”。

### 2) Radon 形式：用 \((\theta,s)\) 描述一条直线

直线方程（法向量角度为 \(\theta\)）：
\[
x\cos\theta + y\sin\theta = s.
\]
于是 \(p(\theta,s)\) 就是对满足该方程的直线做积分（即 Radon 变换的输出）。把 \(\theta\) 作为横轴、\(s\) 作为纵轴排成图，就是 sinogram。

### 3) “点 \(\rightarrow\) 正弦线”的由来（最常考）

若只看某个点 \((x_0,y_0)\) 的贡献，它在角度 \(\theta\) 下投影到
\[
s(\theta)=x_0\cos\theta+y_0\sin\theta,
\]
这是随 \(\theta\) 正弦变化的函数，因此在 sinogram 上画出一条“正弦轨迹”。

### 4) 简单反投影（BP）：把投影“沿原方向铺回去”

反投影（连续形式）的直观表达：
\[
\mu_{\mathrm{BP}}(x,y)=\int_0^{\pi} p\!\left(\theta,\,x\cos\theta+y\sin\theta\right)d\theta.
\]
BP 的问题：会把点“抹开”成模糊背景（低频偏强），边缘发糊、条纹明显。

### 5) 滤波反投影（FBP）：先滤波再反投影

FBP 结构（记住“先滤波再反投影”）：
\[
\mu_{\mathrm{FBP}}(x,y)
=\int_0^{\pi}
\bigl(p(\theta,\cdot)*h(\cdot)\bigr)\!\left(x\cos\theta+y\sin\theta\right)\,d\theta.
\]
其中 \(h\) 是滤波核；在频域中等价于对每个角度的投影做 ramp filter：
\[
P_{\mathrm{filt}}(\omega) = |\omega|\,P(\omega).
\]
直观理解：BP 低频过强 \(\Rightarrow\) 乘上 \(|\omega|\) 补偿高频 \(\Rightarrow\) 边缘更清晰。

### 6) 角度数 \(N_{\mathrm{angles}}\)：为何角度少会出条纹

把积分离散成求和：
\[
\mu(x,y)\approx \sum_{k=0}^{N-1} p\!\left(\theta_k,\,x\cos\theta_k+y\sin\theta_k\right),
\qquad
\theta_k=\frac{k\pi}{N}.
\]
当 \(N\) 变小，角度域欠采样 \(\Rightarrow\) 重建出现条纹伪影（streak artifacts）。

---

## ac_motor

### 目标：三相“stick 伸缩”叠加出旋转矢量

### 1) 单相：端点只会往返

教学近似：绕组在某观察点的磁场矢量与电流成正比，且方向沿绕组轴：
\[
\mathbf{B}_a(t)=k\,i_a(t)\,\hat{\mathbf{u}}_a,\qquad \hat{\mathbf{u}}_a=\text{常向量}.
\]
单相 \(i_a(t)=I_0\sin\omega t\)，因此 \(\mathbf{B}(t)\) 只在固定方向上正负变化 \(\Rightarrow\) 端点轨迹是一条线段（往返）。

### 2) 三相：合成磁场幅值近恒定且在转

三相电流（相差 \(120^\circ\)）：
\[
\begin{aligned}
i_a &= I_0\sin\omega t,\\
i_b &= I_0\sin(\omega t-2\pi/3),\\
i_c &= I_0\sin(\omega t+2\pi/3).
\end{aligned}
\]
绕组轴（空间方向也相差 \(120^\circ\)）：
\[
\hat{\mathbf{u}}_a=(1,0),\quad
\hat{\mathbf{u}}_b=\bigl(\cos120^\circ,\sin120^\circ\bigr),\quad
\hat{\mathbf{u}}_c=\bigl(\cos240^\circ,\sin240^\circ\bigr).
\]
合成：
\[
\mathbf{B}(t)=k\bigl(i_a\hat{\mathbf{u}}_a+i_b\hat{\mathbf{u}}_b+i_c\hat{\mathbf{u}}_c\bigr).
\]
利用三角恒等式可得到（关键结果）：
\[
B_x(t)=\frac{3}{2}kI_0\sin\omega t,\qquad
B_y(t)=-\frac{3}{2}kI_0\cos\omega t.
\]
因此
\[
|\mathbf{B}(t)|=\sqrt{B_x^2+B_y^2}=\frac{3}{2}kI_0=\text{常数},
\]
端点轨迹为圆（旋转磁场）。

> 记忆法：三相时“绕组轴固定”，每相 stick 只在自己的轴上变长/变短，但合成矢量端点绕圈且幅值近恒定。

### 3) 单相 + 电容（两相近似）：椭圆与“接近圆”的条件

把主绕组与辅绕组近似成两正交分量：
\[
B_x = kI_0\sin\omega t,\qquad
B_y = k(rI_0)\sin(\omega t-\varphi).
\]
一般为椭圆；当 \(r\approx 1\) 且 \(\varphi\approx 90^\circ\) 时更接近圆。

---

## rail_launcher

### 目标：从 RLC 放电得到 \(I(t)\)，再到 \(F(t)\propto I^2\) 与能量分配

> 安全边界：仅讨论理想化电路/物理与能量观点，不涉及任何现实可执行制造或操作。

### 1) 串联 RLC 放电：标准二阶方程

KVL（无外加源）：
\[
L\frac{di}{dt}+Ri+V_C=0,
\qquad
i=-C\frac{dV_C}{dt}.
\]
消去 \(i\)：
\[
\frac{d^2V_C}{dt^2}+\frac{R}{L}\frac{dV_C}{dt}+\frac{1}{LC}V_C=0.
\]
定义
\[
\omega_0=\frac{1}{\sqrt{LC}},\qquad
\alpha=\frac{R}{2L}.
\]

### 2) 欠阻尼解（最常见、最直观）

当 \(\alpha<\omega_0\)，令 \(\omega_d=\sqrt{\omega_0^2-\alpha^2}\)，在初始条件 \(V_C(0)=V_0\)、\(i(0)=0\) 下：
\[
V_C(t)=V_0e^{-\alpha t}\left[\cos(\omega_dt)+\frac{\alpha}{\omega_d}\sin(\omega_dt)\right],
\]
\[
i(t)=\frac{V_0}{L\omega_d}\,e^{-\alpha t}\sin(\omega_dt).
\]
结论：线性系统中 \(i(t)\propto V_0\)（加倍 \(V_0\) 电流整体加倍）。

### 3) 教学近似：\(I^2\) 力与运动学

常用近似（能量法写法）：
\[
F(t)\approx \frac12 L' \,i(t)^2.
\]
于是
\[
a(t)=\frac{F(t)}{m},\quad
v(t)=\int a(t)\,dt,\quad
x(t)=\int v(t)\,dt,
\]
并可加入简化摩擦：\(a_{\mathrm{eff}}\approx F/m-\mu g\)（同时用 \(v\ge 0\) 夹紧体现损耗）。

### 4) 能量观点（最稳的自检）

初始电容能量：
\[
E_0=\frac12 CV_0^2.
\]
各部分能量（随时间）：
\[
E_C=\frac12 C V_C^2,\quad
E_L=\frac12 Li^2,\quad
E_R(t)=\int_0^t i^2R\,dt,\quad
E_K=\frac12 mv^2,\quad
E_f\approx \mu m g x.
\]
在理想/近似范围内应满足：
\[
E_C+E_L+E_R+E_K+E_f\approx E_0.
\]

### 5) 缩放律（课堂预测题好用）

因为 \(i\propto V_0\)，所以
\[
F\propto i^2 \propto V_0^2.
\]
在其它参数不变的教学范围内，出口速度/位移的量级往往也随 \(V_0^2\) 明显增长（用于理解趋势）。

---

## mass_spec

### 目标：得到 \(r\propto \sqrt{m/q}/B\)，并理解“落点分离”

### 1) 加速：\(V_{\mathrm{acc}}\rightarrow v\)

\[
qV_{\mathrm{acc}}=\frac12 mv^2
\quad\Rightarrow\quad
v=\sqrt{\frac{2qV_{\mathrm{acc}}}{m}}.
\]

### 2) 匀强磁场偏转：\(B\rightarrow r\)

速度垂直于 \(\mathbf{B}\) 时，磁力提供向心力：
\[
|q|vB=\frac{mv^2}{r}
\quad\Rightarrow\quad
r=\frac{mv}{|q|B}.
\]
代入 \(v\)：
\[
r=\sqrt{\frac{2mV_{\mathrm{acc}}}{|q|B^2}}.
\]
结论（记住比例）：
\[
r\propto \frac{\sqrt{m/|q|}}{B},\qquad
r\propto \sqrt{V_{\mathrm{acc}}},\qquad
r\propto \frac{1}{B}.
\]

### 3) 速度选择器：\(v=E/B\)

交叉场选速（理想化）：
\[
qE=qvB \quad\Rightarrow\quad v=\frac{E}{B}.
\]
进入偏转磁场后：
\[
r=\frac{mv}{|q|B}=\frac{mE}{|q|B^2}.
\]

### 4) 探测屏落点（与页面几何一致）

粒子从原点沿 \(+x\) 进入磁场，圆弧参数式：
\[
x=r\sin\theta,\qquad
y=r(1-\cos\theta).
\]
屏幕为 \(x=x_{\mathrm{det}}\)，则
\[
\sin\theta=\frac{x_{\mathrm{det}}}{r},
\qquad
y_{\mathrm{hit}}=r\left(1-\sqrt{1-(x_{\mathrm{det}}/r)^2}\right).
\]
因此不同 \(m/q\Rightarrow r\) 不同 \(\Rightarrow y_{\mathrm{hit}}\) 分离。

---

## electron_microscope

### 目标：把“电压 \(\rightarrow\) 波长”与“磁透镜 \(\rightarrow\) 聚焦”串起来

### 1) 德布罗意波长：\(V\rightarrow \lambda\)

非相对论近似：
\[
p=\sqrt{2m_eeV},\qquad
\lambda=\frac{h}{p}
\quad\Rightarrow\quad
\lambda(V)=\frac{h}{\sqrt{2m_eeV}}.
\]
结论：\(\lambda\propto 1/\sqrt{V}\)。

### 2) 为什么“电压更高更难聚焦”（高中可接受的量级推导）

磁场只改变动量方向。横向动量改变量级 \(\Delta p_\perp\sim qBl\)（有效长度 \(l\)），纵向动量 \(p\sim \sqrt{V}\)，故偏转角量级
\[
\theta\sim \frac{\Delta p_\perp}{p}\propto \frac{B}{\sqrt{V}}.
\]
因此在同样线圈电流（同样 \(B\)）下，\(V\) 越大，束线越“硬”，聚焦更弱（焦距更长）。

### 3) 薄透镜近似：一条最常用的“束线公式”

把束线视作小角度光线，透镜处横向坐标 \(y\)，入射角 \(\theta_{\mathrm{in}}\)。薄透镜角度跳变：
\[
\theta_{\mathrm{out}}=\theta_{\mathrm{in}}-\frac{y}{f}.
\]
焦距 \(f\) 越小聚焦越强；改变 \(f\) 会改变屏上束斑大小，并通常出现“最佳聚焦”附近的最小束斑。

---

## cyclotron

### 目标：得到 \(\omega_c=|q|B/m\)，理解“共振/失谐”

### 1) 回旋角频率：磁场 \(\rightarrow\) 绕圈

\[
|q|vB=\frac{mv^2}{r}
\quad\Rightarrow\quad
\frac{v}{r}=\frac{|q|B}{m}=: \omega_c.
\]
非相对论下 \(\omega_c\) 与半径无关，是“固定 RF 也能一直加速”的关键。

### 2) 缝隙加速：相位决定加速还是减速

若缝隙电压 \(V_{\mathrm{gap}}(t)=\hat V\sin(\omega_{\mathrm{rf}}t)\)，粒子第 \(n\) 次过缝隙时刻为 \(t_n\)，能量增量（教学量级）：
\[
\Delta K_n \approx q\,V_{\mathrm{gap}}(t_n).
\]
当 \(\omega_{\mathrm{rf}}\approx \omega_c\) 且相位选择合适，\(\Delta K_n\) 多为正，能量逐次累积。

### 3) 失谐：相位漂移导致“有时推有时拉”

若 \(\omega_{\mathrm{rf}}\ne \omega_c\)，到达相位 \(\phi_n=\omega_{\mathrm{rf}}t_n\) 会随 \(n\) 漂移，导致 \(\Delta K_n\) 符号与大小变化，平均加速变差甚至抵消。

### 4) 相对论效应（经典回旋加速器的限制）

能量升高使 \(\gamma\) 增大，回旋频率变为
\[
\omega_c=\frac{|q|B}{\gamma m},\qquad
\gamma=1+\frac{K}{mc^2}.
\]
即使初始对准，也会逐步失谐。

---

## linac

### 目标：推导漂移管长度 \(L_n\approx v_nT/2\)

### 1) 缝隙加速：相位同步

把 RF 场写成 \(E_z(t)=\hat E\cos(\omega t)\)。若缝隙长度为 \(g\)，等效电压近似
\[
V_{\mathrm{gap}}\approx \hat E\,g.
\]
粒子在第 \(n\) 次穿越缝隙时刻 \(t_n\) 的能量增量（教学写法）：
\[
\Delta K_n \approx qV_{\mathrm{gap}}\cos(\omega t_n+\phi_0).
\]
要持续加速，就要让 \(\cos(\cdot)\) 尽量保持为正且不太小。

### 2) 漂移管：让粒子“等半个周期再出来”

漂移管内近似无场（不加速），作用是让粒子用时间对齐 RF 翻转。常取（\(\pi\) 模式直觉）：
\[
\Delta t_n \approx \frac{T}{2}=\frac{1}{2f}.
\]
若该段漂移的速度近似 \(v_n\)，则长度应满足：
\[
L_n\approx v_n\Delta t_n \approx v_n\frac{T}{2}.
\]
速度随能量升高而增大 \(\Rightarrow L_n\) 逐级变长。

### 3) 固定长度为何会相位漂移

若 \(L_n\) 固定，则 \(\Delta t_n=L/v_n\) 会随 \(v_n\) 增大而变小，导致到达相位逐步偏离最佳值，出现加速变差甚至减速。

---

## transformer

### 目标：从法拉第定律得到匝比，再连到功率因数

### 1) 匝比：\(V_s/V_p=N_s/N_p\)

理想变压器假设：两线圈耦合到同一主磁通 \(\Phi(t)\)。由法拉第定律：
\[
v_p(t)=N_p\frac{d\Phi}{dt},\qquad
v_s(t)=N_s\frac{d\Phi}{dt}.
\]
相除：
\[
\frac{v_s}{v_p}=\frac{N_s}{N_p}
\quad\Rightarrow\quad
\frac{V_{s,\mathrm{rms}}}{V_{p,\mathrm{rms}}}=\frac{N_s}{N_p}.
\]

### 2) 电流比：由理想功率守恒得到

忽略损耗：
\[
V_pI_p\approx V_sI_s
\quad\Rightarrow\quad
\frac{I_s}{I_p}\approx \frac{V_p}{V_s}\approx \frac{N_p}{N_s}.
\]

### 3) RL 负载：阻抗与功率因数

负载阻抗：
\[
Z=R+j\omega L,\qquad
|Z|=\sqrt{R^2+(\omega L)^2}.
\]
相位滞后：
\[
\varphi=\arctan\!\left(\frac{\omega L}{R}\right),
\qquad(\text{电流滞后电压 } \varphi).
\]
有功/视在/无功功率：
\[
P=VI\cos\varphi,\qquad
S=VI,\qquad
Q=VI\sin\varphi,\qquad
\cos\varphi=\frac{R}{|Z|}.
\]

---

## rlc_oscillation

### 目标：一套方程记住 \(\omega_0\)、\(\alpha\) 与三种阻尼

### 1) 标准二阶方程与参数

串联 RLC 放电（电容电压）：
\[
\frac{d^2V_C}{dt^2}+\frac{R}{L}\frac{dV_C}{dt}+\frac{1}{LC}V_C=0,
\qquad
\omega_0=\frac{1}{\sqrt{LC}},\quad
\alpha=\frac{R}{2L}.
\]
分类：
\[
\alpha<\omega_0\ (\text{欠阻尼}),\quad
\alpha=\omega_0\ (\text{临界阻尼}),\quad
\alpha>\omega_0\ (\text{过阻尼}).
\]

### 2) 欠阻尼解（本仓库图像主要用它）

令 \(\omega_d=\sqrt{\omega_0^2-\alpha^2}\)：
\[
V_C(t)=V_0e^{-\alpha t}\left[\cos(\omega_dt)+\frac{\alpha}{\omega_d}\sin(\omega_dt)\right],
\]
\[
I(t)=\frac{V_0}{L\omega_d}\,e^{-\alpha t}\sin(\omega_dt).
\]

### 3) Q 值（常用近似）

\[
Q\approx \frac{\omega_0L}{R}=\frac{1}{R}\sqrt{\frac{L}{C}}.
\]
Q 大 \(\Rightarrow\) 损耗相对小、衰减慢，但带宽更窄、对参数更敏感。

### 4) 能量交换与耗散（自检）

\[
E_C=\frac12 CV_C^2,\quad
E_L=\frac12 LI^2,\quad
E_R(t)=\int_0^t I^2R\,dt,
\quad
E_C+E_L+E_R\approx \frac12 CV_0^2.
\]

---

## wireless_power

### 目标：用阻抗矩阵得到 \(I_1,I_2\) 与效率 \(\eta(f)\)

### 1) 互感与 Q 值

互感用耦合系数表示：
\[
M=k\sqrt{L_1L_2},\qquad 0\le k\le 1.
\]
Q 值（常用定义）：
\[
Q\approx \frac{\omega_0L}{R}.
\]

### 2) 频域方程（相量法）

各回路阻抗：
\[
Z_1=R_1+j\omega L_1+\frac{1}{j\omega C_1},\quad
Z_2=(R_2+R_L)+j\omega L_2+\frac{1}{j\omega C_2}.
\]
耦合项为 \(j\omega M\)。列方程：
\[
Z_1I_1+j\omega MI_2=V_s,\qquad
j\omega MI_1+Z_2I_2=0.
\]
解得：
\[
I_1=\frac{V_sZ_2}{Z_1Z_2-(j\omega M)^2},\qquad
I_2=-\frac{V_s(j\omega M)}{Z_1Z_2-(j\omega M)^2}.
\]

### 3) 功率与效率

\[
P_{\mathrm{in}}=\frac12\Re\{V_s I_1^*\},\qquad
P_L=\frac12 |I_2|^2R_L,\qquad
\eta=\frac{P_L}{P_{\mathrm{in}}}.
\]

### 4) 双峰的来源（强耦合的两个正常模）

当 \(k\) 较大且损耗较小（Q 大），系统更像两个耦合振子，出现两个正常模频率，效率曲线可能分裂成双峰。

---

## hall_effect

### 目标：从受力平衡得到 \(V_H=\dfrac{IB}{nqt}\)，并用符号判定载流子类型

### 1) 受力平衡：磁力 \(\leftrightarrow\) 电场力

载流子漂移速度 \(v_d\)（沿电流方向），在磁场 \(B\) 中受磁力 \(qv_dB\)。堆积产生霍尔电场 \(E_H\)，平衡：
\[
qE_H=qv_dB \quad\Rightarrow\quad E_H=v_dB.
\]

### 2) 用电流 \(I\) 消去 \(v_d\)

电流密度：
\[
J=nqv_d.
\]
若样品宽 \(w\)、厚 \(t\)，截面积 \(A=wt\)，电流：
\[
I=JA=nqv_dwt
\quad\Rightarrow\quad
v_d=\frac{I}{nqwt}.
\]
代回 \(E_H=v_dB\) 并乘以宽度 \(w\) 得霍尔电压：
\[
V_H=E_Hw=\frac{IB}{nqt}.
\]
符号由 \(q\) 决定：电子 \(q<0\Rightarrow V_H<0\)，空穴 \(q>0\Rightarrow V_H>0\)。

### 3) 霍尔系数

\[
R_H:=\frac{E_H}{JB}=\frac{1}{nq}.
\]
测得 \(R_H\) 的符号即可判断主要载流子类型。

---

## speaker_microphone

### 目标：用一套方程说明“扬声器/麦克风互逆”（\(BL\cdot I\) 与 \(BL\cdot v\)）

### 1) 机械受迫振动（统一写法）

单自由度模型：
\[
m\ddot x+b\dot x+kx=F(t).
\]
正弦稳态（相量）：
\[
X=\frac{F}{Z_m},\qquad
Z_m = k-m\omega^2+jb\omega.
\]

### 2) 扬声器：\(V_{\mathrm{in}}\rightarrow I\rightarrow F=BL\,I\rightarrow x\)

线圈电阻抗：
\[
Z_e=R_{\mathrm{coil}}+j\omega L_{\mathrm{coil}},
\qquad
I=\frac{V_{\mathrm{in}}}{Z_e}.
\]
力因子（互逆常数） \(BL\)：
\[
F=(BL)\,I
\quad\Rightarrow\quad
X=\frac{BL}{Z_m}\cdot\frac{V_{\mathrm{in}}}{Z_e}.
\]
因此：电感 \(L_{\mathrm{coil}}\) 改变电流相位；机械共振使 \(|Z_m|\) 变小，从而位移变大。

### 3) 麦克风：\(F_{\mathrm{ext}}\rightarrow x\rightarrow v\rightarrow e=BL\,v\)

外力驱动：
\[
X=\frac{F_{\mathrm{ext}}}{Z_m},\qquad
v=j\omega X.
\]
动圈切割磁场产生感应电动势（互逆）：
\[
e=(BL)\,v=j\omega(BL)\,X.
\]
更完整的电路输出还应考虑线圈阻抗与负载分压；教学演示中常取 \(V_{\mathrm{out}}\approx e\) 来突出互逆关系与频率趋势：\(|e|\propto \omega\)。

### 4) 互逆性一句话

同一个 \(BL\) 同时出现在
\[
F=BL\cdot I,\qquad
e=BL\cdot v,
\]
所以改变 \(BL\) 会同时影响“受力能力”和“感应电压能力”。

---

## induction_heating

### 目标：从法拉第定律得到集肤深度 \(\delta\approx\sqrt{\dfrac{2\rho}{\omega\mu}}\)，再理解功率趋势

### 1) 频率为何“放大”感应效应

法拉第定律：
\[
\oint \mathbf{E}\cdot d\mathbf{l}=-\frac{d\Phi}{dt}.
\]
若 \(\Phi(t)=\hat\Phi\sin\omega t\)，则
\[
\left|\frac{d\Phi}{dt}\right|_{\mathrm{peak}}=\omega\hat\Phi,
\]
因此感应电场的量级随 \(\omega\) 增大而增大（趋势记忆：\(E_{\mathrm{ind}}\propto \omega B\)）。

### 2) 涡流与焦耳热（局部形式）

电导率 \(\sigma=1/\rho\)：
\[
\mathbf{J}=\sigma\mathbf{E},\qquad
p=\mathbf{J}\cdot\mathbf{E}=\sigma E^2=J^2\rho.
\]
在几何相近的教学近似下，常见趋势：
\[
P \propto \frac{\omega^2B^2}{\rho}
\quad(\text{忽略集肤}).
\]

### 3) 集肤深度（结果会用即可）

高频下场量向导体内部指数衰减 \(E(x)\sim E_0e^{-x/\delta}\)。集肤深度的标准结果：
\[
\delta=\sqrt{\frac{2\rho}{\omega\mu}},
\qquad
\mu\approx \mu_0\mu_r.
\]
趋势：
\[
\delta\propto \frac{1}{\sqrt f},\qquad
\delta\propto \sqrt{\rho}.
\]

### 4) 厚度 \(t\) 与“有效体积”

当 \(t\gg\delta\) 时，主要是表面一层发热，继续增厚收益不明显；当 \(t\sim\delta\) 时，更多体积参与。
教学上可用一个“参与因子”表达：
\[
\text{fill}\approx 1-e^{-t/\delta},
\qquad
P_{\mathrm{rel}}\sim \frac{\omega^2B^2}{\rho}\cdot(1-e^{-t/\delta}).
\]
