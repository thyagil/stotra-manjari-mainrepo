# orchestrator/tasks/step10_deploy_to_prod.py
import subprocess
from pathlib import Path

def run_cmd(cmd):
    print("🚀", " ".join(cmd))
    subprocess.run(cmd, check=True)

def run(args, resolver):
    """
    Step 10: Deploy staging → production (Google Cloud Storage).
    """
    project_id = args.project_id
    staging_root = resolver.staging_root / project_id
    bucket_root = f"gs://stotra-manjari-assets/projects/{project_id}"

    if not staging_root.exists():
        print(f"❌ No staging folder {staging_root}")
        return

    run_cmd([
        "gsutil", "-m", "rsync", "-r",
        "-x", r"(\.DS_Store$|^\._.*$|\.lock$|\.tmp$|\.swp$|~\$.*|backup/.*)",
        str(staging_root), bucket_root
    ])
    print(f"✅ Deployed {project_id} to {bucket_root}")
