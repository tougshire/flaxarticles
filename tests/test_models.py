from django.test import TestCase
from ..models import Article, StatusUpdate
from django.contrib.auth import get_user_model

class ArticleTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_one = get_user_model().objects.create(
            username="userone"
        )
        cls.article_one = Article.objects.create(
            name="article one"
        )
        cls.statusupdate_one = StatusUpdate.objects.create(
            article = cls.article_one,
            text = 'Update to Article One'
        )

    def test_article_str_is_name(self):
        self.assertEqual(self.article_one.__str__(), self.article_one.name)

    def test_statsupdate_str_is_article_name_and_date(self):
        self.assertEqual(self.statusupdate_one.__str__(), f'{self.article_one} / {self.statusupdate_one.when}')

    def test_statusupdate_is_in_article_statusupdate_set(self):
        self.assertEqual(self.article_one.statusupdate_set.count(), 1)
