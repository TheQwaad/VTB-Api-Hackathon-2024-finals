from story_authenticator.story_authenticator import StoryAuthenticator
import os

class StoryAuthService:
    __incorrect_options = None
    __correct_options = None
    __story = None


    def __init__(self):
        self.__authenticator = StoryAuthenticator(os.getenv("YAGPT_DIRECTORY_ID"), os.getenv("YAGPT_API_TOKEN"))

    async def gen_story(self):
        await self.__authenticator.generate_story()
        self.__story = await self.__authenticator.get_story()
        self.__correct_options = await self.__authenticator.get_objects()
        self.__incorrect_options = await self.__authenticator.get_fake_objects()

    async def get_story(self) -> str:
        return self.__story

    async def get_correct_option(self) -> list[str]:
        return self.__correct_options

    async def get_incorrect_option(self) -> list[str]:
        return self.__incorrect_options
