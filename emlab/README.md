# EMLab：高中物理《电磁场与电路》交互可视化实验室

本项目用 **Python 预计算 + Plotly** 生成一个可离线打开的单文件交互网页，用于高中课堂演示/学生探究。

## 快速开始

1. 创建环境并安装依赖：

   ```bash
   cd emlab
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. 生成离线单文件：

   ```bash
   python build.py
   # 输出：../dist/emlab.html（仓库根目录下的 dist/）
   ```

3. 打开：双击 `dist/emlab.html`（无需任何后端服务）。

## 命令行参数

```bash
python build.py --mode release
python build.py --out dist/emlab.html --mode release
python build.py --mode debug
python build.py --no-ct
```

## 安全边界（重要）

涉及“电磁弹射导轨（rail launcher/railgun 类）”模块仅包含**理想化物理与电路仿真**与课堂讨论，不提供任何现实可执行的制造、加工、装配、危险操作指导或提升威力/效率的实操建议。
