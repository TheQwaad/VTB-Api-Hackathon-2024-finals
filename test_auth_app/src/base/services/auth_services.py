from story_authenticator.story_authenticator import StoryAuthenticator
from base.services.config_reader import config
import os

class StoryAuthService:
    __incorrect_options = None
    __correct_options = None
    __story = None


    def __init__(self):
        self.__authenticator = StoryAuthenticator(config.yadir_key, config.yaapi_key)

    def gen_story(self):
        self.__authenticator.generate_story()
        self.__story = self.__authenticator.get_story()
        self.__correct_options = self.__authenticator.get_objects()
        self.__incorrect_options = self.__authenticator.get_fake_objects()

    def get_story(self) -> str:
        if self.__story is None:
            self.gen_story()
        return self.__story

    def get_correct_option(self) -> list[str]:
        return self.__correct_options

    def get_incorrect_option(self) -> list[str]:
        return self.__incorrect_options
