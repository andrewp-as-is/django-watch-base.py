from django.conf import settings
from django.db import models


class BookmarkModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='+', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # obj = models.ForeignKey(..., on_delete = models.CASCADE)

    class Meta:
        abstract = True


class BookmarkMixin:
    bookmark_model = None

    def get_bookmark_model(self):
        return self.bookmark_model

    def get_bookmark(self, user):
        if user.is_authenticated:
            model = self.get_bookmark_model()
            try:
                return model.objects.get(created_by=user, obj_id=self.pk)
            except model.DoesNotExist:
                pass

    def delete_bookmark(self, user):
        self.get_bookmark_model().objects.filter(
            created_by=user, obj_id=self.pk
        ).delete()

    def create_bookmark(self, user):
        kwargs = {'created_by': user, 'obj_id': self.pk}
        self.get_bookmark_model().objects.get_or_create(**kwargs)

"""
from django.db import models
from django_bookmark_base.models import BookmarkModel

class PostBookmark(BookmarkModel):
    obj = models.ForeignKey(
        'Post', related_name = "+", on_delete = models.CASCADE)

    class Meta:
        unique_together = [('obj', 'created_by')]


class Post(VoteMixin,models.Model):
    ...
    bookmarks_count = models.IntegerField(null=True)

    bookmark_model = PostBookmark
"""
