import json
import os
import pathlib


class Survey:
    """
    Represents survey data from .survey data files
    """

    BLANK = None

    _surveys = {}

    def __init__(self, data):
        """
        Creates survey from data including responses list

        :param data: survey data from file
        """
        self.question = data.get("question", "[INVALID QUESTION]")
        self.id = data.get("id", hash(str(data)))
        self.responses = []
        responses = data.get("responses", [])
        for i in range(len(responses)):
            self.responses.append(Response(self, responses[i]["response"], responses[i]["count"], i + 1))

    @property
    def num_responses(self):
        """
        Get number of responses for this survey.

        :return: number of responses
        """
        return len(self.responses)

    def save_to_file(self, path):
        """
        Saves the survey to the given file path

        :param path: the path to save to

        :return: boolean success of saving
        """
        data = {"question": self.question, "id": self.id,
                "responses": [{"response": response.phrase, "count": response.count} for response in self.responses]}
        try:
            file = open(path, 'w')
            json.dump(data, file)
            file.close()
            return True
        except OSError:
            print("Path (" + path + ") could not be saved to")
        return False

    def __eq__(self, other):
        """
        Equals comparison for surveys.
        Simply compares IDs obtained from data hash.

        :param other: the other survey to compare against

        :return: boolean equality
        """
        if not isinstance(other, Survey):
            return False
        return self.id == other.id

    @classmethod
    def get_surveys(cls):
        """
        Get a copy of the survey list

        :return: a copy of the survey list
        """
        return cls._surveys.copy()

    @classmethod
    def clear_surveys(cls):
        """
        Clear all the loaded surveys.
        """
        cls._surveys.clear()

    @classmethod
    def load_all(cls):
        """
        Load all survey files in the surveys folder.
        """
        for path in pathlib.Path("../surveys").glob("*.survey"):
            Survey.load_survey_file(str(path.resolve()))

    @classmethod
    def reload_all(cls):
        """
        Clear all loaded surveys then load all.
        """
        cls.clear_surveys()
        cls.load_all()

    @classmethod
    def load_survey_file(cls, path):
        """
        Load survey from given path to survey file and add it to survey list if not already loaded

        :param path: path to the file to be loaded

        :return: survey or none if unsuccessful
        """
        try:
            file = open(path)
            s = Survey(json.load(file))
            file.close()
            if s not in cls._surveys.values():
                cls._surveys[os.path.basename(path).rsplit(".")[0]] = s
            return s
        except OSError:
            print("File (" + path + ") could not be opened")
        return None


class Response:
    """
    A response from a survey.
    Acts as a data structure for response info.
    """

    def __init__(self, survey: Survey, phrase: str, count: int, rank: int):
        """
        Set up the data for the response.

        :param survey: the parent survey for this response
        :param phrase: the response phrase
        :param count: the count of respondents with this response
        :param rank: the rank of this response in the survey
        """
        self.survey = survey
        self.phrase = phrase
        self.count = count
        self.rank = rank

    def __eq__(self, other):
        """
        Equals comparison for response
        Checks each of the four fields

        :param other: the other object to compare to

        :return: boolean equality
        """

        if not isinstance(other, Response):
            return False
        return self.survey == other.survey and self.phrase == other.phrase and self.count == other.count and \
               self.rank == other.rank


if not Survey.BLANK:
    Survey.BLANK = Survey({"id": "X", "question": "<No Survey Loaded>"})
