from django.test import TestCase

from theatre.models import Genre


class GenreModelTest(TestCase):
    def setUpTestData(cls):
        Genre.objects.create(name="drama")

    def test_str_works_correctly(self):
        genre = Genre.objects.get(id=1)

        self.assertEqual(str(genre), "drama")
