Deployed: https://lab2-backend-l2tv.onrender.com
Repository: https://github.com/AndriiBurlii/lab2-backend

# Lab 2 — Expenses REST API (Flask)

Базове REST API для обліку витрат **без бази даних** (зберігання в пам’яті).

## Швидкий старт (локально)

```bash
python -m venv .venv && . .venv/Scripts/activate  # Windows PowerShell
pip install -r requirements.txt
python app.py
# Сервіс на http://127.0.0.1:5000
```

Або через Docker:

```bash
docker build -t lab2-expenses-api .
docker run -p 5000:5000 lab2-expenses-api
```

> За замовчуванням Flask слухає порт `5000` (див. `app.py`).

## Ендпоінти (згідно методички)

### Users
- `POST /user` — створити користувача `{ "name": "Max" }`
- `GET /user/<user_id>` — отримати користувача
- `DELETE /user/<user_id>` — видалити користувача (+каскад видалить його записи)
- `GET /users` — список користувачів

### Categories
- `GET /category` — список категорій
- `POST /category` — створити `{ "name": "Food" }`
- `DELETE /category?id=1` — видалити категорію за `id` (можна також надіслати `{"id":1}` у body). Каскадно видалить записи категорії.

### Records
- `POST /record` — створити запис `{ "user_id": 1, "category_id": 1, "amount": 99.9 }`
- `GET /record/<record_id>` — отримати запис
- `DELETE /record/<record_id>` — видалити запис
- `GET /record?user_id=1&category_id=1` — фільтрація за `user_id` **та/або** `category_id`. **Без параметрів → 400**.

## Приклади cURL

```bash
# створення користувача
curl -s -X POST http://localhost:5000/user -H "Content-Type: application/json" -d "{\"name\":\"Max\"}"

# створення категорії
curl -s -X POST http://localhost:5000/category -H "Content-Type: application/json" -d "{\"name\":\"Food\"}"

# створення запису
curl -s -X POST http://localhost:5000/record -H "Content-Type: application/json" -d "{\"user_id\":1,\"category_id\":1,\"amount\":99.9}"

# фільтрація записів
curl -s "http://localhost:5000/record?user_id=1"
```

## Деплой на Render.com

1. Створіть **новий публічний репозиторій** і залийте файли з цієї папки.
2. На [Render](https://render.com) → *New* → *Web Service* → підключіть репозиторій.
3. Runtime: **Python**. Build: `pip install -r requirements.txt`. Start: `gunicorn app:app`.
4. Дочекайтесь `Your service is live` — отримаєте URL виду `https://...onrender.com`.
5. Додайте цей домен в Postman environment `production`.

## Postman

У теці `postman/` знаходяться:
- `Expenses API.postman_collection.json`
- `env.local.postman_environment.json` ({{baseUrl}} = `http://127.0.0.1:5000`)
- `env.prod.postman_environment.json` (порожнє поле `{{baseUrl}}`, заповніть вашим Render URL)
- `flows/Expenses.postman_flow.json` — приклад Flow: створити користувача → категорію → запис → отримати запис/список.

Імпортуйте колекцію та обидва середовища у Postman (**Import → Files**).
## 🔄 Postman Flow 

![Flow](./Знімок%20екрана%202025-10-30%20125451.png)
![Flow](./Знімок%20екрана%202025-10-30%20125456.png)

## Примітки

- Дані зберігаються у пам'яті процесу; після рестарту — очищуються.
- Мінімальна валідація: `POST /record` перевіряє існування `user_id` та `category_id`.
- Код стилізовано під вимоги лабораторної та покриває всі ендпоінти.
