import random
import time

from clickhouse_driver import Client

from test_clickhouse import (
    get_insert_query,
    group_elements,
    generate_data_to_table,
)

ROWS_NUMS = 10000000
CHUNK_SIZE = 5000


def average(lst: list):
    return sum(lst) / len(lst)


def query_time(query_type: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.monotonic()

            res = func(*args, **kwargs)

            query_time_result = time.monotonic() - start_time
            if query_type == 'SELECT':
                return query_time_result

            print(f"Query type {query_type}, query_time {query_time_result}")

            return res

        return wrapper

    return decorator


def clickhouse_test():

    @query_time("INSERT")
    def insert_to_clickhouse(client: Client):
        for chunk in group_elements(generate_data_to_table(ROWS_NUMS), CHUNK_SIZE):
            client.execute(
                get_insert_query(),
                chunk,
            )

    @query_time("SELECT")
    def select_from_clickhouse(client: Client):
        random_id = random.randint(1, ROWS_NUMS)
        client.execute(
            f"SELECT * FROM example.views WHERE (user_id == {random_id})"
        )

    client = Client(host='localhost')
    client.execute(
        f"CREATE DATABASE IF NOT EXISTS example ON CLUSTER company_cluster"
    )
    client.execute("""
        CREATE TABLE IF NOT EXISTS example.views ON CLUSTER company_cluster 
        (id Int64, user_id Int32, movie_id Int64, viewed_frame Int64)
        Engine=MergeTree() ORDER BY id
    """)

    insert_to_clickhouse(client=client)

    # select данных из clickhouse
    # результатом исследования является среднее время получения рандомного значения при 5К запросах
    # из таблицы в 10M записей
    time_for_each_query = []
    for i in range(CHUNK_SIZE):
        time_for_each_query.append(select_from_clickhouse(client=client))

    print(f"Query type SELECT, avg query_time {average(time_for_each_query)}")


if __name__ == "__main__":
    clickhouse_test()
