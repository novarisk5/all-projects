from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.sql import func

engine = create_async_engine(url='postgresql+asyncpg://postgres:v08042006K@localhost/postgres')

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class Group(Base):
    __tablename__ = 't_groups'

    group_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_name: Mapped[str] = mapped_column(String(30), unique=True)


class Role(Base):
    __tablename__ = 't_roles'

    role_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(10), unique=True)
    role_password: Mapped[str] = mapped_column(String(30))


class User(Base):
    __tablename__ = 't_users'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(20))
    user_surname: Mapped[str] = mapped_column(String(20))
    user_group: Mapped[int] = mapped_column(ForeignKey('t_groups.group_id'))
    user_role_id: Mapped[int] = mapped_column(ForeignKey('t_roles.role_id'))


class Skill(Base):
    __tablename__ = 't_skills'

    skill_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    skill_name_rus: Mapped[str] = mapped_column(String(40))
    skill_name_eng: Mapped[str] = mapped_column(String(40))

class Mark(Base):
    __tablename__ = 't_marks'

    mark_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mark: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey('t_users.user_id'))
    user_sender_id: Mapped[int] = mapped_column(ForeignKey('t_users.user_id'))
    skill_id: Mapped[int] = mapped_column(ForeignKey('t_skills.skill_id'))

class Mark_log(Base):
    __tablename__ = 't_marks_log'

    id: Mapped[int] = mapped_column(primary_key=True)
    mark: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey('t_users.user_id'))
    user_sender_id: Mapped[int] = mapped_column(ForeignKey('t_users.user_id'))
    skill_id: Mapped[int] = mapped_column(ForeignKey('t_skills.skill_id'))
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)