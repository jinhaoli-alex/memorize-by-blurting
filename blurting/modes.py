import random
import time

import config
from ask import print_prompt
from utilities import print_test_prompt, highlight_keywords, fprint, print_magenta_emphasis


class Mode:

    def __init__(self, q_index, data, q_id):
        """
        :param q_id: q's id in json file
        :param q_index: the q's index number in one round of quiz
        :param data: one q's dict data
        """
        self.q_index: int = q_index
        self.data: dict = data
        self.q_id: int = q_id
        self.prompt: str = self.data[self.q_id]["prompt"]
        self.right_answer = self.data[self.q_id]["answer"]
        self.notes = self.data[self.q_id]["notes"]

    def _print_notes(self):

        # When notes is not empty, display it after answering
        if self.notes:  # Note that "if notes is True" is a wrong practice
            print_magenta_emphasis("Additional Notes:")
            fprint(self.notes)

    @staticmethod
    def _self_judge():
        while True:
            self_judge = print_prompt("(self-judge) If correct(y/n)").lower()
            if self_judge in ("y", "n"):
                return True if self_judge == "y" else False

    def multiple_choices(self, option_num: int = config.MULTIPLE_CHOICES_OPTION_NUMBER) -> (bool or None, str):
        """
        The mechanism is combine the right answer and several answers
        from other questions into multiple choices.
        :param option_num: the number of choices
        :return: bool
        """
        fprint("--Multiple Choices--")
        # A list excluding the Q's id, used for creating random options:
        other_ids_list = list(ID for ID in list(self.data.keys()) if ID != self.q_id)

        # Get the bunch of options
        if option_num > config.MAX_OPTION_NUMBER:
            print_magenta_emphasis("Too much options selected! Recommend less!")
            return
        elif len(self.data) >= option_num:
            options_ids = random.sample(other_ids_list, k=option_num - 1) + [self.q_id]
        else:
            options_ids = self.data.keys()
        choices = [self.data[q]["answer"] for q in options_ids]
        random.shuffle(choices)  # Shuffle to random sequence

        # UI
        print_test_prompt(self.q_index, self.prompt)
        for index, answer in enumerate(choices):
            fprint(f"{index + 1}) {answer}\n")
            time.sleep(0.05)

        while True:
            try:
                choice_index_input = int(print_prompt("Answer"))
                user_answer = choices[choice_index_input - 1]
                break
            except ValueError:
                pass
        self._print_notes()

        if not self.right_answer == user_answer:
            fprint(f"Right Answer: {self.right_answer}")

        # Check
        return self.right_answer == user_answer

    def filling_blanks(self):
        """
        Filling the blanks by given prompt.
        Suitable for languages' vocab & expression learning.
        :return: bool
        """

        # UI
        fprint("--Filling Blanks--")
        print_test_prompt(self.q_index, self.prompt)
        user_answer = print_prompt("Answer").lower()
        if not self.right_answer == user_answer:
            fprint(f"Right Answer: {self.right_answer}")
        self._print_notes()

        return self.right_answer == user_answer

    def matching_keywords(self):

        # UI
        fprint("--Mathing Keywords--")
        print_test_prompt(self.q_index, self.prompt)
        user_answer = list(print_prompt("Answer(MUST separate with commas)").lower().split("," and "，"))
        keywords_list = [item.strip() for item in user_answer]

        # Verify
        highlighted_answer = highlight_keywords(keywords_list, self.right_answer)
        fprint(highlighted_answer)

        # self-judge the correction
        if_correct = self._self_judge()
        self._print_notes()

        return if_correct

    def just_prompt(self):

        fprint("--Just prompt--")
        print_test_prompt(self.q_index, self.prompt)
        self._print_notes()

        if_correct = self._self_judge()
        return if_correct
