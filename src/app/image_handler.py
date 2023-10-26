import openai
import requests
from decouple import config

openai.api_key = config('OPENAI_API_KEY')
BOT_APP_ID = config('BOT_APP_ID')

def IMAGE(data, user_message, interaction_token):
    response = openai.Image.create(
        prompt=user_message,
        size="1024x1024"
    )
    
    print(response)
    image_url = response['data'][0]['url']
    print(image_url)

    edit_url = f"https://discord.com/api/v8/webhooks/{BOT_APP_ID}/{interaction_token}/messages/@original"
    requests.patch(edit_url, json={"content": image_url})

    return {}  # No further data needs to be returned since we've already responded via editing