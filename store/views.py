from django.shortcuts import render, get_object_or_404
from .models import Product, ai_model
from category.models import Category
from django.db.models import Q
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from pgvector.django import CosineDistance 
from spellchecker import SpellChecker 

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True)

    # --- SORTING LOGIC ---
    sort_by = request.GET.get('sort')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name_az':
        products = products.order_by('product_name')
    elif sort_by == 'name_za':
        products = products.order_by('-product_name')
    elif sort_by == 'newest':
        products = products.order_by('-created_date')
    else:
        products = products.order_by('id') 

    # Price Filter Logic
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

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
    keyword = request.GET.get('keyword')
    sort_by = request.GET.get('sort')
    suggestion = None
    products = Product.objects.none()

    if keyword:
        spell = SpellChecker()
        
        # 1. Get all hardware-specific words from your database
        store_terms = list(Product.objects.values_list('product_name', flat=True))
        category_terms = list(Category.objects.values_list('category_name', flat=True))
        
        hardware_words = set()
        for term in store_terms + category_terms:
            hardware_words.update(term.lower().split())

        word_list = keyword.lower().split()
        corrected_words = []

        for w in word_list:
            if w in hardware_words:
                corrected_words.append(w)
            else:
                hardware_suggestion = spell.candidates(w)
                best_match = None
                if hardware_suggestion:
                    for candidate in hardware_suggestion:
                        if candidate in hardware_words:
                            best_match = candidate
                            break

                if best_match:
                    corrected_words.append(best_match)
                else:
                    cor = spell.correction(w)
                    corrected_words.append(cor if cor else w)

        suggestion_word = " ".join(corrected_words)

        if suggestion_word.lower() != keyword.lower():
            suggestion = suggestion_word

        query_vector = ai_model.encode(keyword)
        
        products = Product.objects.annotate(
            distance=CosineDistance('embedding', query_vector)
        ).filter(
            Q(distance__lt=0.68) | 
            Q(product_name__icontains=keyword) | 
            Q(description__icontains=keyword),
            is_available=True
        )

        if sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'name_az':
            products = products.order_by('product_name')
        elif sort_by == 'name_za':
            products = products.order_by('-product_name')
        elif sort_by == 'newest':
            products = products.order_by('-created_date')
        else:
            products = products.order_by('distance') 

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price: products = products.filter(price__gte=min_price)
    if max_price: products = products.filter(price__lte=max_price)

    product_count = products.count()
    paginator = Paginator(products, 9)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'product_count': product_count,
        'keyword': keyword,
        'suggestion': suggestion,
    }
    return render(request, 'store/store.html', context)