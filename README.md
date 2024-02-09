### Разворачивание проекта:

Выполните команду
`docker-compose up --build`

Теперь можете тестировать сервис, отправляя запросы на указанные эндпоинты

GET http://localhost/check_data?phone=89090000000

POST http://localhost/write_data

PUT http://localhost/write_data

Для указание своего адреса сервера добавьте в файл docker-compose:

    environment:
      - HTTPS_URL=https://your-server-ip-or-domain/


Документацию API можете посмотреть по адресу http://localhost/docs#/
      
      
Задание 2

-- Создаем индексы на столбцы name в таблицах full_names и short_names

`CREATE INDEX idx_full_names_name ON full_names (name);`

`CREATE INDEX idx_short_names_name ON short_names (name);`

-- Обновление данных столбца "status" в таблице "full_names" есть два варианта:

1 -`UPDATE full_names
SET status = short_names.status
FROM short_names
WHERE split_part(full_names.name, '.', 1) = short_names.name;`


2-`UPDATE full_names fn
SET status = sn.status
FROM short_names sn
JOIN (SELECT name, POSITION('.' IN name) - 1 as idx FROM full_names) fn_idx
ON sn.name = SUBSTRING(fn.name FROM 1 FOR fn_idx.idx)
WHERE fn.name = fn_idx.name;`