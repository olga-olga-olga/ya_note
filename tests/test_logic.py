from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    TITLE = 'Заголовок'
    TEXT = 'Текст'
    SLUG = 'slugs'
    NEW_TITLE = 'Новый заголовок'
    NEW_TEXT = 'Новый текст'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
            'author': cls.user
        }
        cls.form_new_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
            'slug': cls.SLUG,
            'author': cls.user
        }
        cls.url = reverse('notes:add')

    def test_anonymous_user_cant_create_note(self):
        '''Проверка утверждения - анонимный пользователь'''
        '''не может создать заметку'''
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        '''Проверка утверждения - залогиненый пользователь'''
        '''может создать заметку'''
        response = self.auth_client.post(self.url, data=self.form_data)
        done_url = reverse('notes:success')
        self.assertRedirects(response, f'{done_url}')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.TITLE)
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.slug, self.SLUG)
        self.assertEqual(note.author, self.user)

    def test_not_use_same_slag(self):
        '''Проверка утверждения - невозможно создать'''
        '''две заметки с одинаковым slug'''
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        response = self.auth_client.post(self.url, data=self.form_new_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(f'{self.SLUG}' + WARNING)
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        self.assertEqual(response.status_code, 200)


class TestAutoFillSlug(TestCase):
    '''Проверка автоматического формировании slug,'''
    '''если slug не заполнен'''

    TITLE = 'Заголовок'
    TEXT = 'Текст'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'author': cls.user
        }
        cls.add_url = reverse('notes:add')
        cls.done_url = reverse('notes:success')
        cls.list_url = reverse('notes:list')

    def test_automatic_slug_filling(self):
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, f'{self.done_url}')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertTrue(note.slug)


class TestNotetEditDelete(TestCase):

    TITLE = 'Заголовок'
    SLUG = 'slugs'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённая заметка'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.notes = Note.objects.create(
            title=cls.TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.SLUG,
            author=cls.author,
        )
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.done_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))
        cls.form_data = {'text': cls.NEW_NOTE_TEXT}

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, f'{self.done_url}')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, f'{self.done_url}')
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.notes.refresh_from_db()
