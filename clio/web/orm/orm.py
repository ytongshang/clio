from prisma import Prisma


class SQLAlchemy:
    def __init__(self):
        self.client: Prisma = Prisma()
