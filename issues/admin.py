from django.contrib import admin

from issues.models import Comment, Issue


admin.site.register(Issue)
admin.site.register(Comment)
