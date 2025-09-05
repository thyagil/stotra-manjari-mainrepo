import json
import os
from pathlib import Path

PROJECTS_DIR = Path("/Volumes/web/stotra-manjari-assets/projects")
MARKETPLACE_PATH = PROJECTS_DIR / "marketplace.json"

def load_project_metadata(project_path):
    metadata_file = project_path / "metadata.json"
    if not metadata_file.exists():
        return None
    with open(metadata_file, "r", encoding="utf-8") as f:
        return json.load(f)

def derive_marketplace_entry(metadata):
    project_id = metadata["id"]
    return {
        "id": project_id,
        "title": metadata.get("friendly_name", ""),
        "subtitle": metadata.get("description", ""),
        "cover": f"projects/{project_id}/images/cover.png",
        "banner": f"projects/{project_id}/images/banner.png",
        "isPremium": metadata.get("app_status", {}).get("monetization", {}).get("isPremium", False),
        "featured": metadata.get("app_status", {}).get("featured", False)
    }

def main():
    marketplace = []
    for project_dir in PROJECTS_DIR.iterdir():
        if project_dir.is_dir():
            metadata = load_project_metadata(project_dir)
            if metadata:
                marketplace.append(derive_marketplace_entry(metadata))
    with open(MARKETPLACE_PATH, "w", encoding="utf-8") as f:
        json.dump(marketplace, f, indent=2, ensure_ascii=False)
    print(f"✅ Marketplace file updated at {MARKETPLACE_PATH}")

if __name__ == "__main__":
    main()
