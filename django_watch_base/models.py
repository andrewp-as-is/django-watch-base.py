from django.conf import settings
from django.db import models


class WatchModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='+', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # obj = models.ForeignKey(..., on_delete = models.CASCADE)

    class Meta:
        abstract = True


class WatchMixin:
    watch_model = None

    def get_watch_model(self):
        return self.watch_model

    def get_watch(self, user):
        if user.is_authenticated:
            model = self.get_watch_model()
            try:
                return model.objects.get(created_by=user, obj_id=self.pk)
            except model.DoesNotExist:
                pass

    def delete_watch(self, user):
        self.get_watch_model().objects.filter(
            created_by=user, obj_id=self.pk
        ).delete()

    def create_watch(self, user):
        kwargs = {'created_by': user, 'obj_id': self.pk}
        self.get_watch_model().objects.get_or_create(**kwargs)
