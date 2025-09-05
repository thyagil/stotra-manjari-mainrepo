from pathlib import Path

class PathResolver:
    """
    Resolve working/staging directory paths for projects.
    Supports volume-based, chapter-based, and standalone projects.
    """
    def find_file_by_projectid(self, directory, project_id, file_extensions=None, multiple=False):
        """
        Find file(s) in a directory that start with the given project_id
        and optionally match one or more file extensions.

        Args:
            directory: folder to search in
            project_id: filename prefix to match
            file_extensions: None, string (".pptx"), or list/tuple of strings
            multiple: if True, return a sorted list of all matches;
                      else return the first match

        Returns:
            - Path object (if multiple=False and a match is found)
            - list[Path] (if multiple=True)
            - None (if no matches and multiple=False)
            - [] (if no matches and multiple=True)
        """
        directory = Path(directory)
        if isinstance(file_extensions, str):
            exts = [file_extensions.lower()]
        elif isinstance(file_extensions, (list, tuple)):
            exts = [ext.lower() for ext in file_extensions]
        else:
            exts = None

        matches = []
        for f in directory.iterdir():
            if f.is_file() and f.name.startswith(project_id):
                if exts is None or f.suffix.lower() in exts:
                    if multiple:
                        matches.append(f.resolve())
                    else:
                        return f.resolve()

        if multiple:
            return sorted(matches, key=lambda x: x.name.lower())
        return None


    def __init__(self, base_dir: Path,
                 artist: str,
                 amrutham_project_name: str,
                 project_name: str,
                 project_type: str = "volume", # project, standalone
                 volume_code: str = None,
                 volume_name: str = None,
                 audio_format: str = "aac",
                 lang: str = "sa"
        ):
        """
        project_type: "volume", "chapter", or "standalone"
        """
        self.base = base_dir / artist / amrutham_project_name
        self.artist = artist
        self.amrutham_project_name = amrutham_project_name
        self.project_name = project_name
        self.project_type = project_type
        self.volume_code = volume_code
        self.volume_name = volume_name
        self.audio_format = audio_format
        self.lang = lang

    ###################
    # INPUT FOLDERS
    # -----------------
    # Video folders
    # Used for extraction of audio from published videos
    # Standalone - /Volumes/AMRUTHAVANI/Bhavadhaarini/Sri Sankara Devi Stotrams/Video/Bounces/Published/Kanakadhara Stotram/
    # -----------------
    @property
    def videos_input_working(self):
        if self.project_type == "volume":
            return self.base / f"Video/Bounces/{self.volume_code} {self.volume_name}/Published"
        else:  # chapter or standalone
            return self.base / f"Video/Bounces/Published"

    # -----------------
    # Metadata folders
    # These are text files with the metadata section
    # -----------------
    @property
    def metadata_input_working(self):
        if self.project_type == "volume":
            return self.base / f"Video/Mastering/Source Files/DOC/TXT/{self.volume_code} {self.volume_name}/{self.lang}"
        else:
            return self.base / f"Video/Mastering/Source Files/DOC/TXT/{self.lang}"

    # -----------------
    # Ppts folders
    # These are powerpoint files to extract content
    # -----------------
    @property
    def ppts_input_working(self):
        if self.project_type == "volume":
            return self.base / f"Video/Mastering/Source Files/PPT/{self.volume_code} {self.volume_name}/Without Dupes/{self.lang}"
        else:
            return self.base / f"Video/Mastering/Source Files/PPT/Without Dupes"

    # -----------------
    # FCPXML folders
    # These are fxpxml files to extract durations
    # -----------------
    @property
    def fcpxml_input_working(self):
        if self.project_type == "volume":
            return self.base / f"Video/Mastering/Final Cut Pro/FCPXML/Localized/{self.volume_code} {self.volume_name}"
        else:
            return self.base / "Video/Mastering/Final Cut Pro/FCPXML/Localized"
    ###################

    ###################
    # OUTPUT FOLDERS
    # -----------------
    # Audio folders
    # /Volumes/AMRUTHAVANI/Bhavadhaarini/Sri Sankara Devi Stotrams/Audio/Bounces/Kanakadhara Stotram/
    # -----------------

    @property
    def audio_output_working(self):
        if self.project_type == "volume":
            return self.base / f"Audio/Bounces/{self.volume_code} {self.volume_name}/audio/{self.audio_format}"
        else:
            return self.base / f"Audio/Bounces/audio/{self.audio_format}"

    @property
    def durations_output_working(self):
        if self.project_type == "volume":
            return self.base / f"Audio/Bounces/{self.volume_code} {self.volume_name}/durations"
        else:
            return self.base / "Audio/Bounces/durations"

    @property
    def meanings_output_working(self):
        if self.project_type == "volume":
            return self.base / f"Video/Mastering/Source Files/DOC/TXT/{self.volume_code} {self.volume_name}/Meanings/{self.lang}"
        else:
            return self.base / f"Video/Mastering/Source Files/DOC/TXT/Meanings/{self.lang}"

    @property
    def content_output_working(self):
        if self.project_type == "volume":
            return self.base / f"Video/Mastering/Source Files/DOC/TXT/{self.volume_code} {self.volume_name}/Bounces/{self.lang}"
        else:
            return self.base / f"Video/Mastering/Source Files/DOC/TXT/Bounces"


    def get_file_by_name(self, lookup_folder, project_name, file_extensions=None, multiple=False):
        """
        Wrapper for find_file_by_projectid that returns Path(s).
        """
        return self.find_file_by_projectid(lookup_folder, project_name, file_extensions, multiple)
