import random
import time
import vertica_python

from locust import TaskSet, task, User, between, events
from itertools import islice

CONNECTION = {
    'host': 'vertica_db',
    'port': 5433,
    'user': 'dbadmin',
    'password': '',
    'database': 'docker',
    'autocommit': True,
    'read_timeout': 600,
    'unicode_error': 'strict',
    'ssl': False
}
ROWS_NUMS = 1000000
CHUNK_SIZE = 5000
SELECT_NUMS = 10000


def group_elements(elements, chunk_size):
    """Group elements by chunk"""
    elements_to_group = iter(elements)
    return iter(lambda: tuple(islice(elements_to_group, chunk_size)), ())


def create_test_table(connection_info: dict):
    with vertica_python.connect(**connection_info) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS views (
                id IDENTITY,
                user_id INTEGER NOT NULL,
                movie_id VARCHAR(256) NOT NULL,
                viewed_frame INTEGER NOT NULL
            );
        """)


def generate_data_to_table(rows: int):
    return [(i, 'tt012033', i + 1) for i in range(rows)]


def delete_test_table(connection_info: dict):
    with vertica_python.connect(**connection_info) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            DROP TABLE views;
        """)


def get_sample_query():
    random_id = random.randint(1, ROWS_NUMS)
    query = f"""
        SELECT * FROM views WHERE user_id = {random_id}
    """

    return query


def get_insert_query():

    query = f"""
        INSERT INTO views(user_id, movie_id, viewed_frame) VALUES(%s, %s, %s)
    """

    return query


def execute_query(conn_info, query, data, select=False):
    with vertica_python.connect(**conn_info) as conn:
        cur = conn.cursor()
        if select:
            cur.execute(query)
        else:
            cur.executemany(query, data, use_prepared_statements=False)


class VerticaClient:

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                execute_query(*args, **kwargs)
                events.request_success.fire(
                    request_type="vertica",
                    name=name,
                    response_time=int((time.time() - start_time) * 1000),
                    response_length=0,
                )
            except Exception as e:
                events.request_failure.fire(
                    request_type="vertica",
                    name=name,
                    response_time=int((time.time() - start_time) * 1000),
                    exception=e,
                )
        return wrapper


class VerticaTaskSet(TaskSet):

    @task(3)
    def execute_insert_query(self):
        for chunk_data in group_elements(generate_data_to_table(ROWS_NUMS), CHUNK_SIZE):
            self.client.execute_query(CONNECTION, get_insert_query(), chunk_data)

    @task
    def execute_select_query(self):
        self.client.execute_query(CONNECTION, get_sample_query(), [], select=True)


class VerticaLocust(User):
    tasks = [VerticaTaskSet]
    wait_time = between(0.1, 1)

    def __init__(self, environment):
        super().__init__(environment)
        self.client = VerticaClient()

    def on_start(self):
        create_test_table(CONNECTION)
