import asyncio
import os
from typing import Union

import yaml
import schedule

RESOURCES_FOLDER_PATH = os.path.join(os.getcwd(), "resources")
CONFIG_PATH = os.path.join(RESOURCES_FOLDER_PATH, "config.yml")
DEFAULT_CONFIG = {
    'timezone': 'Europe/Rome',
    'screen': {
        'delete': "screen -X -S \"<name>\" quit",
        'create': "screen -dmS \"<name>\" bash -c <file>"
    },
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
VERSION = "0.0.1"


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


def restart_server(path_sh: str, name: str, delete_command: str, create_command: str) -> None:
    """Restart screen session with dispatch command"""
    current_dir = os.getcwd()
    next_dir = os.path.dirname(path_sh)
    file_sh = os.path.basename(path_sh)

    os.chdir(next_dir)

    os.system(
        delete_command
        .replace("<name>", name)
    )
    os.system(
        create_command
        .replace("<name>", name)
        .replace("<file>", file_sh)
    )

    os.chdir(current_dir)


async def keep_informed():
    """Check all scheduled tasks and run it"""
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


if __name__ == '__main__':
    print(f"Avvio ServerAutoRestart [{VERSION}]")

    config = get_config()

    try:
        servers = dict(config.pop("servers"))
    except ValueError:
        raise ValueError("Il parametro \"server\" deve essere un dizionario")

    try:
        timezone = str(config.pop("timezone"))
    except ValueError:
        raise ValueError("Il parametro \"timezone\" deve essere una stringa")

    try:
        screen = dict(config.pop("screen"))
        screen_command_delete = str(screen['delete'])
        screen_command_create = str(screen['create'])
    except Union[KeyError, ValueError]:
        raise Exception(f"I parametri per lo screen non sono definiti correttamente")
    print("File di configurazione importato con successo")

    for key in servers.keys():
        try:
            path = str(servers[key]['path'])
            screen_name = str(servers[key]['screen-name'])
            time_to_restart = str(servers[key]['time-to-restart'])

        except Union[KeyError, ValueError]:
            raise Exception(f"I parametri per il server {key} non sono definiti correttamente")
        finally:
            print(f"Server: {key} Stato: OK")


        def restart_server_callback():
            restart_server(path, screen_name, screen_command_delete, screen_command_create)
            print(f"Server {key} ricaricato con successo")

        schedule.every().day.at(time_to_restart).do(restart_server_callback)

    asyncio.run(keep_informed())
