from flask import Flask
from my_flask_server.controllers.user_controller import user_api
from my_flask_server.controllers.store_controller import store_api
from my_flask_server.controllers.pet_controller import pet_api
from my_flask_server import encoder


def main():
    app = Flask(__name__)
    app.json_encoder = encoder.JSONEncoder
    # app.json_decoder
    app.register_blueprint(user_api)
    app.register_blueprint(store_api)
    app.register_blueprint(pet_api)
    app.run(port=8080, debug=False)


if __name__ == '__main__':
    main()
