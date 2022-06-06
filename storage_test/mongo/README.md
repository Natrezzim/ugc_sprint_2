# Исследование MongoDb

### Требования

- Требования к скорости обработки данных = 200 мс.

### Как запустить исследование:

```docker-compose up -d``` - запускаем окружение

```create_claster.sh``` - создаёт кластер из запустившихся контейнеров

```config.py``` - поправить параметры для генерации данных

``` python -m venv venv``` - создаём локальное окружение

```pip install -r requirements.txt``` - устанавливаем нужные пакеты

```python generate_data.py``` - запускаем генерацию данных для тестов

```python test.py``` - запускаем тесты



### Результат исследования

| Название теста                   | Минимальное значение | Максимальное значение | Среднее значение | Количество повторений | 
|----------------------------------|----------------------|-----------------------|------------------|-----------------------| 
| Test select_review               | 0.00099         | 0.00415          | 0.00197 | 10                    |
| Test select_user_bookmarks       | 0.00116         | 0.00162          | 0.00134 | 10                    |
| Test select_movie_likes          | 0.00103         | 0.00181          | 0.00155 | 10                    |
| Test select_coun_movie_likes     | 0.00128         | 0.00218          | 0.00168 | 10                    |
| Test add_like_movie              | 0.00724         | 0.01460          | 0.01039 | 10                    |
| Test add_review                  | 0.00442         | 0.00849          | 0.00541 | 10                    |
| Test add_like_review             | 0.00724         | 0.02194          | 0.01135 | 10                    |
| Test add_bookmarks               | 0.00338         | 0.00748          | 0.00441 | 10                    |


### Выводы:

    Система удовлетворяет требованиям

### Структура документов

*movie_likes:*

    {
        'movie_id': uuid4,
        'like_by': list,
        'dislike_by': list,
        'rating': float
    }

*review:*

    {
        'movie_id': uuid4,
        'user_id': uuid4,
        'created': datetime,
        'text': str,
        'like_by': list,
        'dislike_by': list,
        'rating': float
    }

*user_bookmarks:*

    {
        'user_id': uuid4,
        'movies': list
    }