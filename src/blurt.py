# Exterior packages
import random
import time
from colorama import Fore, Style
from tabulate import tabulate

# Local package
import config
import ask
import modes
import utilities
from utilities import fprint, print_magenta_emphasis
import with_json


class QuizGenerator:

    # This will implement once an instanciation of this class is created
    def __init__(self, subject: str, if_automate_mode_selection: bool):
        self.subject = subject
        self.if_automate_mode_selection = if_automate_mode_selection

        if not if_automate_mode_selection:
            self_chosen_mode = ask.ask_mode()
            self.self_chosen_mode = self_chosen_mode

    def _quiz_and_justify(self,
                          subject: str,
                          q_index: int,
                          if_automate_mode_selection: bool,
                          q_id: int,
                          data: dict,
                          q_content: dict,
                          accuracy: list[int, int]):
        """
        1. Provide general support of justification to different modes of Qs
        2. Raise right answer and additional notes
        3. logging record
        4. BGM
        :param subject: -
        :param q_index: the index of q in current round
        :param if_automate_mode_selection: use defaulted mood stored in resource json if is true
        :param q_id: sequential number printed at the prompts' beginning
        :param data: one subject's json data
        :param q_content: one question's data
        :return: boolean value indicating if it's correct
        """

        # Determine quiz mode used
        if if_automate_mode_selection:
            recommended_mode_list = q_content["recommended mode"]
            if not recommended_mode_list:
                # Check if recommended_mode_list is empty
                mode = config.DEFAULT_QUIZ_MODE
            else:
                mode = random.choice(recommended_mode_list)
        else:
            mode = self.self_chosen_mode

        _rm = config.review_mode
        mode = modes.Mode(q_index, data, q_id)
        if mode == _rm["Multiple Choices"]:
            if_correct: bool = mode.multiple_choices()
        elif mode == _rm["Filling Blanks"]:
            if_correct = mode.filling_blanks()
        elif mode == _rm["Matching Keywords Input"]:
            if_correct = mode.matching_keywords()
        else:  # JP mode will process this one
            if_correct = mode.just_prompt()

        # BGM for encouragement
        if if_correct:
            accuracy[0] += 1
            fprint(f"{Fore.GREEN}Right{Style.RESET_ALL}\n")
            utilities.play_music("do it right")
        elif not if_correct:
            accuracy[1] += 1
            fprint(f"{Fore.RED}Fault{Style.RESET_ALL}\n")
            utilities.play_music("do it wrong")

        # Record into json
        with_json.json_log_record(subject, data, q_id, if_correct)

    def daily_task_qs(self):
        """Ask one pending q derived from subject json data."""

        # specifically for one subject. Return a list of pending questions' indices
        q_indices: list = with_json.Statistics(self.subject).pending_q_index_list
        if not q_indices:  # In case there is no daily task already(i.e. empty), print warning
            print_magenta_emphasis("Today is not scheduled any questions. Try draw new Qs into revision cycle.")
            time.sleep(2)
            return

        accuracy = [0, 0]
        for index in range(1, config.ONE_ROUND_TEST + 1):
            data = with_json.read_json(self.subject)
            q_id = random.choice(q_indices)
            q_indices.pop(q_id)
            q_content = data[q_id]
            self._quiz_and_justify(self.subject,
                                   index,
                                   self.if_automate_mode_selection,
                                   q_id,
                                   data,
                                   q_content,
                                   accuracy)
            if len(q_indices) == index:
                break

        utilities.play_music("finish a quiz")
        fprint(f"Accuracy: r{accuracy[0]} / w{accuracy[1]}")

    def old_qs(self):
        """
        Blurting exercise for a series of random but old qs.
        So qs must have already started.
        """

        accuracy = [0, 0]
        data = with_json.read_json(self.subject)
        if not data:  # In case the subject json file in empty
            return

        # Filter away new qs
        ids: list = list(data.keys())
        for q_id in ids:
            if data[q_id]["total time practiced"] == 0:
                ids.remove(q_id)

        # If No of questions in a subject is smaller than test number prescribed, reset the loop time
        one_round = config.ONE_ROUND_TEST
        if len(data.keys()) < one_round:
            one_round = len(ids)
        for q_index in range(1, one_round + 1):
            data = with_json.read_json(self.subject)
            q_id = random.choice(ids)
            ids.remove(q_id)
            q_content = data[q_id]
            self._quiz_and_justify(self.subject,
                                   q_index,
                                   self.if_automate_mode_selection,
                                   q_id,
                                   data,
                                   q_content,
                                   accuracy)

        utilities.play_music("finish a quiz")
        fprint(f"Accuracy: right {accuracy[0]} / wrong {accuracy[1]}")

    def new_qs(self):
        """
        This function is implicitly wrapped in "random_qs" function
        in case of there are less proportion of questions are in the "revision cycle",
        it will automatically call some new questions into cycle.
        :return: None
        """
        data = with_json.read_json(self.subject)
        new_q_id_list: list = with_json.Statistics(self.subject).new_q_index_list
        if not new_q_id_list:
            print_magenta_emphasis(f"No new questions in {self.subject}.")
            return

        accuracy = [0, 0]
        for q_index in range(1, config.ONE_ROUND_TEST + 1):
            q_id = new_q_id_list[q_index - 1]
            q_content = data[q_id]
            self._quiz_and_justify(self.subject,
                                   q_index,
                                   self.if_automate_mode_selection,
                                   q_id,
                                   data,
                                   q_content,
                                   accuracy)
            if len(new_q_id_list) == q_index:
                break

        utilities.play_music("finish a quiz")
        fprint(f"Accuracy: r{accuracy[0]} / w{accuracy[1]}")


def one_round_blurt_revision(subject):
    fprint("\n--Start blurting quiz--")
    ask_quiz_scenario: str = ask.ask_quiz_scenario()
    if ask_quiz_scenario == "Back to main menu":
        access_point()

    if_automate_mode_selection: bool = ask.ask_if_automate_mode_selection()

    quiz_generator = QuizGenerator(subject, if_automate_mode_selection)

    if ask_quiz_scenario == "Daily tasks":
        quiz_generator.daily_task_qs()
    elif ask_quiz_scenario == "Draw new questions into revision cycle":
        quiz_generator.new_qs()
    elif ask_quiz_scenario == "old questions":
        quiz_generator.old_qs()


def statistics():
    header = ["subjects", "total Number", "new Qs", "pending Qs", "finished Qs"]

    tabular_data = []
    subjects = list(config.subject_path.keys())
    for subject in subjects:
        s = with_json.Statistics(subject)

        total_q = s.total_qs
        new_q = s.new_qs
        pending_q = s.pending_qs
        finished_q = s.finished_qs

        one_column = [subject, total_q, new_q, pending_q, finished_q]
        tabular_data.append(one_column)

    # Print Table
    fprint("---Subject Statistics---")
    print(tabulate(tabular_data=tabular_data,
                   headers=header,
                   tablefmt="fancy_grid",
                   numalign="center",
                   showindex=range(1, len(subjects) + 1)))


def access_point():
    utilities.print_welcome_portal()

    # Check data integrity
    with_json.data_check()

    while True:
        option_input = ask.initialised_ask()

        if option_input == "Add resources":
            subject = ask.ask_subject()
            with_json.add_res(subject)
        elif option_input == 'Start quiz':
            subject = ask.ask_subject()
            one_round_blurt_revision(subject)
        elif option_input == "Back to main manu":
            access_point()
        elif option_input == "Create new subject":
            with_json.create_new_subject()
        elif option_input == "Delete a subject":
            with_json.delete_subject()
        elif option_input == "English dictionary API":
            word: str = ask.print_prompt("Input the English word You want to check")
            utilities.english_word_dictionary(word)
        elif option_input == "Statistics":
            statistics()
