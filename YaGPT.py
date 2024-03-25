import requests
import config
import telebot
bot = telebot.TeleBot(config.TOKEN)

def ask_gpt(text):
    folder_id = config.folder_id

    headers = {
        'Authorization': f'Bearer {create_new_token()}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": config.MAX_TOKENS
        },
        "messages": [
            {
                "role": "user",
                "text": text
            }
        ]
    }


    response = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                             headers=headers,
                             json=data)
    try:
        if response.status_code == 200:
            answer = response.json()["result"]["alternatives"][0]["message"]["text"]
            return answer
    except:
        raise RuntimeError(
            'Invalid response received: code: {}, message: {}'.format(
                    {response.status_code}, {response.text}
            )
        )

def count_tokens(prompt_or_answer):
    """
    ФУНКЦИЯ ДЛЯ ПОТЩЕТА ТОКЕНОВ ИСПОЛЬЗОВАННЫХ ПОЛЬЗОВАТЕЛЕМ
    """
    headers = {
        'Authorization': f'Bearer {create_new_token()}',
        'Content-Type': 'application/json'
    }
    data = {
       "modelUri": f"gpt://{config.folder_id}/yandexgpt/latest",
       "maxTokens": config.MAX_TOKENS,
       "text": prompt_or_answer
    }
    return len(
        requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
            json=data,
            headers=headers
        ).json()['tokens']
    )

def create_new_token():
    """Создание нового токена"""
    metadata_url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_url, headers=headers)
    token = response.json()["access_token"]
    return token

