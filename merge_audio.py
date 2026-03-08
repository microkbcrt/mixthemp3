#!/usr/bin/env python3
"""
GitHub Actions音频文件合并脚本
将仓库中所有mp3、flac、ogg、wav、m4a、aac文件合并为单个320k的ogg文件
"""

import os
import sys
import glob
import logging
import subprocess
from pathlib import Path
from typing import List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AudioMerger:
    def __init__(self, output_file: str = "merged_audio.ogg", bitrate: str = "320k"):
        """
        初始化音频合并器
        
        Args:
            output_file: 输出文件名
            bitrate: 输出音频比特率
        """
        self.output_file = output_file
        self.bitrate = bitrate
        self.supported_formats = ['mp3', 'flac', 'ogg', 'wav', 'm4a', 'aac', 'wma']
        
    def find_audio_files(self, root_dir: str = ".") -> List[str]:
        """
        查找所有支持的音频文件
        
        Args:
            root_dir: 搜索根目录
            
        Returns:
            音频文件路径列表
        """
        audio_files = []
        
        for ext in self.supported_formats:
            # 递归查找所有音频文件
            pattern = os.path.join(root_dir, "**", f"*.{ext}")
            files = glob.glob(pattern, recursive=True)
            audio_files.extend(files)
            
            # 查找大写扩展名
            pattern_upper = os.path.join(root_dir, "**", f"*.{ext.upper()}")
            files_upper = glob.glob(pattern_upper, recursive=True)
            audio_files.extend(files_upper)
        
        # 去重并排序
        audio_files = sorted(list(set(audio_files)))
        
        logger.info(f"找到 {len(audio_files)} 个音频文件")
        for file in audio_files[:10]:  # 只显示前10个文件
            logger.debug(f"  - {file}")
        
        if len(audio_files) > 10:
            logger.info(f"  ... 和另外 {len(audio_files) - 10} 个文件")
            
        return audio_files
    
    def check_ffmpeg(self) -> bool:
        """
        检查ffmpeg是否可用
        
        Returns:
            bool: ffmpeg是否可用
        """
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                logger.info("✓ FFmpeg 可用")
                return True
            else:
                logger.error("✗ FFmpeg 不可用")
                return False
        except FileNotFoundError:
            logger.error("✗ FFmpeg 未安装")
            return False
    
    def merge_audio_files(self, audio_files: List[str]) -> bool:
        """
        合并音频文件
        
        Args:
            audio_files: 音频文件路径列表
            
        Returns:
            bool: 合并是否成功
        """
        if not audio_files:
            logger.error("没有找到音频文件")
            return False
            
        if len(audio_files) == 1:
            logger.info("只有一个音频文件，直接转换格式")
            input_file = audio_files[0]
        else:
            # 创建文件列表
            list_file = "audio_files.txt"
            with open(list_file, 'w', encoding='utf-8') as f:
                for audio_file in audio_files:
                    # 转义特殊字符
                    safe_path = audio_file.replace("'", "'\\''")
                    f.write(f"file '{safe_path}'\n")
            
            input_file = f"concat:{list_file}"
        
        try:
            # 构建ffmpeg命令
            cmd = [
                'ffmpeg',
                '-y',  # 覆盖输出文件
                '-loglevel', 'info',
            ]
            
            if len(audio_files) > 1:
                cmd.extend([
                    '-f', 'concat',
                    '-safe', '0',
                ])
                
            cmd.extend([
                '-i', input_file,
                '-c:a', 'libvorbis',  # OGG编码器
                '-b:a', self.bitrate,
                '-map_metadata', '-1',  # 不复制元数据
                self.output_file
            ])
            
            logger.info(f"开始合并音频文件，输出: {self.output_file}")
            logger.info(f"使用命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("✓ 音频文件合并成功")
            
            # 清理临时文件
            if len(audio_files) > 1 and os.path.exists("audio_files.txt"):
                os.remove("audio_files.txt")
                
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ 音频合并失败: {e}")
            if e.stderr:
                logger.error(f"错误输出:\n{e.stderr}")
            return False
        except Exception as e:
            logger.error(f"✗ 合并过程中发生错误: {e}")
            return False
    
    def get_file_info(self) -> Optional[dict]:
        """
        获取输出文件信息
        
        Returns:
            文件信息字典
        """
        if not os.path.exists(self.output_file):
            return None
            
        try:
            import datetime
            file_size = os.path.getsize(self.output_file)
            
            # 获取音频时长
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 
                  'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', 
                  self.output_file]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            duration = float(result.stdout.strip()) if result.stdout else 0
            
            return {
                'filename': self.output_file,
                'size_bytes': file_size,
                'size_mb': file_size / (1024 * 1024),
                'duration_seconds': duration,
                'duration_formatted': str(datetime.timedelta(seconds=int(duration))),
                'bitrate': self.bitrate
            }
        except Exception as e:
            logger.warning(f"无法获取文件信息: {e}")
            return None

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='合并音频文件为OGG格式')
    parser.add_argument('--input-dir', '-i', default='.', 
                       help='输入目录（默认当前目录）')
    parser.add_argument('--output', '-o', default='merged_audio.ogg',
                       help='输出文件名（默认: merged_audio.ogg）')
    parser.add_argument('--bitrate', '-b', default='320k',
                       help='输出比特率（默认: 320k）')
    parser.add_argument('--dry-run', action='store_true',
                       help='只显示找到的文件，不实际合并')
    
    args = parser.parse_args()
    
    # 创建合并器
    merger = AudioMerger(args.output, args.bitrate)
    
    # 检查ffmpeg
    if not merger.check_ffmpeg():
        sys.exit(1)
    
    # 查找音频文件
    audio_files = merger.find_audio_files(args.input_dir)
    
    if not audio_files:
        logger.error("没有找到任何音频文件")
        sys.exit(1)
    
    if args.dry_run:
        logger.info("干运行模式，不会实际合并文件")
        logger.info(f"将合并 {len(audio_files)} 个文件:")
        for file in audio_files:
            logger.info(f"  - {file}")
        sys.exit(0)
    
    # 合并音频文件
    if merger.merge_audio_files(audio_files):
        # 获取文件信息
        file_info = merger.get_file_info()
        if file_info:
            logger.info("=" * 50)
            logger.info("合并完成！文件信息:")
            logger.info(f"  文件名: {file_info['filename']}")
            logger.info(f"  文件大小: {file_info['size_mb']:.2f} MB")
            logger.info(f"  时长: {file_info['duration_formatted']}")
            logger.info(f"  比特率: {file_info['bitrate']}")
            logger.info("=" * 50)
        
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
