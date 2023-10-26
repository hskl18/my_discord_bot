import sys
sys.path.append('/var/task')
# to ensure that the lambda function can find the modules

import os
import requests

from flask import Flask, jsonify, request
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
from discord_interactions import verify_key_decorator

from decouple import config
# Retrieve keys from .env file
DISCORD_PUBLIC_KEY = config('DISCORD_PUBLIC_KEY')
BOT_APP_ID = config('BOT_APP_ID')
BOT_TOKEN = config('BOT_TOKEN')

# declare the GPT handler
from gpt_handler import GPT
from image_handler import IMAGE

# declare the Flask app & Mangum handler
app = Flask(__name__)
asgi_app = WsgiToAsgi(app)
handler = Mangum(asgi_app)

# declare the Discord bot
@app.route("/", methods=["POST"])
async def interactions():
    print(f"👉 Request: {request.json}")
    raw_request = request.json
    return interact(raw_request)

@verify_key_decorator(DISCORD_PUBLIC_KEY)
def interact(raw_request):
    interaction_token = raw_request["token"] # Used to edit the bot's response later

    # to keep bot alive
    if raw_request["type"] == 1:  # PING
        response_data = {"type": 1}  # PONG

    else:
        # Indicate that the bot is thinking... to eliminate the "This interaction failed" error
        requests.post(
            f"https://discord.com/api/v8/interactions/{raw_request['id']}/{interaction_token}/callback",
            json={"type": 5}
        )

        data = raw_request["data"]
        command_name = data["name"]

        # Determine the user's message
        if command_name == "chat_custom":
            user_message = data["options"][1]["value"]
        else:
            user_message = data["options"][0]["value"]

        if command_name == "image":
            response_data = IMAGE(data, user_message, interaction_token)
        else:
            response_data = GPT(data, command_name, user_message, interaction_token)

    print(f"👉 Response: {response_data}")
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True)