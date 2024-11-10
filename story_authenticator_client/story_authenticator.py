from yandex_gpt_helper import YandexGptHelper, YandexGptModels
import os
import random

def _load(path):
    return open(path, "r", encoding="UTF-8").read().strip()

STORY_GENERATOR_PROMPT = _load("prompts/story_generator.dat")
STORY_GENERATOR_TEMPERATURE = 0.6
STORY_GENERATOR_MAX_TOKEN = 300

OBJECTS_GETTER_PROMPT = _load("prompts/objects_getter.dat")
OBJECTS_GETTER_TEMPERATURE = 0.6
OBJECTS_GETTER_MAX_TOKEN = 100

FAKE_OBJECTS_GETTER_PROMPT = _load("prompts/fake_objects_getter.dat")
FAKE_OBJECTS_GETTER_TEMPERATURE = 0.6
FAKE_OBJECTS_GETTER_MAX_TOKEN = 50
FAKE_OBJECTS_COUNT = 9 # must be the same as in the prompt

AUTH_ITERATIONS = 3 # must be not larger than the number of objects in story generator prompt

VALIDATE_OBJECT_PROMPT = _load("prompts/validate_object.dat")
VALIDATE_OBJECT_TEMPERATURE = 0.6
VALIDATE_OBJECT_MAX_TOKEN = 10
VALIDATION_RESPONSE = {
    "success": ['да'],
    "fail": ['нет']
}

class StoryAuthenticator:

    def __init__(self, api_id, api_token):
        self._model = YandexGptHelper(
            api_id,
            api_token=api_token,
            model=YandexGptModels.PRO4
        )
        self._story = None
        self._objects = None

    async def generate_story(self):
        self._objects = None
        self._story = await self._model.make_message_request(
            STORY_GENERATOR_PROMPT,
            temperature=STORY_GENERATOR_TEMPERATURE,
            max_token=STORY_GENERATOR_MAX_TOKEN
        )
    async def _update_objects(self):
        if self._story is None:
            raise ValueError("Story is not yet generated.")
        while self._objects is None:
            prompt = f"{OBJECTS_GETTER_PROMPT}\n{self._story}"
            objects_text = await self._model.make_message_request(
                prompt,
                temperature=OBJECTS_GETTER_TEMPERATURE,
                max_token=OBJECTS_GETTER_MAX_TOKEN
            )
            self._objects = objects_text.split(", ")
        random.shuffle(self._objects)

    async def get_fake_objects(self):
        fake_objects = None
        while fake_objects is None:
            fake_objects_text = await self._model.make_message_request(
                FAKE_OBJECTS_GETTER_PROMPT,
                temperature=FAKE_OBJECTS_GETTER_TEMPERATURE,
                max_token=FAKE_OBJECTS_GETTER_MAX_TOKEN
            )
            fake_objects = fake_objects_text.split(", ")
            if len(fake_objects) < FAKE_OBJECTS_COUNT:
                fake_objects = None
        return fake_objects

    async def get_auth_objects(self):
        if self._objects is None:
            try:
                await self._update_objects()
            except Exception as e:
                raise e
        fake_objects = await self.get_fake_objects()
        random.shuffle(self._objects)
        fake_objects.append(self._objects[0])
        random.shuffle(fake_objects)
        return fake_objects

    async def validate_object(self, obj):
        if self._objects is None:
            await self._update_objects()

        return obj in self._objects

    def get_story(self):
        return self._story
