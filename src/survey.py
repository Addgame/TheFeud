import json
import pathlib


class Survey:
    """
    Represents survey data from .survey data files
    """

    _surveys = []
    current_survey = None

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
        print(survey for survey in self._surveys if survey == self)
        # TODO: Make sure this works as intended
        # Not sure which will work. Maybe both will. Make sure to figure this out before thinking there is a bug
        if self not in self._surveys:
            self._surveys.append(self)
        # if not (survey for survey in self._surveys if survey == self):
        #     self._surveys.append(self)

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
        Get the survey list

        :return: the survey list
        """
        return cls._surveys

    @classmethod
    def clear_surveys(cls):
        """
        Clear all the loaded surveys.
        """
        cls._surveys.clear()
        cls.current_survey = None

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

    @staticmethod
    def load_survey_file(path):
        """
        Load survey from given path to survey file

        :param path: path to the file to be loaded

        :return: boolean success of loading
        """
        try:
            file = open(path)
            Survey(json.load(file))
            file.close()
            return True
        except OSError:
            print("File (" + path + ") could not be opened")
        return False


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
