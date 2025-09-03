# orchestrator/tasks/step5_generate_meanings.py
import openai
from pathlib import Path

def run(args, resolver):
    """
    Step 5: Generate meanings using OpenAI.
    """
    openai.api_key = args.openai_api_key
    lang = args.lang or "en"
    volume = args.volume if args.project_type == "volume" else None

    input_dir = resolver.resolve("content", volume=volume, lang="sa")
    output_dir = resolver.resolve("meanings", volume=volume, lang=lang)
    output_dir.mkdir(parents=True, exist_ok=True)

    for txt_file in Path(input_dir).glob("*.txt"):
        verses = txt_file.read_text(encoding="utf-8").splitlines()
        prompt = f"Translate the following Sanskrit verses into {lang}, one line each:\n" + "\n".join(verses)
        resp = openai.chat.completions.create(model="gpt-4o-mini",
                                              messages=[{"role": "user", "content": prompt}],
                                              temperature=0.2)
        meanings = resp.choices[0].message.content
        out_file = output_dir / txt_file.name
        out_file.write_text(meanings, encoding="utf-8")
        print(f"💬 Meanings saved → {out_file}")
