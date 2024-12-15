"""
Variables are storing here.
They are modifiable to change programme behaviours.
"""

# Exterior packages
import datetime
import os
import re

# Manually changeable parameters

BGM_SWITCH_ON: bool = True  # Background music switch

ONE_ROUND_TEST: int = 15  # The number of qs one round includes.

DEFAULT_QUIZ_MODE: str = "mc"  # For  a question with unfilled recommended_mode, use it by default.

MAX_LINE_WIDTH: int = 100  # Is applied on all common text printed, in order to make newlines.

MULTIPLE_CHOICES_OPTION_NUMBER = 3  # For multiple choices mode

RESOURCE_CREATION_NO_IN_A_ROW: int = 15  # To facilitate edition, set the number of resource that can add in a row.

TIME_LAG_PRINTING_LINES: float = 0  # for fprint()

SLEEP_TIME_AFTER_CALL_DICTIONARY: int = 8  # The waiting time after checking the eng-word with API

# Unchangeable variables

# Based on The Ebbinghaus Forgetting Curve, apply intervals for reviewing.
# timedelta function in datetime module to create time lag. e.g. lag=datetime.timedelta(day=1)
# Unit: day(s); format: dict{core_time_practiced: interval}
review_interval = (1, 2, 5, 8, 14)

MAX_OPTION_NUMBER: int = 5  # For multiple choices mode

project_absolute_path: str = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
stap = project_absolute_path + "/subject_resources/"  # subject textual (resources) absolute path

aap = project_absolute_path + "/audio_resource/"  # audio's absolute path
audio_path = {
    "done_right": aap + "done_right.wav",
    "done_wrong": aap + "done_wrong.wav",
    "finish_quiz": aap + "finish_quiz.wav"
}

# Interaction patterns*,
# 1. Multiple choices(e.g. langs vocab consolidation),
# 2. Filling blanks(crucial keywords of concepts in ESS & Econ)
# 3. Input keywords and match(check) with right answer**,
# 4. Only prompt displayed but no further interaction***, etc.
# * Based on different characteristics of subjects, methods applied should vary.
# ** Here my idea is input any keywords blurted in mind, and show correct answer with highlighted words input
# *** e.g. Economic diagram can be tested by giving just a prompt and draw it on a paper
review_mode = {
    "Multiple Choices": "mc",
    "Filling Blanks": "fb",
    "Matching Keywords Input": "mk",
    "Just Prompt": "jp",
}

quiz_scenario = {
    '1': "Daily tasks",
    '2': "Draw new questions into revision cycle",
    '3': "old questions",
    '4': "Back to main menu"}

initialise_options = ("Start quiz",
                      "Add resources",
                      "English dictionary API",
                      "Statistics",
                      "Create new subject",
                      "Delete a subject",
                      "Back to main manu")

template_keys = None


class Template:

    def __init__(self):
        """
        Defaulted and general template for creating resources
        strictly followed the blurting method & The Ebbinghaus Forgetting Curve!
        predicted efficiency can be scored using the formula: (right_time)/(total_time)
        links are expected to add some additional resources from web or local.
        """
        self.template = {"subject": None,
                         "recommended mode": None,
                         "prompt": None,
                         "answer": None,
                         "notes": None,  # hints or detailed version of notes
                         "total time practiced": 0,  # by default set to zero
                         "right | wrong times": [0, 0],
                         "first test date": None,
                         "scheduled revision date": None,  # Based on The Ebbinghaus Forgetting Curve's gold interval
                         "Predicted proficiency": None,
                         "if end revision cycle": None,  # This parameter indicates if finish the revision cycle
                         # This parameter indicates if being punished before due to the incompleteness of revision cycle
                         "being punished before": [False, 0],
                         }

    def create_template(self,
                        subject_name: str,
                        recommended_mode,
                        prompt: str,
                        answer: str,
                        notes: str):
        self.template["subject"] = subject_name
        self.template["recommended mode"] = recommended_mode
        self.template["prompt"] = prompt
        self.template["answer"] = answer
        self.template["notes"] = notes  # hints or detailed version of notes

        return self.template

    def get_empty_template(self):
        return self.template

    def get_keys(self):
        return list(self.template.keys())  # used to check the integrity of Q's resources


def get_resource_paths() -> dict:
    subject_paths = dict()
    path_resources: list[str] = [stap + f for f in os.listdir(stap) if os.path.isfile(os.path.join(stap, f))]

    # Derive subject name from absolute path based on the uniform format of json resource files:
    # "xxx_resources.json"
    # And add to resource list
    pattern = r"subject_resources/(.*?)_resources\.json"
    for file_path in path_resources:
        matching = re.search(pattern, file_path)
        if matching:
            subject_name: str = matching.group(1).capitalize()
            subject_paths[subject_name] = file_path
        else:
            print("Error occurs in resource directory, please check.")

    subject_paths = {key: subject_paths[key] for key in sorted(subject_paths)}
    return subject_paths


subject_path = get_resource_paths()

# Date info
DATE_FORMAT = "%Y-%m-%d"
current_date = datetime.datetime.today()
formatted_current_date = current_date.strftime(DATE_FORMAT)