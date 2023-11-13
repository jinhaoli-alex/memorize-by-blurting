from colorama import Fore, Style
from utilities import print_magenta_emphasis, fprint, display_subjects_list
from config import subject_path, quiz_scenario, review_mode, DEFAULT_QUIZ_MODE, initialise_options


def print_prompt(prompt: str, output_type='str'):
    if output_type == 'str':
        return input(f"{Fore.RED}>>> {prompt}: {Style.RESET_ALL}").strip()
    elif output_type == 'int':
        try:
            return int(input(f"{Fore.RED}>>> {prompt}: {Style.RESET_ALL}").strip())
        except ValueError:
            return print_prompt(prompt, output_type)


def ask_quiz_scenario() -> str:
    """
    Ask the intended quiz scenarios:
    1. daily task -> questions that are in revision cycle;
    2. start new questions -> all new points -> introduce more questions into revision cycle
    3. random questions -> i.e. new + old question mix -> consolidate previous knowledge;
    :return:
    """
    _qs = quiz_scenario
    for key, value in _qs.items():
        fprint(f"{key}. {value}")

    while True:
        ask_daily_task_index: str = print_prompt("Enter your selection for quiz scenario")
        if ask_daily_task_index in _qs:
            return _qs[ask_daily_task_index]
        else:
            pass


def ask_subject() -> str:
    display_subjects_list()

    subject_no = ''
    while subject_no not in range(1, len(subject_path) + 1):
        subject_no = print_prompt("Input the subject No", output_type='int')
    return list(subject_path.keys())[subject_no - 1]


def ask_if_automate_mode_selection() -> bool:
    """
    This function will simply ask the willingness for automate(i.e. prescribed recommended_mode),
    or self-determined mode.
    :return:
    """
    fprint("1) Yes")
    fprint("2) No")
    if_automate_mode_selection = ''
    while if_automate_mode_selection not in ['1', '2']:
        if_automate_mode_selection = print_prompt("Use recommended quiz mode")
    return True if if_automate_mode_selection == "1" else False


def ask_mode() -> str:
    """
    Used during the start of the quiz.
    :return: the abbr of a mode
    """
    _rm = review_mode
    _rm["Default Mode"] = DEFAULT_QUIZ_MODE

    for index, mode_index_chosen in enumerate(_rm):
        fprint(f"{index + 1}. {mode_index_chosen}")
    while True:
        try:
            mode_index_chosen = int(print_prompt("Review mode(index)"))
            mode = list(_rm.values())[mode_index_chosen - 1]
            return mode
        except ValueError:
            pass


def ask_recommended_mode() -> list:
    _rm = review_mode

    print_magenta_emphasis("Input the indices of modes without space.")
    for i, key in enumerate(_rm.keys()):
        fprint(f"{i + 1}. '{key}' mode")

    while True:
        try:
            mode_indices: list[int] = [int(i) for i in print_prompt("Recommended mode")]
            recommended_mode_list = list()
            for i in mode_indices:
                recommended_mode_list.append(list(_rm.values())[i - 1])
            return recommended_mode_list
        except ValueError:

            pass


def initialised_ask():
    """
    This function prompts at the beginning of whole project:
    Ask what to do:
    1. create new resources
    2. start a quiz session
    3. restart the whole program -> in case needing change subject
    """
    ios = initialise_options

    print()
    _option_dict = dict()
    for i, item in enumerate(ios):
        _option_dict[str(i + 1)] = item
        fprint(f"{i + 1}) {item}")

    while True:
        option_input: str = print_prompt("Select what to do next(input index)")
        if option_input in _option_dict.keys():
            return _option_dict[option_input]
