import os
import openai
import requests
from flask import Flask, jsonify, request
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
from discord_interactions import verify_key_decorator
from decouple import config


# Retrieve keys from .env file
DISCORD_PUBLIC_KEY = config('DISCORD_PUBLIC_KEY')
openai.api_key = config('OPENAI_API_KEY')
BOT_APP_ID = config('BOT_APP_ID')

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)
handler = Mangum(asgi_app)


@app.route("/", methods=["POST"])
async def interactions():
    print(f"👉 Request: {request.json}")
    raw_request = request.json
    return interact(raw_request)

@verify_key_decorator(DISCORD_PUBLIC_KEY)
def interact(raw_request):
    interaction_token = raw_request["token"]

    if raw_request["type"] == 1:  # PING
        response_data = {"type": 1}  # PONG

    else:
        # Indicate that the bot is thinking...
        requests.post(
            f"https://discord.com/api/v8/interactions/{raw_request['id']}/{interaction_token}/callback",
            json={"type": 5}
        )

        data = raw_request["data"]
        command_name = data["name"]

        user_message = data["options"][0]["value"]
        roles_content = determine_roles_content(command_name, data)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                # "Your response should be within 50 words, " +
                {"role": "system", "content":  roles_content},
                {"role": "user", "content": user_message},
            ],
            max_tokens=666,
            # set the max number of tokens the API should return
        )

        message_content = response['choices'][0]['message']['content']
        print(f"🤖 Response: {message_content}")
        
        # Truncate the response if it's too long
        if len(message_content) > 3000:
            print(f"🤖 Response: {message_content}")
            message_content = "The response is too long. Due to Discord's character limit, the response has been truncated."

        # Edit the thinking message with the bot's response
        edit_url = f"https://discord.com/api/v8/webhooks/{BOT_APP_ID}/{interaction_token}/messages/@original"
        requests.patch(edit_url, json={"content": message_content})

        response_data = {}  # No further data needs to be returned since we've already responded via editing

    print(f"👉 Response: {response_data}")
    return jsonify(response_data)


def determine_roles_content(command_name, data):
    roles_content_map = {
        "chat": "",
        "chat_emo": "You will be provided with a message, and your task is to respond using emojis only.",
        "chat_multplechoice": "You will be provided with a multiple-choice problem, and your task is to only output the correct answer.",
        "chat_custom": data["options"][0]["value"]
    }
    return roles_content_map.get(command_name, "")


if __name__ == "__main__":
    app.run(debug=True)
