import plistlib
from pathlib import Path

PROJECTS_ROOT = Path("/Volumes/WORKBENCH/assets/projects")


def list_projects(root: Path = PROJECTS_ROOT):
    """Return a list of all projects under the root directory."""
    projects = []
    if root.exists():
        for p in root.iterdir():
            if p.is_dir():
                plist_file = p / "project.plist"
                friendly_name = p.name.replace("_", " ").title()
                if plist_file.exists():
                    try:
                        with open(plist_file, "rb") as f:
                            data = plistlib.load(f)
                            friendly_name = data.get("friendly_name", friendly_name)
                    except Exception:
                        pass
                projects.append({
                    "id": p.name,
                    "friendly_name": friendly_name,
                })
    return projects


def create_project(proj_id: str, friendly_name: str, proj_type: str = "audiobook", format: str = "standalone"):
    """Create a new project directory and a default project.plist."""
    proj_dir = PROJECTS_ROOT / proj_id
    proj_dir.mkdir(parents=True, exist_ok=True)

    plist_path = proj_dir / "project.plist"
    if plist_path.exists():
        raise FileExistsError(f"❌ Project already exists: {plist_path}")

    # Minimal project.plist
    project_meta = {
        "id": proj_id,
        "friendly_name": friendly_name,
        "type": proj_type,
        "format": format,
        "description": f"{friendly_name} project",
        "artist": "",
        "category": [],
        "languages": ["sa", "ta", "en"],
        "contributors": [],
        "overview": "",
        "preview": "",
        "images": {
            "cover": "cover.jpg",
            "banner": "banner.png"
        },
        "app_status": {
            "featured": False,
            "published": False,
            "monetization": {
                "isPremium": False,
                "currency": "USD",
                "price": 0.0
            }
        },
        "volumes": []
    }

    with open(plist_path, "wb") as f:
        plistlib.dump(project_meta, f)

    return proj_id


def load_project(proj_id: str, root: Path = PROJECTS_ROOT):
    """Load a project's plist and return its metadata dict."""
    proj_dir = root / proj_id
    plist_file = proj_dir / "project.plist"
    if not plist_file.exists():
        raise FileNotFoundError(f"❌ No plist found for {proj_id}")
    with open(plist_file, "rb") as f:
        return plistlib.load(f)
