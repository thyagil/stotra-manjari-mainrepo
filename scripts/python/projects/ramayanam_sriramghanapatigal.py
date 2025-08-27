from dataclasses import dataclass

@dataclass
class Folders:
    kandam_no: int
    kandam_code: str
    kandam_name: str
    dir_code: str
    _lang: str = "sa"
    _audio_format: str = "aac"

    def __post_init__(self):
        self._update_paths()

    # --- Language property ---
    @property
    def lang(self):
        return self._lang

    @lang.setter
    def lang(self, value):
        self._lang = value
        self._update_paths()

    # --- Audio format property ---
    @property
    def audio_format(self):
        return self._audio_format

    @audio_format.setter
    def audio_format(self, value):
        self._audio_format = value
        self._update_paths()

    # --- Internal: rebuild all folder paths ---
    def _update_paths(self):
        base = "/Volumes/AMRUTHAM/Sriram Ghanapatigal/Srimad Ramayanam"
        # FLDR_CONTENT_VIDEO - This is the original text used for creating the videos
        self.FLDR_CONTENT_VIDEO = f"{base}/Video/Mastering/Source Files/DOC/TXT/{self.kandam_code} {self.kandam_name}/{self._lang}/"

        # FLDR_PPTS - This is the folder of Published PPTs from which text is extracted
        self.FLDR_PPTS = f"{base}/Video/Mastering/Source Files/PPT/{self.kandam_code} {self.kandam_name}/Without Dupes/ta/"

        # FLDR_CONTENT_FINAL - This is the fully edited text that is extracted from the published PPTs
        self.FLDR_CONTENT_FINAL = f"{base}/Video/Mastering/Source Files/DOC/TXT/{self.kandam_code} {self.kandam_name}/Bounces/{self._lang}/"

        # FLDR_VIDEOS - This is the localtion for published videos that is used to extract final audio
        self.FLDR_VIDEOS = f"{base}/Video/Bounces/{self.kandam_code} {self.kandam_name}/Published/"

        # FLDR_AUDIO_FINAL - This is the fully edited audio that is extracted from the published videos
        self.FLDR_AUDIO_FINAL = f"{base}/Audio/Bounces/{self.kandam_code} {self.kandam_name}/audio/{self._audio_format}/"

        # FLDR_FCPXML - This is location where the FCPXML files are located that will be used to export durations
        self.FLDR_FCPXML = f"{base}/Video/Mastering/Final Cut Pro/FCPXML/Localized/{self.kandam_code} {self.kandam_name}/"

        # FLDR_DURATIONS - This is location where the durations are located csv files that will be exported from fcpxml files
        self.FLDR_DURATIONS = f"{base}/Audio/Bounces/{self.kandam_code} {self.kandam_name}/durations/"

        # FLDR_MEANINGS - This is location where the meanings for the content is located
        self.FLDR_MEANINGS = f"{base}/Video/Mastering/Source Files/DOC/TXT/{self.kandam_code} {self.kandam_name}/Meanings/{self._lang}/"

# === Registry of Kandams ===
folders = {
    1: Folders(1, "01", "Bala Kandam", "balakandam"),
    2: Folders(2, "02", "Ayodhya Kandam", "ayodhyakandam"),
    3: Folders(3, "03", "Aranya Kandam", "aranyakandam"),
    4: Folders(4, "04", "Kishkinda Kandam", "kishkindakandam"),
    5: Folders(5, "05", "Sundara Kandam", "sundarakandam"),
    6: Folders(6, "06", "Yuddha Kandam", "yuddhakandam"),
}
