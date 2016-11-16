from pymongo import MongoClient


def get_quiz_words():
    learnt_words = list()
    for x in db.tocheck.find():
        learnt_words.append(x["word"])
    return learnt_words


def learn_word(word):
    db.tocheck.insert_one({"word": word})


client = MongoClient()
client = MongoClient("46.101.249.90", 27017)
db = client.ec

