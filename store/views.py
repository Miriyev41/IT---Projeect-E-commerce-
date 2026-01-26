from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from django.db.models import Q
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from pgvector.django import CosineDistance

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('id')
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')

    # Price Filter Logic
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Pagination Logic
    product_count = products.count()
    paginator = Paginator(products, 9)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
   
    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    context = {
        'single_product': single_product,
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    products = Product.objects.none() # Default to empty
    product_count = 0
    keyword = request.GET.get('keyword')

    if keyword:
        # 1. AI SEMANTIC SEARCH
        # Convert user's keyword into a vector
        query_vector = ai_model.encode(keyword)

        # 2. HYBRID RETRIEVAL
        # Find products by semantic meaning OR by keyword match
        # We use a distance threshold (0.7) to keep results relevant
        products = Product.objects.annotate(
            distance=CosineDistance('embedding', query_vector)
        ).filter(
            Q(distance__lt=0.7) | # AI find (Concepts)
            Q(product_name__icontains=keyword) | # Keyword find (Names)
            Q(description__icontains=keyword),
            is_available=True
        ).order_by('distance') # Most relevant AI match first

        # 3. APPLY YOUR EXISTING FILTERS
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')

        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
        'keyword': keyword,
    }
    return render(request, 'store/store.html', context)
    }
    return render(request, 'store/store.html', context)