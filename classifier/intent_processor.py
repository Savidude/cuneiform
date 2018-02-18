from nltk.stem.lancaster import LancasterStemmer
from nltk.tokenize import word_tokenize

import os
import logging
import json

logging.basicConfig(filename=os.getcwd().replace('classifier', '') + 'system.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')


def get_intents_dir_path():
    """ Searches for the intents directory in the latest application
    :return: intents directory in latest application
    """
    # getting applications directory
    cwd = os.path.realpath(__file__)
    cwd = cwd.replace('classifier' + os.path.sep + 'intent_processor.py', '')
    applications_dir = cwd + os.path.sep + os.path.join("resources", "deployment", "applications")
    dir_list = os.listdir(applications_dir)

    # getting the latest application
    app_list = []
    for dir in dir_list:
        if os.path.isdir(os.path.join(applications_dir, dir)):
            if dir[:3] == 'app':
                try:
                    app_val = int(dir[3:])
                    app_list.append(app_val)
                except ValueError:
                    logging.warning("Invalid application name: " + dir)

    intents_dir_path = applications_dir + os.path.sep + 'app' + str(max(app_list)) + os.path.sep + 'intents'
    return intents_dir_path


def stem_slots(value, synonyms):
    """ Stems each value and its synonyms for slots
    :param value: a value for a slot
    :param synonyms: list of synonyms of the given value
    :return: list of stemmed words for the provided value, and its synonyms
    """
    words = []
    stemmer = LancasterStemmer()

    # stemming the value
    tokenized_value = word_tokenize(value.lower())
    if len(tokenized_value) > 1:
        for i, val in enumerate(tokenized_value):
            if i == 0:
                words.append(stemmer.stem(val) + '-')
            elif i == len(tokenized_value) - 1:
                words.append('-' + stemmer.stem(val))
            else:
                words.append('-' + stemmer.stem(val) + '-')
    else:
        words.append(stemmer.stem(tokenized_value[0]))

    # stemming synonyms
    if synonyms is not None:
        for synonym in synonyms:
            tokenized_synonym = word_tokenize(synonym.lower())
            if len(tokenized_synonym) > 1:
                for i, val in enumerate(tokenized_synonym):
                    if i == 0:
                        words.append(stemmer.stem(val) + '-')
                    elif i == len(tokenized_value) - 1:
                        words.append('-' + stemmer.stem(val))
                    else:
                        words.append('-' + stemmer.stem(val) + '-')
            else:
                words.append(stemmer.stem(tokenized_synonym[0]))

    return words


def process_slots():
    """ Processes slot data from intents and writes processed data to a file
    :return: None
    """
    slots_data = {'intents': []}

    intents = get_intents()
    intent_array = intents['intents']
    for intent in intent_array:
        slots = intent['slots']
        if slots:
            intent_data = {'name': intent['name'], 'slots': []}
            for slot in slots:
                slot_data = {'name': slot['name'], 'type': slot['type'], 'values': []}
                slot_type = slot['type']
                if slot_type == 'custom':
                    synonyms = slot['synonyms']
                    values = slot['values']
                    for value in values:
                        value_data = {'name': value, 'words': []}
                        for synonym in synonyms:
                            if synonym['value'] == value:
                                words = stem_slots(value, synonym['synonyms'])
                                for word in words:
                                    value_data['words'].append(word)
                                slot_data['values'].append(value_data)
                                break
                        if len(value_data['words']) == 0:
                            words = stem_slots(value, None)
                            value_data['words'].append(words[0])
                            slot_data['values'].append(value_data)

                intent_data['slots'].append(slot_data)
            slots_data['intents'].append(intent_data)

    slots_data_file_path = get_intents_dir_path() + os.path.sep + 'slots_data.json'
    with open(slots_data_file_path, 'w') as out_file:
        json.dump(slots_data, out_file)


def get_intents():
    """ Searches for the intent.json file in the latest application
    :return: intents object
    """
    intents_file_path = get_intents_dir_path() + os.path.sep + 'intents.json'
    with open(intents_file_path) as data_file:
        intents = json.load(data_file)
        return intents


def process_intents():
    """ Processes utterance data from intents and writes processed information to a file
    :return: None
    """
    corpus_words = {}
    intent_words = {}
    stemmer = LancasterStemmer()

    intents = get_intents()
    intents_array = intents['intents']
    for intent in intents_array:
        name = intent['name']
        intent_words[name] = []

        sample_utterances = intent['sample_utterances']
        for utterance in sample_utterances:
            slot_detected = False
            for word in word_tokenize(utterance):
                if word == '{':
                    slot_detected = True
                elif word == '}':
                    slot_detected = False
                    continue

                if not slot_detected:
                    stemmed_word = stemmer.stem(word.lower())
                    if stemmed_word not in corpus_words:
                        corpus_words[stemmed_word] = 1
                    else:
                        corpus_words[stemmed_word] += 1

                    intent_words[name].extend([stemmed_word])

        utterance_data = {'corpus_words': corpus_words, 'intent_words': intent_words}
        utterance_data_file_path = get_intents_dir_path() + os.path.sep + 'utterance_data.json'
        with open(utterance_data_file_path, 'w') as out_file:
            json.dump(utterance_data, out_file)


def main():
    process_slots()
    process_intents()


if __name__ == '__main__':
    main()
