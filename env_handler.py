import os


def handler():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    with open(env_path, 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            os.environ[key] = value
