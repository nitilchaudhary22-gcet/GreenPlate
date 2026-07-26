from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    @app.route("/")
    def home():
        return render_template("index.html")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()