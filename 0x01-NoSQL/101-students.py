#!/usr/bin/env python3
""" python module """

from pymongo import MongoClient
list_all = __import__('8-all').list_all
insert_school = __import__('9-insert_school').insert_school


def top_std(mongo_collection):
    '''
    Returns all students sorted by average score

    Args:
        mongo_collection: pymongo collection object

    Returns:
        list of students sorted by average score
    '''
    return mongo_collection.aggregate([
        {"$project":
         {"name": "$name",
          "averageScore": {"$avg": "$topics.score"}
          }},
        {"$sort": {"averageScore": -1}}

    ])


if __name__ == "__main__":
    client = MongoClient('mongodb://127.0.0.1:27017')
    std_colls = client.my_db.students

    j_stds = [
        {'name': "John", 'topics': [{'title': "Algo", 'score': 10.3}, {
            'title': "C", 'score': 6.2}, {'title': "Python", 'score': 12.1}]},
        {'name': "Bob", 'topics': [{'title': "Algo", 'score': 5.4}, {
            'title': "C", 'score': 4.9}, {'title': "Python", 'score': 7.9}]},
        {'name': "Sonia", 'topics': [{'title': "Algo", 'score': 14.8}, {
            'title': "C", 'score': 8.8}, {'title': "Python", 'score': 15.7}]},
        {'name': "Amy", 'topics': [{'title': "Algo", 'score': 9.1}, {
            'title': "C", 'score': 14.2}, {'title': "Python", 'score': 4.8}]},
        {'name': "Julia", 'topics': [{'title': "Algo", 'score': 10.5}, {
            'title': "C", 'score': 10.2}, {'title': "Python", 'score': 10.1}]}
    ]
    for j_std in j_stds:
        insert_school(std_colls, **j_std)

    stds = list_all(std_colls)
    for std in stds:
        print("[{}] {} - {}".format(std.get('_id'),
              std.get('name'), std.get('topics')))

    top_std = top_std(std_colls)
    for std in top_std:
        print("[{}] {} => {}".format(std.get('_id'),
              std.get('name'), std.get('averageScore')))
