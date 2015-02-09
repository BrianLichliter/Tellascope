from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    bio = models.CharField(max_length=250, blank=True, null=True)
    profile_picture = models.CharField(max_length=250, blank=True, null=True)

    shared_articles = models.ManyToManyField('Article', through='UserArticleRelationship',
                                           symmetrical=False,
                                           related_name='shared_by')

    favorited_articles = models.ManyToManyField('Article', related_name='favorited_by')

    following = models.ManyToManyField('self', through='FollowRelationship',
                                           symmetrical=False,
                                           related_name='followed_by')

    topics_followed = models.ManyToManyField('Tag')

    twitter_username = models.CharField(max_length=50, blank=True, null=True)
    twitter_description = models.CharField(max_length=250, blank=True, null=True)
    twitter_profile_picture = models.CharField(max_length=250, blank=True, null=True)

    def __unicode__(self):
        return self.user.username

    def share_article(self, article, comment=''):
    	share, created = UserArticleRelationship.objects.get_or_create(
        	sharer=self,
        	article=article,
        	comment=comment)
    	return share

    def unshare_article(self, article):
    	UserArticleRelationship.objects.filter(
        	sharer=self,
        	article=article).delete()
    	return

    def follow_user(self, profile):
    	relationship, created = FollowRelationship.objects.get_or_create(
    		follower=self,
    		followee=profile)
    	return relationship

    def unfollow_user(self, profile):
    	FollowRelationship.objects.filter(
    		follower=self,
    		folowee=profile).delete()
    	return

    def get_following(self):
    	return self.following.filter(followees__follower=self)
    
    def get_followers(self):
    	return self.followed_by.filter(followers__follower=self)

	def get_mutual_followers(self):
		return self.following.filter(
			folowees__follower=self,
			followers__followee=self)

class Tag(TagBase):
	pass

class TaggedArticle(GenericTaggedItemBase):
	tag = models.ForeignKey('Tag', related_name="%(class)s_items")

class Source(models.Model):
	name = models.CharField(max_length=250, blank=True)
	url = models.URLField(blank=True)

	def __unicode__(self):
		return self.name


class Author(models.Model):
	name = models.CharField(max_length=100, blank=True)

	def __unicode__(self):
		return self.name

class Article(models.Model):
	url = models.URLField(blank=False, null=True)
	title = models.CharField(max_length=500, blank=False, null=True)
	source = models.ForeignKey('Source', blank=True, null=True, 
									related_name='articles_from_source')
	author = models.ForeignKey('Author', blank=True, null=True, 
									related_name='articles_by_author')
	tags = TaggableManager(through=TaggedArticle, blank=True)

	def __unicode__(self):
		return self.title


class UserArticleRelationship(models.Model):
	sharer = models.ForeignKey('UserProfile', related_name='shared_by')
	article = models.ForeignKey('Article', related_name='shared_article')
	comment = models.CharField(max_length=250, blank=True, null=True)
	shared_datetime = models.DateTimeField(auto_now_add=True)

class FollowRelationship(models.Model):
	follower = models.ForeignKey('UserProfile', related_name='followers')
	followee = models.ForeignKey('UserProfile', related_name='followees')
	created_at = models.DateTimeField(auto_now_add=True)


