
#!/usr/bin/env python3
"""
Provisioning Orchestrator for Stotra Manjari projects.
Loads task mappings from configs/tasks.json and runs selected steps.
"""
import argparse
import importlib
import sys
import json
from pathlib import Path
from types import SimpleNamespace

# === Import resolver (your JSON-driven path builder) ===
from orchestrator.path_resolver import PathResolver

BASE_DIR = Path(__file__).resolve().parent

def load_task(step_num: int, tasks_map: dict):
    """
    Dynamically load step module using tasks.json mapping.
    """
    if str(step_num) not in tasks_map:
        print(f"❌ No mapping found for step {step_num} in tasks.json")
        sys.exit(1)

    module_name = tasks_map[str(step_num)]
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        print(f"❌ Task module {module_name} not found.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Provisioning Orchestrator for Stotra Manjari")
    parser.add_argument("--config", required=True, help="Path to project config JSON")
    args = parser.parse_args()

    # --- Load config JSON ---
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = BASE_DIR / "configs" / config_path

    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        cfg = json.load(f)

    cfg_ns = SimpleNamespace(**cfg)

    # === Load tasks.json ===
    tasks_config_file = Path(__file__).parent / "configs" / "tasks.json"
    if not tasks_config_file.exists():
        print(f"❌ Missing tasks.json at {tasks_config_file}")
        sys.exit(1)

    with open(tasks_config_file) as f:
        tasks_map = json.load(f)

    # === Build resolver ===
    resolver = PathResolver(
        base_dir=Path(cfg["base_dir"]),
        artist=cfg["artist"],
        amrutham_project_name=cfg["amrutham_project_name"],
        project_name=cfg["project_name"],
        project_type=cfg["project_type"],
        audio_format=cfg["audio_format"],
    )

    print("🚀 Provisioning started")

    # === Run steps ===
    for step in cfg["steps"]:
        task = load_task(step, tasks_map)
        print(f"\n▶️ Running Step {step} - {task.__doc__.strip() if task.__doc__ else ''}")
        try:
            task.run(cfg_ns, resolver)
        except Exception as e:
            print(f"❌ Error in step {step}: {e}")
            sys.exit(1)

    print("\n✅ Provisioning complete!")


if __name__ == "__main__":
    main()
