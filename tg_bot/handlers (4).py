from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from math import ceil
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
from aiogram.types import BufferedInputFile
from aiogram import Bot
from aiogram.fsm.storage.base import StorageKey
from aiogram.filters import StateFilter
from sqlalchemy.orm import aliased  # Добавлен импорт aliased


import app.keyboards as kb
import app.database.requests as rq

from app.keyboards import (
    get_skills_keyboard,
    get_search_actions_keyboard,
    get_vip_main_keyboard
)

from app.database.requests import find_users_by_skills


router = Router()

class Reg(StatesGroup):
    name = State()
    surname = State()
    group = State()
    user_id = State()
    text = State()
    current_page = State()
    count_pages = State()
    half_groups = State()

class Aut(StatesGroup):
    user_id = State()
    role = State()
    vip_password = State()
    admin_password = State()

class Role(StatesGroup):
    user = State()
    vip = State()
    admin = State()

class User(StatesGroup):
    user_id = State()
    set_skills = State()
    check_skills = State()
    set_more_skills = State()
    delete_skill = State()

class User_delete_skill(StatesGroup):
    user_id = State()
    current_page = State()
    count_pages = State()
    user_sender_id = State()
    skill_name = State()
    skill_id = State()

class Admin_delete_skill(StatesGroup):
    user_id = State()
    current_page = State()
    count_pages = State()
    user_sender_id = State()
    skill_name = State()
    skill_id = State()

class User_skills(StatesGroup):
    user_id = State()
    text = State()
    skill_name = State()
    current_page = State()
    count_pages = State()
    mark = State()

class Admin(StatesGroup):
    set_skills = State()
    set_more_skills = State()
    check_skills = State()
    set_more_skills_for_user = State()
    set_mark_to_user = State()

class Admin_skills(StatesGroup):
    user_id = State()
    text = State()
    skill_name = State()
    current_page = State()
    count_pages = State()
    mark = State()

class Admin_set_skill_for_user(StatesGroup):
    sender_id = State()
    user_name = State()
    text = State()
    delete_user_skill = State()
    user_sender_id = State()
    user_user_id = State()
    skill_page = State()
    skill_count = State()
    skill_delete_name = State()
    user_surname = State()
    user_wait_id = State()
    user_id = State()
    skill_name = State()
    mark = State()
    current_page = State()
    count_pages = State()

class Vip(StatesGroup):
    set_admin_password = State()
    set_vip_password = State()

class Vip_show_users(StatesGroup):
    view_users = State()
    current_page = State()
    count_pages = State()

class Vip_show_current_user(StatesGroup):
    user_id = State()
    user_sender_id = State()
    current_page = State()
    text = State()
    count_pages = State()
    skill_add_wait = State()
    skill_add_name = State()
    skill_delete_wait = State()
    skill_delete_name = State()
    current_add_page = State()
    current_delete_page = State()
    count_add_pages = State()
    count_delete_pages = State()
    add_mark = State()
    delete_mark = State()
    set_more_skills_for_user = State()


class VipFindUserStates(StatesGroup):
    current_page = State()
    current_found_page = State()
    count_found_pages = State()
    count_pages = State()
    input_skill = State()
    select_skill = State()
    select_rating = State()
    waiting_user = State()
    ready_to_search = State()
    text = State()


async def plot_skill_levels_grouped(data, user_data, chat_id: int, bot: Bot):
    if data:
        fig, ax = plt.subplots(figsize=(16, 8))

        grouped_data = {}
        user_names = {}
        for user_id, user_name, level, skill in data:
            grouped_data.setdefault(user_id, {})[skill] = level
            user_names[user_id] = user_name

        skills = sorted({row[3] for row in data})
        users = list(grouped_data.keys())

        x = np.arange(len(skills))
        bar_width = 0.8 / len(users)

        colors = plt.cm.get_cmap('tab10', len(users))

        for i, user_id in enumerate(users):
            y = [grouped_data[user_id].get(skill, 0) for skill in skills]
            ax.bar(x + i * bar_width, y, width=bar_width, alpha=0.8, label=user_names[user_id], color=colors(i))

        # Средние значения по навыкам (учитываем только оценки > 0)
        skill_averages = []
        for skill in skills:
            levels = [grouped_data[user_id].get(skill, 0) for user_id in users]
            # Фильтруем нули, чтобы среднее не было занижено
            filtered_levels = [lvl for lvl in levels if lvl > 0]
            avg = np.mean(filtered_levels) if filtered_levels else 0
            skill_averages.append(avg)

        # Жёсткая красная линия без интерполяции
        ax.plot(x + bar_width * (len(users) - 1) / 2, skill_averages, color='red', marker='o', linewidth=2, label='Средняя оценка')

        ax.set_xticks(x + bar_width * (len(users) - 1) / 2)
        ax.set_xticklabels(skills, rotation=45, ha='right')
        ax.set_ylabel("Уровень владения")
        ax.set_xlabel("Навык")
        ax.set_title("Уровень владения навыками по пользователям")
        ax.legend(title="Пользователи / Среднее значение")
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.set_ylim(0, 10)
        fig.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)

        image = BufferedInputFile(buf.getvalue(), filename="skills_chart.png")

        text_info = (
            f"👤 Профиль пользователя:\n"
            f"Имя: {user_data[0]}\n"
            f"Фамилия: {user_data[1]}\n"
            f"Группа: {user_data[2]}"
        )

        keyboard = await kb.edit_profile_user()

        await bot.send_photo(
            chat_id=chat_id,
            photo=image,
            caption=text_info
        )

        buf.close()
    else:
        text_info = (
            f"👤 Профиль пользователя:\n"
            f"Имя: {user_data[0]}\n"
            f"Фамилия: {user_data[1]}\n"
            f"Группа: {user_data[2]}"
        )
        keyboard = await kb.edit_profile_user()
        await bot.send_message(chat_id=chat_id, text=text_info)


async def plot_skill_levels_grouped_admin(data, user_data, chat_id: int, bot: Bot):
    if data:
        fig, ax = plt.subplots(figsize=(16, 8))

        grouped_data = {}
        user_names = {}
        for user_id, user_name, level, skill in data:
            grouped_data.setdefault(user_id, {})[skill] = level
            user_names[user_id] = user_name

        skills = sorted({row[3] for row in data})
        users = list(grouped_data.keys())

        x = np.arange(len(skills))
        bar_width = 0.8 / len(users)

        colors = plt.cm.get_cmap('tab10', len(users))

        for i, user_id in enumerate(users):
            y = [grouped_data[user_id].get(skill, 0) for skill in skills]
            ax.bar(x + i * bar_width, y, width=bar_width, alpha=0.8, label=user_names[user_id], color=colors(i))

        # Средние значения по навыкам (учитываем только оценки > 0)
        skill_averages = []
        for skill in skills:
            levels = [grouped_data[user_id].get(skill, 0) for user_id in users]
            # Фильтруем нули, чтобы среднее не было занижено
            filtered_levels = [lvl for lvl in levels if lvl > 0]
            avg = np.mean(filtered_levels) if filtered_levels else 0
            skill_averages.append(avg)

        # Жёсткая красная линия без интерполяции
        ax.plot(x + bar_width * (len(users) - 1) / 2, skill_averages, color='red', marker='o', linewidth=2, label='Средняя оценка')

        ax.set_xticks(x + bar_width * (len(users) - 1) / 2)
        ax.set_xticklabels(skills, rotation=45, ha='right')
        ax.set_ylabel("Уровень владения")
        ax.set_xlabel("Навык")
        ax.set_title("Уровень владения навыками по пользователям")
        ax.legend(title="Пользователи / Среднее значение")
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.set_ylim(0, 10)
        fig.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)

        image = BufferedInputFile(buf.getvalue(), filename="skills_chart.png")

        text_info = (
            f"👤 Профиль пользователя:\n"
            f"Имя: {user_data[0]}\n"
            f"Фамилия: {user_data[1]}\n"
            f"Группа: {user_data[2]}"
        )

        keyboard = await kb.edit_profile_user()

        await bot.send_photo(
            chat_id=chat_id,
            photo=image,
            caption=text_info,
            reply_markup=keyboard
        )

        buf.close()
    else:
        text_info = (
            f"👤 Профиль пользователя:\n"
            f"Имя: {user_data[0]}\n"
            f"Фамилия: {user_data[1]}\n"
            f"Группа: {user_data[2]}"
        )
        keyboard = await kb.edit_profile_user()
        await bot.send_message(chat_id=chat_id, text=text_info, reply_markup=keyboard)


async def plot_skill_levels_grouped_vip(data, user_data, chat_id: int, bot: Bot):
    if data:
        fig, ax = plt.subplots(figsize=(16, 8))

        grouped_data = {}
        user_names = {}
        for user_id, user_name, level, skill in data:
            grouped_data.setdefault(user_id, {})[skill] = level
            user_names[user_id] = user_name

        skills = sorted({row[3] for row in data})
        users = list(grouped_data.keys())

        x = np.arange(len(skills))
        bar_width = 0.8 / len(users)

        colors = plt.cm.get_cmap('tab10', len(users))

        for i, user_id in enumerate(users):
            y = [grouped_data[user_id].get(skill, 0) for skill in skills]
            ax.bar(x + i * bar_width, y, width=bar_width, alpha=0.8, label=user_names[user_id], color=colors(i))

        # Средние значения по навыкам (учитываем только оценки > 0)
        skill_averages = []
        for skill in skills:
            levels = [grouped_data[user_id].get(skill, 0) for user_id in users]
            # Фильтруем нули, чтобы среднее не было занижено
            filtered_levels = [lvl for lvl in levels if lvl > 0]
            avg = np.mean(filtered_levels) if filtered_levels else 0
            skill_averages.append(avg)

        # Жёсткая красная линия без интерполяции
        ax.plot(x + bar_width * (len(users) - 1) / 2, skill_averages, color='red', marker='o', linewidth=2, label='Средняя оценка')

        ax.set_xticks(x + bar_width * (len(users) - 1) / 2)
        ax.set_xticklabels(skills, rotation=45, ha='right')
        ax.set_ylabel("Уровень владения")
        ax.set_xlabel("Навык")
        ax.set_title("Уровень владения навыками по пользователям")
        ax.legend(title="Пользователи / Среднее значение")
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.set_ylim(0, 10)
        fig.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)

        image = BufferedInputFile(buf.getvalue(), filename="skills_chart.png")

        text_info = (
            f"👤 Профиль пользователя:\n"
            f"Имя: {user_data[0]}\n"
            f"Фамилия: {user_data[1]}\n"
            f"Группа: {user_data[2]}"
        )

        keyboard = await kb.edit_profile_user_vip()

        await bot.send_photo(
            chat_id=chat_id,
            photo=image,
            caption=text_info,
            reply_markup=keyboard
        )

        buf.close()
    else:
        text_info = (
            f"👤 Профиль пользователя:\n"
            f"Имя: {user_data[0]}\n"
            f"Фамилия: {user_data[1]}\n"
            f"Группа: {user_data[2]}"
        )
        keyboard = await kb.edit_profile_user_vip()
        await bot.send_message(chat_id=chat_id, text=text_info, reply_markup=keyboard)


async def plot_skill_levels_grouped_vip_search(data, user_data, chat_id: int, bot: Bot):
    if data:
        fig, ax = plt.subplots(figsize=(16, 8))

        grouped_data = {}
        user_names = {}
        for user_id, user_name, level, skill in data:
            grouped_data.setdefault(user_id, {})[skill] = level
            user_names[user_id] = user_name

        skills = sorted({row[3] for row in data})
        users = list(grouped_data.keys())

        x = np.arange(len(skills))
        bar_width = 0.8 / len(users)

        colors = plt.cm.get_cmap('tab10', len(users))

        for i, user_id in enumerate(users):
            y = [grouped_data[user_id].get(skill, 0) for skill in skills]
            ax.bar(x + i * bar_width, y, width=bar_width, alpha=0.8, label=user_names[user_id], color=colors(i))

        # Средние значения по навыкам (учитываем только оценки > 0)
        skill_averages = []
        for skill in skills:
            levels = [grouped_data[user_id].get(skill, 0) for user_id in users]
            # Фильтруем нули, чтобы среднее не было занижено
            filtered_levels = [lvl for lvl in levels if lvl > 0]
            avg = np.mean(filtered_levels) if filtered_levels else 0
            skill_averages.append(avg)

        # Жёсткая красная линия без интерполяции
        ax.plot(x + bar_width * (len(users) - 1) / 2, skill_averages, color='red', marker='o', linewidth=2, label='Средняя оценка')

        ax.set_xticks(x + bar_width * (len(users) - 1) / 2)
        ax.set_xticklabels(skills, rotation=45, ha='right')
        ax.set_ylabel("Уровень владения")
        ax.set_xlabel("Навык")
        ax.set_title("Уровень владения навыками по пользователям")
        ax.legend(title="Пользователи / Среднее значение")
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.set_ylim(0, 10)
        fig.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)

        image = BufferedInputFile(buf.getvalue(), filename="skills_chart.png")

        text_info = (
            f"👤 Профиль пользователя:\n"
            f"Имя: {user_data[0]}\n"
            f"Фамилия: {user_data[1]}\n"
            f"Группа: {user_data[2]}"
        )

        await bot.send_photo(
            chat_id=chat_id,
            photo=image,
            caption=text_info,
        )

        buf.close()
    else:
        text_info = (
            f"👤 Профиль пользователя:\n"
            f"Имя: {user_data[0]}\n"
            f"Фамилия: {user_data[1]}\n"
            f"Группа: {user_data[2]}"
        )
        await bot.send_message(chat_id=chat_id, text=text_info)

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    print('start')
    await message.answer('Добро пожаловать!\nВведите ваше имя.')
    user_id = message.from_user.id
    await state.set_state(Reg.user_id)
    await state.update_data(user_id = user_id)
    await state.set_state(Reg.name)

@router.message(Reg.name)
async def reg_name(message: Message, state:FSMContext):
    print('reg_name')
    await state.update_data(name = message.text)
    await state.set_state(Reg.surname)
    await message.answer('Введите вашy фамилию.')

@router.message(Reg.surname)
async def reg_surname(message: Message, state:FSMContext):
    print('reg_surname')
    await state.update_data(surname=message.text)
    await state.set_state(Reg.group)
    await message.answer('Введите название вашей команды.')

@router.message(Reg.group)
async def reg_group(message: Message, state:FSMContext):
    print('reg_group')
    if len(await rq.get_group_list_half(message.text, 1)) > 0:
        groups = await rq.get_group_list_by_name(message.text)
        await state.set_state(Reg.count_pages)
        await state.update_data(count_pages = ceil(len(groups)/5))
        await state.set_state(Reg.text)
        await state.update_data(text = message.text)
        await state.set_state(Reg.current_page)
        await state.update_data(current_page = 1)
        data = await state.get_data()
        keyboard = await kb.half_groups(message.text, 1, data.get("count_pages"))
        await message.answer('Выберите команду из списка.', reply_markup=keyboard)
    elif len(await rq.get_group_list_half(message.text, 1)) == 0:
        groups = await rq.get_group_list_by_name('')
        await state.set_state(Reg.count_pages)
        await state.update_data(count_pages=ceil(len(groups) / 5))
        await state.set_state(Reg.text)
        await state.update_data(text='')
        await state.set_state(Reg.current_page)
        await state.update_data(current_page=1)
        data = await state.get_data()
        keyboard = await kb.half_groups('', 1, data.get("count_pages"))
        await message.answer('Нет совпадений. Выберите команду из списка.', reply_markup=keyboard)


@router.callback_query(F.data.startswith('to_left_group_list'))
async def reg_half_group_left(callback: CallbackQuery, state:FSMContext):
    print('reg_half_group_left')
    data = await state.get_data()
    if int(data.get("current_page")) > 1:
        keyboard = await kb.half_groups(str(data.get("text")),  int(data.get("current_page"))-1, int(data.get("count_pages")))
        await state.set_state(Reg.current_page)
        await state.update_data(current_page = int(data.get("current_page")) - 1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('to_right_group_list'))
async def reg_half_group_right(callback: CallbackQuery, state:FSMContext):
    print('reg_half_group_right')
    data = await state.get_data()
    if int(data.get("current_page")) < int(data.get("count_pages")):
        keyboard = await kb.half_groups(str(data.get("text")),  int(data.get("current_page"))+1, int(data.get("count_pages")))
        await state.set_state(Reg.current_page)
        await state.update_data(current_page= int(data.get("current_page")) +1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('group_'))
async def reg_half_group_group(callback: CallbackQuery, state: FSMContext):
    print('reg_half_group_group')
    await callback.message.delete()
    group_name = callback.data.split('_')[1]
    await state.set_state(Reg.group)
    await state.update_data(group = group_name)
    data = await state.get_data()
    group_id = await rq.get_group_id(group_name)
    await rq.add_user(data.get("name"), data.get("user_id"), 1, group_id, data.get("surname"),)
    await state.clear()
    await callback.message.answer(f'Вы выбрали отдел: {group_name}\nВведите /authorise для авторизации.')


@router.message(Command('authorise'))
async def authorise(message: Message, state: FSMContext):
    print('authorise')
    user_id = message.from_user.id
    await state.set_state(Aut.user_id)
    await state.update_data(user_id = user_id)
    await state.set_state(Aut.role)
    await message.answer('Выберите вашу роль.', reply_markup=kb.authorisation)


@router.message(Aut.role)
async def user_authorise(message: Message, state: FSMContext):
    print('user_authorise')
    await state.update_data(role = message.text)
    if message.text == 'Vip':
        await state.set_state(Aut.vip_password)
        await message.answer('Введите пароль от випки.')
    elif message.text == 'Admin':
        await state.set_state(Aut.admin_password)
        await message.answer('Введите пароль от админки.')
    else:
        await message.answer('Вы вошли как юзер. Выберите действие.', reply_markup=kb.kb_user)
        data = await state.get_data()
        role_id = await rq.get_role_id('user')
        await rq.update_user(data.get("user_id"), role_id[0])
        await state.set_state(Role.user)


@router.message(Aut.vip_password)
async def check_vip_password(message: Message, state: FSMContext):
    print('check_vip_password')
    await state.update_data(vip_password=message.text)
    user_password = message.text
    if user_password == await rq.check_password('vip'):
        await message.answer('Успешный вход!', reply_markup=kb.kb_vip)
        await state.set_state(Role.vip)
        data = await state.get_data()
        role_id = await rq.get_role_id('vip')
        await rq.update_user(data.get("user_id"), role_id[0])
    else:
        await message.answer('Неверный пароль!', reply_markup=kb.authorisation)
        await state.set_state(Aut.role)


@router.message(Aut.admin_password)
async def check_admin_password(message: Message, state: FSMContext):
    print('check_admin_password')
    await state.update_data(admin_password=message.text)
    user_password = message.text
    if user_password == await rq.check_password('admin'):
        await message.answer('Успешный вход!', reply_markup=kb.kb_admin)
        await state.set_state(Role.admin)
        data = await state.get_data()
        role_id = await rq.get_role_id('admin')
        await rq.update_user(data.get("user_id"), role_id[0])
        await state.set_state(Role.admin)
    else:
        await message.answer('Неверный пароль!', reply_markup=kb.authorisation)
        await state.set_state(Aut.role)


@router.message(Role.user)
async def main_window_user(message: Message, state: FSMContext, bot: Bot):
    print('main_window_user')
    if message.text == 'Добавить навык':
        await state.set_state(User.set_skills)
        await message.answer('Введите навык, который хотите добавить.', reply_markup=kb.kb_back_user)

    elif message.text == 'Посмотреть свой профиль':
        user_id = message.from_user.id
        user_info = await rq.user_info(user_id)
        data = await rq.curve(user_id)
        # if not data:
        #     await message.answer("У вас пока нет оцененных навыков.")
        #     return
        print(data)
        await plot_skill_levels_grouped(data, user_info, message.chat.id, bot)
    elif message.text == 'Удалить навык':
        await state.set_state(User_delete_skill.user_id)
        user_sender_id = message.from_user.id
        await state.update_data(user_id = user_sender_id)
        await state.set_state(User_delete_skill.current_page)
        await state.update_data(current_page = 1)
        await state.set_state(User_delete_skill.current_page)
        data = await rq.get_all_skills_by_user_id(user_sender_id)
        count_pages = ceil(len(data)/5)
        await state.update_data(count_pages = count_pages)
        await state.set_state(User_delete_skill.skill_name)
        data = await state.get_data()
        keyboard = await kb.delete_skills_user(user_sender_id, data.get("current_page"), data.get("count_pages"))
        await message.answer('Выберите навык, который хотите удалить', reply_markup= keyboard)


@router.callback_query(F.data.startswith('delete_back_user_menu'))
async def delete_back_user_menu(callback: CallbackQuery, state: FSMContext):
    print('delete_back_user_menu')
    try:
        # Удаляем сообщение с выбором навыков
        await callback.message.delete()

        # Отправляем главное меню
        await callback.message.answer('Выберите действие:', reply_markup=kb.kb_user)

        # Устанавливаем состояние
        await state.set_state(Role.user)
        await callback.answer()

    except Exception as e:
        print(f"Ошибка в delete_back_user_menu: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data.startswith('to_left_delete_skill_user'))
async def set_skill_left(callback: CallbackQuery, state:FSMContext):
    print('set_skill_left')
    data = await state.get_data()
    if int(data.get("current_page")) > 1:
        keyboard = await kb.delete_skills_user(int(data.get("user_id")),  int(data.get("current_page"))-1, int(data.get("count_pages")))
        await state.set_state(User_delete_skill.current_page)
        await state.update_data(current_page = int(data.get("current_page")) - 1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('to_right_delete_skill_user'))
async def set_skill_right(callback: CallbackQuery, state:FSMContext):
    print('set_skill_right')
    data = await state.get_data()
    if int(data.get("current_page")) < int(data.get("count_pages")):
        keyboard = await kb.delete_skills_user(int(data.get("user_id")),  int(data.get("current_page"))+1, int(data.get("count_pages")))
        await state.set_state(User_delete_skill.current_page)
        await state.update_data(current_page= int(data.get("current_page")) +1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)

@router.callback_query(F.data.startswith('delete_skill_user_'))
async def delete_skill_user(callback: CallbackQuery, state: FSMContext):
    print('delete_skill_user')
    await callback.message.delete()
    skill_name = callback.data.split('_')[3]
    await state.set_state(User_delete_skill.skill_name)
    await state.update_data(skill_name=skill_name)
    data = await state.get_data()
    await rq.delete_mark(data.get('user_id'), data.get('skill_name'))
    await callback.message.answer('Выберите действие:', reply_markup=kb.kb_user)
    await state.set_state(Role.user)
    await callback.answer()


@router.message(User.set_more_skills)
async def set_more_skills(message: Message, state: FSMContext):
    print('set_more_skills')
    if not message.text.startswith('Вы выбрали оценку:'):
        await message.answer('Введите навык, который хотите добавить.', reply_markup=kb.kb_back_user)
    await state.set_state(User.set_skills)


@router.message(User.set_skills)
async def set_skills(message: Message, state: FSMContext):
    print('set_skills')
    if message.text.startswith('Назад в меню'):
        await message.answer('Выберите действие.', reply_markup=kb.kb_user)
        await state.set_state(Role.user)
    else:
        user_id = message.from_user.id
        await state.set_state(User_skills.user_id)
        await state.update_data(user_id=user_id)
        if len(await rq.get_skills(message.text, 1)) > 0:
            skills = await rq.get_skill_by_name(message.text)
            await state.set_state(User_skills.count_pages)
            await state.update_data(count_pages = ceil(len(skills)/5))
            await state.set_state(User_skills.text)
            await state.update_data(text = message.text)
            await state.set_state(User_skills.current_page)
            await state.update_data(current_page = 1)
            data = await state.get_data()
            keyboard = await kb.kb_skills(message.text, 1, data.get("count_pages"))
            await message.answer('Выберите навык из списка.', reply_markup=keyboard)

        elif len(await rq.get_skills(message.text, 1)) == 0:
            skills = await rq.get_skill_by_name('')
            await state.set_state(User_skills.count_pages)
            await state.update_data(count_pages=ceil(len(skills) / 5))
            await state.set_state(User_skills.text)
            await state.update_data(text='')
            await state.set_state(User_skills.current_page)
            await state.update_data(current_page=1)
            data = await state.get_data()
            keyboard = await kb.kb_skills('', 1, data.get("count_pages"))
            await message.answer('Нет совпадений. Выберите из списка.', reply_markup=keyboard)


@router.callback_query(F.data.startswith('to_left_user_skills'))
async def set_skill_left(callback: CallbackQuery, state:FSMContext):
    print('set_skill_left')
    data = await state.get_data()
    if int(data.get("current_page")) > 1:
        keyboard = await kb.kb_skills(str(data.get("text")),  int(data.get("current_page"))-1, int(data.get("count_pages")))
        await state.set_state(User_skills.current_page)
        await state.update_data(current_page = int(data.get("current_page")) - 1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('to_right_user_skills'))
async def set_skill_right(callback: CallbackQuery, state:FSMContext):
    print('set_skill_right')
    data = await state.get_data()
    if int(data.get("current_page")) < int(data.get("count_pages")):
        keyboard = await kb.kb_skills(str(data.get("text")),  int(data.get("current_page"))+1, int(data.get("count_pages")))
        await state.set_state(User_skills.current_page)
        await state.update_data(current_page= int(data.get("current_page")) +1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)

@router.callback_query(F.data.startswith('skill_user_'))
async def set_skill(callback: CallbackQuery, state: FSMContext):
    print('set_skill')
    await callback.message.delete()
    skill_name = callback.data.split('_')[2]
    await state.set_state(User_skills.skill_name)
    await state.update_data(skill_name = skill_name)
    await state.set_state(User_skills.mark)
    keyboard = await kb.marks()
    await callback.message.answer(f'Вы выбрали навык: {skill_name}. Выберите оценку: ', reply_markup = keyboard)


@router.callback_query(F.data.startswith('mark_user_'))
async def set_mark(callback: CallbackQuery, state: FSMContext):
    print('set_mark')
    await callback.message.delete()
    mark_name = callback.data.split('_')[2]
    data = await state.get_data()
    await rq.add_mark(data.get("user_id"), data.get("user_id"), data.get("skill_name"), int(mark_name))
    await callback.message.answer(f'Вы выбрали оценку: {mark_name}')
    await set_more_skills(callback.message, state)


@router.callback_query(F.data.startswith('to_back_main_user_menu'))
async def to_back_main_menu(callback: CallbackQuery, state: FSMContext):
    print('to_back_main_menu')
    await callback.message.delete()  # Удаляем сообщение с выбором навыков
    await callback.message.answer('Выберите действие:', reply_markup=kb.kb_user)
    await state.set_state(Role.user)
    await callback.answer()  # Подтверждаем обработку callback


@router.callback_query(F.data.startswith('to_back_skill_user_menu'))
async def back_to_skills(callback: CallbackQuery, state: FSMContext):
    print('back_to_skills')
    data = await state.get_data()
    search_text = data.get("text", "")
    skills = await rq.get_skill_by_name(search_text)
    count_pages = ceil(len(skills) / 5)

    await state.update_data(
        current_page=1,
        count_pages=count_pages
    )

    keyboard = await kb.kb_skills(search_text, 1, count_pages)

    try:
        await callback.message.edit_text(
            'Выберите навык из списка:',
            reply_markup=keyboard
        )
    except:
        await callback.message.answer(
            'Выберите навык из списка:',
            reply_markup=keyboard
        )

    await state.set_state(User.set_skills)
    await callback.answer()

#АДМИНКА
@router.message(Role.admin)
async def main_admin_menu(message: Message, state: FSMContext, bot: Bot):
    print('main_admin_menu')
    if message.text == "Добавить навык":
        await state.set_state(Admin.set_skills)
        await message.answer('Введите навык, который хотите добавить.', reply_markup=kb.kb_back_admin)
    elif message.text == "Посмотреть свой профиль":
        user_id = message.from_user.id
        user_info = await rq.user_info(user_id)
        data = await rq.curve(user_id)
        # if not data:
        #     await message.answer("У вас пока нет оцененных навыков.")
        #     return
        print(data)
        await plot_skill_levels_grouped(data, user_info, message.chat.id, bot)
    elif message.text == "Изменить навык пользователя":
        await state.set_state(Admin_set_skill_for_user.sender_id)
        sender_id = message.from_user.id
        await state.update_data(sender_id = sender_id)
        await state.set_state(Admin_set_skill_for_user.user_wait_id)
        await message.answer('Введите имя и фамилию пользователя, которому хотите добавить навык через пробел(Формат: Иван Иванов)', reply_markup= kb.kb_back_admin_user)
    elif message.text == 'Удалить навык':
        await state.set_state(Admin_delete_skill.user_id)
        user_sender_id = message.from_user.id
        await state.update_data(user_id=user_sender_id)
        await state.set_state(Admin_delete_skill.current_page)
        await state.update_data(current_page=1)
        await state.set_state(Admin_delete_skill.current_page)
        data = await rq.get_all_skills_by_user_id(user_sender_id)
        count_pages = ceil(len(data) / 5)
        await state.update_data(count_pages=count_pages)
        await state.set_state(Admin_delete_skill.skill_name)
        data = await state.get_data()
        keyboard = await kb.delete_skills_admin(user_sender_id, data.get("current_page"), data.get("count_pages"))
        await message.answer('Выберите навык, который хотите удалить', reply_markup=keyboard)


@router.message(Admin_set_skill_for_user.user_wait_id)
async def Admin_set_skill_for_user_user_id_wait(message: Message, state: FSMContext, bot: Bot):
    print('Admin_set_skill_for_user_user_id_wait')
    if message.text == 'Назад в меню':
        await state.set_state(Role.admin)
        await message.answer('Выберите действие', reply_markup=kb.kb_admin)
    else:
        user_info = message.text.split(' ')
        user_name = user_info[0]
        user_surname = user_info[1]
        await state.set_state(Admin_set_skill_for_user.user_name)
        await state.update_data(user_name=user_name)
        await state.set_state(Admin_set_skill_for_user.user_surname)
        await state.update_data(user_surname=user_surname)
        await state.set_state(Admin_set_skill_for_user.current_page)
        await state.update_data(current_page = 1)
        await state.set_state(Admin_set_skill_for_user.count_pages)
        data = await rq.all_users(user_name, user_surname)
        count_pages = ceil(len(data)/5)
        await state.update_data(count_pages = count_pages)
        data = await state.get_data()
        await state.set_state(Admin_set_skill_for_user.user_id)
        keyboard = await kb.half_users(user_name, user_surname, data.get("current_page"), data.get("count_pages") )
        await message.answer('Выберите человека из списка', reply_markup=keyboard)


@router.callback_query(F.data.startswith('alena_back'))
async def alena_back(callback: CallbackQuery, state: FSMContext, bot: Bot):
    print('alena_back')
    # Сбрасываем состояние
    await state.clear()

    # Устанавливаем нужное состояние
    await state.set_state(Admin_set_skill_for_user.sender_id)
    sender_id = callback.from_user.id
    await state.update_data(sender_id=sender_id)
    await state.set_state(Admin_set_skill_for_user.user_wait_id)

    # Отправляем сообщение как в оригинальной функции
    await callback.message.answer(
        'Введите имя и фамилию пользователя, которому хотите добавить навык через пробел(Формат: Иван Иванов)')

    # Подтверждаем обработку callback, чтобы убрать "часики" на кнопке
    await callback.answer()


@router.callback_query(F.data.startswith('to_back_to_users'))
async def to_back_to_users(callback: CallbackQuery, state: FSMContext, bot: Bot):
    print('to_back_to_users')
    # Сбрасываем состояние
    await state.clear()

    # Устанавливаем нужное состояние
    await state.set_state(Admin_set_skill_for_user.sender_id)
    sender_id = callback.from_user.id
    await state.update_data(sender_id=sender_id)
    await state.set_state(Admin_set_skill_for_user.user_wait_id)

    # Отправляем сообщение как в оригинальной функции
    await callback.message.answer(
        'Введите имя и фамилию пользователя, которому хотите добавить навык через пробел(Формат: Иван Иванов)')

    # Подтверждаем обработку callback, чтобы убрать "часики" на кнопке
    await callback.answer()


@router.callback_query(F.data.startswith('delete_user_admin_skill'))
async def delete_user_admin_skill(callback: CallbackQuery, state: FSMContext):
    print('delete_user_admin_skill')
    await state.set_state(Admin_set_skill_for_user.user_sender_id)
    user_sender_id = callback.from_user.id
    await state.update_data(user_sender_id=user_sender_id)
    await state.set_state(Admin_set_skill_for_user.skill_page)
    data = await state.get_data()
    await state.update_data(skill_page = 1)
    await state.set_state(Admin_set_skill_for_user.skill_count)
    h = await rq.get_skills_by_user_id_admin_all(data.get("user_sender_id"), data.get("user_user_id"))
    skill_count = ceil(len(h)/5)
    await state.update_data(skill_count = skill_count)
    await state.set_state(Admin_set_skill_for_user.delete_user_skill)
    data = await state.get_data()
    keyboard = await kb.delete_skills_admin_user(data.get("user_sender_id"), data.get("user_user_id"), 1, data.get("skill_count"))
    await callback.message.answer('Выберите навык', reply_markup=keyboard)


@router.callback_query(F.data.startswith('add_admin_skill'))
async def add_admin_skill(callback: CallbackQuery, state: FSMContext):
    print('add_admin_skill')
    # Сохраняем message_id профиля пользователя
    await state.update_data(profile_message_id=callback.message.message_id)

    # Отправляем запрос навыка и сохраняем его message_id
    msg = await callback.message.answer('Введите название навыка')
    await state.update_data(skill_request_message_id=msg.message_id)

    await state.set_state(Admin_set_skill_for_user.skill_name)


@router.callback_query(F.data.startswith('to_left_user_list_admin'))
async def set_skill_left_user_admin_admin(callback: CallbackQuery, state:FSMContext):
    print('set_skill_left_user_admin_admin')
    data = await state.get_data()
    if int(data.get("current_page")) > 1:
        print(data.get("current_page"))
        keyboard = await kb.half_users(str(data.get("user_name")), str(data.get("user_surname")), int(data.get("current_page"))-1, int(data.get("count_pages")))
        await state.set_state(Admin_set_skill_for_user.current_page)
        await state.update_data(current_page = int(data.get("current_page")) - 1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('to_right_user_list_admin'))
async def set_skill_right_user_admin_admin(callback: CallbackQuery, state:FSMContext):
    print('set_skill_right_user_admin_admin')
    data = await state.get_data()
    if int(data.get("current_page")) < int(data.get("count_pages")):
        keyboard = await kb.half_users(str(data.get("user_name")), str(data.get("user_surname")), int(data.get("current_page"))+1, int(data.get("count_pages")))
        await state.set_state(Admin_set_skill_for_user.current_page)
        await state.update_data(current_page= int(data.get("current_page")) +1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.message(Admin_set_skill_for_user.skill_name)
async def admin_set_skill_for_user_skill_name(message: Message, state: FSMContext):
    print('admin_set_skill_for_user_skill_name')
    if message.text.startswith('Назад в меню'):
        await message.answer('Выберите действие.', reply_markup=kb.kb_admin)
        await state.set_state(Role.admin)
    else:
        user_id = message.from_user.id
        await state.set_state(Admin_set_skill_for_user.sender_id)
        await state.update_data(sender_id=user_id)
        if len(await rq.get_skills(message.text, 1)) > 0:
            skills = await rq.get_skill_by_name(message.text)
            await state.set_state(Admin_set_skill_for_user.count_pages)
            await state.update_data(count_pages=ceil(len(skills) / 5))
            await state.set_state(Admin_set_skill_for_user.text)
            await state.update_data(text=message.text)
            await state.set_state(Admin_set_skill_for_user.current_page)
            await state.update_data(current_page=1)
            data = await state.get_data()
            keyboard = await kb.kb_admin_skills_edit_user(message.text, 1, data.get("count_pages"))
            await message.answer('Выберите навык из списка.', reply_markup=keyboard)

        elif len(await rq.get_skills(message.text, 1)) == 0:
            skills = await rq.get_skill_by_name('')
            await state.set_state(Admin_set_skill_for_user.count_pages)
            await state.update_data(count_pages=ceil(len(skills) / 5))
            await state.set_state(Admin_set_skill_for_user.text)
            await state.update_data(text='')
            await state.set_state(Admin_set_skill_for_user.current_page)
            await state.update_data(current_page=1)
            data = await state.get_data()
            keyboard = await kb.kb_admin_skills_edit_user('', 1, data.get("count_pages"))
            await message.answer('Нет совпадений. Выберите из списка.', reply_markup=keyboard)


async def show_user_skills(chat_id: int, user_id: int, bot: Bot, message_id_to_delete: int | None = None):
    print('show_user_skills')
    data = await rq.curve(user_id)
    user_info = await rq.user_info(user_id)

    # Удаляем сообщение только если передан message_id
    if message_id_to_delete is not None:
        try:
            await bot.delete_message(chat_id, message_id_to_delete)
        except:
            pass  # Игнорируем ошибки, если сообщение уже удалено

    await plot_skill_levels_grouped_admin(data, user_info, chat_id, bot)


@router.callback_query(F.data.startswith('user_'))
async def Admin_set_skill_for_user_user_id(callback: CallbackQuery, state: FSMContext, bot: Bot):
    print('Admin_set_skill_for_user_user_id')
    user_id = int(callback.data.split('_')[1])
    await state.update_data(user_id=user_id)
    await state.set_state(Admin_set_skill_for_user.user_user_id)
    await state.update_data(user_user_id = user_id)
    # Удаляем предыдущее сообщение с кнопкой
    try:
        await callback.message.delete()
    except:
        pass

    # Отображаем профиль и сохраняем его message_id
    data = await rq.curve(user_id)
    user_info = await rq.user_info(user_id)
    msg = await plot_skill_levels_grouped_admin(data, user_info, callback.message.chat.id, bot)

    # Сохраняем message_id профиля для будущего удаления
    if msg:  # если plot_skill_levels_grouped_admin возвращает message
        await state.update_data(profile_message_id=msg.message_id)


@router.callback_query(F.data.startswith('to_back_main_user_admin_menu'))
async def to_back_main_user_admin_menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    print('to_back_main_user_admin_menu')
    data = await state.get_data()
    user_id = data.get('user_id')

    if not user_id:
        await callback.answer("Ошибка: user_id не найден")
        return

    # Удаляем предыдущие сообщения
    messages_to_delete = [
        data.get('profile_message_id'),
        data.get('skill_request_message_id'),
        callback.message.message_id
    ]

    for msg_id in messages_to_delete:
        if msg_id:
            try:
                await bot.delete_message(callback.message.chat.id, msg_id)
            except:
                pass

    # Получаем данные пользователя заново
    user_data = await rq.curve(user_id)
    user_info = await rq.user_info(user_id)

    # Отправляем новый профиль с клавиатурой
    msg = await plot_skill_levels_grouped_admin(user_data, user_info, callback.message.chat.id, bot)

    # Сохраняем message_id нового профиля
    if msg:
        await state.update_data(profile_message_id=msg.message_id)

    await callback.answer()


@router.callback_query(F.data.startswith('to_back_skill_user_admin_menu'))
async def back_to_skills_menu(callback: CallbackQuery, state: FSMContext):
    print('back_to_skills_menu')
    # Получаем сохраненные данные из состояния
    data = await state.get_data()
    skill_name = data.get('text', '')  # Имя навыка, которое вводил админ
    current_page = data.get('current_page', 1)
    count_pages = data.get('count_pages', 1)

    # Удаляем текущее сообщение
    try:
        await callback.message.delete()
    except:
        pass

    # Получаем актуальный список навыков
    if skill_name:
        skills = await rq.get_skill_by_name(skill_name)
    else:
        skills = await rq.get_skill_by_name('')

    # Обновляем количество страниц
    count_pages = ceil(len(skills) / 5)
    await state.update_data(count_pages=count_pages)

    # Создаем клавиатуру с навыками
    keyboard = await kb.kb_admin_skills_edit_user(skill_name, current_page, count_pages)

    # Отправляем новое сообщение со списком навыков
    await callback.message.answer(
        'Выберите навык из списка:' if skill_name else 'Нет совпадений. Выберите из списка:',
        reply_markup=keyboard
    )

    await callback.answer()


@router.callback_query(F.data.startswith('to_left_user_admin_skills'))
async def set_skill_left_user_admin(callback: CallbackQuery, state:FSMContext):
    print('set_skill_left_user_admin')
    data = await state.get_data()
    if int(data.get("current_page")) > 1:
        keyboard = await kb.kb_admin_skills_edit_user(str(data.get("text")),  int(data.get("current_page"))-1, int(data.get("count_pages")))
        await state.set_state(Admin_set_skill_for_user.current_page)
        await state.update_data(current_page = int(data.get("current_page")) - 1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('to_right_user_admin_skills'))
async def set_skill_right_user_admin(callback: CallbackQuery, state:FSMContext):
    print('set_skill_right_user_admin')
    data = await state.get_data()
    if int(data.get("current_page")) < int(data.get("count_pages")):
        keyboard = await kb.kb_admin_skills_edit_user(str(data.get("text")),  int(data.get("current_page"))+1, int(data.get("count_pages")))
        await state.set_state(Admin_set_skill_for_user.current_page)
        await state.update_data(current_page= int(data.get("current_page")) +1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('alena_skill_admin_'))
async def set_admin_skill(callback: CallbackQuery, state: FSMContext):
    print('set_admin_skill')
    skill_name = callback.data.split('_')[3]
    await callback.message.delete()
    await state.set_state(Admin_set_skill_for_user.skill_name)
    await state.update_data(skill_name = skill_name)
    await state.set_state(Admin_set_skill_for_user.mark)
    keyboard = await kb.admin_user_marks()
    await callback.message.answer(f'Вы выбрали навык: {skill_name}. Выберите оценку: ', reply_markup = keyboard)


@router.callback_query(F.data.startswith('alena_mark_user_admin_'))
async def alena_set_mark(callback: CallbackQuery, state: FSMContext):
    print('alena_set_mark')
    await callback.message.delete()
    mark_name = callback.data.split('_')[4]
    data = await state.get_data()
    await rq.add_mark(data.get("sender_id"), data.get("user_id"), data.get("skill_name"), int(mark_name))
    await callback.message.answer(f'Вы выбрали оценку: {mark_name}')
    await set_more_skills_admin_user(callback.message, state)


@router.message(Admin.set_more_skills_for_user)
async def set_more_skills_admin_user(message: Message, state: FSMContext):
    print('set_more_skills_admin_user')
    if not message.text.startswith('Вы выбрали оценку:'):
        await message.answer('Введите навык, который хотите добавить.', reply_markup=kb.kb_back_admin)
    await state.set_state(Admin_set_skill_for_user.skill_name)


@router.message(Admin.set_more_skills)
async def set_more_skills_admin(message: Message, state: FSMContext):
    print('set_more_skills_admin')
    if not message.text.startswith('Вы выбрали оценку:'):
        await message.answer('Введите навык, который хотите добавить.', reply_markup=kb.kb_back_admin)
    await state.set_state(Admin.set_skills)


@router.message(Admin.set_skills)
async def set_skills_admin(message: Message, state: FSMContext):
    print('set_skills_admin')
    if message.text.startswith('Назад в меню'):
        await state.clear()
        await state.set_state(Role.admin)
        await message.answer('Выберите действие:', reply_markup=kb.kb_admin)
    else:
        user_id = message.from_user.id
        await state.set_state(Admin_skills.user_id)
        await state.update_data(user_id=user_id)
        if len(await rq.get_skills(message.text, 1)) > 0:
            skills = await rq.get_skill_by_name(message.text)
            await state.set_state(Admin_skills.count_pages)
            await state.update_data(count_pages = ceil(len(skills)/5))
            await state.set_state(Admin_skills.text)
            await state.update_data(text = message.text)
            await state.set_state(Admin_skills.current_page)
            await state.update_data(current_page = 1)
            data = await state.get_data()
            keyboard = await kb.kb_admin_skills(message.text, 1, data.get("count_pages"))
            await message.answer('Выберите навык из списка.', reply_markup=keyboard)

        elif len(await rq.get_skills(message.text, 1)) == 0:
            skills = await rq.get_skill_by_name('')
            await state.set_state(Admin_skills.count_pages)
            await state.update_data(count_pages=ceil(len(skills) / 5))
            await state.set_state(Admin_skills.text)
            await state.update_data(text='')
            await state.set_state(Admin_skills.current_page)
            await state.update_data(current_page=1)
            data = await state.get_data()
            keyboard = await kb.kb_admin_skills('', 1, data.get("count_pages"))
            await message.answer('Нет совпадений. Выберите из списка.', reply_markup=keyboard)


@router.callback_query(F.data.startswith('to_left_admin_skills'))
async def set_skill_left_admin(callback: CallbackQuery, state:FSMContext):
    print('set_skill_left_admin')
    data = await state.get_data()
    if int(data.get("current_page")) > 1:
        keyboard = await kb.kb_admin_skills(str(data.get("text")),  int(data.get("current_page"))-1, int(data.get("count_pages")))
        await state.set_state(Admin_skills.current_page)
        await state.update_data(current_page = int(data.get("current_page")) - 1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('to_right_admin_skills'))
async def set_skill_right_admin(callback: CallbackQuery, state:FSMContext):
    print('set_skill_right_admin')
    data = await state.get_data()
    if int(data.get("current_page")) < int(data.get("count_pages")):
        keyboard = await kb.kb_admin_skills(str(data.get("text")),  int(data.get("current_page"))+1, int(data.get("count_pages")))
        await state.set_state(Admin_skills.current_page)
        await state.update_data(current_page= int(data.get("current_page")) +1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('skill_admin_'))
async def set_admin_skill(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    skill_name = callback.data.split('_')[2]
    await state.set_state(Admin_skills.skill_name)
    await state.update_data(skill_name = skill_name)
    await state.set_state(Admin_skills.mark)
    keyboard = await kb.admin_marks()
    await callback.message.answer(f'Вы выбрали навык: {skill_name}. Выберите оценку: ', reply_markup = keyboard)


@router.callback_query(F.data.startswith('mark_admin_'))
async def set_mark_admin(callback: CallbackQuery, state: FSMContext):
    print('set_mark_admin')
    await callback.message.delete()
    mark_name = callback.data.split('_')[2]
    data = await state.get_data()
    await rq.add_mark(data.get("user_id"), data.get("user_id"), data.get("skill_name"), int(mark_name))
    await callback.message.answer(f'Вы выбрали оценку: {mark_name}')
    await set_more_skills_admin(callback.message, state)


@router.callback_query(F.data.startswith('to_back_alena_main_admin_menu'))
async def to_back_alena_main_menu(callback: CallbackQuery, state: FSMContext):
    print('to_back_alena_main_menu')
    await callback.message.delete()  # Удаляем сообщение с выбором навыков
    await callback.message.answer('Выберите действие:', reply_markup=kb.kb_admin)
    await state.set_state(Role.admin)
    await callback.answer()  # Подтверждаем обработку callback


@router.callback_query(F.data.startswith('to_back_skill_admin_menu'))
async def back_to_skills(callback: CallbackQuery, state: FSMContext):
    print('back_to_skills')
    data = await state.get_data()
    search_text = data.get("text", "")
    skills = await rq.get_skill_by_name(search_text)
    count_pages = ceil(len(skills) / 5)

    await state.update_data(
        current_page=1,
        count_pages=count_pages
    )

    keyboard = await kb.kb_admin_skills(search_text, 1, count_pages)

    try:
        await callback.message.edit_text(
            'Выберите навык из списка:',
            reply_markup=keyboard
        )
    except:
        await callback.message.answer(
            'Выберите навык из списка:',
            reply_markup=keyboard
        )

    await state.set_state(Admin.set_skills)
    await callback.answer()


@router.callback_query(F.data.startswith('to_left_delete_skill_admin'))
async def set_skill_left_admin(callback: CallbackQuery, state:FSMContext):
    print('set_skill_left_admin')
    data = await state.get_data()
    if int(data.get("current_page")) > 1:
        keyboard = await kb.delete_skills_admin(int(data.get("user_id")),  int(data.get("current_page"))-1, int(data.get("count_pages")))
        await state.set_state(Admin_delete_skill.current_page)
        await state.update_data(current_page = int(data.get("current_page")) - 1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('to_right_delete_skill_admin'))
async def set_skill_right_admin(callback: CallbackQuery, state:FSMContext):
    print('set_skill_right_admin')
    data = await state.get_data()
    if int(data.get("current_page")) < int(data.get("count_pages")):
        keyboard = await kb.delete_skills_admin(int(data.get("user_id")),  int(data.get("current_page"))+1, int(data.get("count_pages")))
        await state.set_state(Admin_delete_skill.current_page)
        await state.update_data(current_page= int(data.get("current_page")) +1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('delete_skill_admin_user_'))
async def delete_skill_admin(callback: CallbackQuery, state: FSMContext):
    print('delete_skill_admin')
    await callback.message.delete()
    skill_name = callback.data.split('_')[4]
    print(f'skill_name - {skill_name}')
    await state.set_state(User_skills.skill_name)
    await state.update_data(skill_name=skill_name)
    data = await state.get_data()
    print(f'data is tatata - {data.get("sender_id")}, {data.get("user_id")}')
    await rq.delete_mark_admin(data.get('sender_id'), data.get('user_id'), data.get('skill_name'))
    await callback.message.answer('Выберите действие:', reply_markup=kb.kb_admin)
    await state.set_state(Role.admin)
    await callback.answer()


@router.callback_query(F.data.startswith('delete_back_user_admin_menu'))
async def delete_back_user_admin_menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    print('to_back_main_user_admin_menu')
    data = await state.get_data()
    user_id = data.get('user_id')

    if not user_id:
        await callback.answer("Ошибка: user_id не найден")
        return

    # Удаляем предыдущие сообщения
    messages_to_delete = [
        data.get('profile_message_id'),
        data.get('skill_request_message_id'),
        callback.message.message_id
    ]

    for msg_id in messages_to_delete:
        if msg_id:
            try:
                await bot.delete_message(callback.message.chat.id, msg_id)
                await bot.delete_message(callback.message.chat.id , msg_id -1)
            except:
                pass

    # Получаем данные пользователя заново
    user_data = await rq.curve(user_id)
    user_info = await rq.user_info(user_id)

    # Отправляем новый профиль с клавиатурой
    msg = await plot_skill_levels_grouped_admin(user_data, user_info, callback.message.chat.id, bot)

    # Сохраняем message_id нового профиля
    if msg:
        await state.update_data(profile_message_id=msg.message_id)

    await callback.answer()


@router.callback_query(F.data.startswith('delete_skill_admin_'))
async def delete_alena_skill_admin(callback: CallbackQuery, state: FSMContext):
    print('delete_alena_skill_admin')
    await callback.message.delete()
    skill_name = callback.data.split('_')[3]
    print(f'skill_name - {skill_name}')
    await state.set_state(Admin_skills.skill_name)
    await state.update_data(skill_name=skill_name)
    data = await state.get_data()
    await rq.delete_mark(data.get('user_id'), data.get('skill_name'))
    await callback.message.answer('Выберите действие:', reply_markup=kb.kb_admin)
    await state.set_state(Role.admin)
    await callback.answer()


#ВИПКА
@router.message(Role.vip)
async def main_vip_menu(message: Message, state: FSMContext, bot: Bot):
    print('main_vip_menu')
    if message.text == "Изменить пароль от админки":
        await state.set_state(Vip.set_admin_password)
        await message.answer('Введите новый пароль для админов', reply_markup=kb.kb_back_vip)
    elif message.text == "Изменить пароль от випки":
        await state.set_state(Vip.set_vip_password)
        await message.answer('Введите новый пароль для випов', reply_markup=kb.kb_back_vip)
    elif message.text == "Посмотреть список админов":
        await state.set_state(Vip_show_users.current_page)
        await state.update_data(current_page = 1)
        data = await rq.all_admins('','')
        count_pages = ceil(len(data)/5)

        await state.set_state(Vip_show_users.count_pages)
        await state.update_data(count_pages = count_pages)
        await state.set_state(Vip_show_users.view_users)

        data = await state.get_data()
        keyboard = await kb.show_users_for_vip('', '', data.get('current_page'), data.get('count_pages'))
        await message.answer('Выберите человека из списка', reply_markup=keyboard)
    elif message.text == "Найти сотрудника по навыкам":
        await state.set_state(VipFindUserStates.input_skill)
        await state.update_data(skills_dict={})
        await message.answer(
            "Введите название навыка для поиска сотрудников:",
            reply_markup=kb.kb_back_vip
        )


# @router.message(Vip_show_users.view_users)
# async def vip_show_users(message: Message, state: FSMContext):
#     print('vip_show_users')


@router.callback_query(F.data.startswith('go_to_vip_main_menu'))
async def go_to_vip_main_menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    print('fo_to_vip_main_menu')
    await state.set_state(Role.vip)
    data = await state.get_data()
    messages_to_delete = [
        data.get('profile_message_id'),
        data.get('skill_request_message_id'),
        callback.message.message_id
    ]

    for msg_id in messages_to_delete:
        if msg_id:
            try:
                await bot.delete_message(callback.message.chat.id, msg_id)
                await bot.delete_message(callback.message.chat.id, msg_id - 1)
                await bot.delete_message(callback.message.chat.id, msg_id - 2)
            except:
                pass

    await callback.message.answer('Выберите действие', reply_markup=kb.kb_vip)


# @router.callback_query(F.data.startswith('vip_to_right_user_list'))
# async def go_to_vip_main_menu(callback: CallbackQuery, state: FSMContext):
    # print('set_skill_right_admin')
    # data = await state.get_data()
    # if int(data.get("current_page")) < int(data.get("count_pages")):
    #     keyboard = await kb.delete_skills_admin(int(data.get("user_id")),  int(data.get("current_page"))+1, int(data.get("count_pages")))
    #     await state.set_state(Admin_delete_skill.current_page)
    #     await state.update_data(current_page= int(data.get("current_page")) +1)
    #     await callback.message.edit_reply_markup(reply_markup = keyboard)

@router.message(Vip.set_admin_password)
async def set_admin_password_by_vip(message: Message, state: FSMContext):
    print('set_admin_password_by_vip')
    if message.text == 'Назад в меню':
        await state.set_state(Role.vip)
        await message.answer('Выберите действие', reply_markup=kb.kb_vip)
    else:
        await rq.set_admin_password_by_vip(message.text, 'admin')
        await state.set_state(Role.vip)
        await message.answer(f'Пароль успешно изменён на: {message.text} \nВыберите действие', reply_markup=kb.kb_vip)


@router.message(Vip.set_vip_password)
async def set_vip_password_by_vip(message: Message, state: FSMContext):
    print('set_vip_password_by_vip')
    if message.text == 'Назад в меню':
        await state.set_state(Role.vip)
        await message.answer('Выберите действие', reply_markup=kb.kb_vip)
    else:
        await rq.set_admin_password_by_vip(message.text, 'vip')
        await state.set_state(Role.vip)
        await message.answer(f'Пароль успешно изменён на: {message.text} \nВыберите действие', reply_markup=kb.kb_vip)


@router.callback_query(F.data.startswith('vip_to_left_user_list'))
async def vip_to_left_user_list(callback: CallbackQuery, state: FSMContext):
    print('vip_to_left_user_list')
    data = await state.get_data()
    if int(data.get("current_page")) > 1:
        keyboard = await kb.show_users_for_vip('', '',data.get('current_page') -1, data.get('count_pages'))
        await state.set_state(Vip_show_users.current_page)
        await state.update_data(current_page= int(data.get("current_page")) -1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('vip_to_right_user_list'))
async def vip_to_right_user_list(callback: CallbackQuery, state: FSMContext):
    print('vip_to_right_user_list')
    data = await state.get_data()
    if int(data.get("current_page")) < int(data.get('count_pages')):
        keyboard = await kb.show_users_for_vip('', '',data.get('current_page') +1, data.get('count_pages'))
        await state.set_state(Vip_show_users.current_page)
        await state.update_data(current_page= int(data.get("current_page")) +1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('vip_show_user'))
async def vip_show_user(callback: CallbackQuery, state: FSMContext, bot: Bot):
    print('vip_show_user')
    user_id = int(callback.data.split('_')[3])

    await state.set_state(Vip_show_current_user.user_id)
    await state.update_data(user_id=user_id)
    await state.set_state(Vip_show_current_user.user_sender_id)
    user_sender_id = callback.from_user.id
    await state.update_data(user_sender_id = user_sender_id)

    # Удаляем предыдущее сообщение с кнопкой
    try:
        await callback.message.delete()
    except:
        pass

    # Отображаем профиль и сохраняем его message_id
    data = await rq.curve(user_id)
    user_info = await rq.user_info(user_id)
    msg = await plot_skill_levels_grouped_vip(data, user_info, callback.message.chat.id, bot)

    # Сохраняем message_id профиля для будущего удаления
    if msg:  # если plot_skill_levels_grouped_admin возвращает message
        await state.update_data(profile_message_id=msg.message_id)


@router.callback_query(F.data.startswith('to_back_vip'))
async def to_back_vip(callback: CallbackQuery, state: FSMContext, bot: Bot):
    # Удаляем предыдущее сообщение с кнопками
    try:
        await callback.message.delete()
    except:
        pass

    # Устанавливаем первую страницу
    await state.set_state(Vip_show_users.current_page)
    await state.update_data(current_page=1)

    # Считаем кол-во страниц
    data = await rq.all_users('', '')
    count_pages = ceil(len(data) / 5)

    await state.set_state(Vip_show_users.count_pages)
    await state.update_data(count_pages=count_pages)

    # Переводим в режим просмотра пользователей
    await state.set_state(Vip_show_users.view_users)

    # Получаем клавиатуру и отправляем новое сообщение
    data = await state.get_data()
    keyboard = await kb.show_users_for_vip('', '', data.get('current_page'), data.get('count_pages'))
    await callback.message.answer('Выберите человека из списка', reply_markup=keyboard)




@router.callback_query(F.data.startswith('add_vip_to_user'))
async def add_vip_to_user(callback: CallbackQuery, state: FSMContext):
    print('add_vip_to_user')
    await state.set_state(Vip_show_current_user.skill_add_wait)
    # await state.update_data(profile_message_id=callback.message.message_id)

    # Отправляем запрос навыка и сохраняем его message_id
    await callback.message.answer('Введите название навыка', reply_markup=kb.kb_back_vip)
    # await state.update_data(skill_request_message_id=msg.message_id)

    # await state.set_state(Admin_set_skill_for_user.skill_name)

@router.message(Vip_show_current_user.skill_add_wait)
async def vip_show_current_user_skill_add_wait(message: Message, state: FSMContext):
    print('vip_show_current_user_skill_add_wait')
    if message.text != 'Назад в меню':
        skill_name = message.text
        await state.set_state(Vip_show_current_user.text)
        await state.update_data(text = skill_name)
        await state.set_state(Vip_show_current_user.skill_add_name)
        await state.update_data(skill_add_name = skill_name)
        await state.set_state(Vip_show_current_user.current_add_page)
        await state.update_data(current_add_page = 1)
        await state.set_state(Vip_show_current_user.count_add_pages)
        data = await rq.get_skill_by_name(skill_name)
        if len(data) == 0:
            data = await rq.get_skill_by_name('')
            await state.set_state(Vip_show_current_user.text)
            await state.update_data(text='')
        count_add_pages = ceil(len(data)/5)
        await state.update_data(count_add_pages=count_add_pages)
        await state.set_state(Vip_show_current_user.add_mark)
        data = await state.get_data()
        keyboard = await kb.add_vip_skill_to_user(data.get('text'), data.get('current_add_page'), data.get('count_add_pages'))
        await message.answer('Выберите навык из списка', reply_markup=keyboard)
    else:
        await state.set_state(Role.vip)
        await message.answer('Выберите действие', reply_markup=kb.kb_vip)


@router.callback_query(F.data.startswith('to_left_user_vip_skills'))
async def to_left_user_vip_skills(callback: CallbackQuery, state:FSMContext):
    print('to_left_user_vip_skills')
    data = await state.get_data()
    if int(data.get("current_add_page")) > 1:
        keyboard = await kb.add_vip_skill_to_user(data.get("text"), int(data.get("current_add_page"))-1, int(data.get("count_add_pages")))
        await state.set_state(Vip_show_current_user.current_add_page)
        await state.update_data(current_add_page = int(data.get("current_add_page")) - 1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('to_right_user_vip_skills'))
async def to_right_user_vip_skills(callback: CallbackQuery, state:FSMContext):
    print('to_right_user_vip_skills')
    data = await state.get_data()
    if int(data.get("current_add_page")) < int(data.get("count_add_pages")):
        keyboard = await kb.add_vip_skill_to_user(data.get("text"), int(data.get("current_add_page"))+1, int(data.get("count_add_pages")))
        await state.set_state(Vip_show_current_user.current_add_page)
        await state.update_data(current_add_page= int(data.get("current_add_page")) +1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('lisa_skill_vip_'))
async def lisa_skill_vip(callback: CallbackQuery, state: FSMContext):
    print('lisa_skill_vip')
    skill_name = callback.data.split('_')[3]
    await callback.message.delete()
    await state.set_state(Vip_show_current_user.skill_add_name)
    await state.update_data(skill_add_name = skill_name)
    await state.set_state(Vip_show_current_user.add_mark)
    keyboard = await kb.vip_marks()
    await callback.message.answer(f'Вы выбрали навык: {skill_name}. Выберите оценку: ', reply_markup = keyboard)


@router.callback_query(F.data.startswith('mark_vip_'))
async def mark_vip(callback: CallbackQuery, state: FSMContext):
    print('mark_vip')
    await callback.message.delete()
    mark_name = callback.data.split('_')[2]
    data = await state.get_data()
    await rq.add_mark(data.get("user_sender_id"), data.get("user_id"), data.get("skill_add_name"), int(mark_name))
    await callback.message.answer(f'Вы выбрали оценку: {mark_name}')
    await set_more_skills_vip_user(callback.message, state)

@router.message(Vip_show_current_user.set_more_skills_for_user)
async def set_more_skills_vip_user(message: Message, state: FSMContext):
    print('set_more_skills_vip_user')
    if not message.text.startswith('Вы выбрали оценку:'):
        await message.answer('Введите навык, который хотите добавить.', reply_markup=kb.kb_back_vip)
    await state.set_state(Vip_show_current_user.skill_add_wait)


@router.callback_query(F.data.startswith('delete_vip_to_user'))
async def delete_vip_to_user(callback: CallbackQuery, state: FSMContext):
    print('delete_vip_to_user')
    await state.set_state(Vip_show_current_user.count_delete_pages)
    data = await state.get_data()
    h = await rq.get_skills_by_user_id_admin_all(data.get("user_sender_id"), data.get("user_id"))
    skill_count = ceil(len(h) / 5)
    await state.update_data(count_delete_pages=skill_count)
    await state.set_state(Vip_show_current_user.current_delete_page)
    await state.update_data(current_delete_page= 1)
    await state.set_state(Vip_show_current_user.skill_delete_name)
    data = await state.get_data()
    keyboard = await kb.delete_skills_vip_user(data.get("user_sender_id"), data.get("user_id"), 1, data.get("count_delete_pages"))
    await callback.message.answer('Выберите навык', reply_markup=keyboard)


@router.callback_query(F.data.startswith('to_left_delete_skill_vip_user'))
async def to_left_delete_skill_vip_user(callback: CallbackQuery, state:FSMContext):
    print('to_left_delete_skill_vip_user')
    data = await state.get_data()
    if int(data.get("current_delete_page")) > 1:
        keyboard = await kb.delete_skills_vip_user(data.get("user_sender_id"), data.get("user_id"), int(data.get("current_delete_page"))-1, int(data.get("count_delete_pages")))
        await state.set_state(Vip_show_current_user.current_delete_page)
        await state.update_data(current_delete_page = int(data.get("current_delete_page")) - 1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('to_right_delete_skill_vip_user'))
async def to_right_delete_skill_vip_user(callback: CallbackQuery, state:FSMContext):
    print('to_right_delete_skill_vip_user')
    data = await state.get_data()
    if int(data.get("current_delete_page")) < int(data.get("count_delete_pages")):
        keyboard = await kb.delete_skills_vip_user(data.get("user_sender_id"), data.get("user_id"), int(data.get("current_delete_page"))+1, int(data.get("count_delete_pages")))
        await state.set_state(Vip_show_current_user.current_delete_page)
        await state.update_data(current_delete_page= int(data.get("current_delete_page")) +1)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('delete_skill_vip_user_'))
async def delete_skill_vip_user(callback: CallbackQuery, state: FSMContext):
    print('delete_skill_vip_user')
    await callback.message.delete()
    skill_name = callback.data.split('_')[4]
    await state.set_state(Vip_show_current_user.skill_delete_name)
    await state.update_data(skill_delete_name=skill_name)
    data = await state.get_data()
    await rq.delete_mark_admin(data.get('user_sender_id'), data.get('user_id'), data.get('skill_delete_name'))
    await callback.message.answer('Выберите действие:', reply_markup=kb.kb_vip)
    await state.set_state(Role.vip)
    await callback.answer()


@router.callback_query(F.data.startswith('to_back_main_user_vip_menu'))
async def to_back_main_user_vip_menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    print('to_back_main_user_vip_menu')
    try:
        await callback.message.delete()
    except:
        pass
    data1 = await state.get_data()

    user_id = data1.get('user_id')
    # Отображаем профиль и сохраняем его message_id
    data = await rq.curve(user_id)
    user_info = await rq.user_info(user_id)
    msg = await plot_skill_levels_grouped_vip(data, user_info, callback.message.chat.id, bot)

    # Сохраняем message_id профиля для будущего удаления
    if msg:  # если plot_skill_levels_grouped_admin возвращает message
        await state.update_data(profile_message_id=msg.message_id)


@router.callback_query(F.data.startswith('go_to_vip_skill'))
async def to_back_main_user_vip_menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        await callback.message.delete()
    except:
        pass
    await state.set_state(Vip_show_current_user.current_add_page)
    await state.update_data(current_add_page=1)
    await state.set_state(Vip_show_current_user.count_add_pages)
    data1 = await state.get_data()
    data = await rq.get_skill_by_name(data1.get('text'))
    if len(data) == 0:
        data = await rq.get_skill_by_name('')
    count_add_pages = ceil(len(data) / 5)
    await state.update_data(count_add_pages=count_add_pages)
    await state.set_state(Vip_show_current_user.add_mark)
    data = await state.get_data()
    keyboard = await kb.add_vip_skill_to_user(data.get('text'), data.get('current_add_page'),
                                              data.get('count_add_pages'))
    await callback.message.answer('Выберите навык из списка', reply_markup=keyboard)


@router.callback_query(F.data.startswith('go_down_by_vip'))
async def delete_back_user_menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    target_user_id = data.get('user_id')

    # Сбрасываем состояние пользователя
    target_state = FSMContext(
        storage=state.storage,
        key=StorageKey(bot_id=callback.bot.id, chat_id=target_user_id, user_id=target_user_id)
    )
    await target_state.clear()

    # Отправляем сервисное сообщение, чтобы узнать последний message_id
    try:
        temp_msg = await bot.send_message(target_user_id, "Сеанс завершается...")
        last_id = temp_msg.message_id

        # Удаляем от последнего к первому
        for msg_id in range(last_id, 0, -1):
            try:
                await bot.delete_message(target_user_id, msg_id)
            except:
                # Просто пропускаем чужие/несуществующие сообщения
                pass
    except Exception as e:
        print(f"Не удалось очистить историю: {e}")

    # Сообщение о старте
    try:
        await bot.send_message(target_user_id, "Ваш сеанс завершён. Чтобы начать заново, отправьте /start")
    except:
        pass

    await callback.answer("Пользователь сброшен.")
    await state.set_state(Role.vip)
    await callback.message.answer('Выберите действие', reply_markup=kb.kb_vip)


@router.message(VipFindUserStates.input_skill)
async def process_skill_input(message: Message, state: FSMContext):
    if message.text == "Назад в меню":
        await state.set_state(Role.vip)
        await message.answer("Выберите действие", reply_markup=kb.kb_vip)
        return
    await state.set_state(VipFindUserStates.text)
    await state.update_data(text = message.text)
    similar_skills = await rq.find_similar_skills_all(message.text)
    if not similar_skills:
        await state.set_state(VipFindUserStates.text)
        await state.update_data(text='')
        similar_skills = await rq.find_similar_skills_all('')
    await state.set_state(VipFindUserStates.current_page)
    await state.update_data(current_page = 1)
    await state.set_state(VipFindUserStates.count_pages)
    count_pages = ceil(len(similar_skills)/5)
    await state.update_data(count_pages=count_pages)
    await state.set_state(VipFindUserStates.select_skill)
    data = await state.get_data()
    keyboard = await kb.get_skills_keyboard(data.get('text'), data.get('current_page'), data.get('count_pages'))
    await message.answer(
        "Выберите подходящий навык из списка:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith('to_left_select_skill'))
async def to_left_select_skill(callback: CallbackQuery, state:FSMContext):
    print('to_left_select_skill')
    data = await state.get_data()
    if int(data.get("current_page")) > 1:
        keyboard = await kb.get_skills_keyboard(str(data.get("text")),  int(data.get("current_page"))-1, int(data.get("count_pages")))
        await state.set_state(VipFindUserStates.current_page)
        await state.update_data(current_page = int(data.get("current_page")) - 1)
        await state.set_state(VipFindUserStates.select_skill)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('to_right_select_skill'))
async def to_right_select_skill(callback: CallbackQuery, state:FSMContext):
    print('to_right_select_skill')
    data = await state.get_data()
    if int(data.get("current_page")) < int(data.get("count_pages")):
        keyboard = await kb.get_skills_keyboard(str(data.get("text")),  int(data.get("current_page"))+1, int(data.get("count_pages")))
        await state.set_state(VipFindUserStates.current_page)
        await state.update_data(current_page= int(data.get("current_page")) +1)
        await state.set_state(VipFindUserStates.select_skill)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


# Выбор навыка из списка
@router.callback_query(F.data.startswith("select_skill:"), VipFindUserStates.select_skill)
async def select_skill(callback: CallbackQuery, state: FSMContext):
    print('selecct_skill')
    skill_name = callback.data.split(":")[1]
    await state.update_data(current_skill=skill_name)
    await state.set_state(VipFindUserStates.select_rating)
    keyboard = await kb.select_marks()
    await callback.message.edit_text(
        f"Выбран навык: {skill_name}\nВыберите минимальную оценку (1-10):",
        reply_markup=keyboard
    )
    await callback.answer()


# Выбор оценки для навыка
@router.callback_query(F.data.startswith("select_rating:"), VipFindUserStates.select_rating)
async def select_rating(callback: CallbackQuery, state: FSMContext):
    print('select_rating')
    rating = int(callback.data.split(":")[1])
    data = await state.get_data()
    skill_name = data.get("current_skill")

    # Обновляем словарь с навыками
    skills_dict = data.get("skills_dict", {})
    skills_dict[skill_name] = rating
    await state.update_data(skills_dict=skills_dict)

    # Формируем список выбранных навыков
    skills_list = "\n".join([f"{k}: {v}" for k, v in skills_dict.items()])

    await state.set_state(VipFindUserStates.ready_to_search)
    keyboard = await kb.get_search_actions_keyboard()
    await callback.message.edit_text(
        f"Текущие критерии поиска:\n{skills_list}\n\n"
        "Хотите добавить еще навыки или начать поиск?",
        reply_markup= keyboard
    )
    await callback.answer()


# Добавление дополнительных навыков
@router.callback_query(F.data.startswith("add_more_skills"), VipFindUserStates.ready_to_search)
async def add_more_skills(callback: CallbackQuery, state: FSMContext):
    await state.set_state(VipFindUserStates.input_skill)
    await callback.message.edit_text(
        "Введите название следующего навыка:"
    )
    await callback.answer()


# Запуск поиска сотрудников
@router.callback_query(F.data == "start_search", VipFindUserStates.ready_to_search)
async def start_search(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    skills_dict = data.get("skills_dict", {})

    # Поиск сотрудников по навыкам
    found_users = await rq.find_users_by_skills_all(skills_dict)

    if not found_users:
        await callback.message.edit_text(
            "Никого не найдено по заданным критериям.",
            reply_markup=None
        )
    else:
        # Форматируем список найденных пользователей
        await state.set_state(VipFindUserStates.count_found_pages)
        count_found_pages = ceil(len(found_users)/5)
        await state.update_data(count_found_pages=count_found_pages)
        await state.set_state(VipFindUserStates.current_found_page)
        await state.update_data(current_found_page=1)
        data = await state.get_data()
        found_users = await rq.find_users_by_skills(skills_dict, data.get('current_found_page'))
        keyboard = await kb.found_people(found_users, data.get('current_found_page'), data.get('count_found_pages'))
        await callback.message.answer(
            f"Найдены сотрудники:",
            reply_markup=keyboard
        )

    # Возвращаем в главное меню VIP
    await state.set_state(Role.vip)
    await callback.answer()


@router.callback_query(F.data.startswith('to_left_found_user'))
async def to_left_found_user(callback: CallbackQuery, state:FSMContext):
    print('to_left_found_user')
    data = await state.get_data()
    if int(data.get("current_found_page")) > 1:
        skills_dict = data.get("skills_dict", {})
        found_users = await rq.find_users_by_skills(skills_dict, data.get('current_found_page')-1)
        keyboard = await kb.get_skills_keyboard(found_users,  int(data.get("current_found_page"))-1, int(data.get("count_pages")))
        await state.set_state(VipFindUserStates.current_found_page)
        await state.update_data(current_page = int(data.get("current_page")) - 1)
        await state.set_state(VipFindUserStates.waiting_user)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('to_right_found_user'))
async def to_right_found_user(callback: CallbackQuery, state:FSMContext):
    print('to_right_found_user')
    data = await state.get_data()
    if int(data.get("current_found_page")) < int(data.get("count_found_pages")):
        skills_dict = data.get("skills_dict", {})
        found_users = await rq.find_users_by_skills(skills_dict, data.get('current_found_page') + 1)
        keyboard = await kb.get_skills_keyboard(found_users, int(data.get("current_found_page")) + 1,int(data.get("count_pages")))
        await state.set_state(VipFindUserStates.current_found_page)
        await state.update_data(current_page=int(data.get("current_page")) + 1)
        await state.set_state(VipFindUserStates.waiting_user)
        await callback.message.edit_reply_markup(reply_markup = keyboard)


@router.callback_query(F.data.startswith('found_people:'))
async def found_people(callback: CallbackQuery, state:FSMContext, bot: Bot):
    print('found_people')
    user_id = int(callback.data.split(':')[1])

    await state.set_state(Vip_show_current_user.user_id)
    await state.update_data(user_id=user_id)
    await state.set_state(Vip_show_current_user.user_sender_id)
    user_sender_id = callback.from_user.id
    await state.update_data(user_sender_id=user_sender_id)

    try:
        await callback.message.delete()
    except:
        pass

    data = await rq.curve(user_id)
    user_info = await rq.user_info(user_id)
    msg = await plot_skill_levels_grouped_vip_search(data, user_info, callback.message.chat.id, bot)

    if msg:
        await state.update_data(profile_message_id=msg.message_id)

# Отмена поиска
@router.callback_query(F.data == "cancel_search")
async def cancel_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Role.vip)
    await callback.message.edit_text(
        "Поиск отменен.",
        reply_markup=None
    )
    await callback.message.answer(
        "Выберите действие",
        reply_markup=get_vip_main_keyboard()
    )
    await callback.answer()


# Обработка некорректных действий
@router.callback_query(StateFilter(VipFindUserStates))
async def handle_incorrect_actions(callback: CallbackQuery):
    await callback.answer(
        "Некорректное действие в текущем состоянии. Пожалуйста, следуйте инструкциям.",
        show_alert=True
    )


# Обработка некорректных сообщений
# @router.message(StateFilter(VipFindUserStates))
# async def handle_incorrect_messages(message: Message):
#     await message.answer(
#         "Пожалуйста, следуйте инструкциям или нажмите 'Назад в меню' для отмены.",
#         reply_markup=get_back_keyboard()
#     )
