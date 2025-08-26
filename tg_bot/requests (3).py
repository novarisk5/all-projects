from app.database.models import async_session
from app.database.models import Role, User, Skill, Mark, Mark_log, Group
from sqlalchemy import select, or_, insert, update, and_, delete
from sqlalchemy import text
from sqlalchemy.orm import aliased  # Добавлен импорт aliased
from aiogram import Bot
from sqlalchemy.orm import selectinload



async def check_password(role: str):
    async with async_session() as session:
        password = await session.scalar(select(Role.role_password).where(Role.role_name == role))
        return password


async def select_user(user_id):
    async with async_session() as session:
        role = await session.scalar(select(User.user_role_id).where(User.user_id == user_id))
        return role


async def get_group_id(group_name):
    async with async_session() as session:
        role = await session.scalar(select(Group.group_id).where(Group.group_name == group_name))
        return role


async def get_group_list_half(group_name: str, page: int):
    async with async_session() as session:
        result = await session.execute(
            select(Group.group_name).where(Group.group_name.ilike(f"%{group_name}%")).limit(5).offset((page-1)*5)
        )
        groups_list = [row[0] for row in result.all()]

        return groups_list


async def get_group_list_by_name(group_name: str):
    async with async_session() as session:
        result = await session.execute(
            select(Group.group_name).where(Group.group_name.ilike(f"%{group_name}%"))
        )
        groups_list = [row[0] for row in result.all()]

        return groups_list


async def get_group_list_all():
    async with async_session() as session:
        result = await session.execute(
            select(Group.group_name).limit(5).offset(5)
        )
        groups_list = [row[0] for row in result.all()]

        return groups_list


async def get_skills(skill_name: str, page: int):
    async with async_session() as session:
        condition = or_(
            Skill.skill_name_rus.ilike(f"%{skill_name}%"),
            Skill.skill_name_eng.ilike(f"%{skill_name}%")
        )
        result = await session.execute(
            select(Skill.skill_name_rus)
            .where(condition)
            .limit(5)
            .offset((page - 1) * 5)
        )
        skills_list = [row[0] for row in result.all()]
        return skills_list


async def get_skill_by_name(skill_name: str):
    async with async_session() as session:
        condition = or_(
            Skill.skill_name_rus.ilike(f"%{skill_name}%"),
            Skill.skill_name_eng.ilike(f"%{skill_name}%")
        )

        result = await session.execute(
            select(Skill.skill_name_rus)
            .where(condition)
        )
        skills_list = [row[0] for row in result.all()]
        return skills_list


async def add_user(user_name: str, user_id: int, user_role_id: int, user_group: str, user_surname: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        if user:
            stmt = update(User).where(User.user_id == user_id)
            if user_role_id:
                stmt = stmt.values(user_role_id=user_role_id)
            if user_group:
                stmt = stmt.values(user_group=user_group)
            if user_name:
                stmt = stmt.values(user_name=user_name)
            if user_surname:
                stmt = stmt.values(user_surname=user_surname)
            await session.execute(stmt)
            await session.commit()

        else:
            await session.execute(
                insert(User).values(
                    user_name=user_name,
                    user_surname = user_surname,
                    user_id=user_id,
                    user_role_id=user_role_id,
                    user_group=user_group
                )
            )
        await session.commit()


async def user_info(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(
                User.user_name,
                User.user_surname,
                Group.group_name
            )
            .join(Group, User.user_group == Group.group_id)
            .where(User.user_id == user_id)
        )

        for row in result:
            user_info = [row.user_name, row.user_surname, row.group_name]
        return user_info

async def curve(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(
                Mark.user_sender_id,
                User.user_name,
                Mark.mark,
                Skill.skill_name_rus
            )
            .join(Skill, Mark.skill_id == Skill.skill_id)
            .join(User, Mark.user_sender_id == User.user_id)
            .where(Mark.user_id == user_id)
        )

        matrix = [
            [row.user_sender_id, row.user_name, row.mark, row.skill_name_rus]
            for row in result
        ]
        return matrix


async def delete_mark(user_id: int, skill_name: str):
    """
    Удаляет оценку из таблицы marks по:
    - ID отправителя (кто поставил оценку)
    - ID пользователя (кому поставили оценку)
    - Названию навыка (на русском)

    Возвращает количество удаленных записей (0 если не найдено)
    """
    async with async_session() as session:
        try:
            # 1. Находим skill_id по названию навыка
            skill_id = await session.scalar(
                select(Skill.skill_id)
                .where(Skill.skill_name_rus == skill_name)
            )

            if not skill_id:
                print(f"Навык '{skill_name}' не найден")
                return 0

            # 2. Удаляем оценки с указанными параметрами
            stmt = delete(Mark).where(
                (Mark.user_sender_id == user_id) &
                (Mark.skill_id == skill_id) &
                (Mark.user_id == user_id)
            )

            result = await session.execute(stmt)
            await session.commit()

            deleted_count = result.rowcount
            print(f"Удалено {deleted_count} записей")
            return deleted_count

        except Exception as e:
            await session.rollback()
            print(f"Ошибка при удалении оценки: {e}")
            return 0

async def delete_mark_admin(sender_id: int,user_id: int, skill_name: str):
    """
    Удаляет оценку из таблицы marks по:
    - ID отправителя (кто поставил оценку)
    - ID пользователя (кому поставили оценку)
    - Названию навыка (на русском)

    Возвращает количество удаленных записей (0 если не найдено)
    """
    async with async_session() as session:
        try:
            # 1. Находим skill_id по названию навыка
            skill_id = await session.scalar(
                select(Skill.skill_id)
                .where(Skill.skill_name_rus == skill_name)
            )

            if not skill_id:
                print(f"Навык '{skill_name}' не найден")
                return 0

            # 2. Удаляем оценки с указанными параметрами
            stmt = delete(Mark).where(
                (Mark.user_sender_id == sender_id) &
                (Mark.skill_id == skill_id) &
                (Mark.user_id == user_id)
            )

            result = await session.execute(stmt)
            await session.commit()

            deleted_count = result.rowcount
            print(f"Удалено {deleted_count} записей")
            return deleted_count

        except Exception as e:
            await session.rollback()
            print(f"Ошибка при удалении оценки: {e}")
            return 0

async def add_mark(sender_id: int, user_id: int, skill_name: str, mark: int):
    async with async_session() as session:
        skill_id = await session.scalar(select(Skill.skill_id).where(Skill.skill_name_rus==skill_name))
        mark_id = await session.scalar(
            select(Mark.mark_id).where(
                and_(
                    Mark.user_id == user_id,
                    Mark.skill_id == skill_id,
                    Mark.user_sender_id == sender_id
                )
            )
        )

        if mark_id:
            stmt = update(Mark).where(Mark.mark_id == mark_id)
            if user_id:
                stmt = stmt.values(user_id=user_id)
            if skill_id:
                stmt = stmt.values(skill_id=skill_id)
            if mark:
                stmt = stmt.values(mark=mark)
            if sender_id:
                stmt = stmt.values(user_sender_id = sender_id)
            await session.execute(stmt)
            await session.commit()
        else:
            await session.execute(
                insert(Mark).values(
                    user_id=user_id,
                    skill_id=skill_id,
                    mark=mark,
                    user_sender_id=sender_id,
                )
            )
        await session.commit()




async def add_skill(skill_name_rus: str, skill_name_eng: str):
    async with async_session() as session:
        await session.execute(
            insert(Skill).values(
                skill_name_rus=skill_name_rus,
                skill_name_eng=skill_name_eng
            )
        )
        await session.commit()

async def get_skills_by_user_id_admin(sender_id: int, user_id: int, current_page: int, count_pages: int):
    async with async_session() as session:
        result = await session.execute(
            select(Skill.skill_name_rus)
            .join(Mark, Mark.skill_id == Skill.skill_id)
            .where(
                and_(
                    Mark.user_id == user_id,
                    Mark.user_sender_id == sender_id
                )
            )
            .limit(5)
            .offset((current_page - 1) * 5)
        )
        skills = [row[0] for row in result.all()]

        return skills

async def get_skills_by_user_id_admin_all(sender_id: int, user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Skill.skill_name_rus)
            .join(Mark, Mark.skill_id == Skill.skill_id)
            .where(
                and_(
                    Mark.user_id == user_id,
                    Mark.user_sender_id == sender_id
                )
            )
        )
        skills = [row[0] for row in result.all()]

        return skills
async def get_skills_by_user_id(user_id: int, current_page: int, count_pages: int):
    async with async_session() as session:
        result = await session.execute(
            select(Skill.skill_name_rus)
            .join(Mark, Mark.skill_id == Skill.skill_id)
            .where(
                and_(
                    Mark.user_id == user_id,
                    Mark.user_sender_id == user_id
                )
            )
            .limit(5)
            .offset((current_page - 1) * 5)
        )
        skills = [row[0] for row in result.all()]

        return skills
async def get_all_skills_by_user_id(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Skill.skill_name_rus)
            .join(Mark, Mark.skill_id == Skill.skill_id)
            .where(
                and_(
                    Mark.user_id == user_id,
                    Mark.user_sender_id == user_id
                )
            ))
        skills = [row[0] for row in result.all()]

        return skills


async def get_role_id(role_name: str):
    async with async_session() as session:
        result = await session.execute(
            select(Role.role_id).where(Role.role_name == role_name)
        )
        role_id = [row[0] for row in result.all()]

        return role_id


async def update_user(user_id: int, new_role: int = None):
    async with async_session() as session:
        stmt = update(User).where(User.user_id == user_id)
        if new_role:
            stmt = stmt.values(user_role_id=new_role)

        await session.execute(stmt)
        await session.commit()


async def get_user_skills_data(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(
                Mark.user_sender_id,
                User.user_name,
                Mark.mark,
                Skill.skill_name_rus
            )
            .join(User, Mark.user_sender_id == User.user_id)
            .join(Skill, Mark.skill_id == Skill.id)
            .where(Mark.user_id == user_id)
        )
        return result.all()




async def users(user_name: str, user_surname: str, current_page: int):
    async with async_session() as session:
        condition = and_(
            User.user_name.ilike(f"%{user_name}%"),
            User.user_surname.ilike(f"%{user_surname}%")
        )
        print(current_page)
        result = await session.execute(
            select(
                User.user_name,
                User.user_surname,
                User.user_id
            )
            .where(condition)
            .limit(5)
            .offset((current_page - 1) * 5)
        )

        matrix = [
            [row.user_name, row.user_surname, row.user_id]
            for row in result
        ]

        return matrix

async def admins(user_name: str, user_surname: str, current_page: int):
    async with async_session() as session:
        condition = and_(
            User.user_name.ilike(f"%{user_name}%"),
            User.user_surname.ilike(f"%{user_surname}%"),
            Role.role_name == 'admin'
        )
        print(current_page)
        result = await session.execute(
            select(
                User.user_name,
                User.user_surname,
                User.user_id
            )
            .join(Role, Role.role_id == User.user_role_id)
            .where(condition)
            .limit(5)
            .offset((current_page - 1) * 5)
        )

        matrix = [
            [row.user_name, row.user_surname, row.user_id]
            for row in result
        ]

        return matrix


async def all_users(user_name: str, user_surname: str):
    async with async_session() as session:
        condition = and_(
            User.user_name.ilike(f"%{user_name}%"),
            User.user_surname.ilike(f"%{user_surname}%")
        )

        result = await session.execute(
            select(
                User.user_name,
                User.user_surname,
                User.user_id
            )
            .where(condition)
        )

        matrix = [
            [row.user_name, row.user_surname, row.user_id]
            for row in result
        ]

        return matrix

async def all_admins(user_name: str, user_surname: str):
    async with async_session() as session:
        condition = and_(
            User.user_name.ilike(f"%{user_name}%"),
            User.user_surname.ilike(f"%{user_surname}%"),
            Role.role_name == 'admin'
        )

        result = await session.execute(
            select(
                User.user_name,
                User.user_surname,
                User.user_id
            )
            .join(Role, User.user_role_id == Role.role_id)
            .where(condition)
        )

        matrix = [
            [row.user_name, row.user_surname, row.user_id]
            for row in result
        ]

        return matrix

async def set_admin_password_by_vip(password: str, role: str):
    async with async_session() as session:
        await session.execute(
            text("UPDATE t_roles SET role_password = :password WHERE role_name = :role"),
            {"password": password, "role": role}
        )
        await session.commit()




async def find_similar_skills(query: str, current_page: int, count_pages: int) -> list[str]:
    async with async_session() as session:
        result = await session.execute(
            select(Skill.skill_name_rus)
            .where(Skill.skill_name_rus.ilike(f"%{query}%"))
            .limit(5)
            .offset((current_page - 1) * 5)

        )
        return [row[0] for row in result.all()]

async def find_similar_skills_all(query: str) -> list[str]:
    async with async_session() as session:
        result = await session.execute(
            select(Skill.skill_name_rus)
            .where(Skill.skill_name_rus.ilike(f"%{query}%"))

        )
        return [row[0] for row in result.all()]


async def find_users_by_skills_all(skills_dict: dict[str, int]) -> list[dict]:
    if not skills_dict:
        return []

    async with async_session() as session:
        conditions = []
        joins = []

        for i, (skill_name, min_rating) in enumerate(skills_dict.items()):
            mark_alias = aliased(Mark, name=f"mark_{i}")
            skill_alias = aliased(Skill, name=f"skill_{i}")

            # Добавляем условия для каждого навыка
            conditions.extend([
                skill_alias.skill_name_rus == skill_name,
                mark_alias.mark >= min_rating
            ])

            # Добавляем JOIN для каждой пары mark-skill
            joins.append(
                (mark_alias, mark_alias.user_id == User.user_id)
            )
            joins.append(
                (skill_alias, mark_alias.skill_id == skill_alias.skill_id)
            )

        # Строим базовый запрос
        query = select(
            User.user_id,
            User.user_name,
            User.user_surname
        ).distinct()

        # Добавляем все JOIN-ы
        for join_entity, join_condition in joins:
            query = query.join(join_entity, join_condition)

        # Добавляем все условия
        query = query.where(and_(*conditions))

        # Выполняем запрос
        result = await session.execute(query)
        matrix = [
            [row.user_name, row.user_surname, row.user_id]
            for row in result
        ]
        return matrix


async def find_users_by_skills(skills_dict: dict[str, int],  current_page: int) -> list[dict]:
    if not skills_dict:
        return []

    async with async_session() as session:
        conditions = []
        joins = []

        for i, (skill_name, min_rating) in enumerate(skills_dict.items()):
            mark_alias = aliased(Mark, name=f"mark_{i}")
            skill_alias = aliased(Skill, name=f"skill_{i}")

            # Добавляем условия для каждого навыка
            conditions.extend([
                skill_alias.skill_name_rus == skill_name,
                mark_alias.mark >= min_rating
            ])

            # Добавляем JOIN для каждой пары mark-skill
            joins.append(
                (mark_alias, mark_alias.user_id == User.user_id)
            )
            joins.append(
                (skill_alias, mark_alias.skill_id == skill_alias.skill_id)
            )

        # Строим базовый запрос
        query = select(
            User.user_id,
            User.user_name,
            User.user_surname
        ).distinct().limit(5).offset((current_page - 1) * 5)

        # Добавляем все JOIN-ы
        for join_entity, join_condition in joins:
            query = query.join(join_entity, join_condition)

        # Добавляем все условия
        query = query.where(and_(*conditions))

        # Выполняем запрос
        result = await session.execute(query)
        matrix = [
            [row.user_name, row.user_surname, row.user_id]
            for row in result
        ]
        return matrix