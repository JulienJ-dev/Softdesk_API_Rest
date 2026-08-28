from django.conf import settings
from django.db import models


class Project(models.Model):
    class Type(models.TextChoices):
        BACK_END = 'BACK_END', 'Back-end'
        FRONT_END = 'FRONT_END', 'Front-end'
        IOS = 'IOS', 'iOS'
        ANDROID = 'ANDROID', 'Android'

    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=10, choices=Type.choices)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects',
    )
    contributors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Contributor',
        related_name='projects',
    )
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Contributor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contributions',
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='contributor_links',
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'project'],
                name='unique_project_contributor',
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.project.title}'
