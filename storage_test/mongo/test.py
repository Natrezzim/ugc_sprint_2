import datetime
import logging
import random
import time
from functools import wraps
from uuid import uuid4

import lorem
from pymongo import MongoClient

from config import DB_NAME, COUNT_ITERATION_TEST

_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logging.basicConfig(level=logging.INFO, format=_log_format)

logger = logging.getLogger(__name__)


def check_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        func(*args, **kwargs)
        return time.perf_counter() - start_time

    return wrapper


def get_like_movie_ids(count=1):
    response = db['movie_likes'].find(
        {'rating': {'$gt': random.randint(1, 8)}},
        {'_id': 0, 'movie_id': 1}
    ).limit(count)
    return [id['movie_id'] for id in response]


def get_review_ids(count=1):
    response = db['review'].find(
        {'rating': {'$gt': random.randint(1, 8)}},
        {'_id': 1}
    ).limit(count)
    return [id['_id'] for id in response]


def query_random_movie_id():
    return {'movie_id': get_like_movie_ids()[0]}


def query_random_review_id():
    return {'_id': get_review_ids()[0]}


def get_bookmarks_user_ids(count=1):
    response = db['user_bookmarks'].find(
        {'movies': {'$size': random.randint(10, 80)}},
        {'_id': 1}
    ).limit(count)
    return [id['_id'] for id in response]


def query_random_bookmarks_id():
    return {'_id': get_bookmarks_user_ids()[0]}


def average_test(func, collection_name, query, count_test):
    collection = db[collection_name]
    result = []
    for _ in range(count_test):
        result.append(func(collection, query()))
    return (
        '{:.5f}'.format(round(min(result), 5)),
        '{:.5f}'.format(round(max(result), 5)),
        '{:.5f}'.format(round(sum(result) / len(result), 5)))


def random_operators():
    return random.choice(
        ['$gt', '$lt', '$gte', '$lte', '$eq', '$ne']
    )


def stdout_test(name_test, result_test, count_test):
    print(
        ("{:<40}\t"
         "min: {:<10} \t"
         "max: {:<10} \t"
         "average: {:<10} \t"
         "test count: {}").format(name_test, *result_test, count_test))


@check_time
def select(collection, find_query):
    try:
        collection.find_one(find_query)
    except StopIteration:
        pass


@check_time
def get_count_like(collections, query):
    result = collections.aggregate(
        [
            {
                '$match': query
            },
            {
                '$project': {
                    'likes': {'$size': '$like_by'},
                }
            }
        ]
    )
    result.next()


@check_time
def add_like(collection, query):
    new_id = str(uuid4())
    resp = collection.find_one(
        query, {'_id': 0, 'like_by': 1, 'dislike_by': 1, 'rating': 1}
    )
    like = resp['like_by']
    dislike = resp['dislike_by']
    count_like = len(like) + 1
    count_dislike = len(dislike)
    count_dislike = count_dislike - 1 if new_id in dislike else count_dislike
    rating = count_like * 10 / (count_like + count_dislike)
    collection.update_one(
        query,
        {
            '$push': {'like_by': new_id},
            '$set': {'rating': rating},
            '$pull': {'dislike_by': new_id}
        }
    )
    resp = collection.find_one(query)


@check_time
def add_review(collection, movie_id):
    movie_id = str(movie_id)
    user_id = str(uuid4())
    review_data = {
        'movie_id': movie_id,
        'user_id': user_id,
        'created': datetime.datetime.now(),
        'text': lorem.paragraph(),
        'like_by': list(),
        'dislike_by': list(),
        'rating': 0
    }
    collection.insert_one(review_data)
    collection.find_one({'movie_id': movie_id})


@check_time
def add_bookmarks(collection, query):
    movie_id = str(uuid4())
    collection.update_one(
        query,
        {
            '$push': {'movies': movie_id},
        }
    )
    collection.find(query)


test_select = {
    'select_review': {
        'collection': 'review',
        'query': lambda x=None: {
            'rating': {random_operators(): random.randint(2, 10)}
        },
        'func': select
    },
    'select_user_bookmarks': {
        'collection': 'user_bookmarks',
        'query': lambda x=None: {
            'bookmarks': {random_operators(): random.randint(10, 100)}
        },
        'func': select
    },
    'select_movie_likes': {
        'collection': 'movie_likes',
        'query': lambda x=None: {
            'rating': {random_operators(): random.randint(1, 10)}
        },
        'func': select
    },
    'select_coun_movie_likes': {
        'collection': 'movie_likes',
        'query': query_random_movie_id,
        'func': select
    },
    'add_like_movie': {
        'collection': 'movie_likes',
        'query': query_random_movie_id,
        'func': add_like
    },
    'add_review': {
        'collection': 'review',
        'query': uuid4,
        'func': add_review
    },
    'add_like_review': {
        'collection': 'review',
        'query': query_random_review_id,
        'func': add_like
    },
    'add_bookmarks': {
        'collection': 'user_bookmarks',
        'query': query_random_bookmarks_id,
        'func': add_bookmarks
    },

}


def run_test():
    for test_name, data in test_select.items():
        result = average_test(data['func'], data['collection'],
                              data['query'], COUNT_ITERATION_TEST)
        stdout_test(
            'Test {} '.format(test_name),
            result,
            COUNT_ITERATION_TEST
        )


if __name__ == '__main__':
    client = MongoClient('localhost', 27017)
    db = client[DB_NAME]
    run_test()
