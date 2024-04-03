import sqlalchemy

from .bd_session import SqlAlchemyBase


class Keywords(SqlAlchemyBase):
    __tablename__ = 'keywords'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    word = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)