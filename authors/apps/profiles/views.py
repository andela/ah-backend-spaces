from rest_framework import status, serializers
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .renderers import ProfileJSONRenderer
from .serializers import ProfileSerializer, RetriveFollowersSerializer
from .exceptions import ProfileDoesNotExist


class ProfileRetrieveAPIView(RetrieveAPIView):
    """
    Class endpoint for retrivving an user profile
    """
    permission_classes = (AllowAny,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def retrieve(self, request, username, *args, **kwargs):
        """ function to retrieve a requested profile """
        try:
            profile = Profile.objects.select_related('user').get(
                user__username=username
            )
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        serializer = self.serializer_class(profile)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileFollowingAPIView(APIView):
    """
    class endpoint to follow and unfollow a person
    follower == person trying to follow someone
    followee == person being followed
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def post(self, request, username=None):
        follower = self.request.user.profile

        try:
            followee = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        if follower.pk is followee.pk:
            raise serializers.ValidationError('You can not follow yourself.')

        if follower.is_following(followee):
            raise serializers.ValidationError('Already following this user')

        follower.follow(followee)

        # increase the count of followers for the person being followed (followee)
        followee.followers = followee.followers + 1
        followee.save()
        # increase the count of following for the follower
        follower.following = follower.following + 1
        follower.save()

        serializer = self.serializer_class(followee, context={
            'request': request
        })

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, username=None):
        follower = self.request.user.profile

        try:
            followee = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        if not follower.is_following(followee):
            raise serializers.ValidationError("You do not follow this user")

        follower.unfollow(followee)

        # decrease the count of followers for the person being unfollowed (followee)
        followee.followers = followee.followers - 1
        followee.save()

        # decrease the count of following for the follower
        follower.following = follower.following - 1
        follower.save()

        serializer = self.serializer_class(followee, context={
            'request': request
        })

        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveFollowersAPIView(RetrieveAPIView):
    """
    Authenticate a user.
    Get their profile. Check what people are following this user
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = RetriveFollowersSerializer

    def retrieve(self, request, username, *args, **kwargs):
        list_of_followers = []

        try:
            profile = Profile.objects.select_related('user').get(
                user__username=username
            )
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        user_followers = Profile.follows.through.objects.filter(
            to_profile_id=profile.id)
        for a_follower in user_followers:
            list_of_followers.append(
                str(Profile.objects.get(id=a_follower.from_profile_id)))
        res = {
            "followers": list_of_followers
        }
        return Response(res, status=status.HTTP_200_OK)
