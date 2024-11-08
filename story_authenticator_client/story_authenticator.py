from yandex_gpt_helper import YandexGptHelper, YandexGptModels
import asyncio
import os
import random

STORY_GENERATOR_PROMPT = open("prompts/story_generator.dat")
STORY_GENERATOR_TEMPERATURE = 0.6
STORY_GENERATOR_MAX_TOKEN = 300

OBJECTS_GETTER_PROMPT = open("prompts/objects_getter.dat")
OBJECTS_GETTER_TEMPERATURE = 0.6
OBJECTS_GETTER_MAX_TOKEN = 100

FAKE_OBJECTS_GETTER_PROMPT = open("prompts/fake_objects_getter.dat")
FAKE_OBJECTS_GETTER_TEMPERATURE = 0.6
FAKE_OBJECTS_GETTER_MAX_TOKEN = 100
FAKE_OBJECTS_COUNT = 9 # must be the same as in the prompt

AUTH_ITERATIONS = 3 # must be not larger than the number of objects in story generator prompt

VALIDATE_OBJECT_PROMPT = open("prompts/validate_object.dat")
VALIDATE_OBJECT_TEMPERATURE = 0.6
VALIDATE_OBJECT_MAX_TOKEN = 30
VALIDATION_RESPONSE = {
    "success": ['да'],
    "fail": ['нет']
}

class StoryAuthenticator:

    def __init__(self):
        self._model = YandexGptHelper(
            os.getenv('YANDEX_API_DIRECTORY'),
            os.getenv('YANDEX_API_KEY'),
            model=YandexGptModels.PRO
        )
        self._story = None
        self._objects = None
        self._last_used = None

    async def generate_story(self):
        self._objects = None
        self._last_used = None
        self._story = asyncio.run(self._model.make_message_request(
            STORY_GENERATOR_PROMPT,
            temperature=STORY_GENERATOR_TEMPERATURE,
            max_token=STORY_GENERATOR_MAX_TOKEN
        ))

    async def _update_objects(self):
        if self._story is None:
            raise ValueError("Story is not yet generated.")
        while self._objects is None:
            prompt = f"{OBJECTS_GETTER_TEMPERATURE}\n{self._story}"
            objects_text = asyncio.run(self._model.make_message_request(
                prompt,
                temperature=OBJECTS_GETTER_TEMPERATURE,
                max_token=OBJECTS_GETTER_MAX_TOKEN
            ))
            self._objects = objects_text.split(", ")
            if len(self._objects) == 1:
                self._objects = None
            random.shuffle(self._objects)

    async def _get_fake_objects(self):
        fake_objects = None
        while fake_objects is None:
            fake_objects_text = asyncio.run(self._model.make_message_request(
                FAKE_OBJECTS_GETTER_PROMPT,
                FAKE_OBJECTS_GETTER_TEMPERATURE,
                FAKE_OBJECTS_GETTER_MAX_TOKEN
            ))
            fake_objects = fake_objects_text.split(", ")
            if len(fake_objects) < FAKE_OBJECTS_COUNT:
                fake_objects = None
        return fake_objects

    async def get_objects_for_auth(self):
        if self._objects is None:
            try:
                asyncio.run(self._update_objects())
            except Exception as e:
                raise e
        if self._last_used is None:
            self._last_used = -1
        self._last_used += 1
        fake_objects = asyncio.run(self._get_fake_objects())
        fake_objects.append(self._objects[self._last_used])
        return fake_objects

    async def validate_object(self, object):
        prompt = f"{VALIDATE_OBJECT_TEMPERATURE}\nОбъект: {object}\nИстория: {self._story}"
        response = asyncio.run(self._model.make_message_request(
            prompt,
            temperature=VALIDATE_OBJECT_TEMPERATURE,
            max_token=VALIDATE_OBJECT_MAX_TOKEN
        ))
        return response in VALIDATION_RESPONSE['success']


