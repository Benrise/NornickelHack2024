### Локальное развертывание проекта

```
docker-compose up --build -d
```

### Интерфейс
http://localhost/search/api/v1/docs - интерфейс работы с API

- documents/process - обработка документа и его последующая загрузка в хранилище

- documents/multimodal_search - мультимодальный поиск

- documents/- классический полнотекстовый поиск

### Переменные окружения
Скопировать `.env.examlpe` и переименовать в `.env`