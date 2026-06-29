import os
import subprocess

def merge_audio_files(input_files: list[str], output_path: str) -> bool:
    """
    Merges multiple audio files into a single output file using FFmpeg concat demuxer.
    Requires FFmpeg to be installed and in the system PATH.
    """
    if not input_files:
        return False
        
    if len(input_files) == 1:
        # If only one file, just rename/move it
        import shutil
        shutil.copy(input_files[0], output_path)
        return True
        
    # Create a temporary concat file
    # We must format it as: file 'path/to/file'
    list_file_path = output_path + ".list.txt"
    
    try:
        with open(list_file_path, "w", encoding="utf-8") as f:
            for file_path in input_files:
                # Convert to absolute path to avoid relative path resolution issues in FFmpeg
                abs_path = os.path.abspath(file_path)
                # FFmpeg requires forward slashes or escaped backslashes, even on Windows
                safe_path = abs_path.replace('\\', '/')
                f.write(f"file '{safe_path}'\n")
                
        # Run FFmpeg
        # -f concat: use concat demuxer
        # -safe 0: allow any file path
        # -c copy: stream copy without re-encoding (preserves quality and is lightning fast)
        cmd = [
            "ffmpeg",
            "-y", # overwrite output
            "-f", "concat",
            "-safe", "0",
            "-i", list_file_path,
            "-c", "copy",
            output_path
        ]
        
        # Capture stderr as ffmpeg writes logs to stderr
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            print("FFmpeg Merge Error:", result.stderr)
            return False
            
        return os.path.exists(output_path)
        
    except Exception as e:
        print("Merge Exception:", str(e))
        return False
    finally:
        # Cleanup list file
        if os.path.exists(list_file_path):
            os.remove(list_file_path)
