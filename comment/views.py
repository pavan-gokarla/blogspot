import pytz
from datetime import datetime
from django.core.paginator import Paginator

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


from .services import update_comment, delete_comment
from .serializers import CommentSerializer
from decorators import has_logged_in
from app.models import Comment


@api_view(["GET"])
@has_logged_in
def fetch_comments(request, blog_id):
    """
    Author : Pavan
    Params : request object, blog_id
    Returns : returns comments of the blog if exists
    Created On : 17-10-2024
    """
    parent = request.GET.get("parent_comment", None)
    comments = Comment.objects.filter(blog_id=blog_id, parent=parent)
    comments = comments.order_by("-date_created")
    per_page = request.GET.get("per_page", 3)
    page_number = request.GET.get("page_no", 1)
    paginator = Paginator(comments, per_page)
    page_objects = paginator.get_page(page_number)
    comments_data = [
        {
            "comment": comment.content,
            "host": comment.host.username,
            "likes": comment.likes.count(),
            "liked": request.user.user_id
            in [user["user_id"] for user in comment.likes.values()],
            "commentId": comment.comment_id,
            "can_delete": request.user.user_id == comment.host.user_id,
            "editable": (datetime.now(pytz.UTC) - comment.date_created).seconds < 300
            and request.user.user_id == comment.host.user_id,
        }
        for comment in page_objects.object_list
    ]
    return Response(
        {
            "comments": comments_data,
            "page": {
                "page": page_objects.number,
                "has_next": page_objects.has_next(),
                "has_previous": page_objects.has_previous(),
            },
        }
    )


@api_view(["GET"])
@has_logged_in
def get_subcomments(request, parent_comment):
    """
    Author : Pavan
    Params : request object, comment_id
    Returns : returns sub comments of the comment if exists
    Created On : 17-12-2024
    """
    comments = Comment.objects.filter(parent=parent_comment)
    per_page = request.GET.get("per_page", 1)
    page_numnber = request.GET.get("page_no", 1)
    paginator = Paginator(comments, per_page)
    page_objects = paginator.get_page(page_numnber)
    comments_data = [
        {
            "comment": comment.content,
            "host": comment.host.username,
            "likes": comment.likes.count(),
            "liked": request.user.user_id
            in [user["user_id"] for user in comment.likes.values()],
            "commentId": comment.comment_id,
        }
        for comment in page_objects.object_list
    ]

    return Response(
        {
            "comments": comments_data,
            "page": {
                "page": page_objects.number,
                "has_next": page_objects.has_next(),
                "has_previous": page_objects.has_previous(),
            },
        }
    )


@api_view(["POST"])
@has_logged_in
def add_comment(request, blog_id):
    """
    Author : Pavan
    Params : request object, blog_id
    Returns : returns comments of the blog after creating
    Created On : 14-10-2024
    """
    data = request.data
    user = request.user.user_id
    data["host"] = user
    data["blog_id"] = blog_id
    parent_comment = request.GET.get("parent_comment", None)
    if parent_comment is not None:
        data["parent"] = parent_comment
    serializer = CommentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "comment": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(
        {
            "error": serializer.errors,
        },
        status=status.HTTP_206_PARTIAL_CONTENT,
    )


@api_view(["PATCH", "DELETE", "GET"])
@has_logged_in
def delete_update_comment(request, comment_id):
    """
    Author : Pavan
    Params : request object, comment_id
    Returns : return comment object if is PATCH else returns numbers of comments deleted if request is DELETE.
    Created On : 14-10-2024
    """
    if request.method == "PATCH":
        return update_comment(request, comment_id)
    if request.method == "DELETE":
        return delete_comment(request, comment_id)
    if request.method == "GET":
        comment = Comment.objects.filter(comment_id=comment_id)
        serializer = CommentSerializer(comment, many=True)
        return Response(
            {
                "comment": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@has_logged_in
def like_comment(request, comment_id):
    """
    Author : Pavan
    Params : request object, blog object
    Returns : returns comments of the blog if exists
    Created On : 14-10-2024
    """
    try:
        Comment.objects.get(comment_id=comment_id).likes.add(request.user.user_id)
    except:
        return Response(
            {"error": "comment not found"},
            status=404,
        )
    return Response(
        {
            "liked": True,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@has_logged_in
def unlike_comment(request, comment_id):
    """
    Author : Pavan
    Params : request object, blog object
    Returns : returns comments of the blog if exists
    Created On : 15-10-2024
    """
    try:
        Comment.objects.get(comment_id=comment_id).likes.remove(request.user.user_id)
    except:
        return Response(
            {"error": "comment not found"},
            status=404,
        )
    return Response(
        {
            "unliked": True,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@has_logged_in
def add_subcomment(request, blog_id, parent_comment):
    """
    Author : Pavan
    Params : request object, blog object, parent_comment
    Returns : returns comment of the blog after creating the comment object.
    Created On : 15-10-2024
    """
    data = request.data
    data["host"] = request.user.user_id
    data["parent"] = parent_comment
    data["blog_id"] = blog_id

    serializer = CommentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"Comment": serializer.data},
            status=status.HTTP_201_CREATED,
        )
    return Response(
        {"errors": serializer.errors},
        status=400,
    )
