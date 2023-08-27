from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContext(TestCase):

    LIST_URL = reverse('notes:list')

    TITLE = 'Заголовок'
    TEXT = 'Текст'
    SLUG = 'slugs'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Аутентифицированный и авторизованы пользователь'
        )
        cls.reader = User.objects.create(
            username='Аутентифицированный пользователь'
        )
        cls.notes = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author,
        )

    def test_note_get_into_list(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.notes, object_list)
    
    def test_note_not_get_into_someone_list(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes, object_list)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
