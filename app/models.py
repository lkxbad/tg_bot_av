# app/queries.py
import  asyncpg
from config import user, password, host, database1, database2, port, database3
# порве
async def get_user_by_login(login):
    conn = await asyncpg.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database1
    )
    query = 'SELECT * FROM users_schema.app_user WHERE login = $1'
    row = await conn.fetchrow(query, login)
    await conn.close()
    return row

async def get_name(login):
    conn = await asyncpg.connect(
        user=user,
        password=password,
        host=host,
        port=5433,
        database=database1
    )
    query = 'SELECT full_name FROM users_schema.app_user WHERE login = $1'
    row = await conn.fetchrow(query, login)
    await conn.close()
    return row

async def not_end_tasks(login):
    conn = await asyncpg.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database2
    )
    query = 'SELECT COUNT(*) AS count from process_schema.act_hi_taskinst where assignee_ = $1 and end_time_ is NULL'
    rows = await conn.fetch(query, login)
    await conn.close()
    return rows

async def end_tasks(login):
    conn = await asyncpg.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database2
    )
    query = 'SELECT COUNT(*) AS count from process_schema.act_hi_taskinst where assignee_ = $1 and end_time_ is not NULL'
    rows = await conn.fetch(query, login)
    await conn.close()
    return rows


async def get_user_by_id(login):
    # Подключение к первой базе данных
    conn = await asyncpg.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database2
    )

    # Первый запрос: получаем все v.text_ для заданного логина
    query = """
    SELECT v.text_
    FROM process_schema.act_hi_taskinst t
    JOIN process_schema.act_hi_varinst v ON t.proc_inst_id_ = v.proc_inst_id_
    WHERE t.assignee_ = $1 AND t.end_time_ IS NULL AND v.name_ = 'entityGuid';
    """

    texts = await conn.fetch(query, login)  # Получаем все строки
    await conn.close()  # Закрываем соединение после первого запроса

    # Извлекаем все v.text_ в список
    text_list = [row['text_'] for row in texts]

    if not text_list:
        return None  # Если нет текстов, возвращаем None

    # Подключение ко второй базе данных
    conn2 = await asyncpg.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database3
    )

    # Второй запрос: получаем все created_by и guid для всех v.text_
    query2 = """
    SELECT *
    FROM documents_schema.document t
    WHERE t.guid = ANY($1::text[])
    """

    created_by_list = await conn2.fetch(query2, text_list)  # Получаем все значения
    await conn2.close()  # Закрываем соединение после второго запроса

    # Преобразуем результат в список словарей
    return [dict(row) for row in created_by_list]