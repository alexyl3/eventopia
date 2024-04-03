import sqlalchemy
from .bd_session import SqlAlchemyBase


class Events(SqlAlchemyBase):
    __tablename__ = 'events'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    key_words = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("keywords.id"))
    link = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("keywords.id"))
    grade = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    image_link = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)