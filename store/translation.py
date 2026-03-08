from modeltranslation.translator import register, TranslationOptions
from .models import Category, Product, Page, HeroSlide, SiteSettings, PaymentMethod, Coupon

# @register(Category)
# class CategoryTranslationOptions(TranslationOptions):
#     fields = ('name',)

# @register(Product)
# class ProductTranslationOptions(TranslationOptions):
#     fields = ('name', 'description', 'specs')

@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

@register(HeroSlide)
class HeroSlideTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'button_text')

