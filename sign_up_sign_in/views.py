from django.utils.timezone import now

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from app.models import User
from decorators import has_logged_in
from sign_up_sign_in._services import decrypt
from .serializers import UserSerializer
from ._services import get_token, get_refresh_access_tokens


@api_view(["POST"])
def sign_up(request):
    """
    Author : Pavan
    Params : request object
    Returns : returns user details
    Created On :
    """
    data = request.data
    try:
        serializer = UserSerializer(data=data)
    except Exception as e:
        return Response({"error", str(e)})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=200)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def user_login(request):
    """
    Author : Pavan
    Params : request object
    Returns : returns refresh and access tokens
    Created On :
    """
    data = request.data
    username = data.get("username", None)
    password = data.get("password", None)
    if username is None or password is None:
        return Response(
            {"error": "Both Username and Password is required"},
            status=status.HTTP_206_PARTIAL_CONTENT,
        )
    return get_refresh_access_tokens(username=username, password=password)


@api_view(["POST"])
def renew_refresh_token(request):

    refresh_token = request.data.get("token", None)
    refresh_token = str(refresh_token).strip()
    verified_token = decrypt(refresh_token)
    if "exception" not in verified_token.keys():
        access_token = get_token(verified_token["user_id"], minutes=30)
        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            status=status.HTTP_200_OK,
        )
    return Response(
        {
            "exception": verified_token["exception"],
        },
        status=500,
    )


@api_view(["GET"])
@has_logged_in
def get_user(request):
    """
    Author : Pavan
    Params : request object
    Returns : returns refresh and access tokens
    Created On : 21-11-2024
    """
    user = User.objects.get(user_id=request.user.user_id)
    serializer = UserSerializer(user)
    return Response({"user": serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@has_logged_in
def update_user(request):
    data = request.data
    data["date_updated"] = now()
    user = User.objects.filter(user_id=request.user.user_id).update(**data)
    user = User.objects.get(user_id=request.user.user_id)
    serializer = UserSerializer(user)
    return Response(
        {
            "user": serializer.data,
        },
        status=status.HTTP_200_OK,
    )
