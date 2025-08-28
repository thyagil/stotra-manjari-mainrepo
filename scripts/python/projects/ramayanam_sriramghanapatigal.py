from dataclasses import dataclass

@dataclass
class Folders:
    volume: int
    volume_code: str
    volume_name: str
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

        ### SOURCE STAGING FOLDERS
        # FLDR_CONTENT_VIDEO - This is the original text used for creating the videos
        # The files here is primarily used to get the metadata for STEP 2 - Extract from ppts
        # Only sa and ta is used in the hope that ta metadata is already localized.
        # EX: /Volumes/AMRUTHAM/Sriram Ghanapatigal/Srimad Ramayanam/Video/Mastering/Source Files/DOC/TXT/01 Bala Kandam/sa/
        self.FLDR_METADATA = f"{base}/Video/Mastering/Source Files/DOC/TXT/{self.volume_code} {self.volume_name}/{self._lang}/"

        # FLDR_PPTS - This is the folder of Published PPTs from which text is extracted
        # In most cases ta is the only folder to get the source ppts from
        # EX: /Volumes/AMRUTHAM/Sriram Ghanapatigal/Srimad Ramayanam/Video/Mastering/Source Files/PPT/01 Bala Kandam/Without Dupes/ta/
        self.FLDR_PPTS = f"{base}/Video/Mastering/Source Files/PPT/{self.volume_code} {self.volume_name}/Without Dupes/ta/"

        # FLDR_VIDEOS - This is the localtion for published videos that is used to extract final audio
        # EX: /Volumes/AMRUTHAM/Sriram Ghanapatigal/Srimad Ramayanam/Video/Bounces/01 Bala Kandam/Published/
        self.FLDR_VIDEOS = f"{base}/Video/Bounces/{self.volume_code} {self.volume_name}/Published/"

        # FLDR_FCPXML - This is location where the FCPXML files are located that will be used to export durations
        # EX: /Volumes/AMRUTHAM/Sriram Ghanapatigal/Srimad Ramayanam/Video/Mastering/Final Cut Pro/FCPXML/Localized/01 Bala Kandam/
        self.FLDR_FCPXML = f"{base}/Video/Mastering/Final Cut Pro/FCPXML/Localized/{self.volume_code} {self.volume_name}/"
        ###### END SOURCE FOLDERS

        ### DESTINATION STAGING FOLDERS
        # FLDR_CONTENT_FINAL - This is the fully edited text that is extracted from the published PPTs
        # EX: /Volumes/AMRUTHAM/Sriram Ghanapatigal/Srimad Ramayanam/Video/Mastering/Source Files/DOC/TXT/01 Bala Kandam/Bounces/sa/
        self.STAGING_FLDR_CONTENT = f"{base}/Video/Mastering/Source Files/DOC/TXT/{self.volume_code} {self.volume_name}/Bounces/{self._lang}/"

        # FLDR_AUDIO_FINAL - This is the fully edited audio that is extracted from the published videos
        # EX: /Volumes/AMRUTHAM/Sriram Ghanapatigal/Srimad Ramayanam/Audio/Bounces/01 Bala Kandam/audio/aac/
        self.STAGING_FLDR_AUDIO = f"{base}/Audio/Bounces/{self.volume_code} {self.volume_name}/audio/{self._audio_format}/"

        # FLDR_DURATIONS - This is location where the durations are located csv files that will be exported from fcpxml files
        # EX: /Volumes/AMRUTHAM/Sriram Ghanapatigal/Srimad Ramayanam/Audio/Bounces/01 Bala Kandam/durations/
        self.STAGING_FLDR_DURATIONS = f"{base}/Audio/Bounces/{self.volume_code} {self.volume_name}/durations/"

        # FLDR_MEANINGS - This is location where the meanings for the content is located
        # EX: /Volumes/AMRUTHAM/Sriram Ghanapatigal/Srimad Ramayanam/Video/Mastering/Source Files/DOC/TXT/01 Bala Kandam/Meanings/en/
        self.STAGING_FLDR_MEANINGS = f"{base}/Video/Mastering/Source Files/DOC/TXT/{self.volume_code} {self.volume_name}/Meanings/{self._lang}/"

# === Registry of Kandams ===
folders = {
    1: Folders(1, "01", "Bala Kandam", "balakandam"),
    2: Folders(2, "02", "Ayodhya Kandam", "ayodhyakandam"),
    3: Folders(3, "03", "Aranya Kandam", "aranyakandam"),
    4: Folders(4, "04", "Kishkinda Kandam", "kishkindakandam"),
    5: Folders(5, "05", "Sundara Kandam", "sundarakandam"),
    6: Folders(6, "06", "Yuddha Kandam", "yuddhakandam"),
}
