from functools import wraps

from rest_framework import status
from rest_framework.response import Response

from blogspot.settings import SECRET_KEY

SECRET_KEY = SECRET_KEY[15:]


def has_logged_in(fun):
    @wraps(fun)
    def wrapper(request, *args, **kwargs):
        try:
            token = request.headers["Authorization"].split(" ")[1]
        except Exception as e:

            return Response(str(e), status=status.HTTP_401_UNAUTHORIZED)
        from sign_up_sign_in._services import decrypt

        verified_token = decrypt(token=token)

        if "user_id" in verified_token.keys():

            from app.models import User

            request.user = User.objects.get(username=verified_token["user_id"])
        # print(request.user)
        else:
            return Response(verified_token, status=status.HTTP_401_UNAUTHORIZED)
        return fun(request, *args, **kwargs)

    return wrapper
