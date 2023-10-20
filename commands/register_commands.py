import requests
import yaml
from decouple import config

TOKEN = config('BOT_TOKEN')
APPLICATION_ID = config('BOT_APP_ID')
URL = f"https://discord.com/api/v9/applications/{APPLICATION_ID}/commands"

headers = {
    "Authorization": f"Bot {TOKEN}",
    "Content-Type": "application/json"
}

# Delete all existing commands first
responseGet = requests.get(URL, headers=headers)

if responseGet.status_code == 200:
    existing_commands = responseGet.json()
    for cmd in existing_commands:
        cmd_id = cmd["id"]
        delete_url = f"{URL}/{cmd_id}"
        del_response = requests.delete(delete_url, headers=headers)
        if del_response.status_code == 204:
            print(f"Command {cmd['name']} deleted successfully!")
        else:
            print(f"Failed to delete command {cmd['name']}. Status code: {del_response.status_code}")
else:
    print(f"Failed to fetch existing commands. Status code: {responseGet.status_code}")
    
# Read the commands from the YAML file
with open("discord_commands.yaml", "r") as file:
    yaml_content = file.read()

commands = yaml.safe_load(yaml_content)
headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}

# Send the POST request for each command
for command in commands:
    response = requests.post(URL, json=command, headers=headers)
    command_name = command["name"]
    print(f"Command {command_name} created: {response.status_code}")