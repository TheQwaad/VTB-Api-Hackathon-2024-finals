import aiohttp


CLOUD_API_URL = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'

class YandexGptModels:
    LITE3="yandexgpt-lite/latest"
    PRO3="yandexgpt/latest"
    PRO4="yandexgpt/rc"

YANDEX_GPT_MODELS = {YandexGptModels.LITE3, YandexGptModels.PRO3, YandexGptModels.PRO4}


class YandexGptHelper:
    def __init__(self, directory, api_token=None, iam_token=None, model=YandexGptModels.LITE3):
        self.directory = directory
        if api_token is not None and iam_token is not None:
            raise ValueError("Choose only one token")
        if api_token is None and iam_token is None:
            raise ValueError("Choose either api_token or iam_token")
        if model not in YANDEX_GPT_MODELS:
            raise ValueError("Choose a valid model")
        self.api_token = api_token
        self.iam_token = iam_token
        self.modelUri = f"gpt://{self.directory}/{model}"

    def _make_request_headers(self):
        if self.iam_token is not None:
            return {"Accept": "application/json", "Authorization": f"Bearer {self.iam_token}"}
        elif self.api_token is not None:
            return {"Accept": "application/json", "Authorization": f"Api-Key {self.api_token}"}

    def _make_request_data(self, messages, stream=False, temperature=0.5, max_token='100'):
        data = {
            'modelUri': self.modelUri,
            'completionOptions': {"stream": stream, "temperature": temperature, 'maxToken': max_token},
            'messages': messages
        }
        return data

    async def make_request(self, messages=None, stream=False, temperature=0.5, max_token='100'):
        if messages is None:
            raise AttributeError("Choose at least one message")
        headers = self._make_request_headers()
        data = self._make_request_data(messages, stream, temperature, max_token)
        async with aiohttp.ClientSession() as session:
            async with session.post(CLOUD_API_URL, json=data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data['result']['alternatives'][0]['message']
                else:
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message=f"Unexpected status: {response.status}"
                    )

    async def make_message_request(self, text, role='system', stream=False, temperature=0.5, max_token='100'):
        response_data = await self.make_request(messages=[{'role':role, 'text':text}], stream=stream,
                                                temperature=temperature, max_token=str(max_token))
        return response_data['text']