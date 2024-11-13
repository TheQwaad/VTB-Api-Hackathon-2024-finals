from rest_framework import serializers
from datetime import datetime


# class KeysSoRsyaSerializer(serializers.Serializer):
#     hash = serializers.CharField(allow_null=True)
#     id = serializers.CharField(max_length=255)
#     title = serializers.CharField(max_length=255)
#     company_name = serializers.CharField(max_length=255, allow_blank=True)
#     second_title = serializers.CharField(max_length=255, allow_blank=True)
#     body = serializers.CharField(allow_blank=True)
#     files = serializers.ListField(child=serializers.CharField(), allow_empty=True)
#     target_url = serializers.CharField()
#     domain = serializers.CharField()
#     found_at = serializers.DateTimeField(input_formats=["%d.%m.%Y %H:%M"])
#     updated_at = serializers.DateTimeField(input_formats=["%d.%m.%Y %H:%M"])
#     region_name = serializers.CharField(max_length=255, allow_blank=True)
#     legal = serializers.CharField(max_length=255, allow_blank=True)
#
#     def get_rsya_ads_data(self, target_word: str) -> dict:
#         self.is_valid()
#         url = self.validated_data['target_url']
#         return {
#             'target_word': target_word,
#             'url': url,
#             'domain': UrlHelper(url).get_domain(),
#             'title': self.validated_data['title'],
#             'description': self.validated_data['body'],
#             'remote_id': self.validated_data['id'],
#             'founded_at': self.validated_data['found_at'],
#             'parsed_at': datetime.now(),
#         }
