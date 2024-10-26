# Проект RecipeService

![Workflow](https://github.com/V1sl3t/foodgram/actions/workflows/main.yml/badge.svg)


## Описание
Проект "RecipeService" – это сервис, который даёт возможность людям делиться рецептами, и создавать свои списки покупок, для упрощения похода в магазин.


## Стек проекта
- Python 
- Docker 
- Django 
- Nginx 
- Gunicorn
- REST framework
- Djoser

## Ссылка на развернутый проект
(https://foodgram.publicvm.com)

## Процесс запуска проекта 

```sh
sudo docker compose -f docker-compose.yml up
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

## Автор проекта 
 
V1sl3t
