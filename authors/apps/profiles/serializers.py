from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True, required=False)
    image = serializers.SerializerMethodField()
    followers = serializers.IntegerField(min_value=0)
    following = serializers.IntegerField(min_value=0)

    class Meta:
        model = Profile
        fields = ('username', 'bio', 'image', 'followers', 'following')
        read_only_fields = ('username',)

    def get_image(self, obj):
        if obj.image:
            return obj.image

        return ''


class RetriveFollowersSerializer(serializers.ModelSerializer):
    pass
