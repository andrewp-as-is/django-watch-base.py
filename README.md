<!--
https://readme42.com
-->


[![](https://img.shields.io/pypi/v/django-bookmark-base.svg?maxAge=3600)](https://pypi.org/project/django-bookmark-base/)
[![](https://img.shields.io/badge/License-Unlicense-blue.svg?longCache=True)](https://unlicense.org/)
[![](https://github.com/andrewp-as-is/django-bookmark-base.py/workflows/tests42/badge.svg)](https://github.com/andrewp-as-is/django-bookmark-base.py/actions)

### Installation
```bash
$ [sudo] pip install django-bookmark-base
```

##### `settings.py`
```python
INSTALLED_APPS+=['django_bookmark_base']
```

##### `models.py`
```python
from django.db import models
from django_bookmark_base.models import BookmarkModel

class CollectionBookmark(BookmarkModel):
    obj = models.ForeignKey(
        'Collection', related_name="bookmark_set", on_delete=models.CASCADE)

    class Meta:
        unique_together = [('obj', 'created_by')]

class Collection(models.Model):
    bookmarks_count = models.IntegerField(default=0) # use triggers

    def get_bookmark_url(self):
        return 'bookmark/collection/%s' % self.pk
```

##### `urls.py`
```python
from django.urls import include, path

import views

urlpatterns = [
    path('bookmark/collection/<int:pk>',
         views.CollectionBookmarkToggleView.as_view(), name='collection'),
]
```

##### `views.py`
`DetailView` - context variables `{{ bookmark_obj }}` and `{{ bookmark }}`
```python
from apps.collections.models import Collection, CollectionBookmark
from django_bookmark_base.views import BookmarkViewMixin

class CollectionDetailView(BookmarkViewMixin):
    bookmark_model = CollectionBookmark
```

`XMLHttpRequest` view
```python
from django_bookmark_base.views import BookmarkToggleView
from apps.collections.models import Collection, CollectionBookmark

class CollectionBookmarkToggleView(BookmarkToggleView):
    bookmark_model = CollectionBookmark

    def get_data(self):
        collection = Collection.objects.get(pk=self.kwargs['pk'])
        return {
            'bookmarked': self.bookmarked,
            'bookmarks_count': collection.bookmarks_count
        }
```

`ListView` prefetch user bookmarks
```python
from django.db.models import Prefetch
from django.views.generic.list import ListView
from apps.collections.models import Collection, CollectionBookmark

class CollectionListView(ListView):
    def get_queryset(self, **kwargs):
        qs = Collection.objects.all()
        if self.request.user.is_authenticated:
            qs = qs.prefetch_related(
                Prefetch("bookmark_set", queryset=CollectionBookmark.objects.filter(created_by=self.request.user),to_attr='bookmarks')
            )
        return qs
```

##### Templates
```html
<a data-id="{{ bookmark_obj.pk }}" class="btn bookmark-btn {% if bookmark %}selected{% endif %}" {% if request.user.is_authenticated %}data-href="{{ bookmark_obj.get_bookmark_url }}"{% else %}href="{% url 'login' %}?next={{ request.path }}"{% endif %}>
</a>
<a data-id="{{ bookmark_obj.pk }}" class="bookmark-count">{{ bookmark_obj.bookmarks_count }}</a>
```

##### JavaScript
```javascript
function bookmark_toggle(btn) {
    data_id = btn.getAttribute('data-id');

    var bookmark_count = document.querySelector(".bookmark-count[data-id='"+data_id+"']");

    var xhr = new XMLHttpRequest();
    xhr.open('GET', btn.getAttribute('data-href'));
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.responseType = 'json';
    xhr.onload = function() {
        if (xhr.status != 200) {
            console. error(`Error ${xhr.status}: ${xhr.statusText}`);
        }
        if (xhr.status == 200) {
            bookmark_count.innerHTML=xhr.response.bookmarks_count;
            if (xhr.response.bookmarked) {
                btn.classList.add('text-green');
            } else {
                btn.classList.remove('text-green');
            }
        }
    };
    xhr.send();
}

document.addEventListener("DOMContentLoaded", function(event) {
const bookmark_buttons = document.querySelectorAll(".bookmark-btn");
for (const btn of bookmark_buttons) {
    if (btn.hasAttribute('data-href')) {
        btn.addEventListener('click', function(event){
            event.preventDefault();
            bookmark_toggle(btn);
        });
    }
}
});
```

<p align="center">
    <a href="https://readme42.com/">readme42.com</a>
</p>