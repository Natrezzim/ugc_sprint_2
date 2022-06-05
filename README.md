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
Документация    
API

CI/CD
-
Добавлены notifications в telegram при pull_request. 
Используется https://github.com/marketplace/actions/telegram-message-notify

Добавлена проверка линтерами wemake-python-styleguide и проверка типов mypy

При создании pull_request срабатывает CI на версиях python 3.7, 3.8 и 3.9

Репорты по codestyle и проверки типов сохраняются в artifacts в html

Для того, чтобы скачать отчет, переходим в actions, заходим в последний Linter check

Внизу страницы видим отчет.