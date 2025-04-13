from modeltranslation.translator import register, TranslationOptions
from .models import Category, Tag, Article, Story, Landmark, Image, Video

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'summary')

@register(Story)
class StoryTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'summary', 'location', 'period')

@register(Landmark)
class LandmarkTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'summary', 'location', 'historical_period')

@register(Image)
class ImageTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'alt_text')

@register(Video)
class VideoTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
