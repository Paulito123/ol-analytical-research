import os
import pathlib


class Config(object):
    PYTHONPATH = os.getenv("PYTHONPATH", f"{pathlib.Path(__file__).parent.resolve()}".replace('/tokenomics', ''))
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://ol_intel:ol_intel@localhost:6543/viz_dev")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


if __name__ == "__main__":
    # print(pathlib.Path(__file__).parent.resolve())
    ...
