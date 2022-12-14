import logging
import random
from datetime import datetime
from functools import partial
from uuid import uuid4

import lorem
from pymongo import MongoClient

from config import COUNT_USERS, COUNT_MOVIES, INSERT_CHUNK, COUNT_REVIEWS, DB_NAME, MAX_BOOKMARKS, MAX_LIKES

_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logging.basicConfig(level=logging.INFO, format=_log_format)

logger = logging.getLogger(__name__)

collections_settings: dict = {
    'review': {
        'shard_key': 'movie_id'
    },
    'user_bookmarks': {
        'shard_key': 'user_id'
    },
    'movie_likes': {
        'shard_key': 'movie_id'
    }
}


def generate_bookmarks(movie_ids, user_id):
    return {
        'user_id': user_id,
        'movies': random.sample(movie_ids, k=random.randint(10, MAX_BOOKMARKS))
    }


def generate_likes(user_ids):
    return [uid for uid in random.sample(user_ids, k=random.randint(10, MAX_LIKES))]


def generate_movie_likes(user_ids, movie_id):
    like_by = generate_likes(user_ids)
    dislike_by = generate_likes(user_ids)
    rating = len(like_by) * 10 / (len(like_by) + len(dislike_by))
    return {
        'movie_id': movie_id,
        'like_by': like_by,
        'dislike_by': dislike_by,
        'rating': rating
    }


def generate_review(user_ids, movie_id):
    user_id = random.choice(user_ids)
    like_by = generate_likes(user_ids)
    dislike_by = generate_likes(user_ids)
    rating = len(like_by) * 10 / (len(like_by) + len(dislike_by))
    return {
        'movie_id': movie_id,
        'user_id': user_id,
        'created': datetime.now(),
        'text': lorem.paragraph(),
        'like_by': like_by,
        'dislike_by': dislike_by,
        'rating': rating
    }


def insert_data(collection, collection_ids, func, count_reviews):
    data = []
    insert_count = 0
    for index, ids in enumerate(random.sample(collection_ids, k=count_reviews), start=1):
        data.append(func(ids))
        if index % INSERT_CHUNK == 0:
            try:
                collection.insert_many(data, ordered=False)
            except Exception:
                continue
            insert_count += len(data)
            logger.info('insert_{}: {}/{}'.format(collection.name, insert_count, count_reviews))
            data = []
    if len(data):
        collection.insert_many(data, ordered=False)


def init_collections_data():
    user_ids = [str(uuid4()) for _ in range(COUNT_USERS)]
    movie_ids = [str(uuid4()) for _ in range(COUNT_MOVIES)]
    return {
        'review': {
            'collection_ids': movie_ids,
            'func': partial(generate_review, user_ids),
            'count_reviews': COUNT_REVIEWS,
            'indexes': ['rating', 'like_by', 'dislike_by']
        },
        'user_bookmarks': {
            'collection_ids': user_ids,
            'func': partial(generate_bookmarks, movie_ids),
            'count_reviews': len(user_ids),
            'indexes': ['bookmarks']
        },
        'movie_likes': {
            'collection_ids': movie_ids,
            'func': partial(generate_movie_likes, user_ids),
            'count_reviews': COUNT_REVIEWS,
            'indexes': ['rating', 'like_by', 'dislike_by']
        }
    }


def create_collections(client_db, settings):
    logger.info("Start setting collections")
    for collection_name, config in settings.items():
        shard_key = config.get('shard_key', None)
        if shard_key:
            client_db.admin.command('enableSharding', DB_NAME)
            client_db.admin.command('shardCollection', '{}.{}'.format(DB_NAME, collection_name),
                                    key={shard_key: "hashed"})


def generate_data(db, structure_data):
    logger.info("Started creating data")
    for collection_name, setting in structure_data.items():
        logger.info("Started insert data to collection: {}".format(collection_name))
        collection = db[collection_name]
        insert_data(
            collection,
            setting['collection_ids'],
            setting['func'],
            setting['count_reviews'],
        )
        indexes = setting.get('indexes', None)
        if indexes:
            for index in indexes:
                logger.info("Started create index '{}' to collection: {}".format(index, collection_name))
                collection.create_index(index)


if __name__ == '__main__':
    collections_data = init_collections_data()
    client = MongoClient('localhost', 27017)
    database = client[DB_NAME]
    create_collections(client, collections_settings)
    generate_data(database, collections_data)
