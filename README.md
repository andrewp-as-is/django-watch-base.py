<!--
https://readme42.com
-->


[![](https://img.shields.io/pypi/v/django-watch-base.svg?maxAge=3600)](https://pypi.org/project/django-watch-base/)
[![](https://img.shields.io/badge/License-Unlicense-blue.svg?longCache=True)](https://unlicense.org/)
[![](https://github.com/andrewp-as-is/django-watch-base.py/workflows/tests42/badge.svg)](https://github.com/andrewp-as-is/django-watch-base.py/actions)

### Installation
```bash
$ [sudo] pip install django-watch-base
```

##### `settings.py`
```python
INSTALLED_APPS+=['django_watch_base']
```

##### `models.py`
```python
from django.db import models
from django_watch_base.models import WatchModel

class CollectionWatch(WatchModel):
    obj = models.ForeignKey(
        'Collection', related_name="watch_set", on_delete=models.CASCADE)

    class Meta:
        unique_together = [('obj', 'created_by')]

class Collection(models.Model):
    watchers_count = models.IntegerField(default=0) # use triggers

    def get_watch_url(self):
        return '/watch/collection/%s' % self.pk
```

##### `urls.py`
```python
from django.urls import include, path

import views

urlpatterns = [
    path('/watch/collection/<int:pk>',views.ToggleView.as_view()),
]
```

##### `views.py`
`DetailView` - context variables `{{ watch_obj }}` and `{{ watch }}`
```python
from apps.collections.models import Collection, CollectionWatch
from django_watch_base.views import WatchViewMixin

class CollectionDetailView(WatchViewMixin):
    watch_model = CollectionWatch
```

`XMLHttpRequest` view
```python
from django_watch_base.views import WatchToggleView
from apps.collections.models import Collection, CollectionWatch

class ToggleView(WatchToggleView):
    watch_model = CollectionWatch

    def get_data(self):
        collection = Collection.objects.get(pk=self.kwargs['pk'])
        return {
            'is_watching': self.is_watching,
            'watchers_count': collection.watchers_count
        }
```

`ListView` prefetch user watch
```python
from django.db.models import Prefetch
from django.views.generic.list import ListView
from apps.collections.models import Collection, CollectionWatch

class CollectionListView(ListView):
    def get_queryset(self, **kwargs):
        qs = Collection.objects.all()
        if self.request.user.is_authenticated:
            qs = qs.prefetch_related(
                Prefetch("watch_set", queryset=CollectionWatch.objects.filter(created_by=self.request.user),to_attr='watching')
            )
        return qs
```

##### Templates
```html
<a data-id="{{ watch_obj.pk }}" class="btn watch-btn {% if watch %}selected{% endif %}" {% if request.user.is_authenticated %}data-href="{{ watch_obj.get_watch_url }}"{% else %}href="{% url 'login' %}?next={{ request.path }}"{% endif %}>
</a>
<a data-id="{{ watch_obj.pk }}" class="watch-count">{{ watch_obj.watchers_count }}</a>
```

##### JavaScript
```javascript
function toggle_watch(btn) {
    data_id = btn.getAttribute('data-id');

    var watch_count = document.querySelector(".watch-count[data-id='"+data_id+"']");

    var xhr = new XMLHttpRequest();
    xhr.open('GET', btn.getAttribute('data-href'));
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.responseType = 'json';
    xhr.onload = function() {
        if (xhr.status != 200) {
            console. error(`Error ${xhr.status}: ${xhr.statusText}`);
        }
        if (xhr.status == 200) {
            bookmark_count.innerHTML=xhr.response.watchers_count;
            if (xhr.response.is_watching) {
                btn.classList.add('text-green');
            } else {
                btn.classList.remove('text-green');
            }
        }
    };
    xhr.send();
}

document.addEventListener("DOMContentLoaded", function(event) {
const watch_buttons = document.querySelectorAll(".watch-btn");
for (const btn of watch_buttons) {
    if (btn.hasAttribute('data-href')) {
        btn.addEventListener('click', function(event){
            event.preventDefault();
            toggle_watch(btn);
        });
    }
}
});
```

<p align="center">
    <a href="https://readme42.com/">readme42.com</a>
</p>