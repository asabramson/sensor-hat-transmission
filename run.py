from app import create_app, db
from config import Config

app = create_app(Config)

@app.before_request
def initDB(*args, **kwargs):
    if app._got_first_request:
        db.create_all()

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)