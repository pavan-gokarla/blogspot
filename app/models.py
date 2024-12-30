from django.db import models


class Tags(models.Model):
    tag_id = models.AutoField(primary_key=True)
    tag = models.TextField(unique=True)

    def __str__(self) -> str:
        return self.tag


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    email = models.EmailField()

    def __str__(self):
        return self.username


class Blog(models.Model):
    blog_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    likes = models.ManyToManyField(User, related_name="likes", blank=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    tags = models.ManyToManyField(Tags, related_name="tag_names", blank=True)
    is_removed = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
     ordering = ["-date_created"]


class CodeSnippets(models.Model):
    code_id = models.AutoField(primary_key=True)
    code_description = models.TextField()
    code_content = models.TextField()
    blog_id = models.ForeignKey(Blog, on_delete=models.CASCADE)


class Media(models.Model):
    media_id = models.AutoField(primary_key=True)
    media = models.BinaryField()
    media_name = models.CharField(max_length=300)
    blog_id = models.ForeignKey(Blog, on_delete=models.CASCADE)


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    content = models.TextField()
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, blank=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="host")
    blog_id = models.ForeignKey(Blog, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class DeletedBlogs(models.Model):
    blog_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    host = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    tags = models.ManyToManyField(Tags, related_name="tags", blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

