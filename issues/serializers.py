from rest_framework import serializers

from issues.models import Comment, Issue


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            'id',
            'title',
            'description',
            'priority',
            'tag',
            'status',
            'project',
            'author',
            'assignee',
            'created_time',
        ]
        read_only_fields = [
            'id',
            'project',
            'author',
            'created_time',
        ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'description',
            'issue',
            'author',
            'created_time',
        ]
        read_only_fields = [
            'id',
            'issue',
            'author',
            'created_time',
        ]
