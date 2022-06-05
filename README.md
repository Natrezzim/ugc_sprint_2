# UGC
Сервис UGC

Комманды для запуска проекта
-

**make ugc_build_up**
- Поднимает все контейнеры
 
**make ugc_destroy**
- Убивает все контейнеры
- Чистит вольюмы

**Все комманды make**
- make help

Инфрастуктура
-

Clickhouse доступен по адресу http://localhost:8123/play  
Kibana достуна по адресу http://127.0.0.1:5601/  
- Для создания доступно 3 индекса apm etl nginx   
- apm полная информация по сервису API
- etl лог сервиса etl
- nginx лог запросов

Документация достуна по адресу http://127.0.0.1/api/openapi  
API http://127.0.0.1/api/v1/view_film/  

CI/CD
-
Добавлены notifications в telegram при pull_request. 
Используется https://github.com/marketplace/actions/telegram-message-notify

Добавлена проверка линтерами wemake-python-styleguide и проверка типов mypy

При создании pull_request срабатывает CI на версиях python 3.7, 3.8 и 3.9

Репорты по codestyle и проверки типов сохраняются в artifacts в html

Для того, чтобы скачать отчет, переходим в actions, заходим в последний Linter check

Внизу страницы видим отчет.