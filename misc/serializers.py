#NOTIFICATION SERIALIZER
from rest_framework import serializers
from notifications.models import Notification
class NotificationSerializer(serializers.ModelSerializer):

    is_seen = serializers.SerializerMethodField()
    meta_data = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "verb",
            "is_seen",
            "meta_data"
        ]

    def get_is_seen(self, obj):
        c= not obj.unread
        obj.unread = False
        obj.save()

        return c

    def get_meta_data(self, obj):

        data = obj.data
        return data


