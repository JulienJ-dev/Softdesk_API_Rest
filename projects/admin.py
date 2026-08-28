from django.contrib import admin

from projects.models import Contributor, Project


admin.site.register(Project)
admin.site.register(Contributor)
