from rest_framework import serializers
from django.db.models import Avg
from .models import *


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'
  
        
class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Comment
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.EmailField(required=False)
    comments = CommentSerializer(many=True, read_only = True)
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        
    def create(self, validated_data):
        request = self.context.get('request')
        files_data = request.FILES
        product = Product.objects.create(**validated_data)

        for image in files_data.getlist('images'):
            Image.objects.create(product=product, image=image)  
        return product

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['likes'] = instance.likes.filter(like=True).count()
        rep['rating'] = instance.ratings.all().aggregate(Avg('rating'))['rating__avg']
        rep['favorite'] = instance.favorite.filter(favorite=True)
        return rep
    
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        print(instance)
        if not instance.parent:
            rep.pop('parent')
        return rep
        
        
class RatingSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Rating
        fields = ['rating']
