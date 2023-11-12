from test.api import api
from test.controller.test_controller import test_bp

from flask import Flask

from clio import exception_handler, hack_json, hook_make_response

hook_make_response()
hack_json()

app = Flask(__name__)
api.register(app)
app.register_blueprint(test_bp)
exception_handler(app)
app.run(debug=False, port=8101, host="0.0.0.0")
