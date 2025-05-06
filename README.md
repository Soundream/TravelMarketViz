# Travel Company Revenue Visualization

这个项目创建了一个交互式的旅游公司收入可视化动画，展示了各大在线旅游公司的季度收入变化。

## 运行说明

### 基本运行命令

```bash
python3 travel_company_viz_new.py
```

这将使用默认参数生成可视化，并保存在`output/travel_revenue_plotly.html`文件中。

### 自定义参数

脚本支持多个命令行参数来自定义可视化效果：

```bash
python3 travel_company_viz_new.py --height 900 --width 1800 --transition-duration 3000 --output output/travel_company_viz_custom.html
```

#### 参数说明

- `--output`: 输出HTML文件路径（默认：output/travel_revenue_plotly.html）
- `--frames-per-year`: 每年生成的帧数（默认：4，代表季度数据）
- `--height`: 可视化高度（像素，默认：800）
- `--width`: 可视化宽度（像素，默认：1600）
- `--max-companies`: 显示的最大公司数量（默认：15）
- `--transition-duration`: 帧之间的过渡时间（毫秒，默认：500）

### 关于动画时长

动画的总时长取决于数据集中的季度数量和`transition-duration`参数值。以当前数据集为例：

- 当`transition-duration`设置为3000（3秒）时，整个动画循环大约需要5分钟完成一次。
- 当`transition-duration`设置为2000（2秒）时，整个动画循环大约需要3.5分钟完成一次。
- 当`transition-duration`设置为1000（1秒）时，整个动画循环大约需要2分钟完成一次。

### 示例：生成5分钟长的动画

```bash
python3 travel_company_viz_new.py --height 900 --width 1800 --transition-duration 3000 --output output/travel_company_viz_5min_duration.html
```

## 航空公司可视化工具

本项目还包含两个航空公司数据可视化工具：`airline_plotly_viz`和`airline_plotly_line`。

### airline_plotly_viz（航空公司柱状图可视化）

这个脚本生成航空公司收入的柱状图动画可视化。

#### 基本使用方法

```bash
python3 airline_plotly_viz.py
```

#### 自定义参数

```bash
python3 airline_plotly_viz.py --height 900 --width 1800 --transition-duration 3000 --output output/airline_revenue_viz.html
```

支持的参数与`travel_company_viz_new.py`类似：
- `--output`: 输出HTML文件路径
- `--height`: 可视化高度（像素）
- `--width`: 可视化宽度（像素）
- `--transition-duration`: 帧之间的过渡时间（毫秒）
- `--max-companies`: 显示的最大航空公司数量

### airline_plotly_line（航空公司折线图可视化）

这个脚本生成航空公司收入的折线图动画可视化。

#### 基本使用方法

```bash
python3 airline_plotly_line.py
```

#### 自定义参数

```bash
python3 airline_plotly_line.py --height 900 --width 1800 --transition-duration 3000 --output output/airline_revenue_line.html
```

支持的参数：
- `--output`: 输出HTML文件路径
- `--height`: 可视化高度（像素）
- `--width`: 可视化宽度（像素）
- `--transition-duration`: 帧之间的过渡时间（毫秒）
- `--line-width`: 折线宽度（默认：2）
- `--include-markers`: 在折线上显示数据点标记

## 注意事项

- 生成的HTML文件会自动在浏览器中打开
- 所有可视化都包含播放、暂停和重置按钮，可以控制动画播放
- 旅游公司数据来源于`bar-video/Animated Bubble Chart_ Historic Financials Online Travel Industry - Revenue2.csv`文件
- 航空公司数据来源于相应的CSV文件 