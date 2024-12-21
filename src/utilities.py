# Exterior packages import
import json
import re
import time
from pprint import pformat
import requests
import simpleaudio
from colorama import Fore, Style
from datetime import datetime
import textwrap
import pyfiglet

# Interior package import
from config import TIME_LAG_PRINTING_LINES, MAX_LINE_WIDTH, subject_path, audio_path, SLEEP_TIME_AFTER_CALL_DICTIONARY, \
    BGM_SWITCH_ON


def english_word_dictionary(word: str):
    def search_eng_word_info():
        api = "https://api.dictionaryapi.dev/api/v2/entries/en/<word>"

        result = requests.request(url=api.replace("<word>", word.lower()), method="get")
        result = json.loads(result.text)

        try:
            if result["title"] == "No Definitions Found":
                return "An error occurred: " + Fore.RED + "No info retrieved!" + Style.RESET_ALL
        except TypeError:
            return result[0]["meanings"]

    result = search_eng_word_info()
    print_magenta_emphasis(pformat(result))
    time.sleep(SLEEP_TIME_AFTER_CALL_DICTIONARY)


def play_music(status):
    """
    There are three conditions:
    1. "Do it right"
    2. "Do it wrong"
    3. "Finish a quiz"

    Copyright (c) : Audios are derived from Duolingo.
    :param status: one of the three above
    :return: None
    """
    if BGM_SWITCH_ON:
        _ap = audio_path
        if status == "do it right":
            wave_obj = simpleaudio.WaveObject.from_wave_file(_ap["done_right"])
        elif status == "do it wrong":
            wave_obj = simpleaudio.WaveObject.from_wave_file(_ap["done_wrong"])
        elif status == "finish a quiz":
            wave_obj = simpleaudio.WaveObject.from_wave_file(_ap["finish_quiz"])
        else:
            return Exception("Error (Fail to display audio_resource)")
        play_obj = wave_obj.play()
        play_obj.wait_done()


def print_test_prompt(q_index: int, prompt):
    fprint(Fore.GREEN + f"{q_index})Prompt: " + Style.RESET_ALL + prompt)


def highlight_keywords(keywords_list, answer_string):
    escaped_keywords = [re.escape(keyword) for keyword in keywords_list]  # Escape special characters in keywords

    pattern = "|".join(escaped_keywords)

    def replace_keywords(match):
        return f"{Fore.LIGHTYELLOW_EX}{match.group(0)}{Style.RESET_ALL}"

    highlighted_string = re.sub(pattern, replace_keywords, answer_string, flags=re.IGNORECASE)

    return highlighted_string


def print_magenta_emphasis(text: str, initial_indent: str = ''):
    fprint(Fore.MAGENTA + f"{text}" + Style.RESET_ALL, initial_indent=initial_indent)


def print_welcome_portal():
    """
    At the initialisation part, print welcome texts and graphs.
    :return: None
    """

    def _get_greeting():
        current_time = datetime.now().time()

        if datetime.strptime("07:00", "%H:%M").time() <= current_time <= datetime.strptime("12:00", "%H:%M").time():
            return "Good morning! Have a nice and fulfilling experience with Blurt Bee!"

        elif datetime.strptime("12:01", "%H:%M").time() <= current_time <= datetime.strptime("13:40", "%H:%M").time():
            return "It is lunch time now! Have you had lunch already?"

        elif datetime.strptime("13:41", "%H:%M").time() <= current_time <= datetime.strptime("18:30", "%H:%M").time():
            return "Good afternoon, now start your happy blurting journey with Blurting Bee!"

        elif datetime.strptime("18:31", "%H:%M").time() <= current_time <= datetime.strptime("20:00", "%H:%M").time():
            return "Have you finished your dinner? Show your learning to me by starting a new blurting quiz!"

        elif datetime.strptime("20:01", "%H:%M").time() <= current_time <= datetime.strptime("23:00", "%H:%M").time():
            return "It is approaching bedtime! Do some small quiz and go to sleep for a good brain rest."

        elif datetime.strptime("23:01", "%H:%M").time() <= current_time \
                or current_time <= datetime.strptime("05:00", "%H:%M").time():
            return "Though study is beneficial, but having a good rest is more crucial for a sustainable study journey!"

        elif datetime.strptime("05:01", "%H:%M").time() <= current_time <= datetime.strptime("06:59", "%H:%M").time():
            return "You get up so early! Don't waste the golden period during the morning, do Blurting Bee now!"

    logo = "Blurting  Bee"
    f = pyfiglet.figlet_format(logo, font="slant")
    print(f)

    print_magenta_emphasis(
        """!!!----- Here Is Blurting Bee To Boost Your Memory Efficiency-----!!!""",
        initial_indent=" " * 10)
    print_magenta_emphasis(
        f"""Welcome! {_get_greeting()} Let us start!""")
    input("Press Return key to continue...")


def fprint(text: str,
           max_width: int = MAX_LINE_WIDTH,
           time_lag: float = TIME_LAG_PRINTING_LINES,
           initial_indent: str = ''):
    """
    Ensure the uniform format for common texts printed.
    :param text: -
    :param max_width: the maximum length of characters for one line
    :param time_lag: the time lag between lines printed
    :param initial_indent: -
    :return: None
    """
    # If the text is within one-line length, just print it without further do
    if len(text) <= max_width:
        print(text)
        return
    # Else, need to be chunked
    else:
        wrapped_lines = textwrap.wrap(text, width=max_width, initial_indent=initial_indent)
        for line in wrapped_lines:
            print(line)
            time.sleep(time_lag)


def display_subjects_list():
    _sp = subject_path
    for i, sub_abbr in enumerate(_sp):
        fprint(f"{i + 1}) {sub_abbr}")
