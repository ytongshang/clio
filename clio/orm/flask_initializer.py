def flask_create_table(
    app, database, bind_key: str | None | list[str | None] = "__all__"
):
    with app.app_context():
        database.create_all(bind_key=bind_key)
