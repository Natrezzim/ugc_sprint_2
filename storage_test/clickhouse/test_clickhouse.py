import random
import time
from itertools import islice

from clickhouse_driver import Client
from locust import TaskSet, task, User, between, events


click_client = Client(host='clickhouse-node1')
ROWS_NUMS = 1000000
CHUNK_SIZE = 5000
SELECT_NUMS = 10000


def group_elements(elements, chunk_size):
    """Group elements by chunk"""
    elements_to_group = iter(elements)
    return iter(lambda: tuple(islice(elements_to_group, chunk_size)), ())


def generate_data_to_table(rows: int):
    return [(i, i, i + 1) for i in range(rows)]


def create_test_table():
    click_client.execute("""
    CREATE DATABASE IF NOT EXISTS example ON CLUSTER company_cluster
    """)
    click_client.execute("""
        CREATE TABLE IF NOT EXISTS example.views ON CLUSTER company_cluster 
        (id Int64, user_id Int32, movie_id Int64, viewed_frame Int64)
        Engine=MergeTree() ORDER BY id
    """)


def get_insert_query():

    query = "INSERT INTO example.views (user_id, movie_id, viewed_frame) VALUES"

    return query


def get_sample_query():
    random_id = random.randint(1, ROWS_NUMS)
    query = f"SELECT * FROM example.views WHERE (user_id == {random_id})"
    return query


def execute_query(query, data=None, select=False):
    if select:
        click_client.execute(query)
    else:
        click_client.execute(query, data)


class ClickhouseClient:
    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                execute_query(*args, **kwargs)
                events.request_success.fire(
                    request_type="clickhouse",
                    name=name,
                    response_time=int((time.time() - start_time) * 1000),
                    response_length=0,
                )
            except Exception as e:
                events.request_failure.fire(
                    request_type="clickhouse",
                    name=name,
                    response_time=int((time.time() - start_time) * 1000),
                    exception=e
                )
        return wrapper


class ClickhouseTaskSet(TaskSet):

    @task(3)
    def execute_insert_query(self):
        for chunk_data in group_elements(generate_data_to_table(ROWS_NUMS), CHUNK_SIZE):
            self.client.execute_query(get_insert_query(), chunk_data)

    @task
    def execute_select_query(self):
        self.client.execute_query(get_sample_query())


class ClickhouseLocust(User):
    tasks = [ClickhouseTaskSet]
    wait_time = between(0.1, 1)

    def __init__(self, environment):
        super().__init__(environment)
        self.client = ClickhouseClient()

    def on_start(self):
        create_test_table()
