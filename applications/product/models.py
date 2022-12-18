from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Category(models.Model):
    name = models.SlugField(primary_key=True)
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    
    def __str__(self) -> str:
        return self.name
    

class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product')
    title = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-id']
    
    
class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')
    
    def __str__(self):
        return self.product
        

class Comment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='comments', null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return f'{self.owner.username} {self.product.title}'

    
class Like(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes') 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='likes')
    like = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f'{self.owner} - {self.like}'

    
class Rating(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    rating = models.SmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ], blank=True, null=True
    )
    
    def __str__(self) -> str:
        return f'{self.owner} - {self.rating}'
    
    
class Favorite(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite') 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorite')
    favorite = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f'{self.owner} - {self.favorite}'
