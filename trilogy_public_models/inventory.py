from os import listdir
from os.path import dirname, join

from preql import Environment
from preql.constants import ENV_CACHE_NAME
from preql.parser import parse


def parse_initial_models(fpath: str) -> Environment:
    parent_folder = dirname(fpath)
    files = listdir(dirname(fpath))
    cache_path = join(parent_folder, ENV_CACHE_NAME)
    for file in files:
        if file == ENV_CACHE_NAME:
            env = Environment.from_cache(join(parent_folder, file))
            if env:
                return env
    for file in files:
        if file.endswith("entrypoint.preql"):
            with open(join(parent_folder, file), "r", encoding="utf-8") as f:
                contents = f.read()
                env = Environment(working_path=parent_folder)
                environment, statements = parse(contents, environment=env)
                env.to_cache(cache_path)
                return environment
    raise ValueError("Missing entrypoint.preql")
