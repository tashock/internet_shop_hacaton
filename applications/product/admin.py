from django.contrib import admin
from .models import (
    Product, Category, Image, Comment, Rating, Like, Favorite
)


class ImageAdmin(admin.TabularInline):
    model = Image
    fields = ('image',)
    max_num = 10


class PostAdmin(admin.ModelAdmin):
    inlines = [
        ImageAdmin
    ]
    list_display = ['id', 'title', 'product_count_like']
    
    def post_count_like(self, obj):
        return obj.likes.filter(like=True).count()


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Image)
admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(Like)
admin.site.register(Favorite)
