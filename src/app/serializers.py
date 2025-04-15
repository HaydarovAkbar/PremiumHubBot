from rest_framework import serializers
from . import models


class TgUserSerializers(serializers.ModelSerializer):
    date_from = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    date_to = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    slug = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = models.TGUsers
        fields = ('id', 'date_from', 'date_to', 'slug',)
