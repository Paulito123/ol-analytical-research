import os


class Config:
    # PROJECT_PATH = os.path.abspath(os.getcwd())
    PROJECT_DIR = "/home/user/projects/ol-analytical-research"
    CONTRIBUTORS_FILEPATH = f"{PROJECT_DIR}/assets/contributors.json"
    PAYMENTS_DIR = f"{PROJECT_DIR}/assets/generated/payments"
    PAYMENT_ROUND = "PR20221001_002"
    START_BLOCK = 70340592
    END_BLOCK = 70500000

# print(Config.PROJECT_PATH)
