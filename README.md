# praktikum_new_diplom
# «Продуктовый помощник».

### Технологии
- Python 
- Django 
- DRF
- PEP8
- PostgreSQL
- Docker
- Docker-compose
- Gunicorn
- Nginx
- React



## Описание
- Проект работает с СУБД PostgreSQL.
- В nginx настроена раздача статики, запросы с фронтенда переадресуются в контейнер с Gunicorn. 
Джанго-админка работает напрямую через Gunicorn.

## Как запустить
### Запуск через docker-compose:  
```
docker-compose up -d --build
```
##### Выполнить миграции:
```  
docker-compose exec web python manage.py migrate  
```  
##### Cоздать суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```
##### Собрать статику:
```
docker-compose exec web python manage.py collectstatic --no-input
```

