from django.contrib import admin
from django.urls import path, include

from sign_up_sign_in import views
from app import urls
from comment import views as commentViews

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", views.user_login, name="login"),
    path("signup/", views.sign_up, name="signup"),
    path("get-users/", views.get_user),
    path("update-user/", views.update_user),
    path("blog/", include(urls)),
    path("refresh_token/", views.renew_refresh_token),
    path("comment", commentViews.add_comment),
    path("comment", commentViews.delete_update_comment),
    path("comment/like/", commentViews.like_comment),
    path("comment/unlike/", commentViews.unlike_comment),
    path(
        "sub-comment/",
        commentViews.add_subcomment,
    ),
    path("subcomments/", commentViews.get_subcomments),
    path("blog_comments/", commentViews.fetch_comments),
]
