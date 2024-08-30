from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
import app.keybords as kb  # Импортируем клавиатуры
import app.models as q  # Импортируем SQL-запросы
from openpyxl import Workbook
from aiogram.types import FSInputFile
router = Router()

class Reg(StatesGroup):
    login = State()

# Ввод логина
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Reg.login)
    await message.answer(f'Привет! Введите ваш логин')

# Проверка логина
@router.message(Reg.login)
async def reg_two(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    data = await state.get_data()

    try:
        row = await q.get_user_by_login(data['login'])  # Используем функцию из queries.py
        if row:
            await message.answer(f"Пользователь найден:\nИмя: {row['login']}", reply_markup=kb.main_menu)
        else:
            await message.answer(f"Пользователь не найден, проверьте корректны ли данные и попробуйте ввести логин заново!")
            await state.set_state(Reg.login)
    except Exception as error:
        print(f"Ошибка при получении данных: {error}")
        await message.answer("Не удалось получить данные из базы данных.")

@router.callback_query(F.data.startswith('pipi'))
async def docs(callback: CallbackQuery):
     await callback.message.edit_reply_markup(reply_markup=kb.status_keyboard)

# Пример использования клавиатуры для статуса документа
@router.callback_query(F.data.startswith('document'))
async def docsss(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    login = data.get('login')
    try:
        rows = await q.not_end_tasks(login)  # Используем функцию из models.py
        response = "Количество документов в работе:\n"
        for row in rows:
            response += f"{row['count']}\n"

        await callback.message.edit_text(f'{response}')
        cmd_back = kb.status_keyboard  # Используем статус клавиатуру
        await callback.message.edit_reply_markup(reply_markup=cmd_back)


    except Exception as error:
        print(f"Ошибка при получении данных: {error}")
        await callback.message.edit_text("Не удалось получить данные из базы данных.")


# Пример использования клавиатуры для статуса документа
@router.callback_query(F.data.startswith('EXECUTED'))
async def docs_not(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    login = data.get('login')

    try:

        ro = await q.end_tasks(login)  # Используем функцию из models.py

        response1 = "Количество документов не в работе:\n"
        for row in ro:
            response1 += f"{row['count']}\n"
        await callback.message.edit_text(f'{response1}')
        cmd_back = kb.status_keyboard  # Используем статус клавиатуру
        await callback.message.edit_reply_markup(reply_markup=cmd_back)


    except Exception as error:
        print(f"Ошибка при получении данных: {error}")
        await callback.message.edit_text("Не удалось получить данные из базы данных.")


async def create_excel_file(data, file_path, login, name):

    # Создаем новый рабочий файл Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Created By Data"

    # Заголовки столбцов
    ws.append(["Login", login])
    ws.append(["Login", name])
    ws.append(list(data[0].keys()))
    # Добавляем данные
    for item in data:
        ws.append(list(item.values()))

    # Сохраняем файл
    wb.save(file_path)



@router.callback_query(F.data.startswith('OTHERS'))
async def get_by(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    login = data.get('login')

    name_rec = await q.get_name(login)
    name = name_rec['full_name']
    try:
        created_by_list = await q.get_user_by_id(login)  # Используем вашу функцию

        if created_by_list:
            # Путь к файлу
            excel_file_path = 'created_by_data.xlsx'

            # Создаем Excel-файл
            await create_excel_file(created_by_list, excel_file_path, login, name)

            # Отправляем файл пользователю
            await callback.message.answer_document(FSInputFile(excel_file_path))

        else:
            await callback.message.edit_text(
                "Пользователи не найдены, проверьте корректны ли данные и попробуйте ввести логин заново!\n",
                reply_markup=kb.main_menu
            )

        cmd_back = kb.status_keyboard  # Используем статус клавиатуру
        await callback.message.answer(f"выберит кнопку",reply_markup=cmd_back)

    except Exception as error:
        print(f"Ошибка при получении данных: {error}")
        await callback.message.edit_text("Не удалось получить данные из базы данных.")


@router.callback_query(F.data == 'back')
async def go_back(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Reg.login)
    await callback.message.edit_text('Введите ваш логин')
'''
@router.callback_query(F.data.startswith('OTHERS'))
async def get_by(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    login = data.get('login')

    try:
        created_by_list = await q.get_user_by_id(login)  # Вызываем функцию

        if created_by_list:
            # Создаем DataFrame из списка
            df = pd.DataFrame(created_by_list)

            # Сохраняем DataFrame в Excel-файл
            excel_file = 'created_by_data.xlsx'
            df.to_excel(excel_file, index=False)

            # Отправляем файл пользователю
            with open(excel_file, 'rb') as file:
                await callback.message.answer_document(InputFile(file, filename='created_by_data.xlsx'))

        else:
            await callback.message.edit_text(
                "Пользователи не найдены, проверьте корректны ли данные и попробуйте ввести логин заново!\n",
                reply_markup=kb.main_menu
            )

        cmd_back = kb.status_keyboard  # Используем статус клавиатуру
        await callback.message.edit_reply_markup(reply_markup=cmd_back)

    except Exception as error:
        print(f"Ошибка при получении данных: {error}")
        await callback.message.answer("Не удалось получить данные из базы данных.")

'''
