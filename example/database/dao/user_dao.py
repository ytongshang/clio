from example.database.database import db
from example.database.entity import User


class UserDao:
    @staticmethod
    def get_all():
        resp = db.session.query(User).all()
        return resp
