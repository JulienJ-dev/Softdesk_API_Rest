from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from issues.models import Comment, Issue
from projects.models import Contributor, Project


User = get_user_model()


class ApiHomeTests(APITestCase):
    def test_api_home_is_public(self):
        response = self.client.get(reverse('api-home'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'API SoftDesk Support')


class PermissionTests(APITestCase):
    def setUp(self):
        self.password = 'Password123!'
        self.author = User.objects.create_user(
            username='alice',
            password=self.password,
            age=25,
        )
        self.contributor = User.objects.create_user(
            username='bob',
            password=self.password,
            age=30,
        )
        self.project = Project.objects.create(
            title='Site SoftDesk',
            description='API du support',
            type=Project.Type.BACK_END,
            author=self.author,
        )
        Contributor.objects.create(
            user=self.author,
            project=self.project,
        )
        Contributor.objects.create(
            user=self.contributor,
            project=self.project,
        )
        self.issue = Issue.objects.create(
            title='Erreur de connexion',
            description='La connexion échoue',
            priority=Issue.Priority.HIGH,
            tag=Issue.Tag.BUG,
            project=self.project,
            author=self.author,
            assignee=self.contributor,
        )
        self.comment = Comment.objects.create(
            description='Je reproduis le problème',
            issue=self.issue,
            author=self.contributor,
        )

    def test_authentication_is_required(self):
        urls = [
            reverse('user-list'),
            reverse('project-list'),
            reverse(
                'contributor-list',
                kwargs={'project_pk': self.project.pk},
            ),
            reverse(
                'issue-list',
                kwargs={'project_pk': self.project.pk},
            ),
            reverse(
                'comment-list',
                kwargs={
                    'project_pk': self.project.pk,
                    'issue_pk': self.issue.pk,
                },
            ),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
            )

    def test_jwt_allows_authenticated_access(self):
        token_response = self.client.post(
            reverse('token_obtain_pair'),
            {
                'username': self.author.username,
                'password': self.password,
            },
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )

        response = self.client.get(reverse('project-list'))

        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_only_accesses_own_profile_and_rgpd_fields(self):
        self.client.force_authenticate(self.author)

        own_response = self.client.get(
            reverse('user-detail', args=[self.author.pk])
        )
        other_response = self.client.get(
            reverse('user-detail', args=[self.contributor.pk])
        )

        self.assertEqual(own_response.status_code, status.HTTP_200_OK)
        self.assertFalse(own_response.data['can_be_contacted'])
        self.assertFalse(own_response.data['can_data_be_shared'])
        self.assertEqual(other_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_profile_deletion_erases_personal_data(self):
        self.client.force_authenticate(self.contributor)
        contributor_id = self.contributor.pk

        response = self.client.delete(
            reverse('user-detail', args=[contributor_id])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=contributor_id).exists())
        self.assertFalse(
            Contributor.objects.filter(user_id=contributor_id).exists()
        )
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())
        self.issue.refresh_from_db()
        self.assertIsNone(self.issue.assignee)

    def test_comment_list_is_paginated(self):
        Comment.objects.bulk_create(
            [
                Comment(
                    description=f'Commentaire {index}',
                    issue=self.issue,
                    author=self.author,
                )
                for index in range(10)
            ]
        )
        self.client.force_authenticate(self.author)
        url = reverse(
            'comment-list',
            kwargs={
                'project_pk': self.project.pk,
                'issue_pk': self.issue.pk,
            },
        )

        first_page = self.client.get(url)
        second_page = self.client.get(f'{url}?page=2')

        self.assertEqual(first_page.status_code, status.HTTP_200_OK)
        self.assertEqual(first_page.data['count'], 11)
        self.assertEqual(len(first_page.data['results']), 10)
        self.assertIsNotNone(first_page.data['next'])
        self.assertEqual(second_page.status_code, status.HTTP_200_OK)
        self.assertEqual(len(second_page.data['results']), 1)

    def test_list_queries_are_bounded(self):
        self.client.force_authenticate(self.author)
        urls = [
            (reverse('project-list'), 2),
            (
                reverse(
                    'contributor-list',
                    kwargs={'project_pk': self.project.pk},
                ),
                4,
            ),
            (
                reverse(
                    'issue-list',
                    kwargs={'project_pk': self.project.pk},
                ),
                4,
            ),
            (
                reverse(
                    'comment-list',
                    kwargs={
                        'project_pk': self.project.pk,
                        'issue_pk': self.issue.pk,
                    },
                ),
                5,
            ),
        ]

        for url, maximum in urls:
            with self.subTest(url=url):
                with CaptureQueriesContext(connection) as queries:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertLessEqual(len(queries), maximum)
