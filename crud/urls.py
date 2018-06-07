from django.conf.urls import url
from django.contrib import admin
from apis import apis

urlpatterns = [
    url(r'^', admin.site.urls),
    url(r'^box/add', apis.ADD.as_view()),
    url(r'^box/update', apis.Update.as_view()),
    url(r'^box/all', apis.All.as_view()),
    url(r'^box/myboxes', apis.MyBoxes.as_view()),
]
