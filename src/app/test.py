import pytest
from unittest.mock import patch
import json
from main import app, interact
from gpt_handler import GPT
from image_handler import IMAGE

app.testing = True

@patch("gpt_handler.requests.patch")
def test_image(mock_requests):
    user_message = "A sunset over a mountain"
    interaction_token = "test_token"
    data = {}

    mock_openai_response = {
        "data": [{"url": "https://image_url.com"}]
    }

    with patch("gpt_handler.openai.Image.create", return_value=mock_openai_response):
        result = IMAGE(data, user_message, interaction_token)
        assert result == {}
        mock_requests.assert_called_once()

@patch("gpt_handler.requests.patch")
def test_gpt(mock_requests):
    user_message = "Tell me a joke"
    command_name = "chat"
    interaction_token = "test_token"
    data = {
        "options": [{"value": "Some Value"}]
    }

    mock_openai_response = {
        "choices": [{"message": {"content": "Why did the chicken cross the road?"}}],
        "usage": {
            "total_tokens": 50,
            "prompt_tokens": 10,
            "completion_tokens": 40,
            "total_completions": 1
        }
    }


    with patch("gpt_handler.openai.ChatCompletion.create", return_value=mock_openai_response):
        result = GPT(data, command_name, user_message, interaction_token)
        assert result == {}
        mock_requests.assert_called_once()
        call_args = mock_requests.call_args[1]
        assert call_args['json']['content'].startswith("Why did the chicken cross the road?")


def test_roles_content():
    from gpt_handler import determine_roles_content
    data = {"options": [{"value": "custom_content"}]}
    
    assert determine_roles_content("chat", data) == ""
    assert determine_roles_content("chat_emo", data) == "You will be provided with a message, and your task is to respond using emojis only."
    assert determine_roles_content("chat_multplechoice", data) == "You will be provided with a multiple-choice problem, and your task is to only output the correct answer."
    assert determine_roles_content("chat_custom", data) == "custom_content"

if __name__ == "__main__":
    pytest.main([__file__])