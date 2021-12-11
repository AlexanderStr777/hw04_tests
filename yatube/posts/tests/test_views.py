# posts/tests/test_views.py
import random

from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from mixer.backend.django import mixer
from posts.models import Group, Post, User

USER_NAME = 'HasNoName'
INDEX_URL = 'posts:index'
GROUP_URL = 'posts:group_list'
MAIN_GROUP_SLUG = 'test0'
MAIN_GROUP_URL = f'/group/{MAIN_GROUP_SLUG}/'
PROFILE_URL = 'posts:profile'
USER_PROFILE_URL = f'/profile/{USER_NAME}/'
POST_DETAIL_URL = 'posts:post_detail'
POST_CREATE_URL = 'posts:post_create'
POST_EDIT_URL = 'posts:post_edit'


class PostPagesTemplatesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        Group.objects.create(
            title='Test Group 1',
            slug=MAIN_GROUP_SLUG,
            description='Test Group 1'
        )
        Post.objects.create(
            text='Test text 1',
            author=cls.user,
            group=(Group.objects.get(slug=MAIN_GROUP_SLUG))
        )

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse(INDEX_URL): 'posts/index.html',
            MAIN_GROUP_URL: ('posts/group_list.html'),
            USER_PROFILE_URL: ('posts/profile.html'),
            reverse(POST_DETAIL_URL, args=[1]): (
                'posts/post_detail.html'
            ),
            reverse(POST_CREATE_URL): 'posts/create_post.html',
            reverse(POST_EDIT_URL, args=[1]): (
                'posts/create_post.html'
            )
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PostPagesContentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        mixer.cycle(3).blend(
            Group,
            title=mixer.sequence('Test Group {0}'),
            slug=mixer.sequence('test{0}'),
            description=mixer.sequence('Test Group {0}')
        )
        mixer.cycle(19).blend(
            Post,
            text=mixer.sequence('Тестовый текст {0}'),
            author=cls.user,
            group=(Group.objects.get(slug=MAIN_GROUP_SLUG))
        )
        random_group_index = random.randrange(1, 2)
        mixer.cycle(10).blend(
            Post,
            text=mixer.sequence('Тестовый текст {0}'),
            author=cls.user,
            group=(Group.objects.get(slug=f'test{random_group_index}'))
        )

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_show_correct_context(self):
        """Шаблон posts/index.html сформирован с правильным контекстом """
        response = self.authorized_client.get(reverse('posts:index'))
        expected_post_text = Post.objects.latest('pub_date').text
        expected_post_group = Post.objects.latest('pub_date').group
        title = response.context['title']
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertEqual(
            title,
            'Последние обновления на сайте',
            'Передается не правильный title'
        )
        self.assertEqual(
            post_text_0,
            expected_post_text,
            'Передан не вырный текст поста'
        )
        self.assertEqual(
            post_group_0,
            expected_post_group,
            'Передана не верная группа поста'
        )

    def test_group_list_page_show_correct_context(self):
        """Шаблон posts/group_list.html сформирован с правильным контекстом"""
        response = self.authorized_client.get(MAIN_GROUP_URL)
        expected_post = Post.objects.filter(
            group=Group.objects.get(slug=MAIN_GROUP_SLUG)
        ).latest('pub_date')
        expected_group = Group.objects.get(slug=MAIN_GROUP_SLUG)
        group = response.context['group']
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(group, expected_group, 'Не верно отображается группа')
        self.assertEqual(post_text_0, expected_post.text)

    def test_profile_page_show_correct_context(self):
        """Шаблон posts/profile.html сформирован с правильным контекстом"""
        response = self.authorized_client.get(USER_PROFILE_URL)
        expected_post = Post.objects.filter(
            author=User.objects.get(username=USER_NAME)
        ).latest('pub_date')
        author = response.context['author']
        first_object = response.context['page_obj'][0]
        self.assertEqual(
            author,
            User.objects.get(username=USER_NAME),
            'Передается не верный автор'
        )
        self.assertEqual(
            first_object,
            expected_post,
            'Первый пост передается не верно'
        )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон posts/post_detail.html сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(POST_DETAIL_URL, args=[29])
        )
        expected_post = Post.objects.get(id=29)
        expected_title = expected_post.text[:31]
        expected_author = User.objects.get(username=USER_NAME)
        post = response.context['post']
        author = response.context['author']
        title = response.context['title']
        self.assertEqual(post, expected_post)
        self.assertEqual(author, expected_author)
        self.assertEqual(title, expected_title)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон posts/create_post.html на странице редактирования поста
        сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(POST_EDIT_URL, args=[29])
        )
        is_edit = response.context['is_edit']
        self.assertTrue(is_edit)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон posts/create_post.html на странице создания поста
        сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(POST_CREATE_URL))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PostPagesPaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        mixer.cycle(2).blend(
            Group,
            title=mixer.sequence('Test Group {0}'),
            slug=mixer.sequence('test{0}'),
            description=mixer.sequence('Test Group {0}')
        )
        mixer.cycle(16).blend(
            Post,
            text=mixer.sequence('Тестовый текст {0}'),
            author=cls.user,
            group=(Group.objects.get(slug=MAIN_GROUP_SLUG))
        )

        mixer.cycle(11).blend(
            Post,
            text=mixer.sequence('Тестовый текст {0}'),
            author=cls.user,
            group=(Group.objects.get(slug='test1'))
        )

    def setUp(self):
        self.guest_client = Client()

    def test_index_first_page_contains_ten_posts(self):
        """Проверка количества постов на первой странице
        шаблона posts/index.html"""
        response = self.guest_client.get(reverse(INDEX_URL))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_last_page_contains_seven_posts(self):
        """Проверка количества постов на последней странице
        шаблона posts/index.html"""
        response = self.guest_client.get(reverse(INDEX_URL) + '?page=3')
        self.assertEqual(len(response.context['page_obj']), 7)

    def test_group_first_page_contains_ten_posts(self):
        """Проверка количества постов на первой странице
        шаблона posts/group_list.html"""
        response = self.guest_client.get(MAIN_GROUP_URL)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_last_page_contains_six_posts(self):
        """Проверка количества постов на последней странице
        шаблона posts/group_list.html"""
        response = self.guest_client.get(MAIN_GROUP_URL + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 6)

    def test_profile_first_page_contains_ten_posts(self):
        """Проверка количества постов на первой странице
        шаблона posts/profile.html"""
        response = self.guest_client.get(USER_PROFILE_URL)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_last_page_contains_seven_posts(self):
        """Проверка количества постов на последней странице
        шаблона posts/profile.html"""
        response = self.guest_client.get(USER_PROFILE_URL + '?page=3')
        self.assertEqual(len(response.context['page_obj']), 7)


class PostConnectPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        mixer.cycle(2).blend(
            Group,
            title=mixer.sequence('Test Group {0}'),
            slug=mixer.sequence('test{0}'),
            description=mixer.sequence('Test Group {0}')
        )
        Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=(Group.objects.get(slug=MAIN_GROUP_SLUG))
        )
        mixer.cycle(7).blend(
            Post,
            text=mixer.sequence('Тестовый текст {0}'),
            author=cls.user,
            group=(Group.objects.get(slug='test1'))
        )

    def setUp(self):
        self.guest_client = Client()

    def test_connection_between_post_and_index(self):
        """Проверка отображения поста на главной странице"""
        response = self.guest_client.get(reverse(INDEX_URL))
        posts = response.context['page_obj']
        self.assertTrue(Post.objects.get(text='Тестовый текст') in posts)

    def test_connection_between_post_and_group_page(self):
        """Проверка отображения поста на странице соответствующей группе"""
        response = self.guest_client.get(MAIN_GROUP_URL)
        posts = response.context['page_obj']
        self.assertTrue(Post.objects.get(text='Тестовый текст') in posts)

    def test_not_connection_between_post_and_another_group_page(self):
        """Проверка отсутствия поста на странице другой группы"""
        response = self.guest_client.get(
            reverse(GROUP_URL, args=['test1'])
        )
        posts = response.context['page_obj']
        self.assertFalse(Post.objects.get(text='Тестовый текст') in posts)

    def test_connection_between_post_and_profile_page(self):
        """Проверка наличия поста на странице автора"""
        response = self.guest_client.get(USER_PROFILE_URL)
        posts = response.context['page_obj']
        self.assertTrue(Post.objects.get(text='Тестовый текст') in posts)
