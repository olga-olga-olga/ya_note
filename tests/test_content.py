from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Зарегистрированный пользователь'
        )
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                slug=f'slug{index}',
                author=cls.author,
            )
            for index in range(2)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        all_id = [note.id for note in object_list]
        sorted_id = sorted(all_id)
        self.assertEqual(all_id, sorted_id)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
       
