from Global.Translation import Translator
from Global.Translation import InputType
import sys, os
from projects.ramayanam_sriramghanapatigal import folders
def translate(input_txt_folder, output_txt_folder, lang):
        print("✅ Translation is running.")
        print("=============")
        # First Generate the Clean Input File
        print("Translating sanskrit to desired language.")
        translator = Translator(FILE_LOGGER=False)
        translator.input_directory = input_txt_folder
        translator.output_directory = output_txt_folder
        translator.exception_list = ["title", "--", "detail", "##", "$"]
        translator.input_language = "sa"
        translator.output_language = lang
        translator.skip_lines = 0
        processed_text = translator.transliterate(True, False, InputType.FILE)

if __name__ == "__main__":
    volume =  5
    ##langs=["be", "ka", "ma", "gu", "en", "te", "sa", "ta"]
    langs=["te"]
    # NEVER send out ta for translation
    for lang in langs:
        output_lang = lang
        input_txt_folder = folders[volume].STAGING_FLDR_CONTENT
        if lang == "ta":
            print("CANT send tamil for translations")
            exit()
        elif lang == "sa":
            folders[volume].lang = "sa_bt"
        else:
            folders[volume].lang = lang
        output_txt_folder = folders[volume].STAGING_FLDR_CONTENT
        os.makedirs(output_txt_folder, mode=0o777, exist_ok=True)
        translate(input_txt_folder, output_txt_folder, output_lang)
