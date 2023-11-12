from flask_sqlalchemy import SQLAlchemy


def flask_init_database(app, config):
    database = SQLAlchemy()
    app.config.from_mapping(config)
    database.init_app(app)
    return database


def flask_create_table(
    app, database, bind_key: str | None | list[str | None] = "__all__"
):
    with app.app_context():
        database.create_all(bind_key=bind_key)
