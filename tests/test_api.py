from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from content.models import Category, Tag, Article

class ArticleAPITestCase(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='testuser@example.com', 
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create admin user
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            role=User.ROLE_ADMIN,
            is_staff=True
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            description='A test category'
        )
        
        # Create test tag
        self.tag = Tag.objects.create(
            name='Test Tag',
            slug='test-tag'
        )
        
        # Create a published article
        self.article = Article.objects.create(
            title='Published Article',
            slug='published-article',
            content='This is a published article',
            summary='Published article summary',
            user=self.admin,
            category=self.category,
            status='published',
            is_published=True
        )
        self.article.tags.add(self.tag)
        
        # Create a draft article
        self.draft_article = Article.objects.create(
            title='Draft Article',
            slug='draft-article',
            content='This is a draft article',
            summary='Draft article summary',
            user=self.user,
            category=self.category,
            status='draft',
            is_published=False
        )
        
        # Get article list URL
        self.article_list_url = reverse('article-list')
        
        # URL for article detail
        self.article_detail_url = reverse('article-detail', kwargs={'slug': self.article.slug})
        self.draft_article_detail_url = reverse('article-detail', kwargs={'slug': self.draft_article.slug})
    
    def test_can_get_published_articles_without_auth(self):
        """Unauthenticated users can see published articles"""
        response = self.client.get(self.article_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only published articles should be visible
    
    def test_cannot_get_draft_articles_without_auth(self):
        """Unauthenticated users cannot see draft articles"""
        response = self.client.get(self.draft_article_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_author_can_see_own_draft(self):
        """Authors can see their own drafts"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.draft_article_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_article_authenticated(self):
        """Authenticated users can create articles"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Article',
            'slug': 'new-article',
            'content': 'This is a new article',
            'summary': 'New article summary',
            'category': self.category.id,
            'tag_ids': [self.tag.id]
        }
        response = self.client.post(self.article_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_submit_for_review(self):
        """Authors can submit their articles for review"""
        self.client.force_authenticate(user=self.user)
        url = reverse('article-submit-for-review', kwargs={'slug': self.draft_article.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if the status has been updated
        self.draft_article.refresh_from_db()
        self.assertEqual(self.draft_article.status, 'submitted')
    
    def test_admin_can_approve_content(self):
        """Admins can approve submitted content"""
        # First submit the article for review
        self.draft_article.status = 'submitted'
        self.draft_article.save()
        
        # Now try to approve it as admin
        self.client.force_authenticate(user=self.admin)
        url = reverse('moderation-approve-content')
        data = {
            'content_type': 'article',
            'object_id': self.draft_article.id,
            'comment': 'Looks good!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if the status has been updated
        self.draft_article.refresh_from_db()
        self.assertEqual(self.draft_article.status, 'approved')
