# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def about_author(self):
        """Страница об авторе доступна всем"""
        response = self.guest_client.get('about/author/')
        self.assertEqual(response.status_code, 200)

    def about_tech(self):
        """Страницы о технологиях доступнав всем"""
        response = self.guest_client.get('about/tech/')
        self.assertEqual(response.status_code, 200)


class TaskURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )
        Group.objects.create(
            title='Test Group',
            slug='test',
            description='Test Group',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(id=1)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_url(self):
        '''Главная страница доступна всем'''
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_url(self):
        '''Страница группы доступна всем'''
        response = self.guest_client.get('/group/test/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url(self):
        '''Страница профиля доступна всем'''
        response = self.guest_client.get('/profile/HasNoName/')
        self.assertEqual(response.status_code, 200)

    def test_post_url(self):
        '''Страница поста доступна всем'''
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url(self):
        '''Страница редактирования поста доступна автору'''
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 200)

    def test_post_create_url(self):
        '''Страница создания поста доступна авторизированным пользователям'''
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        '''Проверка ответа несуществующей страницы'''
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html'
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
