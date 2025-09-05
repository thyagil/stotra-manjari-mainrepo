#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
from scripts.python.stotra_manjari.projects.ramayanam_sriramghanapatigal import folders

# Default values (can override via CLI args)
volume = 1
audio_format = "aac"
folders[volume].audio_format = audio_format

INPUT_DIR = folders[volume].FLDR_VIDEOS
OUTPUT_DIR = folders[volume].FLDR_AUDIO_FINAL

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Loop through all .mp4 files in input dir
for f in sorted(Path(INPUT_DIR).glob("*.mp4")):
    base = f.stem  # filename without extension
    if audio_format == "mp3":
        print(f"🎵 Extracting {base}.mp3")
        cmd = [
            "ffmpeg", "-y", "-i", str(f),
            "-vn", "-acodec", "libmp3lame", "-qscale:a", "2",
            str(Path(OUTPUT_DIR) / f"{base}.mp3")
        ]
    elif audio_format == "aac":
        print(f"🎵 Extracting {base}.m4a")
        cmd = [
            "ffmpeg", "-y", "-i", str(f),
            "-vn", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            str(Path(OUTPUT_DIR) / f"{base}.m4a")
        ]
    else:
        print(f"❌ Unknown format: {audio_format} (use mp3 or aac)")
        sys.exit(1)

    # Run ffmpeg
    subprocess.run(cmd, check=True)
    exit()

print(f"✅ Extraction complete. Files saved in {OUTPUT_DIR}")
