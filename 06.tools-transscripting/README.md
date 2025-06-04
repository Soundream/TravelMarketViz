# Video Transcriber

这个工具可以将视频文件（MP4格式）转写成文本，并以JSON格式保存。输出的JSON格式与word-swarm项目的输出格式相兼容。

## 功能特点

- 支持处理单个或多个MP4视频文件
- 使用OpenAI的Whisper模型进行语音识别
- 自动提取视频中的音频
- 生成标准化的JSON输出
- 自动清理临时文件

## 安装要求

1. 安装Python 3.7或更高版本
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 创建输入视频目录：
```bash
mkdir input_videos
```

2. 将MP4视频文件放入`input_videos`目录

3. 运行脚本：
```bash
python video_transcriber.py
```

4. 转写结果将保存在`output`目录中，每个视频文件对应一个JSON文件

## 输出格式

JSON输出格式如下：
```json
[
  {
    "title": "视频文件名",
    "url": "视频文件路径",
    "date": "处理日期",
    "content": "转写文本内容"
  }
]
```

## 注意事项

- 确保有足够的磁盘空间用于临时音频文件
- 转写大文件可能需要较长时间
- 建议使用高质量的音频以获得更好的转写效果 