# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    # bind to 0.0.0.0 so localhost works inside containers too
    app.run(host='0.0.0.0', port=5000, debug=True)
