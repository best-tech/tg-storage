# Файловое хранилище Telegram по HTTP

### Отправка нового файла

`POST` `http://127.0.0.1:8083/<chat_id>` 

Параметры формы:

    - `file` - файл для отправки
    - `caption` - Текст сообщения

Ответ:
```json
{
  "chat_id": -100234234,
  "id": 344
}
```

### Удаление файла по идентификатору
`DELETE` `http://127.0.0.1:8083/<chat_id>/<id>`

### Получение файла по идентификатору
`GET` `http://127.0.0.1:8083/<chat_id>/<id>`

# Запуск:

Размещаем текущий проект по пути: `/etc/tg-storage`

- Зависимости `pip3 install -r requirements.txt`
- Настроить сессию `python3 deploy.py`
- Тест `export API_ID=1 && export API_HASH=2b && export API_KEY=kef && python3 app.py`

Как сервис:

- Переменные окружения `./tg-storage.config`
    - `API_ID` - Идентификатор
    - `API_HASH` - и хэш [my.telegram.org](https://my.telegram.org/)
    - `API_KEY` - Произвольный ключ доступа для заголовка авторизации `Bearer jfnlekjwrfebgt....`. Если не заполнено - доступ не ограничивается
     
- Установка сервиса 

```
sudo cp tg-storage.service /etc/systemd/system/
sudo systemctl enable tg-storage.service
sudo systemctl daemon-reload
sudo systemctl start tg-storage.service
sudo systemctl status tg-storage.service -l
```