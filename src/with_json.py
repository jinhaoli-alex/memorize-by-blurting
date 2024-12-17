import datetime
import json
import re
import sys
import time
from datetime import timedelta
import os

import config
from ask import ask_recommended_mode, print_prompt
from config import DATE_FORMAT, current_date, formatted_current_date
from utilities import print_magenta_emphasis, fprint, display_subjects_list


def add_res(subject):
    print_magenta_emphasis(
        f"\n---Store resource in {subject}(default, {config.RESOURCE_CREATION_NO_IN_A_ROW} qs in a row)---")
    for i in range(config.RESOURCE_CREATION_NO_IN_A_ROW):
        print(f"{str(i + 1)})")

        prompt = ""
        while not prompt:  # Empty prompt is not acceptable, same point for input answer
            prompt = print_prompt("Enter prompt")

        answer = ""
        while not answer:
            answer = print_prompt("Enter answer")

        # Optional
        recommended_mode: list = ask_recommended_mode()
        notes = print_prompt("Enter additional notes")

        data = read_json(subject)

        # This must convert to list and then can be subscriptable.
        keys = list(data.keys())

        # increment by 1 if keys list is not empty, else start from 1.
        prompt_id = str(int(keys[-1]) + 1) if keys else "1"
        data[prompt_id] = config.Template().create_template(subject, recommended_mode, prompt, answer, notes)

        _write_json(subject, data)
        fprint("Topic created.")


def json_log_record(subject, data, q_id, correct: bool):
    """
    Used to change the record of json file. Facilitate & improve next revision experience.
    :param subject: -
    :param data: whole file of a subject
    :param q_id: question id
    :param correct: determine total time practiced/ "right | wrong times"
    :return: None
    """

    # One particular question's data
    q_data = data[q_id]

    # Initialise the scheduled revision date if it's a new question(i.e. q_data["total time practiced"] = 0)
    if q_data["total time practiced"] == 0:
        q_data["first test date"] = formatted_current_date
        q_data["scheduled revision date"] = {pending_date: "pending" for pending_date in list(
            (current_date + timedelta(days=day_interval)).strftime(DATE_FORMAT) for day_interval in
            config.review_interval)}
        q_data["if end revision cycle"] = False  # From None -> False

    # Change necessary logging info to facilitate checking or next practice.
    q_data["total time practiced"] += 1
    q_data["right | wrong times"][0 if correct else 1] += 1

    proficiency = q_data["right | wrong times"][0] / q_data["total time practiced"]
    q_data["Predicted proficiency"] = round(proficiency, 2)

    # Check the completion of daily task
    if formatted_current_date in q_data["scheduled revision date"].keys():
        q_data["scheduled revision date"][formatted_current_date] = "finished"

    # If finish revision cycle, turn "if end revision cycle" into True
    if_end_revision_cycle = False
    while not if_end_revision_cycle:
        if list(q_data["scheduled revision date"].values()) == ["finished"] * len(q_data["scheduled revision date"]):
            if_end_revision_cycle = True
    if if_end_revision_cycle:
        q_data["if end revision cycle"] = True

    # Re-write
    data[q_id] = q_data
    _write_json(subject, data)


def read_json(subject) -> dict:
    with open(config.subject_path[subject], "r") as f:
        try:
            data = dict(json.load(f))  # A dictionary returned.
        except json.decoder.JSONDecodeError:
            print_magenta_emphasis("File is not able to be decoded, please check the json file")
            sys.exit()
    return data


def _write_json(subject, updated_data) -> None:
    """
    Only accept the global data to rewrite,rather than q_data.
    :param subject: -
    :param updated_data: the updated version of data
    :return:None
    """
    with open(config.subject_path[subject], "w+") as f:
        json.dump(obj=updated_data,
                  fp=f,
                  indent=4,
                  ensure_ascii=False)  # In case sometimes wanting to input Chinese, set ensure_ascii to false.


def data_check():
    """
    This module ensures:
    I. Check if the resource portal is empty, and force to create a new subject to start if is.
    II. The question snippets' ids are in right order(i.e. 1, 2, 3...);
    III. Check the integrity of q template and correct the missing ones;
    IV. Empty all answering records as punishment if certain points are missed to review;
    :return: None
    """

    # Task I:
    def task1():
        while not os.listdir(config.stap):
            print_magenta_emphasis("Database is empty!\nYou MUST create a subject portal before start.")
            create_new_subject()

    # Task II:
    def task2(subject):
        def _is_sequential_keys(json_data):
            # Check if the JSON data is a dictionary
            if not isinstance(json_data, dict):
                return False

            keys = json_data.keys()
            # Convert the keys to integers and sort them
            sorted_keys = sorted(map(int, keys))

            # Check if the sorted keys form a sequential sequence starting from 1
            return sorted_keys == list(range(1, len(keys) + 1))

        # Load the JSON data from a file (replace 'your_file.json' with the actual filename)
        try:
            original_json_data = read_json(subject)
            original_keys_list = list(original_json_data.keys())
            ordered_key_list = list(range(1, len(original_json_data) + 1))
            if _is_sequential_keys(original_json_data):
                fprint(f" - {subject} already is in order.")
            else:
                print_magenta_emphasis(f" - {subject} disorder is discovered, fixing...")
                new_json = dict()
                for i in ordered_key_list:
                    new_key = str(i)
                    new_json[new_key] = original_json_data[original_keys_list[i - 1]]

                    # Write the new JSON data back to the original file
                    _write_json(subject, new_json)
                    print_magenta_emphasis(" - Now the JSON file has sequential ids starting from 1.")
        except Exception as e:
            print_magenta_emphasis(f"An error occurred: {str(e)}")

    # Task III:
    def task3(subject):
        try:
            json_data = read_json(subject)
            template_keys = config.Template().get_keys()
            for key, item in json_data.items():
                if item.keys() != template_keys:
                    # Create new, blank template for fill in
                    new_data_template = config.Template().get_empty_template()
                    try:
                        for _key in item.keys():
                            new_data_template[_key] = item[_key]
                    except KeyError:
                        fprint("Certain key does not match to rewrite, please check.")
                    json_data[key] = new_data_template
            _write_json(subject, json_data)
            fprint(" - Template integrity now is guaranteed.")
        except Exception as e:
            print_magenta_emphasis(f"An error occurred: {str(e)}")

    # Task IV
    def task4():

        # For one subject.
        def check_punished_qs() -> int:
            q_punished: int = 0

            data: dict = read_json(subject)
            for q in data:

                # For one Q
                if data[q]["if end revision cycle"] is False:
                    prescribed_dates: list = [date for date in data[q]["scheduled revision date"].keys()]

                    for date in prescribed_dates:

                        # First convert the time string into a datetime object, facilitating to compare
                        that_date = datetime.datetime.strptime(date, config.DATE_FORMAT)

                        # If satisfying the two condition, it is a missing Q
                        if that_date < current_date and data[q]["scheduled revision date"][date] == "pending":
                            q_punished += 1

                            # back_up the knowledge part
                            recommended_mode = data[q]["recommended mode"]
                            prompt = data[q]["prompt"]
                            answer = data[q]["answer"]
                            notes = data[q]["notes"]

                            # Change raw data for one q (i.e. complete empty)
                            q_data = config.Template().create_template(subject, recommended_mode, prompt, answer, notes)
                            q_data["being punished before"][0] = True
                            q_data["being punished before"][1] += 1

                            # replace raw data in whole dictionary
                            data[q] = q_data
                            break

            if q_punished != 0:
                # Rewrite into json
                _write_json(subject, data)
                print_magenta_emphasis(
                    f"{subject} has {q_punished} Q(s) is/are emptied due to disobedience of revision cycle")
                return q_punished
            else:
                fprint(f"You finished all previous {subject}'s daily tasks.")
                return 0

        d = dict()
        for subject in config.subject_path.keys():
            q_punished_amount = check_punished_qs()
            d[subject] = q_punished_amount

        print_magenta_emphasis(" ---Punishment--- ")
        for subj in d:
            if d[subj] == 0:
                fprint(f'> {subj}: {d[subj]}')
            elif d[subj] > 0:
                print_magenta_emphasis(f'> {subj}: {d[subj]}')

        if sum(d.values()) == 0:
            fprint(f"Total: {sum(d.values())}")
        elif sum(d.values()) > 0:
            print_magenta_emphasis(f"Total: {sum(d.values())}")

    fprint("--Checking data integrity--")
    fprint("Now start cleansing...")
    task1()
    for sub_abbr in config.subject_path.keys():
        task2(sub_abbr)
        task3(sub_abbr)
        print()
    task4()
    fprint("Finish cleansing")
    time.sleep(1)


def search_string_in_nested_json(json_data, target_string, current_path=''):
    results = []

    for key, value in json_data.items():
        current_key_path = f"{current_path}.{key}" if current_path else key

        # Check if the key contains the target string
        if isinstance(key, str) and target_string in key:
            results.append(current_key_path)

        # Check if the value is a string and contains the target string
        elif isinstance(value, str) and target_string in value:
            results.append(current_key_path)

        # Recursively search in nested dictionaries
        elif isinstance(value, dict):
            nested_results = search_string_in_nested_json(value, target_string, current_key_path)
            results.extend(nested_results)

    return results


def create_new_subject():
    """
    Create a new json file for a new subject in the resource folder
    :return: None
    """
    existing_subjects_name = config.subject_path.keys()
    while True:
        subject_name = print_prompt("Subject name(should be unique)").capitalize()
        if subject_name not in existing_subjects_name:
            file_path = os.path.join(config.stap, f"{subject_name}_resources.json")
            break
        else:
            print_magenta_emphasis(f"{subject_name} is existing, please change the subject name.")

    with open(file_path, "w+") as jf:
        json.dump({}, jf)
        print_magenta_emphasis("Please wait a sec...")

    while not os.path.isfile(file_path):
        time.sleep(1)
    print_magenta_emphasis(
        f"\"{subject_name}\" portal successfully created, REBOOT programme to become effective.")
    sys.exit()


def delete_subject():
    display_subjects_list()

    # If database is empty, return the function
    if len(config.subject_path) == 0:
        print("Resource base is empty")
        return

    subject_no = print_prompt("Input the subject No", output_type="int")
    confirm = ''
    while confirm not in ['y', 'n']:
        confirm = print_prompt("This will delete all the subject resource in it, are you sure?(y/n)").lower()
    if confirm.lower() == 'y':
        try:
            if subject_no in range(1, len(config.subject_path) + 1):
                get_json_file_path = list(config.subject_path.values())[subject_no - 1]
                os.remove(get_json_file_path)
                print_magenta_emphasis("Delete successfully, REBOOT for updated list.")
                sys.exit()
            else:
                print_magenta_emphasis("This index is out of bound. Retry later.")
        except FileNotFoundError as e:
            print(str(e))
        except Exception as e:
            print(str(e))
    elif confirm.lower() == 'n':
        print_magenta_emphasis('Deletion canceled.')


class Statistics:
    def __init__(self, subject):
        self.subject: str = subject
        self.data = read_json(self.subject)
        self.total_qs = len(self.data.keys())

        self.new_q_index_list = list()
        self.new_qs = self._new_q

        self.pending_q_index_list = list()
        self.pending_qs = self._pending_q

        self.finished_q_index_list = list()
        self.finished_qs = self._finished_q

    def __repr__(self):  # For programmers
        return f"Statistics(subject: {self.subject}, total: {self.total_qs}, " \
               f"pending: {self.pending_qs}, finished: {self.finished_qs}, new: {self.new_qs})"

    def __str__(self):  # For users
        report = f"""
In {self.subject}, totally {self.total_qs} Qs,
there are:
{self.finished_qs} Qs finished,
{self.new_qs} Qs new,
{self.pending_qs} Qs pending.
"""
        return report

    # Set read-only vars with @Property decorator
    @property
    def _pending_q(self) -> int:
        """
        This function checks the daily tasks(all pending qs) in ONE subject.
        :return: one list of string indices of upcoming tasks
        """
        data = read_json(self.subject)
        today: str = config.formatted_current_date
        list_of_path = search_string_in_nested_json(data, today)  # Full path to the date info

        # Write a regex that follows the pattern "1.scheduled revision date.2023-10-07"
        # For checking format of path
        path_pattern = r'^(\d+)\.scheduled revision date\.(\d{4}-\d{2}-\d{2})$'  # Must in "scheduled revision date"

        # Derivation of questions' id by checking regex
        pending_q_ids_list = []
        for path_string in list_of_path:
            matching = re.match(path_pattern, path_string)
            if matching:
                current_q_id = str(matching.group(1))
                pending_q_ids_list.append(current_q_id)
        self.pending_q_index_list = pending_q_ids_list

        return len(self.pending_q_index_list)

    @property
    def _finished_q(self) -> int:
        finished_q_index_list = list()
        for index, q in enumerate(self.data):
            if self.data[q]["if end revision cycle"]:
                finished_q_index_list.append(index)
        self.finished_q_index_list = finished_q_index_list

        return len(finished_q_index_list)

    @property
    def _new_q(self) -> int:
        data = read_json(self.subject)

        new_q_index_list = []
        for q_id in data:
            time_practiced: int = data[q_id]["total time practiced"]
            if time_practiced == 0:
                new_q_index_list.append(q_id)
        self.new_q_index_list = new_q_index_list

        return len(new_q_index_list)
