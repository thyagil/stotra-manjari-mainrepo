#!/usr/bin/env python3
import subprocess
from pathlib import Path

# === CONFIG ===
LOCAL_BASE = Path("/Volumes/web/stotra_manjari/projects")
LOCAL_VOLUMES = LOCAL_BASE / "ramayanam_sriramghanapatigal" / "volumes"
LOCAL_IMAGES = LOCAL_BASE / "ramayanam_sriramghanapatigal" / "images"
LOCAL_METADATA = LOCAL_BASE / "ramayanam_sriramghanapatigal" / "metadata"
LOCAL_INDEX = LOCAL_BASE / "stotras.json"

BUCKET_BASE = "gs://stotra-manjari-assets/projects"
BUCKET_VOLUMES = f"{BUCKET_BASE}/ramayanam_sriramghanapatigal/volumes"
BUCKET_IMAGES = f"{BUCKET_BASE}/ramayanam_sriramghanapatigal/images"
BUCKET_METADATA = f"{BUCKET_BASE}/ramayanam_sriramghanapatigal/metadata"
BUCKET_INDEX = f"{BUCKET_BASE}/stotras.json"

# Exclude regex (skip junk/lock/temp/backup files)
EXCLUDE_REGEX = r"(\.DS_Store$|^\._.*$|\.lock$|\.tmp$|\.swp$|~\$.*|backup/.*)"

def run_cmd(cmd):
    print("🚀 Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

def sync_folder(local: Path, bucket: str):
    if not local.exists():
        print(f"⚠️ Skipping {local}, not found.")
        return
    run_cmd([
        "gsutil", "-m", "rsync", "-r",
        "-x", EXCLUDE_REGEX,
        str(local), bucket
    ])

def upload_file(local: Path, bucket: str, content_type=None):
    if not local.exists():
        print(f"⚠️ Skipping {local}, not found.")
        return
    cmd = ["gsutil"]
    if content_type:
        cmd += ["-h", f"Content-Type:{content_type}"]
    cmd += ["cp", str(local), bucket]
    run_cmd(cmd)

def main():
    # 1. sync volumes
    sync_folder(LOCAL_VOLUMES, BUCKET_VOLUMES)

    # 2. sync images
    sync_folder(LOCAL_IMAGES, BUCKET_IMAGES)

    # 3. sync metadata
    sync_folder(LOCAL_METADATA, BUCKET_METADATA)

    # 4. upload stotras.json with correct content-type
    upload_file(LOCAL_INDEX, BUCKET_INDEX, content_type="application/json")

    print("✅ Sync complete!")

def enforce_utf8():
    print("🔧 Setting correct MIME types with UTF-8...")

    # TXT
    subprocess.run([
        "gsutil", "-m", "setmeta",
        "-h", "Content-Type:text/plain; charset=utf-8",
        f"{BUCKET_BASE}/**.txt"
    ])

    # CSV
    subprocess.run([
        "gsutil", "-m", "setmeta",
        "-h", "Content-Type:text/csv; charset=utf-8",
        f"{BUCKET_BASE}/**.csv"
    ])

    # JSON
    subprocess.run([
        "gsutil", "-m", "setmeta",
        "-h", "Content-Type:application/json; charset=utf-8",
        f"{BUCKET_BASE}/**.json"
    ])

    print("✅ UTF-8 metadata enforced.")

if __name__ == "__main__":
    # main()
    enforce_utf8()