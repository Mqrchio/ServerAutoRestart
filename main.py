import asyncio
import os
from typing import Union

import yaml
import schedule

RESOURCES_FOLDER_PATH = os.path.join(os.getcwd(), "resources")
CONFIG_PATH = os.path.join(RESOURCES_FOLDER_PATH, "config.yml")
DEFAULT_CONFIG = {
    'timezone': 'Europe/Rome',
    'servers': {
        'kitpvp-op': {
            'path': 'path/to/start.sh',
            'screen-name': 'kitpvp-op',
            'time-to-restart': '03:00'
        },
        'lifesteal': {
            'path': 'path/to/start.sh',
            'screen-name': 'lifesteal',
            'time-to-restart': '03:00'
        }
    }
}


def get_config() -> dict:
    """Getter for config.yml"""
    try:
        with open(CONFIG_PATH, 'r') as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        os.makedirs(RESOURCES_FOLDER_PATH, exist_ok=True)
        with open(CONFIG_PATH, 'w') as file:
            yaml.dump(DEFAULT_CONFIG, file)
            data = DEFAULT_CONFIG

    return data


async def restart_server(path_sh: str, name: str) -> None:
    """Restart screen session with dispatch command"""
    current_dir = os.getcwd()
    next_dir = os.path.dirname(path_sh)
    file_sh = os.path.basename(path_sh)

    os.chdir(next_dir)

    os.system(f"screen -X -S {name} quit")
    os.system(f"screen -dmS {name} bash -c {file_sh}")

    os.chdir(current_dir)


async def keep_informed():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


if __name__ == '__main__':
    config = get_config()

    try:
        servers = dict(config.pop("servers"))
    except ValueError:
        raise ValueError("Il parametro \"server\" deve essere un dizionario")

    try:
        timezone = str(config.pop("timezone"))
    except ValueError:
        raise ValueError("Il parametro \"timezone\" deve essere una stringa")

    for key in servers.keys():
        try:
            path = str(servers[key]['path'])
            screen_name = str(servers[key]['screen-name'])
            time_to_restart = str(servers[key]['time-to-restart'])

        except Union[KeyError, ValueError]:
            raise Exception(f"I parametri per il server {key} non sono definiti correttamente")

        async def restart_server_callback():
            await restart_server(path, screen_name)

        schedule.every().day.at(time_to_restart).do(restart_server_callback)

    asyncio.run(keep_informed())