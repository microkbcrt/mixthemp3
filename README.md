# 音频文件自动合并与发布

此仓库配置了自动合并音频文件并发布到GitHub Release的功能。

## 功能

- 自动扫描仓库中的所有音频文件（mp3, flac, ogg, wav, m4a, aac, wma）
- 合并为单个OGG格式文件
- 可配置输出文件名和比特率
- 自动发布到GitHub Release
- 支持手动触发和标签触发

## 使用方法

### 1. 本地测试

bash
安装依赖

sudo apt-get install ffmpeg  # Ubuntu/Debian
或 brew install ffmpeg     # macOS

运行脚本

python merge_audio.py

带参数运行

python merge_audio.py --output "my_audio.ogg" --bitrate "192k"


### 2. 在GitHub Actions上运行

#### 自动触发（推荐）：
推送一个以`v`开头的标签，例如：
bash
git tag v1.0.0
git push origin v1.0.0


#### 手动触发：
1. 在GitHub仓库页面，点击"Actions"标签
2. 选择"Merge Audio and Create Release"工作流
3. 点击"Run workflow"
4. 可选的输入参数：
   - 输出文件名（默认：merged_audio.ogg）
   - 比特率（默认：320k）

## 文件结构


.github/workflows/merge-and-release.yml  # GitHub Actions工作流
merge_audio.py                           # 音频合并脚本
README_AUDIO_MERGE.md                    # 本说明文件


## 支持的音频格式

- MP3 (.mp3)
- FLAC (.flac)
- OGG (.ogg)
- WAV (.wav)
- M4A (.m4a)
- AAC (.aac)
- WMA (.wma)

## 输出格式

- 格式：OGG (Vorbis编码)
- 默认比特率：320kbps
- 元数据：不保留原始元数据

## 注意事项

1. 确保仓库中有音频文件
2. 首次运行可能需要几分钟安装依赖
3. 合并顺序按文件名排序
4. 大型音频文件可能需要较长时间处理
5. GitHub Release有2GB文件大小限制
