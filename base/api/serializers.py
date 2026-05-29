from rest_framework.serializers import ModelSerializer
from base.models import Room, Message, Topic


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'