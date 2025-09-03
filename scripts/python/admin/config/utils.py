from pathlib import Path
from . import CONFIG_ROOT


def get_project_path(project_id: str) -> Path:
    """
    Return base path for a project under config/projects.
    """
    return CONFIG_ROOT / "projects" / project_id
