import random
from nltk.stem.lancaster import LancasterStemmer
from nltk.tokenize import word_tokenize

# Response System Operation constants
RESPONSE_SET = 'responseSet'
USER_ACTION = 'userAction'
OPTIONS = 'options'
SEND = 'send'

CONFIRM_CORPUS = {
    -1: ['don\'t know', 'not sure', 'undecided', 'haven\'t decided', 'have not decided'],
    1: ['yes', 'yeah', 'yea', 'ya', 'yep', 'affirmative', 'fine', 'good', 'okay', 'ok', 'true', 'alright', 'all right',
        'aye', 'certainly', 'definitely', 'exactly', 'of course', 'positively', 'precisely', 'sure', 'very well'],
    0: ['no', 'negative', 'not', 'never']
}


class Response(object):
    def __init__(self, sys_op):
        self.response_set = None
        self.user_action = None
        self.options = None
        self.update_properties(sys_op)

    def update_properties(self, sys_op):
        properties = sys_op.properties
        for property in properties:
            property_name = property[0].value
            property_value = property[1]

            if property_name == RESPONSE_SET:
                self.response_set = []
                for response in property_value.array:
                    self.response_set.append(response.value)
            elif property_name == USER_ACTION:
                self.user_action = property_value.value
            elif property_name == OPTIONS:
                attributes = property_value.attributes
                options = {}
                for attribute in attributes:
                    sample_utterances = []
                    key = attribute[0].value
                    values = attribute[1].array
                    for value in values:
                        utterance = value.value
                        sample_utterances.append(utterance)
                    options[key] = sample_utterances
                self.options = options

    def execute_operation(self, name):
        operate = getattr(self, name, self.invalid_operation)
        return operate(name)

    def invalid_operation(self, name):
        raise Exception('{} operation not identified in Response'.format(name))

    def send(self, name):
        response = random.choice(self.response_set)
        user_action = self.user_action
        response_data = (response, user_action)
        return response_data

    def get_confirm(self, message):
        """ Identified the user's type of confirmation
        :param message: message sent by the user
        :return: -1 : undecided
                0 : denied
                1 : accepted
                2 : unable to identify
        """
        message = message.lower()
        for key, value in CONFIRM_CORPUS.items():
            for word in value:
                if word in message:
                    return key
        return 2

    def select_option(self, message):
        corpus_words = {}
        option_words = {}
        stemmer = LancasterStemmer()

        for option, sample_utterances in self.options.items():
            option_words[option] = []
            for utterance in sample_utterances:
                for word in word_tokenize(utterance):
                    stemmed_word = stemmer.stem(word.lower())
                    if stemmed_word not in corpus_words:
                        corpus_words[stemmed_word] = 1
                    else:
                        corpus_words[stemmed_word] += 1

                    option_words[option].extend([stemmed_word])

        option_scores = []
        tokenized_message = word_tokenize(message.lower())
        for option, words in option_words.items():
            score = 0
            for word in tokenized_message:
                stemmed_word = stemmer.stem(word)
                if stemmed_word in words:
                    score += (1 / corpus_words[stemmed_word])
            option_score = {'option': option, 'score': score}
            option_scores.append(option_score)

        max_score = 0
        option_index = -1
        for index, option_data in enumerate(option_scores):
            option_score = option_data['score']
            if option_score > max_score:
                max_score = option_score
                option_index = index
        option = option_scores[option_index]
        option_name = option['option']
        return option_name
