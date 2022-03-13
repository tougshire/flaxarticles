from django.test import  SimpleTestCase, TestCase, Client
from ..forms import ArticleForm
from ..models import Article, StatusUpdate
from django.urls import reverse
from django.contrib.auth import get_user_model

class ViewTests(TestCase):

    fixtures=[]

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='admin', password='admin', is_superuser=True)

    def test_article_list_view(self):
        client = Client()
        response = client.get('/flaxarticles/articles/')
        self.assertEqual(response.status_code, 200)

    def test_article_detail_view(self):
        Article.objects.create()
        client = Client()
        response = client.get('/flaxarticles/article/1/')
        self.assertEqual(response.status_code, 200)

    def test_get_article_create_view_no_auth(self):
        client = Client()
        response = client.get('/flaxarticles/article/create/')
        self.assertEqual(response.status_code, 302)

    def test_get_article_create_view(self):
        client = Client()
        client.login(username='admin', password='admin')
        response = client.get('/flaxarticles/article/create/')
        self.assertEqual(response.status_code, 200)


    def test_get_article_detail_view(self):
        client = Client()
        article = Article.objects.create()
        ppk = article.pk
        response = client.get(f'/flaxarticles/article/{ppk}/')
        self.assertEqual(response.status_code, 200)

    def test_article_detail_name(self):
        client = Client()
        article = Article.objects.create()
        ppk = article.pk
        self.assertEqual(reverse('flaxarticles:article_detail', kwargs={'pk':ppk}), f'/flaxarticles/article/{ppk}/')


    def test_post_article_create_view_no_auth(self):
        client = Client()
        Article.objects.filter(name="Test Article").delete()
        response = client.post('/flaxarticles/article/create/', {'name': 'Test Article', 'start': '1/1/2021'})
        article_count = Article.objects.filter(name="Test Article").count()
        self.assertEqual(article_count, 0)

    def test_post_article_create_view(self):
        client = Client()
        client.login(username='admin', password='admin')
        Article.objects.filter(name="Test Article").delete()
        response = client.post('/flaxarticles/article/create/', {'name': 'Test Article', 'start': '1/1/2021'})
        article_count = Article.objects.filter(name="Test Article").count()
        self.assertEqual(article_count, 1)

    def test_get_article_update_view_no_auth(self):
        client = Client()
        article = Article.objects.create( name='Test Article' )
        response = client.get(f'/flaxarticles/article/{article.pk}/update/')
        self.assertEqual(response.status_code, 302)

    def test_get_article_update_view(self):
        client = Client()
        client.login(username='admin', password='admin')
        article = Article.objects.create( name='Test Article' )
        response = client.get(f'/flaxarticles/article/{article.pk}/update/')
        self.assertEqual(response.status_code, 200)


    def test_post_article_update_view_no_auth(self):
        client = Client()
        article = Article.objects.create( name='Article before post' )
        ppk = article.pk
        response = client.post(f'/flaxarticles/article/{ ppk }/update/', {'name': 'Article after post', 'start': '1/2/2021'})
        article = Article.objects.get( pk=ppk )
        self.assertEqual(article.name, 'Article before post')

    def test_post_article_update_view_auth(self):
        client = Client()
        client.login(username='admin', password='admin')
        article = Article.objects.create( name='Article before post' )
        ppk = article.pk
        response = client.post(f'/flaxarticles/article/{ ppk }/update/', {'name': 'Article after post', 'start': '1/2/2021'})
        article = Article.objects.get( pk=ppk )
        self.assertEqual(article.name, 'Article after post')

    def test_post_article_created_by(self):
        client = Client()
        client.login(username='admin', password='admin')
        response = client.post(f'/flaxarticles/article/create/', {'name': 'New Article', 'start': '1/2/2021'})
        self.assertEqual(Article.objects.get(name='New Article').created_by, get_user_model().objects.get(username="admin") )

class ArticleCreatestatusupdateFormsetTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.superuser = get_user_model().objects.create_user(
            username = "superone",
            password = "TestSuper#1",
            is_superuser = True
        )

    def test_article_post_with_statusupdate_create_with_superuser(self):
        c = Client()
        c.login(username = "superone", password="TestSuper#1")
        response = c.post('/flaxarticles/article/create/', {
            'name':'Article One',
            'start':'1/1/2021',
            'statusupdate_set-TOTAL_FORMS':3,
            'statusupdate_set-INITIAL_FORMS':0,
            'statusupdate_set-MIN_NUM_FORMS':0,
            'statusupdate_set-MAX_NUM_FORMS':0,
            'statusupdate_set-0-when':'2021-11-19',
            'initial-statusupdate_set-0-when':'2021-11-19',
            'statusupdate_set-0-text':'Article Update One',
            'statusupdate_set-1-when':'2021-11-19',
            'initial-statusupdate_set-1-when':'2021-11-19',
            'statusupdate_set-1-text':'',
            'statusupdate_set-2-when':'2021-11-19',
            'initial-statusupdate_set-2-when':'2021-11-19',
            'statusupdate_set-2-text':'',
        })
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(StatusUpdate.objects.count(), 1)
        self.assertEqual(StatusUpdate.objects.first().article.pk, Article.objects.first().pk)

class ArticleUpdatestatusupdateFormsetTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.superuser = get_user_model().objects.create_user(
            username = "superone",
            password = "TestSuper#1",
            is_superuser = True
        )
        cls.article_one = Article.objects.create(
            name = 'Article one'
        )
        cls.statusupdate_one = StatusUpdate.objects.create(
            article = cls.article_one,
            text = 'Article Note One',
        )

    def test_article_post_with_statusupdate_update_with_superuser(self):
        c = Client()
        c.login(username = "superone", password="TestSuper#1")
        response = c.post('/flaxarticles/article/' + str(self.article_one.pk) + '/update/', {
            'name':'Article One Updated',
            'start':'1/1/2001',
            'statusupdate_set-TOTAL_FORMS':4,
            'statusupdate_set-INITIAL_FORMS':1,
            'statusupdate_set-MIN_NUM_FORMS':0,
            'statusupdate_set-MAX_NUM_FORMS':0,
            'statusupdate_set-0-id':self.statusupdate_one.pk,
            'statusupdate_set-0-article':self.article_one.pk,
            'statusupdate_set-0-when':'2021-11-19',
            'initial-statusupdate_set-0-when':'2021-11-19',
            'statusupdate_set-0-text':'Article Note One Updated',

            'statusupdate_set-1-Article':self.article_one.pk,
            'statusupdate_set-1-when':'2021-11-19',
            'initial-statusupdate_set-1-when':'2021-11-19',
            'statusupdate_set-1-text':'Article Note Two',

            'statusupdate_set-2-Article':self.article_one.pk,
            'statusupdate_set-2-when':'2021-11-19',
            'initial-statusupdate_set-2-when':'2021-11-19',
            'statusupdate_set-2-text':'',
            'statusupdate_set-3-when':'2021-11-19',
            'initial-statusupdate_set-3-when':'2021-11-19',
            'statusupdate_set-3-text':'',
        })
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(StatusUpdate.objects.count(), 2)
        self.assertEqual(StatusUpdate.objects.first().article.pk, Article.objects.first().pk)
        self.assertEqual(StatusUpdate.objects.all()[1].article.pk, Article.objects.first().pk)
