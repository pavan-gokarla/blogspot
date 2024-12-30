from django.urls import path


from . import views


urlpatterns = [
    path("create/", views.create_blog),
    path("update/", views.update_blog),
    path("delete/", views.delete_blog),
    path("like/", views.like_blog),
    path("unlike/", views.unlike_blog),
    path("tags/", views.get_tags),
    path("tags/add-tag", views.add_tag),
    path("get-blogs/", views.get_blogs),
    path("get-blog//", views.get_blog),
]
