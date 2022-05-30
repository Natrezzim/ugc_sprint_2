Performance test Vertica and Clickhouse

Для каждого хранилища поднимаются свои контейнеры
     docker-compose up --scale worker=4

Тесты которые были проведены:
1) Локальный тест на запись 10M строк чанками по 5К.
2) Локальный тест на получение рандомных данных в цикле 5К.
        Для запуска локального теста запускаем скрипт local_test_clickhouse.py и local_test_vertica.py.
        Результатом будет время выполнения 10М записей + среднее время чтения при 5К запросах.
4) Для тестирования нагрузки при записи/чтении данных в реальном времени использовалась либа Locust.
    После поднятия контейнеров заходим в http://localhost:8089/


VERTICA:

        Вставка батчами по 5К
        Query type INSERT, query_time 224.51499999999942 sec

        Получение данных
        результатом исследования является среднее время получения рандомного значения при 5К запросах
        в таблице с 10M записей
        Query type SELECT, avg query_time 0.025868799999999463 sec
        
   Запись чтение в реальном времени:
            
![total_requests_per_second_1653337493](https://user-images.githubusercontent.com/62523428/169901046-9cef31c9-0b14-4f39-a499-c4e140492351.png)
![response_times_(ms)_1653337493](https://user-images.githubusercontent.com/62523428/169901062-b156c9a4-e987-4617-8adf-6706b1a941ad.png)
![Screenshot 2022-05-23 222503](https://user-images.githubusercontent.com/62523428/169901084-836de461-d622-43cd-891e-c7094ca3c968.png)
![Screenshot 2022-05-23 222413](https://user-images.githubusercontent.com/62523428/169901101-f2838201-57be-4c85-9b36-2f03d0bd79e9.png)

![number_of_users_1653221606](https://user-images.githubusercontent.com/62523428/169695821-010a8e55-d706-4c61-9e57-f12b646ea7f6.png)



CLICKHOUSE:

        Вставка батчами по 5К
        Query type INSERT, query_time 209.65599999999995 sec

        Получение данных
        результатом исследования является среднее время получения рандомного значения при 5К запросах
        в таблице с 10M записей
        Query type SELECT, avg query_time 0.08222179999999935 sec
 
  Запись чтение в реальном времени:
![total_requests_per_second_1653334141](https://user-images.githubusercontent.com/62523428/169901279-ff801ac3-650b-4e6b-9e81-1a02f9da5c4d.png)
![response_times_(ms)_1653334141](https://user-images.githubusercontent.com/62523428/169901292-33802e6e-b1c7-49b8-9d63-ca0842c069e4.png)
![Screenshot 2022-05-23 213044](https://user-images.githubusercontent.com/62523428/169901320-b6a9413d-11c1-49c4-af59-5cfcab2f1b5d.png)
![Screenshot 2022-05-23 212844](https://user-images.githubusercontent.com/62523428/169901347-0c5e835d-43aa-408f-9776-fb0dbc2fe0fc.png)
![number_of_users_1653222231](https://user-images.githubusercontent.com/62523428/169696195-42ec1c9c-24b1-4b14-96bd-04cf752ad232.png)

