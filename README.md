# Booker API Tests

[![API tests](https://github.com/A160LKN/booker-api-tests/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/A160LKN/booker-api-tests/actions/workflows/tests.yml)

Автотесты REST API учебного сервиса бронирования отелей [Restful Booker](https://restful-booker.herokuapp.com/apidoc/index.html).

**Allure-отчёт последнего прогона:** https://a160lkn.github.io/booker-api-tests/

## Стек

- Python 3.10+
- requests
- pytest
- jsonschema
- Allure Report

## Что проверяется — 18 тестов

**Доступность и авторизация**
- сервис отвечает на `/ping`;
- с верными данными выдаётся токен, с неверными — нет.

**Бронирования (CRUD)**
- создание, получение по id, поиск по имени и фамилии;
- полное обновление (`PUT`) и частичное (`PATCH`) с проверкой, что изменения сохранились;
- удаление и проверка, что бронирование больше не находится;
- `404` для несуществующего бронирования.

**Безопасность**
- без токена и с поддельным токеном нельзя изменить или удалить бронирование — и данные при этом не меняются.

**Валидация**
- создание без обязательных полей (параметризованный тест).

## Найденные особенности и баги API

| Что | Ожидалось | Фактически |
| --- | --- | --- |
| Неверный пароль в `POST /auth` | `401 Unauthorized` | `200 OK` с `{"reason": "Bad credentials"}` |
| Успешный `DELETE /booking/{id}` | `200 OK` или `204 No Content` | `201 Created` |
| `POST /booking` без обязательного поля | `400 Bad Request` | `500 Internal Server Error` |

Тесты на последний баг помечены `xfail`: прогон остаётся зелёным, а в отчёте видно, что дефект известен. Когда баг исправят, тест покажет `XPASS`.

## Особенности проекта

- **API-клиент** `BookerClient` — один метод на эндпоинт, тесты не знают об URL и заголовках;
- **проверка структуры ответов** по JSON-схемам (`jsonschema`);
- **фикстуры с уборкой**: каждое бронирование, созданное тестом, удаляется после него;
- **уникальные тестовые данные**: API общий для всех, поэтому имя в каждом бронировании уникальное;
- токен запрашивается **один раз** на весь прогон (`scope="session"`);
- каждый запрос и ответ **прикрепляется к Allure-отчёту**;
- **CI на GitHub Actions**: прогон при каждом изменении и раз в день по расписанию.

## Структура

```
├── api
│   └── client.py         — клиент API
├── data
│   ├── payloads.py       — тестовые данные
│   └── schemas.py        — JSON-схемы ответов
├── tests
│   ├── test_health_auth.py
│   └── test_booking.py
├── conftest.py           — фикстуры: клиент, токен, бронирование с уборкой
├── pytest.ini
└── requirements.txt
```

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pytest

# Allure-отчёт
allure serve allure-results
```
