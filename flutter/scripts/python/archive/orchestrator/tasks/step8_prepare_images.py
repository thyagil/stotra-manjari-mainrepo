# orchestrator/tasks/step8_prepare_images.py
from pathlib import Path
import shutil

def run(args, resolver):
    """
    Step 8: Prepare images (banner, cover, thumbnail, volume cover).
    (Currently assumes images are created manually and placed in staging/images)
    """
    project_id = args.project_id
    img_dir = resolver.project_root / project_id / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    # For now: copy from working folder → staging/images
    source_images = resolver.resolve("images")
    if not source_images.exists():
        print("⚠️ No images found in working dir")
        return

    for img in source_images.glob("*.*"):
        dest = img_dir / img.name
        shutil.copy2(img, dest)
        print(f"🖼 Copied {img.name} → {dest}")
