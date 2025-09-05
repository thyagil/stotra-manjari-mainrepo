# orchestrator/tasks/step1_extract_audio.py
import subprocess
from pathlib import Path

def run(args, resolver):
    """
    Step 1: Extract audio tracks from MP4 videos using ffmpeg.
    Args:
        args.audio_format -> "aac" or "mp3"
        args.volume (optional for volume-based projects)
    """
    project_type = args.project_type
    audio_format = args.audio_format or "aac"

    input_dir = ""
    # Resolve input and output dirs
    if project_type == "volume":
        input_dir = resolver.resolve("videos", volume=args.volume)
        output_dir = resolver.resolve("audio", volume=args.volume, audio_format=audio_format)
    else:  # standalone or chapter-based
        input_dir = resolver.videos_input_working #resolver.resolve("videos")
        output_dir = resolver.audio_output_working

    output_dir.mkdir(parents=True, exist_ok=True)

    files_to_process = []

    if args.project_type == "standalone":
        project_file = resolver.get_file_by_name(input_dir, args.project_name)
        if project_file:  # safety check
            files_to_process = [Path(input_dir) / project_file]
    else:
        files_to_process = sorted(Path(input_dir).glob("*.mp4"))

    for f in files_to_process:   # <-- no .glob() here
        base = f.stem
        if audio_format == "mp3":
            outfile = output_dir / f"{base}.mp3"
            cmd = ["ffmpeg", "-y", "-i", str(f), "-vn", "-acodec", "libmp3lame", "-qscale:a", "2", str(outfile)]
        else:
            outfile = output_dir / f"{base}.m4a"
            cmd = ["ffmpeg", "-y", "-i", str(f), "-vn", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(outfile)]

        print(f"🎵 Extracting {outfile.name}")
        subprocess.run(cmd, check=True)


    print(f"✅ Extraction complete → {output_dir}")
