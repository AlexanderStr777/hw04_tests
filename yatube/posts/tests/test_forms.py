# posts/tests/test_forms.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group_1 = Group.objects.create(
            title='Test Group 1',
            slug='test1',
            description='Test Group 1'
        )
        cls.post_1 = Post.objects.create(
            text='Test text 1',
            author=cls.user,
            group=(Group.objects.get(slug='test1'))
        )

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка работы формы создания поста"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Test text 2',
            'group': 1
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Test text 2',
                author=PostFormTest.user,
                group=PostFormTest.group_1
            ).exists()
        )

    def test_post_edit(self):
        """Проверка работы формы изменения поста"""
        form_data = {
            'text': 'Test text 1 Update',
            'group': 1
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[1]),
            form_data
        )
        self.assertEqual(response.status_code, 302)
        PostFormTest.post_1.refresh_from_db()
        self.assertEqual(PostFormTest.post_1.text, 'Test text 1 Update')
