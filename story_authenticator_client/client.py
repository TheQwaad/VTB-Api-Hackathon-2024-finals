from story_authenticator import StoryAuthenticator, AUTH_ITERATIONS

REQUIRED_ITERATIONS = 2 #must be not larger than auth iterations

class AuthSession:
    def __init__(self, api_id, api_token):
        self.authenticator = StoryAuthenticator(api_id, api_token)
        self.started = False
        self.opened = False
        self.validation_end = False
        self.failed = False
        self.last = 0
        self.success = 0

    async def start(self):
        if not self.started and not self.validation_end:
            self.started = True
            response = await self.authenticator.get_story()
            return response
        return None

    async def get_objects(self):
        if not self.opened:
            self.opened = True
            response = await self.authenticator.get_auth_objects()
            return response
        return None

    async def validate_object(self, obj):
        if not self.opened:
            return None
        if self.authenticator.validate_object(obj):
            self.success += 1
        self.last += 1
        if self.last == AUTH_ITERATIONS:
            self.failed = (self.success >= REQUIRED_ITERATIONS)
            self.validation_end = True
            self.opened = False
        await self.authenticator.generate_story()


    async def get_status(self):
        if self.failed:
            return 403
        if not self.failed and not self.validation_end:
            return 206
        if self.validation_end:
            return 200