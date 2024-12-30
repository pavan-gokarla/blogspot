from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Count
import pytz

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


from app.services import add_codes, save_files
from decorators import has_logged_in
from .serializers import BlogSerializer, TagSerializer
from .models import Blog, Tags, Comment


@api_view(["GET"])
@has_logged_in
def get_blogs(request):
    """
    Author : Pavan
    Params : request object
    Returns : Response Blog objects
    Created On : 17-10-2024
    """
    user = request.user.user_id
    tags = dict(request.GET).get("tag", None)
    if request.GET.get("blogs") == "myblogs":
        blogs = Blog.objects.filter(host=user, is_removed=False)
    elif request.GET.get("blogs") == "removed-blogs":
        blogs = Blog.objects.filter(host=user, is_removed=True)
    else:
        blogs = Blog.objects.filter(is_removed=False)

    if tags is not None:
        for tag in tags:
            blogs = blogs.filter(tags__tag=tag)
    if request.GET.get("sortBy") == "likes":
        blogs = blogs.annotate(likes_count=Count("likes")).order_by("-likes_count")
    per_page = request.GET.get("per_page", 5)
    page_no = request.GET.get("page_no", 1)
    paginatior = Paginator(blogs, per_page)
    page_objects = paginatior.get_page(page_no)

    blogs_data = [
        {
            "title": blog.title,
            "content": blog.content,
            "host": blog.host.username,
            "tags": blog.tags.values(),
            "likes": len(blog.likes.values()),
            "date_created": blog.date_created,
            "liked": user in BlogSerializer(blog).data["likes"],
            "date_updated": blog.date_updated,
            "blog_id": blog.blog_id,
            "is_removed": blog.is_removed,
        }
        for blog in page_objects.object_list
    ]
    return Response(
        {
            "Blogs": blogs_data,
            "page": {
                "per_page": per_page,
                "current": page_objects.number,
                "has_next": page_objects.has_next(),
                "has_previous": page_objects.has_previous(),
            },
        }
    )


@api_view(["GET"])
@has_logged_in
def get_blog(request, blog_id):
    """
    Author : Pavan
    Params : request object
    Returns : Response Blog objects
    Created On : 28-11-2024
    """
    try:
        blog = Blog.objects.get(blog_id=blog_id)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    return Response(
        {
            "title": blog.title,
            "content": blog.content,
            "tags": blog.tags.values_list(),
            "liked": request.user.user_id
            in [user["user_id"] for user in blog.likes.values()],
            "date_created": blog.date_created,
            "date_updated": blog.date_updated,
            "likes": len(blog.likes.values()),
            "host": blog.host.username,
            "editable": (datetime.now(pytz.UTC) - blog.date_created).days < 1
            and request.user.user_id == blog.host.user_id,
            "can_delete": request.user.user_id == blog.host.user_id,
            "is_removed": blog.is_removed,
            "comments": Comment.objects.filter(blog_id=blog_id).count(),
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@has_logged_in
def create_blog(request):
    """
    Author : Pavan
    Params : request object
    Returns : Response Blog objects after creating Blog
    Created On : 12-10-2024
    """
    user = request.user.user_id
    data = request.data.copy()
    data["host"] = user

    blog_serialzer = BlogSerializer(data=data)
    if blog_serialzer.is_valid():
        blog = blog_serialzer.save()
    else:
        return Response(blog_serialzer.errors, status=status.HTTP_400_BAD_REQUEST)
    media_files = save_files(request, blog)
    code_snippets = add_codes(request, blog)
    return Response(
        {
            "Blog": blog_serialzer.data,
            "media": media_files,
            "code_snippets": code_snippets,
        },
        status=200,
    )


@api_view(["PATCH"])
@has_logged_in
def update_blog(request, blog_id):
    """
    Author : Pavan
    Params : request object
    Returns : Response Blog objects after updating Blog if exists
    Created On : 12-10-2024
    """
    user = request.user.user_id
    data = request.data
    try:
        blog = Blog.objects.get(host=user, blog_id=blog_id)
        editable = (datetime.now(pytz.UTC) - blog.date_created).days < 1
        if not editable:
            return Response({"error": "Can't Edit"}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response(
            {
                "error": str(e),
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    serializer = BlogSerializer(blog, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()

    code_snippets = add_codes(request, blog)
    media_files = save_files(request, blog)

    return Response(
        {
            "Blog": serializer.data,
            "code_snippets": code_snippets,
            "media_files": media_files,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@has_logged_in
def delete_blog(request, blog_id):
    """
    Author : Pavan
    Params : request object,blog id.
    Returns : Returns 1 if blog is deleted else 0
    Created On : 13-10-2024
    """
    republish = request.GET.get("republish")
    if republish == "true":
        republish = True
    else:
        republish = False
    query = Blog.objects.filter(blog_id=blog_id, host=request.user.user_id).update(
        is_removed=republish
    )

    return Response(
        {"Blogs deleted": query},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@has_logged_in
def like_blog(request, blog_id):
    """
    Author : Pavan
    Params : request object, blog id
    Returns : Returns true if blog exists else false.
    Created On : 13-10-2024
    """
    try:
        Blog.objects.get(blog_id=blog_id).likes.add(request.user.user_id)
    except:
        return Response(
            {"error": "Blog not found"},
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
def unlike_blog(request, blog_id):
    """
    Author : Pavan
    Params : request object, blog id
    Returns : Returns true if blog exists else false.
    Created On : 13-10-2024
    """
    try:
        Blog.objects.get(blog_id=blog_id).likes.remove(request.user.user_id)
    except:
        return Response(
            {"error": "Blog not found"},
            status=404,
        )
    return Response(
        {
            "unliked": True,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def get_tags(request):
    """
    Author : Pavan
    Params : request object
    Returns : returns all tags.
    Created On : 19-11-2024
    """
    tags = Tags.objects.all()
    serializer = TagSerializer(tags, many=True)
    return Response({"tags": serializer.data}, status=200)


# @api_view(["POST"])
# def upload_post(request):
# """
# Author : Pavan
# Params : request object
# Returns : returns all tags.
# Created On : 19-11-2024
# """
# print(request.data)
# blog = Blog.objects.get(blog_id=245)
# print("hi")
# files = save_files(request, blog)
# return Response({"comleted ": files})


@api_view(["POST"])
# @has_logged_in
def add_tag(request):
    """
    Author : Pavan
    Params : request object
    Returns : returns all tags.
    Created On : 23-11-2024
    """
    tag = request.data
    newTag = Tags.objects.create(**tag)
    # print(newTag)
    return Response({"tag": newTag.tag_id}, status=status.HTTP_201_CREATED)
