from prisma import Prisma


class SQLAlchemy:
    def __init__(
        self,
        database_uri: str,
    ):
        self.client: Prisma = Prisma()
