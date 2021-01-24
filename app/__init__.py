import dash
from flask import Flask
from flask.helpers import get_root_path

from config import BaseConfig


def create_app():
    server = Flask(__name__)
    server.config.from_object(BaseConfig)

    register_dashapps(server)
    register_blueprints(server)

    return server

external_stylesheets = ['https://gist.githubusercontent.com/dclliu/ea4755af8d5f3bae9456757d23e4d93b/raw/059d2f5db0129b662b05666c5a680c4b28560241/style.css', 'https://codepen.io/chriddyp/pen/brPBPO.css', '/static/style.css']

def register_dashapps(app):
    from app.dashapp1.layout import layout
    from app.dashapp1.callbacks import register_callbacks

    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    dashapp1 = dash.Dash(__name__,
                         server=app,
                         url_base_pathname='/dashboard/',
                         assets_folder=get_root_path(__name__) + '/dashboard/assets/',
                         meta_tags=[meta_viewport],
                         external_stylesheets=external_stylesheets)

    with app.app_context():
        dashapp1.title = 'Pictojams'
        dashapp1.layout = layout
        register_callbacks(dashapp1)

def register_blueprints(server):
    from app.webapp import server_bp

    server.register_blueprint(server_bp)
