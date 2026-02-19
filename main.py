from flask.cli import load_dotenv

from pipeline import run_all

if __name__ == "__main__":
    load_dotenv()
    run_all()
