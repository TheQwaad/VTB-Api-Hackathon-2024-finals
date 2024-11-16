class StoryAuthService:
    __incorrect_options = ['1', '2', 'correct']
    __correct_options = ['1afdfa', '2_ssd', 'incorrect']
    __story = 'Test stoory kdjdjopwsfk'

    def __init__(self):
        pass

    def gen_story(self):
        # todo: Kirill do stuff here
        pass

    def get_story(self) -> str:
        return self.__story

    def get_correct_option(self) -> list[str]:
        return self.__correct_options

    def get_incorrect_option(self) -> list[str]:
        return self.__incorrect_options
