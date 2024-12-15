#!/usr/bin/env python
# Author:  Mario S. Könz <mskoenz@gmx.net>
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring


import os
import subprocess
import time
from pathlib import Path


def main():
    env = dict(timeout=60, filename=Path(__file__).name)
    env.update(os.environ)

    if "POSTGRES_USER_FILE" in env:
        with Path(env["POSTGRES_USER_FILE"]).open("r", encoding="utf-8") as f:
            env["POSTGRES_USER"] = f.readline().strip()

    cmd = "pg_isready -q --username={POSTGRES_USER} --host={POSTGRES_HOST} --port={POSTGRES_PORT}"
    cmd = cmd.format_map(env).split(" ")

    start = time.time()
    msg = "{filename}: waiting {timeout} seconds for {POSTGRES_HOST}:{POSTGRES_PORT}"
    print(msg.format_map(env))
    while True:
        res = subprocess.run(cmd, check=False)  # dont raise from exit!=0
        if res.returncode == 0:
            msg = "{filename}: {POSTGRES_HOST}:{POSTGRES_PORT} is ready"
            print(msg.format_map(env))
            return
        if time.time() - start > env["timeout"]:
            msg = "{filename}: {POSTGRES_HOST}:{POSTGRES_PORT} was not ready within {timeout}"
            raise TimeoutError(msg.format_map(env))
        time.sleep(1)


if __name__ == "__main__":
    main()
