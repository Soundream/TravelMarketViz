# 航空公司收入条形图动画生成器

这个工具包含两个独立的脚本，用于生成航空公司收入的动态条形图竞赛动画。第一个脚本负责生成单独的图像帧，第二个脚本将这些帧合成为视频。通过分离这两个过程，可以避免同步问题并提高整体性能。

## 依赖项

确保已安装以下依赖项：

```bash
pip install pandas matplotlib numpy pillow tqdm
```

同时，视频合成需要安装 FFmpeg。

## 使用方法

### 步骤 1：生成图像帧

使用 `airline_frame_generator.py` 脚本生成单独的图像帧：

```bash
python airline_frame_generator.py [选项]
```

选项：
- `--frames-per-year`: 每年生成的帧数（默认：60，即每季度15帧）
- `--quarters-only`: 仅生成季度帧，不进行插值
- `--output-dir`: 输出目录（默认：frames）
- `--dpi`: 输出帧的DPI（默认：108）
- `--start-idx`: 起始帧索引
- `--end-idx`: 结束帧索引

示例：
```bash
# 生成全部插值帧
python airline_frame_generator.py

# 仅生成季度帧（不插值）
python airline_frame_generator.py --quarters-only

# 生成指定范围的帧
python airline_frame_generator.py --start-idx 10 --end-idx 20
```

### 步骤 2：合成视频

使用 `airline_video_maker.py` 脚本将生成的帧合成为视频：

```bash
python airline_video_maker.py [选项]
```

选项：
- `--fps`: 帧率（默认：30）
- `--input-dir`: 包含帧的输入目录（默认：frames）
- `--output`: 输出视频文件路径（默认：output/airline_revenue.mp4）
- `--quality`: 视频质量：high、medium 或 low（默认：high）
- `--duration`: 目标视频时长（秒），覆盖 --fps 设置

示例：
```bash
# 使用默认设置创建视频
python airline_video_maker.py

# 创建高品质、10fps的视频
python airline_video_maker.py --fps 10 --quality high

# 创建正好60秒长的视频（自动调整fps）
python airline_video_maker.py --duration 60
```

## 工作原理

1. `airline_frame_generator.py` 从 CSV 数据中读取航空公司收入数据，并为每个时间点创建一个条形图帧。
   - 它支持季度之间的平滑插值
   - 添加了公司标志和颜色编码
   - 包含时间轴可视化

2. `airline_video_maker.py` 读取生成的帧并使用 FFmpeg 将它们合成为平滑的视频。
   - 按照正确顺序处理帧
   - 允许自定义视频质量和帧率
   - 提供合理的默认值

## 疑难解答

- 如果帧生成过程中出现内存错误，请尝试减少 `--dpi` 值或分批生成帧
- 如果视频创建失败，请确保已安装 FFmpeg 并且可以从命令行访问
- 对于大量帧，视频创建过程可能需要较长时间 