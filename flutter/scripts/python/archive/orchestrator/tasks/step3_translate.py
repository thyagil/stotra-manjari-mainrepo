# orchestrator/tasks/step3_translate.py
import os
from Global.Translation import Translator, InputType
from pathlib import Path

def run(args, resolver):
    """
    Step 3: Translate Sanskrit text into target languages.
    """
    langs = args.langs or ["en"]
    volume = args.volume if args.project_type == "volume" else None

    # input dir is always sanskrit
    input_dir = Path(resolver.content_output_working) / "sa"

    for lang in langs:
        if lang in ["sa", "ta"]:
            print(f"⚠️ Skipping {lang} (no translation needed)")
            continue

        output_dir = Path(resolver.content_output_working) / lang
        os.makedirs(output_dir, exist_ok=True)

        translator = Translator(FILE_LOGGER=False)
        translator.input_directory = str(input_dir)
        translator.output_directory = str(output_dir)
        translator.exception_list = ["title", "--", "detail", "##", "$"]
        translator.input_language = "sa"
        translator.output_language = lang
        translator.transliterate(True, False, InputType.FILE)

        print(f"🌍 Translated Sanskrit → {lang}, saved to {output_dir}")
