from story_authenticator.yandex_gpt_helper import YandexGptHelper, YandexGptModels
from story_authenticator.prompts import *
import os
import random

class StoryAuthenticator:

    def __init__(self, api_id, api_token):
        self._model = YandexGptHelper(
            api_id,
            api_token=api_token,
            model=YandexGptModels.PRO4
        )
        self._story = None
        self._objects = None

    def generate_story(self):
        self._objects = None
        self._story = self._model.make_message_request(
            STORY_GENERATOR_PROMPT,
            temperature=STORY_GENERATOR_TEMPERATURE,
            max_token=STORY_GENERATOR_MAX_TOKEN
        )
    def _update_objects(self):
        if self._story is None:
            raise ValueError("Story is not yet generated.")
        while self._objects is None:
            prompt = f"{OBJECTS_GETTER_PROMPT}\n{self._story}"
            objects_text = self._model.make_message_request(
                prompt,
                temperature=OBJECTS_GETTER_TEMPERATURE,
                max_token=OBJECTS_GETTER_MAX_TOKEN
            )
            self._objects = objects_text.split(", ")
        random.shuffle(self._objects)

    def get_fake_objects(self):
        fake_objects = None
        while fake_objects is None:
            fake_objects_text = self._model.make_message_request(
                FAKE_OBJECTS_GETTER_PROMPT,
                temperature=FAKE_OBJECTS_GETTER_TEMPERATURE,
                max_token=FAKE_OBJECTS_GETTER_MAX_TOKEN
            )
            fake_objects = fake_objects_text.split(", ")
            if len(fake_objects) < FAKE_OBJECTS_COUNT:
                fake_objects = None
        return fake_objects

    def get_objects(self):
        self._update_objects()
        return self._objects

    def get_auth_objects(self):
        if self._objects is None:
            try:
                 self._update_objects()
            except Exception as e:
                raise e
        fake_objects =  self.get_fake_objects()
        random.shuffle(self._objects)
        fake_objects.append(self._objects[0])
        random.shuffle(fake_objects)
        return fake_objects

    def validate_object(self, obj):
        if self._objects is None:
             self._update_objects()

        return obj in self._objects

    def get_story(self):
        return self._story
