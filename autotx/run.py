from autotx.config import Config
from os import popen as opopen
from autotx.config import Config


def example_fund():
    command_string = f"{Config.FUNDME_FILEPATH} {Config.SEND_TO_ADDRESS} \"{Config.MNEM}\""
    stdout = opopen(command_string,'w')
    print(stdout)
    stdout.close()


def example_onboard():
    command_string = f"{Config.ONBOARD_FILEPATH} {Config.NEW_ACCOUNT_AUTH} \"{Config.MNEM}\""
    stdout = opopen(command_string,'w')
    print(stdout)
    stdout.close()


if __name__ == "__main__":
    print("Onboarding...")
    example_onboard()
    print("Funding...")
    example_fund()
