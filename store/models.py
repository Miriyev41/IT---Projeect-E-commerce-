from django.db import models
from category.models import Category
from django.urls import reverse
from pgvector.django import VectorField
from sentence_transformers import SentenceTransformer

ai_model = SentenceTransformer('all-MiniLM-L6-v2')

class Product(models.Model):
    product_name    = models.CharField(max_length=100, unique=True)
    slug            = models.CharField(max_length=100, unique=True)
    description     = models.TextField(max_length=600, blank=True)
    price           = models.IntegerField()
    images          = models.ImageField(upload_to='photo/products')
    stock           = models.IntegerField()
    is_available    = models.BooleanField(default=True)
    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)

    embedding = VectorField(dimensions=384, null=True, blank=True)

    def save(self, *args, **kwargs):
        text_to_embed = f"{self.product_name} {self.description}" 
        self.embedding = ai_model.encode(text_to_embed) 
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name
    
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])