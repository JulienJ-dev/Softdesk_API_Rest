import uuid

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from issues.models import Comment, Issue
from projects.models import Contributor, Project


User = get_user_model()


class IssueApiTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='alice',
            password='Password123!',
            age=25,
        )
        self.contributor = User.objects.create_user(
            username='bob',
            password='Password123!',
            age=30,
        )
        self.outsider = User.objects.create_user(
            username='charlie',
            password='Password123!',
            age=22,
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

    def issue_list_url(self):
        return reverse(
            'issue-list',
            kwargs={'project_pk': self.project.pk},
        )

    def issue_detail_url(self):
        return reverse(
            'issue-detail',
            kwargs={
                'project_pk': self.project.pk,
                'pk': self.issue.pk,
            },
        )

    def comment_list_url(self):
        return reverse(
            'comment-list',
            kwargs={
                'project_pk': self.project.pk,
                'issue_pk': self.issue.pk,
            },
        )

    def comment_detail_url(self):
        return reverse(
            'comment-detail',
            kwargs={
                'project_pk': self.project.pk,
                'issue_pk': self.issue.pk,
                'pk': self.comment.pk,
            },
        )

    def test_contributor_can_create_and_list_issues(self):
        self.client.force_authenticate(self.contributor)
        data = {
            'title': 'Ajouter une page',
            'description': 'Créer la page de profil',
            'priority': Issue.Priority.MEDIUM,
            'tag': Issue.Tag.FEATURE,
            'assignee': self.author.pk,
        }

        create_response = self.client.post(self.issue_list_url(), data)
        list_response = self.client.get(self.issue_list_url())

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data['status'], Issue.Status.TO_DO)
        self.assertEqual(create_response.data['author'], self.contributor.pk)
        self.assertEqual(len(list_response.data['results']), 2)

    def test_assignee_must_be_project_contributor(self):
        self.client.force_authenticate(self.author)
        data = {
            'title': 'Nouvelle tâche',
            'description': 'Description de la tâche',
            'priority': Issue.Priority.LOW,
            'tag': Issue.Tag.TASK,
            'assignee': self.outsider.pk,
        }

        response = self.client.post(self.issue_list_url(), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_contributor_can_read_but_cannot_modify_issue(self):
        self.client.force_authenticate(self.contributor)

        read_response = self.client.get(self.issue_detail_url())
        update_response = self.client.patch(
            self.issue_detail_url(),
            {'status': Issue.Status.FINISHED},
        )
        delete_response = self.client.delete(self.issue_detail_url())

        self.assertEqual(read_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_issue_author_can_update_and_delete_issue(self):
        self.client.force_authenticate(self.author)

        invalid_response = self.client.patch(
            self.issue_detail_url(),
            {'assignee': self.outsider.pk},
        )
        update_response = self.client.patch(
            self.issue_detail_url(),
            {'status': Issue.Status.FINISHED},
        )
        delete_response = self.client.delete(self.issue_detail_url())

        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_outsider_cannot_access_issues(self):
        self.client.force_authenticate(self.outsider)

        list_response = self.client.get(self.issue_list_url())
        detail_response = self.client.get(self.issue_detail_url())

        self.assertEqual(list_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(detail_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_contributor_can_create_and_list_comments(self):
        self.client.force_authenticate(self.author)

        create_response = self.client.post(
            self.comment_list_url(),
            {'description': 'Le correctif est prêt'},
        )
        list_response = self.client.get(self.comment_list_url())

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        uuid.UUID(str(create_response.data['id']))
        self.assertEqual(create_response.data['author'], self.author.pk)
        self.assertEqual(len(list_response.data['results']), 2)

    def test_contributor_can_read_but_cannot_modify_comment(self):
        self.client.force_authenticate(self.author)

        read_response = self.client.get(self.comment_detail_url())
        update_response = self.client.patch(
            self.comment_detail_url(),
            {'description': 'Texte modifié'},
        )
        delete_response = self.client.delete(self.comment_detail_url())

        self.assertEqual(read_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_author_can_update_and_delete_comment(self):
        self.client.force_authenticate(self.contributor)

        update_response = self.client.patch(
            self.comment_detail_url(),
            {'description': 'Texte corrigé'},
        )
        delete_response = self.client.delete(self.comment_detail_url())

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_outsider_cannot_access_comments(self):
        self.client.force_authenticate(self.outsider)

        list_response = self.client.get(self.comment_list_url())
        detail_response = self.client.get(self.comment_detail_url())

        self.assertEqual(list_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(detail_response.status_code, status.HTTP_403_FORBIDDEN)
