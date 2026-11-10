import re
from rest_framework.serializers import ValidationError

class YoutubeOnlyValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        url = value.get(self.field)
        if not url:
            return


        if "youtube.com" not in url and "youtu.be" not in url:
            raise ValidationError({self.field: "Разрешены ссылки исключительно на ресурсы youtube.com"})
