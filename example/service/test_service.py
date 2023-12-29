from example.database.dao.user_dao import UserDao


class TestService:
    @staticmethod
    async def get_all():
        return UserDao.get_all()
