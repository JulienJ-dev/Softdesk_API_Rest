from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from issues.models import Issue
from projects.models import Contributor, Project


User = get_user_model()


class ProjectApiTests(APITestCase):
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
        self.other_user = User.objects.create_user(
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
        self.author_link = Contributor.objects.create(
            user=self.author,
            project=self.project,
        )
        self.contributor_link = Contributor.objects.create(
            user=self.contributor,
            project=self.project,
        )

    def test_project_creation_adds_author_as_contributor(self):
        self.client.force_authenticate(self.author)
        data = {
            'title': 'Application mobile',
            'description': 'Application Android',
            'type': Project.Type.ANDROID,
        }

        response = self.client.post(reverse('project-list'), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(pk=response.data['id'])
        self.assertEqual(project.author, self.author)
        self.assertTrue(
            Contributor.objects.filter(
                project=project,
                user=self.author,
            ).exists()
        )

    def test_project_list_only_contains_contributed_projects(self):
        self.client.force_authenticate(self.contributor)
        contributor_response = self.client.get(reverse('project-list'))

        self.client.force_authenticate(self.other_user)
        other_response = self.client.get(reverse('project-list'))

        self.assertEqual(contributor_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(contributor_response.data['results']), 1)
        self.assertEqual(other_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(other_response.data['results']), 0)

    def test_contributor_can_read_but_cannot_modify_project(self):
        self.client.force_authenticate(self.contributor)
        url = reverse('project-detail', args=[self.project.pk])

        read_response = self.client.get(url)
        update_response = self.client.patch(url, {'title': 'Nouveau titre'})
        delete_response = self.client.delete(url)

        self.assertEqual(read_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_contributor_cannot_access_project_resources(self):
        self.client.force_authenticate(self.other_user)
        project_url = reverse('project-detail', args=[self.project.pk])
        contributors_url = reverse(
            'contributor-list',
            kwargs={'project_pk': self.project.pk},
        )

        project_response = self.client.get(project_url)
        contributors_response = self.client.get(contributors_url)

        self.assertEqual(
            project_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            contributors_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_author_can_modify_and_delete_project(self):
        self.client.force_authenticate(self.author)
        url = reverse('project-detail', args=[self.project.pk])

        update_response = self.client.patch(url, {'title': 'Nouveau titre'})
        delete_response = self.client.delete(url)

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_author_can_add_and_list_contributors(self):
        self.client.force_authenticate(self.author)
        url = reverse(
            'contributor-list',
            kwargs={'project_pk': self.project.pk},
        )

        create_response = self.client.post(
            url,
            {'user': self.other_user.pk},
        )
        duplicate_response = self.client.post(
            url,
            {'user': self.other_user.pk},
        )
        list_response = self.client.get(url)

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            duplicate_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data['results']), 3)

    def test_contributor_cannot_manage_contributors(self):
        self.client.force_authenticate(self.contributor)
        list_url = reverse(
            'contributor-list',
            kwargs={'project_pk': self.project.pk},
        )
        detail_url = reverse(
            'contributor-detail',
            kwargs={
                'project_pk': self.project.pk,
                'pk': self.author_link.pk,
            },
        )

        create_response = self.client.post(
            list_url,
            {'user': self.other_user.pk},
        )
        delete_response = self.client.delete(detail_url)

        self.assertEqual(
            create_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            delete_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_author_can_remove_contributor_but_not_self(self):
        self.client.force_authenticate(self.author)
        contributor_url = reverse(
            'contributor-detail',
            kwargs={
                'project_pk': self.project.pk,
                'pk': self.contributor_link.pk,
            },
        )
        author_url = reverse(
            'contributor-detail',
            kwargs={
                'project_pk': self.project.pk,
                'pk': self.author_link.pk,
            },
        )

        contributor_response = self.client.delete(contributor_url)
        author_response = self.client.delete(author_url)

        self.assertEqual(
            contributor_response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertEqual(
            author_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_removing_contributor_unassigns_their_issues(self):
        issue = Issue.objects.create(
            title='Erreur de connexion',
            description='La connexion échoue',
            priority=Issue.Priority.HIGH,
            tag=Issue.Tag.BUG,
            project=self.project,
            author=self.author,
            assignee=self.contributor,
        )
        self.client.force_authenticate(self.author)
        url = reverse(
            'contributor-detail',
            kwargs={
                'project_pk': self.project.pk,
                'pk': self.contributor_link.pk,
            },
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        issue.refresh_from_db()
        self.assertIsNone(issue.assignee)
