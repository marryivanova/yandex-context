from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, status, Response
from sqlalchemy import and_, exists
from sqlalchemy.exc import SQLAlchemyError


from src.api.schema.booking import BookingListResponse, BookingResponse
from src.database.core import session_scope
from src.database.model import Booking

router = APIRouter(tags=["Bookings"])


@router.post("/book", status_code=status.HTTP_200_OK)
async def book(
    place_id: int = Query(..., gt=0),
    user_id: int = Query(..., gt=0),
    from_date: datetime = Query(..., alias="from"),
    to_date: datetime = Query(..., alias="to"),
):
    """
    Создает новое бронирование места на указанный интервал времени

    ### Параметры запроса:
    - `place_id` (int > 0): Уникальный идентификатор места для бронирования
    - `user_id` (int > 0): Уникальный идентификатор пользователя
    - `from` (datetime): Начало бронирования в формате RFC3339 (ISO 8601)
    - `to` (datetime): Окончание бронирования в формате RFC3339 (ISO 8601)

    ### Логика работы:
    1. Проверяет валидность временного интервала:
        - `from` < `to`
        - Конвертирует время в UTC при наличии временной зоны
    2. Проверяет наличие конфликтов бронирования:
        - Интервалы считаются полуоткрытыми: [`from`, `to`)
        - Пересечение существует если: `existing_from` < `to` AND `existing_to` > `from`
    3. Создает новое бронирование при отсутствии конфликтов

    ### Ответы:
    - `200 OK`: Бронирование успешно создано
    - `400 Bad Request`: Некорректный временной интервал
    - `409 Conflict`: Пересечение с существующим бронированием
    - `500 Internal Server Error`: Ошибка работы с базой данных

    ### Пример запроса:
    ```http
    POST /book?place_id=5&user_id=10&from=2024-01-01T10:00:00Z&to=2024-01-01T12:00:00Z
    ```
    """
    if from_date >= to_date:
        raise HTTPException(400, "Invalid time interval")

    if from_date.tzinfo:
        from_date = from_date.astimezone(timezone.utc).replace(tzinfo=None)
    if to_date.tzinfo:
        to_date = to_date.astimezone(timezone.utc).replace(tzinfo=None)

    try:
        with session_scope() as session:
            conflict = session.query(
                exists().where(
                    and_(
                        Booking.place_id == place_id,
                        Booking.time_from < to_date,
                        Booking.time_to > from_date,
                    )
                )
            ).scalar()

            if conflict:
                raise HTTPException(409, "Booking conflict")

            new_booking = Booking(
                user_id=user_id, place_id=place_id, time_from=from_date, time_to=to_date
            )
            session.add(new_booking)

        return Response(status_code=200)

    except SQLAlchemyError:
        raise HTTPException(500, "Database error")


@router.get("/booklist", response_model=BookingListResponse)
async def booklist(
    user_id: int = Query(None, gt=0),
    place_id: int = Query(None, gt=0),
):
    """
    Возвращает список бронирований по указанному пользователю или месту

    ### Параметры запроса:
    - `user_id` (int > 0): Фильтр по идентификатору пользователя
    - `place_id` (int > 0): Фильтр по идентификатору места

    ### Правила использования:
    1. Должен быть указан **ровно один** параметр:
       - Либо `user_id` для получения всех бронирований пользователя
       - Либо `place_id` для получения всех бронирований места
    2. Указание обоих параметров или отсутствие параметров вызовет ошибку

    ### Ответ:
    - HTTP 200: Успешный запрос с телом:
      ```json
      {
        "bookings": [
          {
            "id": 1,
            "user_id": 10,
            "place_id": 5,
            "from": "2024-01-01T10:00:00Z",
            "to": "2024-01-01T12:00:00Z"
          }
        ]
      }
      ```
    - Бронирования сортируются по возрастанию:
      $$(\text{time\_from}, \text{id})$$

    ### Ошибки:
    - `400 Bad Request`: Не указан ни один параметр или указаны оба
    - `500 Internal Server Error`: Ошибка работы с базой данных

    ### Примеры запросов:
    ```http
    GET /booklist?user_id=10
    GET /booklist?place_id=5
    ```

    ### Логика работы:
    1. Проверка условия $(\text{user\_id} \oplus \text{place\_id}) = 1$
    2. Формирование SQL-запроса с фильтрацией по выбранному параметру
    3. Сортировка результатов:
        - Первичный ключ: `time_from` (по возрастанию)
        - Вторичный ключ: `id` (по возрастанию)
    4. Преобразование результатов в Pydantic-модель `BookingListResponse`
    """
    if not (bool(user_id) ^ bool(place_id)):
        raise HTTPException(400, "Exactly one parameter required")

    try:
        with session_scope() as session:
            query = session.query(Booking)

            if user_id:
                query = query.filter(Booking.user_id == user_id)
            else:
                query = query.filter(Booking.place_id == place_id)

            bookings = query.order_by(Booking.time_from, Booking.id).all()

            return BookingListResponse(
                bookings=[
                    BookingResponse(
                        id=b.id,
                        user_id=b.user_id,
                        place_id=b.place_id,
                        from_=b.time_from,
                        to_=b.time_to,
                    )
                    for b in bookings
                ]
            )

    except SQLAlchemyError:
        raise HTTPException(500, "Database error")
