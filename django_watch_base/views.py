from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic.base import View


class WatchViewMixin:
    watch_model = None
    watch_obj = None
    watch_obj_pk = None

    def get_watch_model(self):
        return self.watch_model

    def get_watch_obj(self):
        if not self.request.user.is_authenticated:
            return
        model = self.get_watch_model()
        try:
            return model.objects.get(**self.get_watch_kwargs())
        except model.DoesNotExist:
            pass

    def get_watch_obj_pk(self):
        if self.watch_obj_pk:
            return self.watch_obj_pk
        return self.get_watch_obj().pk

    def get_watch(self):
        if self.request.user.is_authenticated:
            model = self.get_watch_model()
            try:
                return model.objects.get(**self.get_watch_kwargs())
            except model.DoesNotExist:
                pass

    def get_watch_kwargs(self):
        return {
            'created_by': self.request.user,
            'obj_id': self.get_watch_obj_pk()
        }

    def delete_watch(self):
        kwargs = self.get_watch_kwargs()
        self.get_watch_model().objects.filter(**kwargs).delete()

    def create_watch(self):
        kwargs = self.get_watch_kwargs()
        self.get_watch_model().objects.get_or_create(**kwargs)

    def toggle_watch(self):
        watch = self.get_watch()
        if watch:
            self.get_watch_model().objects.filter(pk=watch.pk).delete()
            return False
        self.create_watch()
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        watch_obj = self.get_watch_obj()
        context['watch_obj'] = watch_obj
        if self.request.user.is_authenticated:
            try:
                context['watch'] = self.watch_model.objects.get(
                    obj_id=watch_obj.id, created_by=self.request.user
                )
            except self.watch_model.DoesNotExist:
                pass
        return context


class WatchToggleView(LoginRequiredMixin, WatchViewMixin, View):

    def dispatch(self, *args, **kwargs):
        self.watch_obj_pk = self.kwargs['pk']
        return super(WatchToggleView, self).dispatch(*args, **kwargs)

    def get_data(self):
        raise NotImplementedError('get_data() not implemented')

    def get_context_data(self, **kwargs):
        return {}

    def get(self, request, *args, **kwargs):
        self.is_watching = self.toggle_watch()
        return JsonResponse(self.get_data(), status=200)
