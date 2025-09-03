import json
from pathlib import Path

class PathBuilder:
    def __init__(self, json_path: str, volume_code: str, volume_name: str, lang="sa", audio_format="aac"):
        with open(json_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.base = Path(self.data["base"])
        self.volume_code = volume_code
        self.volume_name = volume_name
        self.lang = lang
        self.audio_format = audio_format

    def build(self, template: str) -> Path:
        return self.base / template.format(
            volume_code=self.volume_code,
            volume_name=self.volume_name,
            lang=self.lang,
            audio_format=self.audio_format,
        )

    # === Staging folders ===
    @property
    def staging_content(self): return self.build(self.data["staging"]["content"])
    @property
    def staging_audio(self): return self.build(self.data["staging"]["audio"])
    @property
    def staging_durations(self): return self.build(self.data["staging"]["durations"])
    @property
    def staging_meanings(self): return self.build(self.data["staging"]["meanings"])

    # === Source folders ===
    @property
    def src_metadata(self): return self.build(self.data["source"]["metadata"])
    @property
    def src_ppts(self): return self.build(self.data["source"]["ppts"])
    @property
    def src_videos(self): return self.build(self.data["source"]["videos"])
    @property
    def src_fcpxml(self): return self.build(self.data["source"]["fcpxml"])
