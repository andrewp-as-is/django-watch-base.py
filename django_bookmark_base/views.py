from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic.base import View


class BookmarkViewMixin:
    bookmark_model = None
    bookmark_obj = None
    bookmark_obj_pk = None

    def get_bookmark_model(self):
        return self.bookmark_model

    def get_bookmark_obj(self):
        if not self.request.user.is_authenticated:
            return
        model = self.get_bookmark_model()
        try:
            return model.objects.get(**self.get_bookmark_kwargs())
        except model.DoesNotExist:
            pass

    def get_bookmark_obj_pk(self):
        if self.bookmark_obj_pk:
            return self.bookmark_obj_pk
        return self.get_bookmark_obj().pk

    def get_bookmark(self):
        if self.request.user.is_authenticated:
            model = self.get_bookmark_model()
            try:
                return model.objects.get(**self.get_bookmark_kwargs())
            except model.DoesNotExist:
                pass

    def get_bookmark_kwargs(self):
        return {
            'created_by': self.request.user,
            'obj_id': self.get_bookmark_obj_pk()
        }

    def delete_bookmark(self):
        kwargs = self.get_bookmark_kwargs()
        self.get_bookmark_model().objects.filter(**kwargs).delete()

    def create_bookmark(self):
        kwargs = self.get_bookmark_kwargs()
        self.get_bookmark_model().objects.get_or_create(**kwargs)

    def bookmark_toggle(self):
        bookmark = self.get_bookmark()
        if bookmark:
            self.get_bookmark_model().objects.filter(pk=bookmark.pk).delete()
            return False
        self.create_bookmark()
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bookmark_obj = self.get_bookmark_obj()
        context['bookmark_obj'] = bookmark_obj
        if self.request.user.is_authenticated:
            try:
                context['bookmark'] = self.bookmark_model.objects.get(
                    obj_id=bookmark_obj.id, created_by=self.request.user
                )
            except self.bookmark_model.DoesNotExist:
                pass
        return context


class BookmarkToggleView(LoginRequiredMixin, BookmarkViewMixin, View):

    def dispatch(self, *args, **kwargs):
        self.bookmark_obj_pk = self.kwargs['pk']
        return super(BookmarkToggleView, self).dispatch(*args, **kwargs)

    def get_data(self):
        return {}

    def get_context_data(self, **kwargs):
        return {}

    def get(self, request, *args, **kwargs):
        self.bookmarked = self.bookmark_toggle()
        return JsonResponse(self.get_data(), status=200)
