from flask import Flask, render_template, send_from_directory
import os

from src.router.api_gateway.endpoints import app as api_app

app = Flask(__name__,
            template_folder='../view/web/templates',
            static_folder='../view/web/static')

app.register_blueprint(api_app, url_prefix='')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)