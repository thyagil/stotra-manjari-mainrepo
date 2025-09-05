import plistlib
from pathlib import Path
from admin.support.translation import Translator, InputType
from admin.config.utils import get_project_path


def translate_project(project_id: str):
    """
    Step 3: Translate Sanskrit text into target languages.
    Uses new orchestrator.plist schema:
      - staging_root as base
      - format controls chaptering
      - input_dir/output_dir inferred from staging_root
    """

    project_dir = get_project_path(project_id)
    orch_plist = project_dir / "orchestrator.plist"

    if not orch_plist.exists():
        raise FileNotFoundError(f"❌ orchestrator.plist not found: {orch_plist}")

    with open(orch_plist, "rb") as f:
        config = plistlib.load(f)

    project_format = config.get("format", "volume")
    staging_root = Path(config.get("staging_root", ""))
    if not staging_root:
        raise ValueError("❌ staging_root not defined in orchestrator.plist")

    step_cfg = config.get("translation", {})
    langs = step_cfg.get("langs", [])
    volumes_cfg = step_cfg.get("volumes", {})

    for vol_id, vol_cfg in volumes_cfg.items():
        if not vol_cfg.get("orchestrate", False):
            print(f"⏭️ Skipping {vol_id}")
            continue

        input_lang = vol_cfg.get("input_lang", "sa")

        # Input folder is always text/<volume>/<input_lang>
        input_dir = staging_root / "content" / vol_id / input_lang
        if not input_dir.exists():
            print(f"⚠️ Input dir not found for {vol_id}: {input_dir}")
            continue

        print(f"🌍 Translating {vol_id} (from {input_lang})")

        for lang in langs:
            if lang in ["sa", "ta"]:  # never auto-translate Sanskrit or Tamil
                print(f"   ⏭️ Skipping {lang}")
                continue

            lang_out_dir = staging_root / "content" / vol_id / lang
            lang_out_dir.mkdir(parents=True, exist_ok=True)

            translator = Translator(FILE_LOGGER=False)
            translator.input_directory = str(input_dir)
            translator.output_directory = str(lang_out_dir)
            translator.exception_list = ["title", "--", "detail", "##", "$"]
            translator.input_language = input_lang
            translator.output_language = lang

            translator.transliterate(True, False, InputType.FILE)
            print(f"   ✅ {input_lang} → {lang}, saved to {lang_out_dir}")


if __name__ == "__main__":
    translate_project("skp_srimad_bhagavatam")
