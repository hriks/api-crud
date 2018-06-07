from django.conf.urls import url
from django.contrib import admin
from apis import apis

urlpatterns = [
    url(r'^', admin.site.urls),
    url(r'^box/add', apis.Box.as_view())
]
