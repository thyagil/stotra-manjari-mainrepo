#!/usr/bin/env python3
import shutil
import sys
import plistlib
from pathlib import Path
from typing import Optional

# -------------------------------
# Helpers
# -------------------------------

def safe_copy(src: Path, dest: Path, backup_root: Optional[Path], artifact: str, vol_id: str, lang: Optional[str] = None):
    """Copy file safely with optional backup before overwrite."""
    if dest.exists() and backup_root:
        if artifact in ["content", "meanings"] and lang in ["sa", "sa_bt"]:
            # Always backup both sa and sa_bt
            for bkup_lang in ["sa", "sa_bt"]:
                backup_path = backup_root / vol_id / artifact / bkup_lang / src.name
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(dest, backup_path)
                print(f"   🗄️  Backed up {dest} → {backup_path}")
        else:
            # Normal backup
            if lang:
                backup_path = backup_root / vol_id / artifact / lang / src.name
            else:
                backup_path = backup_root / vol_id / artifact / src.name
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest, backup_path)
            print(f"   🗄️  Backed up {dest} → {backup_path}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    print(f"   📂 Copied {src} → {dest}")


def confirm_deployment(project_id, pre_staging_root, staging_root, plan):
    print(f"\n📋 Deployment Summary for project: {project_id}")
    print(f"Pre-staging root: {pre_staging_root}")
    print(f"Staging root:    {staging_root}")
    print(f"Backup enabled:  {'Yes' if plan.get('backup') else 'No'}\n")

    for vol_id, vol_cfg in plan.get("volumes", {}).items():
        print(f"{vol_id}:")
        if "audio" in vol_cfg:
            print("  - audio")
        if "content" in vol_cfg:
            langs = ", ".join(vol_cfg["content"]["langs"].keys())
            print(f"  - content (langs: {langs})")
        if "durations" in vol_cfg:
            print("  - durations")
        if "meanings" in vol_cfg:
            langs = ", ".join(vol_cfg["meanings"]["langs"].keys())
            print(f"  - meanings (langs: {langs})")
        print("")

    reply = input("⚠️ Proceed with deployment? (y/N): ").strip().lower()
    return reply == "y"


def normalize_langs(langs: dict) -> dict:
    """
    Normalize langs so that 'sa' and 'sa_bt' are handled correctly:
    - If both present → keep only sa_bt
    - If only sa → replace with sa_bt
    - All other langs untouched
    """
    normalized = dict(langs)

    if "sa_bt" in normalized and "sa" in normalized:
        # Drop plain sa
        normalized.pop("sa", None)

    elif "sa" in normalized and "sa_bt" not in normalized:
        # Replace sa with sa_bt
        normalized.pop("sa")
        normalized["sa_bt"] = True

    return normalized


# -------------------------------
# Deployment
# -------------------------------

def deploy_volume(pre_staging_root: Path, staging_root: Path, project_id: str,
                  vol_id: str, vol_plan: dict, backup: bool):
    stage_root = Path(staging_root) / project_id / "volumes" / vol_id
    stage_root.mkdir(parents=True, exist_ok=True)

    print(f"\n🚀 Deploying {vol_id} → {stage_root}")

    backup_root = None
    if backup:
        backup_root = Path(staging_root) / project_id / "backup"
        print(f"📦 Backup → {backup_root}")
        backup_root.mkdir(parents=True, exist_ok=True)

    # === AUDIO ===
    if "audio" in vol_plan:
        src_dir = Path(pre_staging_root) / project_id / "audio" / vol_id
        if src_dir.exists():
            for src in src_dir.glob("*.m4a"):
                chap_id = src.stem
                dest = stage_root / "chapters" / chap_id / "audio.m4a"
                safe_copy(src, dest, backup_root, "audio", vol_id)

    # === DURATIONS ===
    if "durations" in vol_plan:
        src_dir = Path(pre_staging_root) / project_id / "durations" / vol_id
        if src_dir.exists():
            for src in src_dir.glob("*.csv"):
                chap_id = src.stem
                dest = stage_root / "chapters" / chap_id / "durations.csv"
                safe_copy(src, dest, backup_root, "durations", vol_id)

    # === CONTENT ===
    if "content" in vol_plan:
        langs = normalize_langs(vol_plan["content"]["langs"])
        for lang in langs.keys():
            src_dir = Path(pre_staging_root) / project_id / "content" / vol_id / lang
            if src_dir.exists():
                for src in src_dir.glob("*.txt"):
                    chap_id = src.stem
                    dest_lang = "sa" if lang == "sa_bt" else lang
                    dest = stage_root / "chapters" / chap_id / dest_lang / "verses.txt"
                    safe_copy(src, dest, backup_root, "content", vol_id, lang)

    # === MEANINGS ===
    if "meanings" in vol_plan:
        langs = normalize_langs(vol_plan["meanings"]["langs"])
        for lang in langs.keys():
            src_dir = Path(pre_staging_root) / project_id / "meanings" / vol_id / lang
            if src_dir.exists():
                for src in src_dir.glob("*.txt"):
                    chap_id = src.stem
                    dest_lang = "sa" if lang == "sa_bt" else lang
                    dest = stage_root / "chapters" / chap_id / dest_lang / "meanings.txt"
                    safe_copy(src, dest, backup_root, "meanings", vol_id, lang)

    print(f"✅ {vol_id} deployment complete.")


# -------------------------------
# Main
# -------------------------------

def build_deployment_plan(deployment_cfg: dict) -> dict:
    """Return a dict of only the volumes/artifacts/langs to deploy."""
    plan = {"backup": deployment_cfg.get("backup", False), "volumes": {}}
    for vol_id, vol_cfg in deployment_cfg.get("volumes", {}).items():
        vol_plan = {}

        if vol_cfg.get("audio", {}).get("deploy"):
            vol_plan["audio"] = {"deploy": True}

        if vol_cfg.get("content", {}).get("deploy"):
            langs = {k: v for k, v in vol_cfg["content"].get("langs", {}).items() if v}
            if langs:
                vol_plan["content"] = {"deploy": True, "langs": langs}

        if vol_cfg.get("durations", {}).get("deploy"):
            vol_plan["durations"] = {"deploy": True}

        if vol_cfg.get("meanings", {}).get("deploy"):
            langs = {k: v for k, v in vol_cfg["meanings"].get("langs", {}).items() if v}
            if langs:
                vol_plan["meanings"] = {"deploy": True, "langs": langs}

        if vol_plan:
            plan["volumes"][vol_id] = vol_plan

    return plan


def deploy_from_plist(project_id: str):
    project_dir = Path(__file__).resolve().parent.parent / "config/projects" / project_id
    plist_file = project_dir / "staging_deployer.plist"

    if not plist_file.exists():
        raise FileNotFoundError(f"❌ staging_deployer.plist not found at {plist_file}")

    with open(plist_file, "rb") as f:
        config = plistlib.load(f)

    pre_staging_root = Path(config["pre_staging"]["root"])
    staging_root = Path(config["staging"]["root"])
    deployment_cfg = config["deployment"]

    deployment_plan = build_deployment_plan(deployment_cfg)

    if not confirm_deployment(project_id, pre_staging_root, staging_root, deployment_plan):
        print("❌ Deployment cancelled.")
        sys.exit(0)

    for vol_id, vol_cfg in deployment_plan["volumes"].items():
        deploy_volume(pre_staging_root, staging_root, project_id, vol_id, vol_cfg, deployment_plan.get("backup", False))


if __name__ == "__main__":
    deploy_from_plist("skp_srimad_bhagavatam")
