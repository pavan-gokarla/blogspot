from datetime import datetime
import pytz
from rest_framework.response import Response
from rest_framework import status


from app.models import Comment


def update_comment(request, comment_id):
    """
    Author : Pavan
    Params : request object, comment_id
    Returns : return 1 object if comment exists else 0.
    Created On : 14-10-2024
    Updated On : 20-12-2024
    """
    data = request.data
    user = request.user.user_id
    comment = Comment.objects.get(comment_id=comment_id)
    editable = (
        (datetime.now(pytz.UTC) - comment.date_created).seconds < 300
        and request.user.user_id == comment.host.user_id,
    )

    if not editable[0]:
        return Response(
            {"error": "can't edit time limit exceeded"},
            status=status.HTTP_400_BAD_REQUEST,
        )
        comment = Comment.objects.filter(host=user, comment_id=comment_id).update(
            **data
        )
    return Response({"comments_updated": comment}, status=status.HTTP_200_OK)


def delete_comment(request, comment_id):
    """
    Author : Pavan
    Params : request object, comment_id
    Returns : return 1 object if comment exists else 0.
    Created On : 14-10-2024
    """
    data = request.data
    user = request.user.user_id
    comment = Comment.objects.filter(host=user, comment_id=comment_id).delete()
    return Response({"comments_deleted": comment}, status=status.HTTP_200_OK)
