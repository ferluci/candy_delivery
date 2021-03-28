# Candy delivery
Реализованно на Django
Зависимости описаны в `requirements.txt`

## Запуск на сервере
1. Заполнить .env 
```bash
cp .env.example .env
cp .env-db.example .env
```
2. Запустить сервис через docker-compose
```bash
docker-compose up --build -d
```

## Запуск тестов
docker exec -it candy_delivery_web_1 python manage.py test
