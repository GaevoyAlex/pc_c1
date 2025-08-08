# Liberandum API


## Архитектура проекта

```
app/
├── 📁 core/                      # Ядро приложения
│   ├── 📁 database/              # Работа с базой данных
│   │   ├── base.py               # Базовый DynamoDB коннектор
│   │   ├── connector.py          # Главный коннектор
│   │   ├── table_schemas.py      # Схемы таблиц
│   │   └── 📁 repositories/      # Репозитории для работы с данными
│   │       ├── generic.py        # Универсальный репозиторий
│   │       ├── user.py          # Пользователи
│   │       └── otp.py           # OTP коды
│   ├── config.py                 # Конфигурация приложения
│   ├── security.py               # JWT, хеширование, авторизация
│   └── permissions.py            # Проверки ролей и прав доступа
├── 📁 routes/                    # API эндпоинты
│   ├── 📁 auth/                  # Аутентификация
│   │   ├── base.py               # Регистрация, логин, токены
│   │   ├── oauth.py              # Google OAuth
│   │   ├── otp.py                # Управление OTP кодами
│   │   ├── protected.py          # Защищенные эндпоинты
│   │   └── password_change.py    # Смена пароля
│   ├── 📁 admin/                 # Административные функции
│   │   └── admin.py              # CRUD для всех сущностей
│   └── 📁 data/                  # Публичные данные
│       └── markets.py            # Market data + WebSocket
├── 📁 services/                  # Бизнес-логика
│   ├── 📁 auth/                  # Сервисы аутентификации
│   │   ├── auth_service.py       # Google OAuth логика
│   │   ├── otp_service.py        # Генерация и проверка OTP
│   │   └── email_service.py      # Отправка email
│   └── 📁 market/                # Market data сервисы
│       ├── market_service.py     # Обработка рыночных данных
│       ├── coingecko_service.py  # Интеграция с CoinGecko API
│       └── websocket_manager.py  # WebSocket соединения
├── 📁 schemas/                   # Pydantic модели
│   ├── user.py                   # Схемы пользователей
│   ├── token.py                  # JWT токены
│   ├── market.py                 # Рыночные данные
│   └── chart.py                  # График данные
├── 📁 models/                    # Модели данных
│   └── market.py                 # Модели токенов и бирж
└── main.py                       # Точка входа приложения
```





### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```


- **Swagger UI**: http://localhost:8000/docs для интерактивного тестирования
- **Health check**: http://localhost:8000/health для мониторинга
- **Логи**: все операции логируются в консоль
