# posts/tests/test_forms.py
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

POST_CREATE_URL = 'posts:post_create'
POST_EDIT_URL = 'posts:post_edit'
TEST_USERNAME = 'HasNoName'
TEST_GROUP_TITLE = 'Test Group 1'
TEST_GROUP_SLUG = 'test1'
TEST_GROUP_DESCRIPTION = 'Test Group 1'
TEST_POST_TEXT = 'Test text 1'
TEST_POST_TEXT_UPDATE = 'Test text 1 Update'
TEST_POST_TEXT_2 = 'Test text 2'


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.group_1 = Group.objects.create(
            title=TEST_GROUP_TITLE,
            slug=TEST_GROUP_SLUG,
            description=TEST_GROUP_DESCRIPTION
        )
        cls.post_1 = Post.objects.create(
            text=TEST_POST_TEXT,
            author=cls.user,
            group=cls.group_1
        )

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка работы формы создания поста"""
        posts_count = Post.objects.count()
        form_data = {
            'text': TEST_POST_TEXT_2,
            'group': PostFormTest.group_1.id
        }
        self.authorized_client.post(
            reverse(POST_CREATE_URL),
            data=form_data
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=TEST_POST_TEXT_2,
                author=PostFormTest.user,
                group=PostFormTest.group_1
            ).exists()
        )

    def test_post_edit(self):
        """Проверка работы формы изменения поста"""
        form_data = {
            'text': TEST_POST_TEXT_UPDATE,
            'group': PostFormTest.group_1.id
        }
        response = self.authorized_client.post(
            reverse(POST_EDIT_URL, args=[1]),
            form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        PostFormTest.post_1.refresh_from_db()
        self.assertEqual(PostFormTest.post_1.text, TEST_POST_TEXT_UPDATE)
