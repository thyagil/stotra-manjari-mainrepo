import sys, os, re, io
from pathlib import Path
import csv
import unicodedata

from enum import Enum
from aksharamukha import transliterate
class InputType(Enum):
    FILE = 1
    STRING = 2

from Global.Support.chanda import Chanda

BASE_DIR = Path(__file__).resolve().parent
MAIN_DATA_PATH = BASE_DIR / "data"
SUPPORT_DATA_PATH = BASE_DIR / "Support/data"
TMP_PATH = BASE_DIR / "temp"
SANDHI_RULES_FILE = MAIN_DATA_PATH / "sandhi_rules.txt"

class Sandhi:
    def parse_sandhi_rules(self):
        rules_dict = {}
        sandhi_rules_filename = SANDHI_RULES_FILE
        # Open and read the sandhi rules file
        with open(sandhi_rules_filename, 'r', encoding='utf-8') as file:
            for line in file:
                # Split the line by spaces
                parts = line.strip().split()

                # We expect lines to have the format: "ं क ङ्क rule_number label"
                # This should mean 5 parts: original_char, replacement_char, rule_number, label
                if len(parts) == 5:
                    original_part1, original_part2, replacement, rule_number, label = parts
                    original = original_part1 + original_part2
                    # Add the rule to the dictionary
                    rules_dict[(original, label)] = replacement

        return rules_dict

    # Function to filter rules by a list of labels
    def get_sandhi_rules_by_labels(self, rule_labels):
        combined_rules = {}
        rules_dict = self.parse_sandhi_rules()
        for (original, label), replacement in rules_dict.items():
            # If the label matches one of the rule_labels, include it
            if label in rule_labels:
                combined_rules[original] = replacement

        return combined_rules

class Translator:
    def __init__(self, FILE_LOGGER=False):
        self.RESULTS_PATH = TMP_PATH / "results"
        self.RESULTS_PATH.mkdir(parents=True, exist_ok=True)
        self.CHANDA = Chanda(SUPPORT_DATA_PATH)
        self.SASPLITS = list()
        self.FILE_LOGGER = FILE_LOGGER
        self.mapping_sa = [(':', 'ः'), ('सहस्त्र', 'सहस्र'), ('\ue341', 'त्'), ('\ue332', 'क्'), ('\ue348', 'ब्'),
                           ('\u200c', '्')]
        self.mapping_ta = [('(அ)', u'ऽ'),
                           ('(ஆ)', u'ऽऽ'),
                           ('ஶ்ரீ', 'ஸ்ரீ'),
                           ('\ue341', 'த்'),
                           ('\ue332', 'க்'),
                           ('\ue348', 'ப்³'),
                           ('்்', '்'),
                           ('²்', '²'),
                           ('³்', '³'),
                           ('⁴்', '⁴'),
                           ('Ḹ', 'த்³த்⁴யா'),
                           ('¡', 'த்³த்⁴ய'),
                           ('ட்⁴்', 'ட்⁴'),
                           ('அா', 'ஆ'),
                           ('நானா', 'நாநா'),
                           ('முநி', 'முனி'),
                           ('ஸஹஸ்த்ர', 'ஸஹஸ்ர'),
                           ('Þ', 'த்³த்⁴யே')]
        self.exception_list = ["title", "##", "detail", "--", "\t", "$"]
        ## Define the properties
        self.input_language = "sa"
        self.output_language = "ta"
        self.input_directory = ""
        self.output_directory = ""
        self.do_splits = False
        self.insert_tabandbreak_in_output = True

    @property
    def input_directory(self):
        return self._input_directory

    @input_directory.setter
    def input_directory(self, value):
        self._input_directory = value

    @property
    def output_directory(self):
        return self._output_directory

    @output_directory.setter
    def output_directory(self, value):
        self._output_directory = value

    @property
    def do_splits(self):
        return self._do_splits

    @do_splits.setter
    def do_splits(self, value):
        self._do_splits = value

    @property
    def insert_tabandbreak_in_output(self):
        return self._insert_tabandbreak_in_output

    @insert_tabandbreak_in_output.setter
    def insert_tabandbreak_in_output(self, value):
        self._insert_tabandbreak_in_output = value

    @property
    def exception_list(self):
        return self._exception_list

    @exception_list.setter
    def exception_list(self, value):
        self._exception_list = value

    def translate_from_to(self, line, in_lang, out_lang):
        out_line = line
        # TAMIL
        if (in_lang == "sa" or in_lang == "") and out_lang == "ta":
            out_line = transliterate.process('Devanagari', 'Tamil', line, True,
                                             post_options=['RetainTamilDanda', 'TamilRemoveApostrophe', 'TamilNNa'])
        # TELUGU
        elif in_lang == "sa" and out_lang == "te":
            out_line = transliterate.process('Devanagari', 'Telugu', line, False,
                                             post_options=['RetainTeluguDanda', 'PreserveSource'])
        # KANNADA
        elif in_lang == "sa" and out_lang == "ka":
            out_line = transliterate.process('Devanagari', 'Kannada', line, False,
                                             post_options=['RetainKannadaDanda'])
        # ENGLISH
        elif in_lang == "sa" and out_lang == "en":
            out_line = transliterate.process('Devanagari', 'ISO', line, True, post_options=['RetainTamilDanda'])

        elif in_lang == "sa" and out_lang == "roman":
            out_line = transliterate.process('Devanagari', 'RomanReadable', line, True,
                                             post_options=['capitalizeSentence'])
        # GUJARATI
        elif in_lang == "sa" and out_lang == "gu":
            out_line = transliterate.process('Devanagari', 'Gujarati', line, True,
                                             post_options=['RetainGujaratiDanda'])  # AnusvaratoNasalASTISO
        # BENGALI
        elif in_lang == "sa" and out_lang == "be":
            out_line = transliterate.process('Devanagari', 'Bengali', line, True,
                                             post_options=[''])
        # MALAYALAM
        elif in_lang == "sa" and out_lang == "ma":
            out_line = transliterate.process('Devanagari', 'Malayalam', line, True,
                                             post_options=['RetainMalayalamDanda'])  # AnusvaratoNasalASTISO

        return out_line


    def split_clusters(self, txt):
        """ Generate grapheme clusters for the Devanagari text."""
        stop = '्'
        cluster = u''
        end = None
        for char in txt:
            category = unicodedata.category(char)
            if (category == 'Lo' and end == stop) or category[0] == 'M':
                cluster = cluster + char
            else:
                if cluster:
                    yield cluster
                cluster = char
            end = char
        if cluster:
            yield cluster

    def split_syllables(self, input_text):
        data = {}
        data['title'] = 'Identify from Text'
        data['text_mode'] = 'line'
        data['text'] = input_text
        data['output_scheme'] = "devanagari"
        verse_mode = data['text_mode'] == "verse"
        try:
            answer = self.CHANDA.identify_from_text(
                data['text'],
                verse=verse_mode,
                fuzzy=True,
                save_path=self.RESULTS_PATH
            )
            data['result'] = answer['result']
            data['result_path'] = answer['path']
            data['summary'] = self.CHANDA.summarize_results(data['result'])
            data['summary_pretty'] = self.CHANDA.format_summary(data['summary'])
        except Exception as e:
            print(f"Something went wrong. ({e})")
        return data

    def split_line(self, input):
        input = input.strip()
        # If the input already has {b}{t} in it then dont further split the line. just returen it
        pattern = r'\{b\}\{t\}'
        if re.search(pattern, input):
            return input

        split_list_full = list(self.split_clusters(input))
        split_dict_raw = self.split_syllables(input)
        split_dict = split_dict_raw["result"]["line"][0]["result"]
        split_list_lg = list(split_dict['display_lg'])
        print(split_list_full)
        len_lg = len(list(filter(bool, split_list_lg)))
        print("Total aksharas is " + str(len_lg))
        len_lg_1 = 0
        if (len_lg % 2 == 0):
            len_lg_1 = int(len_lg / 2)
        else:
            len_lg_1 = int((len_lg - 1) / 2)
        line = ""
        idx_lg = 0
        idx_syb = 0
        cnt_full = 0
        sep = ""
        if self.insert_tabandbreak_in_output:
            self.LINE_SEP = "{b}{t}"
        else:
            self.LINE_SEP = "\n\t"

        for char in split_list_full:
            line += char
            if split_list_lg[idx_lg] != "" and char != " ":
                idx_syb += 1
            if char != " ":
                idx_lg += 1
            if idx_syb == len_lg_1:
                if split_list_lg[idx_lg] != "":
                    if split_list_full[cnt_full + 1] == " ":
                        sep = self.LINE_SEP
                    else:
                        sep = "-" + self.LINE_SEP
                    break
            cnt_full += 1
        i = 0
        line2 = ""
        for char in split_list_full:
            if i > cnt_full:
                line2 += char
            i += 1
        line = line + sep + line2.strip()
        return line

    def split_line_into_two(self, line):
        line = self.split_line(line)
        SASPLITS = self.read_splits(os.path.join(MAIN_DATA_PATH, 'splits.csv'))
        for k, v in SASPLITS:
            if line.find(k) != -1:
                line = line.replace(k, v)
        return line

    def do_transliteration(self, input_string, input_lang, output_lang, do_splits=False):
        line = input_string
        # do some replaces
        for k, v in self.mapping_sa:
            line = line.replace(k, v)

        if do_splits:
            line = self.split_line(line)
            print("Split line - " + line)
            SASPLITS = self.read_splits(os.path.join(MAIN_DATA_PATH, 'splits.csv'))
            for k, v in SASPLITS:
                if line.find(k) != -1:
                    line = line.replace(k, v)
                    break
        out_line = self.translate_from_to(line, input_lang, output_lang)
        if output_lang == "ta":
            for k, v in self.mapping_ta:
                out_line = out_line.replace(k, v)
        elif output_lang == "roman":
            if out_line.rstrip().endswith(".."):
                out_line = out_line.replace("..", '॥')
            # Check if the last two characters are '..'
            elif out_line.rstrip().endswith('.'):
                # Replace the last character with '॥'
                out_line = out_line[:-1] + '।'
        return out_line

    def get_filepaths(self, directory=None, files_only=False):
        file_paths = []  # List which will store all of the full filepaths.

        # Walk the tree.
        if not directory:
            directory = self.input_directory

        file_paths = []
        if files_only:
            for filename in os.listdir(directory):
                if filename.endswith(".txt") or filename.endswith(".csv"):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        file_paths.append(file_path)
        else:
            for root, directories, files in os.walk(directory):
                for filename in files:
                    if filename.endswith(".txt") or filename.endswith(".csv"):
                        # Join the two strings in order to form the full filepath.
                        file_path = os.path.join(root, filename)
                        if os.path.isfile(file_path):
                            file_paths.append(file_path)

        file_paths.sort()
        return file_paths  # Self-explanatory.

    def read_splits(self, file):
        with open(file, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
        return data

    def process_text(self, input_lang, output_lang, do_splits, process_only_dandas):
        processed_text = []
        input_folder_for_processing = self.input_directory

        self.read_splits(os.path.join(MAIN_DATA_PATH, 'splits.csv'))

        end_exception_list = ["।", "॥"]
        full_file_paths = self.get_filepaths(input_folder_for_processing)
        for file in full_file_paths:
            with io.open(file, 'r') as file3:
                # start reading the input file
                lines = file3.readlines()
                file3.close()
            outfile_name = os.path.basename(file)
            with open(self.output_directory + "/" + outfile_name, 'w+', encoding="utf-8") as outfile:
                outfile.truncate()
                cnt = 0
                lines_count = len(lines)
                metasection = False
                while cnt < lines_count:
                    line = lines[cnt].rstrip()
                    # Metadata section requires special handling
                    out_line = ""
                    if line.strip().startswith("--") and "METADATA" in line.strip() and "END" not in line.strip():
                        metasection = True
                    elif line.strip().startswith("--") and "END" in line.strip():
                        metasection = False
                        outfile.write(line + "\n")
                        cnt += 1
                        line = lines[cnt].rstrip()
                    if metasection:
                        metadata = line.split(":", maxsplit=1)
                        if len(metadata) == 2:
                            meta_label = metadata[0]
                            meta_value = metadata[1]
                            out_line = self.do_transliteration(meta_value, input_lang, output_lang, False)
                            outfile.write(meta_label + ":" + out_line.rstrip() + "\n")
                        else:
                            outfile.write(line + "\n")
                    else:
                        out_line = self.do_transliteration(line, input_lang, output_lang, False)
                        if process_only_dandas:
                            if not line.strip() == "" and all(
                                    not line.startswith(elem) for elem in self.exception_list) and any(
                                line.endswith(elem) for elem in end_exception_list) and not re.match(r'\t', line):
                                # do some replaces
                                out_line = self.do_transliteration(line, input_lang, output_lang, do_splits)
                        else:
                            nextline = ""
                            if cnt + 1 != lines_count:
                                nextline = lines[cnt + 1]
                            nextline_has_tab = False
                            if nextline.startswith("\t"):
                                nextline_has_tab = True
                            if not line.strip() == "" and all(
                                    not line.startswith(elem) for elem in self.exception_list) and not re.match(r'\t',
                                                                                                                line) and not nextline_has_tab:
                                out_line = self.do_transliteration(line, input_lang, output_lang, do_splits)
                        # write output

                        outfile.write(out_line + "\n")
                    processed_text.append(out_line)
                    cnt += 1
            outfile.close()
            processed_text.append("\n")

        return processed_text

    def transliterate(self, do_splits=False, process_only_dandas=False, input_type=InputType.FILE, input_string="",
                      insert_tabandbreak_in_output=True):
        output = ""
        if self.FILE_LOGGER:
            old_stdout = sys.stdout
            log_file = open("out.log", "w")
            sys.stdout = log_file

        self.do_splits = do_splits
        self.insert_tabandbreak_in_output = insert_tabandbreak_in_output
        if input_type == InputType.FILE:
            processed_text = self.process_text(self.input_language, self.output_language, do_splits,
                                               process_only_dandas)
            output = processed_text
        else:
            line = input_string
            out_line = ""
            if line != "":
                out_line = self.do_transliteration(input_string, self.input_language, self.output_language, do_splits)
            output = out_line

        if self.FILE_LOGGER:
            log_file.close()
            sys.stdout = log_file

        return output