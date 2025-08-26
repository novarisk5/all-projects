from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from app.database.requests import (get_group_list_half, get_group_list_all, admins, get_skills, users, get_skills_by_user_id,
                                   get_skills_by_user_id_admin, get_skills_by_user_id_admin_all, find_similar_skills)

from aiogram.utils.keyboard import InlineKeyboardBuilder

authorisation = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='User'), KeyboardButton(text='Admin'), KeyboardButton(text='Vip')]], resize_keyboard=True)

kb_vip = ReplyKeyboardMarkup(keyboard= [[KeyboardButton(text='Посмотреть список админов')],
                              [KeyboardButton(text='Изменить пароль от админки'), KeyboardButton(text='Изменить пароль от випки')],
                              [KeyboardButton(text='Найти сотрудника по навыкам')]], resize_keyboard=True)


kb_admin = ReplyKeyboardMarkup(keyboard= [[KeyboardButton(text='Добавить навык'), KeyboardButton(text='Удалить навык')],
                              [KeyboardButton(text='Посмотреть свой профиль')],
                              [KeyboardButton(text='Изменить навык пользователя')]], resize_keyboard=True)


kb_user = ReplyKeyboardMarkup(keyboard= [[KeyboardButton(text='Добавить навык'), KeyboardButton(text='Удалить навык')],
                              [KeyboardButton(text='Посмотреть свой профиль')]], resize_keyboard=True)



kb_back_user = ReplyKeyboardMarkup(keyboard= [[KeyboardButton(text='Назад в меню')]], resize_keyboard=True)
kb_back_admin = ReplyKeyboardMarkup(keyboard= [[KeyboardButton(text='Назад в меню')]], resize_keyboard=True)

kb_back_admin_user = ReplyKeyboardMarkup(keyboard= [[KeyboardButton(text='Назад в меню')]], resize_keyboard=True)

kb_back_vip = ReplyKeyboardMarkup(keyboard= [[KeyboardButton(text='Назад в меню')]], resize_keyboard=True)


async def delete_skills_user(user_id: int, current_page: int, count_pages: int):
    skill_list = await get_skills_by_user_id(user_id, current_page, count_pages)
    keyboard = InlineKeyboardBuilder()

    for skill in skill_list:
        keyboard.row(InlineKeyboardButton(text=skill, callback_data=f"delete_skill_user_{skill}"))

    keyboard.row(
        InlineKeyboardButton(text='<', callback_data='to_left_delete_skill_user'),
        InlineKeyboardButton(text=(str(current_page) + '/' + str(count_pages)), callback_data='page_number'),
        InlineKeyboardButton(text='>', callback_data='to_right_delete_skill_user')
    )
    keyboard.row(
        InlineKeyboardButton(text='Отмена', callback_data='delete_back_user_menu')
    )
    return keyboard.as_markup()


async def marks():
    keyboard = InlineKeyboardBuilder()
    for mark in range(1,11):
        keyboard.add(InlineKeyboardButton(text=str(mark), callback_data=f"mark_user_{mark}"))
    keyboard.add(InlineKeyboardButton(text='Назад к навыкам', callback_data='to_back_skill_user_menu'))
    return keyboard.adjust(1).as_markup()

async def half_groups(text: str, current_page: int, count_pages: int):
    group_list = await get_group_list_half(text, current_page)
    keyboard = InlineKeyboardBuilder()

    for group in group_list:
        keyboard.row(InlineKeyboardButton(text=group, callback_data=f"group_{group}"))

    keyboard.row(
        InlineKeyboardButton(text='<', callback_data='to_left_group_list'),
        InlineKeyboardButton(text=(str(current_page) + '/' + str(count_pages)), callback_data='page_number'),
        InlineKeyboardButton(text='>', callback_data='to_right_group_list')
    )

    return keyboard.as_markup()


async def kb_skills(text: str, current_page: int, count_pages: int):
    skill_list = await get_skills(text, current_page)
    keyboard = InlineKeyboardBuilder()

    for skill in skill_list:
        keyboard.row(InlineKeyboardButton(text=skill, callback_data=f"skill_user_{skill}"))

    keyboard.row(
        InlineKeyboardButton(text='<', callback_data='to_left_user_skills'),
        InlineKeyboardButton(text=(str(current_page) + '/' + str(count_pages)), callback_data='skill_number'),
        InlineKeyboardButton(text='>', callback_data='to_right_user_skills')
    )
    keyboard.row(InlineKeyboardButton(text='Отменить выбор', callback_data='to_back_main_user_menu'))

    return keyboard.as_markup()

async def kb_admin_skills(text: str, current_page: int, count_pages: int):
    skill_list = await get_skills(text, current_page)
    keyboard = InlineKeyboardBuilder()

    for skill in skill_list:
        keyboard.row(InlineKeyboardButton(text=skill, callback_data=f"skill_admin_{skill}"))

    keyboard.row(
        InlineKeyboardButton(text='<', callback_data='to_left_admin_skills'),
        InlineKeyboardButton(text=(str(current_page) + '/' + str(count_pages)), callback_data='skill_number'),
        InlineKeyboardButton(text='>', callback_data='to_right_admin_skills')
    )
    keyboard.row(InlineKeyboardButton(text='Отменить выбор', callback_data='to_back_alena_main_admin_menu'))

    return keyboard.as_markup()


async def kb_admin_skills_edit_user(text: str, current_page: int, count_pages: int):
    skill_list = await get_skills(text, current_page)
    keyboard = InlineKeyboardBuilder()

    for skill in skill_list:
        print(skill)
        keyboard.row(InlineKeyboardButton(text=skill, callback_data=f"alena_skill_admin_{skill}"))

    keyboard.row(
        InlineKeyboardButton(text='<', callback_data='to_left_user_admin_skills'),
        InlineKeyboardButton(text=(str(current_page) + '/' + str(count_pages)), callback_data='skill_number'),
        InlineKeyboardButton(text='>', callback_data='to_right_user_admin_skills')
    )
    keyboard.row(InlineKeyboardButton(text='Отменить выбор', callback_data='to_back_main_user_admin_menu'))

    return keyboard.as_markup()


async def admin_user_marks():
    keyboard = InlineKeyboardBuilder()
    for mark in range(1,11):
        keyboard.add(InlineKeyboardButton(text=str(mark), callback_data=f"alena_mark_user_admin_{mark}"))
    keyboard.add(InlineKeyboardButton(text='Назад к навыкам', callback_data='to_back_skill_user_admin_menu'))
    return keyboard.adjust(1).as_markup()


async def admin_marks():
    keyboard = InlineKeyboardBuilder()
    for mark in range(1,11):
        keyboard.add(InlineKeyboardButton(text=str(mark), callback_data=f"mark_admin_{mark}"))
    keyboard.add(InlineKeyboardButton(text='Назад к навыкам', callback_data='to_back_skill_admin_menu'))
    return keyboard.adjust(1).as_markup()


async def half_users(user_name: str, user_surname: str, current_page: int, count_pages: int):
    user_list = await users(user_name, user_surname, current_page)
    keyboard = InlineKeyboardBuilder()
    print(current_page)
    for user in user_list:
        keyboard.row(InlineKeyboardButton(text=user[0] + " " + user[1], callback_data=f"user_{user[2]}"))

    keyboard.row(
        InlineKeyboardButton(text='<', callback_data='to_left_user_list_admin'),
        InlineKeyboardButton(text=(str(current_page) + '/' + str(count_pages)), callback_data='page_number'),
        InlineKeyboardButton(text='>', callback_data='to_right_user_list_admin')
    )

    keyboard.row(
        InlineKeyboardButton(text='Отмена', callback_data='alena_back'),
    )
    return keyboard.as_markup()

async def edit_profile_user():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text='Добавить навык', callback_data='add_admin_skill')
    )
    keyboard.row(
        InlineKeyboardButton(text='Удалить навык', callback_data='delete_user_admin_skill')
    )
    keyboard.row(
        InlineKeyboardButton(text='Отмена', callback_data='to_back_to_users')
    )
    return keyboard.as_markup()


async def delete_skills_admin_user(sender_id: int, user_id: int, current_page: int, count_pages: int):
    print(sender_id,user_id)
    skill_list = await get_skills_by_user_id_admin(sender_id, user_id, current_page, count_pages)
    keyboard = InlineKeyboardBuilder()

    for skill in skill_list:
        keyboard.row(InlineKeyboardButton(text=skill, callback_data=f"delete_skill_admin_user_{skill}"))

    keyboard.row(
        InlineKeyboardButton(text='<', callback_data='to_left_delete_skill_admin_user'),
        InlineKeyboardButton(text=(str(current_page) + '/' + str(count_pages)), callback_data='page_number'),
        InlineKeyboardButton(text='>', callback_data='to_right_delete_skill_admin_user')
    )
    keyboard.row(
        InlineKeyboardButton(text='Отмена', callback_data='delete_back_user_admin_menu')
    )
    return keyboard.as_markup()

async def delete_skills_admin(user_id: int, current_page: int, count_pages: int):
    skill_list = await get_skills_by_user_id(user_id, current_page, count_pages)
    keyboard = InlineKeyboardBuilder()

    for skill in skill_list:
        keyboard.row(InlineKeyboardButton(text=skill, callback_data=f"delete_skill_admin_{skill}"))

    keyboard.row(
        InlineKeyboardButton(text='<', callback_data='to_left_delete_skill_admin'),
        InlineKeyboardButton(text=(str(current_page) + '/' + str(count_pages)), callback_data='page_number'),
        InlineKeyboardButton(text='>', callback_data='to_right_delete_skill_admin')
    )
    keyboard.row(
        InlineKeyboardButton(text='Отмена', callback_data='to_back_alena_main_admin_menu')
    )
    return keyboard.as_markup()

async def show_users_for_vip(user_name: str, user_surname: str, current_page: int, count_pages: int):
    user_list = await admins(user_name, user_surname, current_page)
    keyboard = InlineKeyboardBuilder()
    print(current_page)
    for user in user_list:
        keyboard.row(InlineKeyboardButton(text=user[0] + " " + user[1], callback_data=f"vip_show_user_{user[2]}"))

    keyboard.row(
        InlineKeyboardButton(text='<', callback_data='vip_to_left_user_list'),
        InlineKeyboardButton(text=(str(current_page) + '/' + str(count_pages)), callback_data='page_number'),
        InlineKeyboardButton(text='>', callback_data='vip_to_right_user_list')
    )

    keyboard.row(
        InlineKeyboardButton(text='Отмена', callback_data='go_to_vip_main_menu'),
    )
    return keyboard.as_markup()


async def edit_profile_user_vip():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text='Понизить до юзера', callback_data='go_down_by_vip')
    )
    keyboard.row(
        InlineKeyboardButton(text='Добавить навык', callback_data='add_vip_to_user')
    )
    keyboard.row(
        InlineKeyboardButton(text='Удалить навык', callback_data='delete_vip_to_user')
    )
    keyboard.row(
        InlineKeyboardButton(text='Отмена', callback_data='to_back_vip')
    )
    return keyboard.as_markup()


async def add_vip_skill_to_user(skill_name: str, current_page: int, count_pages: int):
    print(f'а это я {skill_name}')
    skill_list = await get_skills(skill_name, current_page)
    if len(skill_list) == 0:
        print('Я тута')
        skill_list = await get_skills('', current_page)
    keyboard = InlineKeyboardBuilder()

    for skill in skill_list:
        print(skill)
        keyboard.row(InlineKeyboardButton(text=skill, callback_data=f"lisa_skill_vip_{skill}"))

    keyboard.row(
        InlineKeyboardButton(text='<', callback_data='to_left_user_vip_skills'),
        InlineKeyboardButton(text=(str(current_page) + '/' + str(count_pages)), callback_data='skill_number'),
        InlineKeyboardButton(text='>', callback_data='to_right_user_vip_skills')
    )
    keyboard.row(InlineKeyboardButton(text='Отменить выбор', callback_data='to_back_main_user_vip_menu'))

    return keyboard.as_markup()

async def vip_marks():
    keyboard = InlineKeyboardBuilder()
    for mark in range(1,11):
        keyboard.add(InlineKeyboardButton(text=str(mark), callback_data=f"mark_vip_{mark}"))
    keyboard.add(InlineKeyboardButton(text='Назад к навыкам', callback_data="go_to_vip_skills")) #----------------
    return keyboard.adjust(1).as_markup()


async def delete_skills_vip_user(sender_id: int, user_id: int, current_page: int, count_pages: int):
    skill_list = await get_skills_by_user_id_admin(sender_id, user_id, current_page, count_pages)
    keyboard = InlineKeyboardBuilder()

    for skill in skill_list:
        keyboard.row(InlineKeyboardButton(text=skill, callback_data=f"delete_skill_vip_user_{skill}"))

    keyboard.row(
        InlineKeyboardButton(text='<', callback_data='to_left_delete_skill_vip_user'),
        InlineKeyboardButton(text=(str(current_page) + '/' + str(count_pages)), callback_data='page_number'),
        InlineKeyboardButton(text='>', callback_data='to_right_delete_skill_vip_user')
    )
    keyboard.row(
        InlineKeyboardButton(text='Отмена', callback_data='to_back_main_user_vip_menu')
    )
    return keyboard.as_markup()




async def get_skills_keyboard(skill_name: str, current_page: int, count_pages: int):
    skills = await find_similar_skills(skill_name, current_page, count_pages)
    keyboard = InlineKeyboardBuilder()
    for skill in skills:
        keyboard.row(InlineKeyboardButton(text=skill, callback_data=f"select_skill:{skill}"))
    keyboard.row(
        InlineKeyboardButton(text='<', callback_data='to_left_select_skill'),
        InlineKeyboardButton(text=(str(current_page) + '/' + str(count_pages)), callback_data='page_number'),
        InlineKeyboardButton(text='>', callback_data='to_right_select_skill')
    )
    keyboard.row(
        InlineKeyboardButton(text='Отмена', callback_data='to_back_main_user_vip_menu')
    )
    return keyboard.as_markup()

async def select_marks():
    keyboard = InlineKeyboardBuilder()
    for mark in range(1,11):
        keyboard.add(InlineKeyboardButton(text=str(mark), callback_data=f"select_rating:{mark}"))
    keyboard.add(InlineKeyboardButton(text='Назад к навыкам', callback_data='to_back_skill_user_menu'))
    return keyboard.adjust(1).as_markup()

async def get_search_actions_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Добавить еще навык", callback_data="add_more_skills")
    builder.button(text="Найти сотрудников", callback_data="start_search")
    builder.button(text="Отмена", callback_data="cancel_search")
    builder.adjust(1)
    return builder.as_markup()

async def get_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад в меню", callback_data="cancel_search")
    return builder.as_markup()

async def get_vip_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Изменить пароль от админки", callback_data="change_admin_pass")
    builder.button(text="Изменить пароль от випки", callback_data="change_vip_pass")
    builder.button(text="Посмотреть список админов", callback_data="show_admins")
    builder.button(text="Найти сотрудника по навыкам", callback_data="find_by_skills")
    builder.adjust(1)
    return builder.as_markup()


async def found_people(users, current_page: int, count_pages: int):
    keyboard = InlineKeyboardBuilder()
    for user in users:
        print(user)
        keyboard.row(InlineKeyboardButton(text=user[0] + ' ' + user[1], callback_data=f"found_people:{user[2]}"))
    keyboard.row(
        InlineKeyboardButton(text='<', callback_data='to_left_found_user'),
        InlineKeyboardButton(text=(str(current_page) + '/' + str(count_pages)), callback_data='page_number'),
        InlineKeyboardButton(text='>', callback_data='to_right_found_user')
    )
    keyboard.row(
        InlineKeyboardButton(text='Отмена', callback_data='to_back_main_user_vip_menu')
    )
    return keyboard.as_markup()