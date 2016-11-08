#!/usr/bin/python
# -*- coding: utf-8 -*-

from pprint import pprint
from pymongo import MongoClient


def get_db(db_name):
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db


class Pipeline(object):

    def __init__(self):
        pass

    def top_user(self):
        """ returns pipeline for user with most contributions """

        return [{'$group': {'_id': '$created.user',
                'count': {'$sum': 1}}}, {'$sort': {'count': -1}},
                {'$limit': 1}]

    def top_users(self):
        """ returns pipeline for user with most contributions """

        return [{'$group': {'_id': '$created.user',
                'count': {'$sum': 1}}}, {'$sort': {'count': -1}},
                {'$limit': 5}]

    def single_post_users(self):
        """ returns pipeline for number of users contributing only once """

        return [{'$group': {'_id': '$created.user',
                'count': {'$sum': 1}}}, {'$group': {'_id': '$count',
                'num_users': {'$sum': 1}}}, {'$sort': {'_id': 1}},
                {'$limit': 1}]

    def building_heights(self):
        """ returns pipeline for collecting heights """

        return [{'$group': {'_id': '$building',
                'minHeight': {'$min': '$height'},
                'maxHeight': {'$max': '$height'}}}]

    def all_heights(self):
        return [{'$match': {'height': {'$gt': 0}}}, {'$group': {
            '_id': None,
            'count': {'$sum': 1},
            'min': {'$min': '$height'},
            'max': {'$max': '$height'},
            'avg': {'$avg': '$height'},
            }}, {'$sort': {'height': -1}}]

    def top_cuisines(self):
        return [{'$match': {'cuisine': {'$exists': 1}}},
                {'$group': {'_id': '$cuisine', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}, {'$limit': 10}]

    def top_amenities(self):
        return [{'$match': {'amenity': {'$exists': 1}}},
                {'$group': {'_id': '$amenity', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}, {'$limit': 10}]

    def timestamps(self):
        return [{'$match': {'created.timestamp': {'$exists': 1}}},
                {'$group': {'_id': {'$substr': ['$created.timestamp',
                0, 4]}, 'count': {'$sum': 1}}},
                {'$project': {'Year': '$_id'}},
                {'$sort': {'count': -1}}, {'$limit': 10}]


if __name__ == '__main__':

    db = get_db('nanodegree')
    pipeline = Pipeline()

    print 'Overview:'
    print '---------'
    print 'Document count: ', db.manhattan.count()
    print 'Node count: ', db.manhattan.find({'type': 'node'}).count()
    print 'Ways count: ', db.manhattan.find({'type': 'way'}).count()

    # comment out error: AttributeError: 'list' object has no attribute length
    # print "Unique users: ", db.manhattan.distinct('$created.user').length

    print 'Top contributing user: ',
    [pprint(a) for a in db.manhattan.aggregate(pipeline.top_user())]
    print 'Top contributing users: ',
    [pprint(a) for a in db.manhattan.aggregate(pipeline.top_users())]
    print 'Single post users: ',
    [pprint(a) for a in
     db.manhattan.aggregate(pipeline.single_post_users())]
    print '---------'
    print 'Top cuisines: '

    # print[pprint(a) for a in db.manhattan.aggregate(pipeline.top_cuisines())]

    for a in db.manhattan.aggregate(pipeline.top_cuisines()):
        pprint(a)
    print '---------'
    print 'Top amenities: '
    for a in db.manhattan.aggregate(pipeline.top_amenities()):
        pprint(a)
    print '---------'
    print 'Timestamps: '
    for a in db.manhattan.aggregate(pipeline.timestamps()):
        pprint(a)
    print '---------'
    print 'Height stats: '
    for a in db.manhattan.aggregate(pipeline.all_heights()):
        pprint(a)

    # # tabled queries
    # print "First version count: ",
    #           db.manhattan.find( { "created.version" : "1" } ).count()
    # print "---------"
    # print "Building heights: "
    # for a in db.manhattan.aggregate(pipeline.building_heights()):
    #     pprint(a)
