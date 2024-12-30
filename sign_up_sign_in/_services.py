import datetime
import jwt


from rest_framework.response import Response
from rest_framework import status
from app.models import User
from blogspot.settings import SECRET_KEY

SECRET_KEY = SECRET_KEY[15:]


def get_token(username, minutes):
    """
    Author : Pavan
    Params : username, minutes(expiration time of the token)
    Returns : Token generated using HS256 hashing algorithm
    Created : 10-Oct-2024
    """
    payload = {
        "user_id": username,
        "exp": datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(minutes=minutes),
        "iat": datetime.datetime.now(tz=datetime.timezone.utc),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def get_refresh_access_tokens(username, password):
    """
    Author: Pavan
    params : Username, Password,
    returns : Access_token, Refresh Token
    Created_date : 9-Oct-2024
    """
    if is_valid_user(username, password):
        return Response(
            {
                "token": {
                    "access_token": get_token(username=username, minutes=30),
                    "refresh_token": get_token(username=username, minutes=180),
                }
            },
            status=status.HTTP_200_OK,
        )
    else:

        return Response(
            {"error": "username or password is invalid"},
            status=status.HTTP_400_BAD_REQUEST,
        )


def is_valid_user(username, password) -> bool:
    """
    Author : Pavan
    Params : username, Password
    Returns : True if the User is valid or else False
    Created : 10-Oct-2024
    """
    return User.objects.filter(username=username, password=password).count() == 1


def decrypt(token):
    """
    Author : Pavan
    Params : Token
    Returns : Decrypted token if valid or else returns the description of the exception
    Created : 10-Oct-2024
    """
    try:

        verify_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return verify_token
    except Exception as e:

        return {"exception": str(e)}
