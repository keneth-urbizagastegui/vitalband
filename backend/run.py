from app import create_app, Config

app = create_app(Config)

if __name__ == "__main__":
    # Permite `python run.py`
    app.run(host="127.0.0.1", port=5000)