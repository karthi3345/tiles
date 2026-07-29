import json
import uuid
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import cloudinary.uploader


from .models import (
    Country, State, City, Village,
    TileCategory, TileEffect, TileFinish, TileSize, TileProduct,
    MarketInsight, ChatSession, ChatMessage, GeneratedImage
)
from .forms import ChatForm, ImageGenerateForm, TileSearchForm
from .services.ai_chat import chat_service
from .services.image_gen import image_gen_service


def _build_breadcrumbs(items):
    return items


def _get_tiles_for_country(country):
    qs = TileProduct.objects.filter(
        countries=country, is_active=True
    ).select_related('category').prefetch_related('effects', 'finishes', 'sizes')
    if not qs.exists():
        qs = TileProduct.objects.filter(is_active=True).select_related('category').prefetch_related('effects', 'finishes', 'sizes')
    return qs


def _build_tile_prompt(tile):
    parts = []
    effects = [e.name.lower() for e in tile.effects.all()[:3]]
    if effects:
        parts.append(', '.join(effects))
    if tile.material:
        parts.append(tile.material.lower())
    finishes = [f.name.lower() for f in tile.finishes.all()[:2]]
    if finishes:
        parts.append(', '.join(finishes))
    sizes = list(tile.sizes.all()[:1])
    if sizes:
        s = sizes[0]
        parts.append(f'{s.width_mm}x{s.height_mm}mm')
    if tile.category:
        parts.append(tile.category.name.lower())
    return ' '.join(parts)


def upload_to_cloudinary(image_file):
    print("UPLOAD FILE:", image_file)
    print("FILE NAME:", image_file.name if hasattr(image_file, 'name') else 'In-Memory File')

    result = cloudinary.uploader.upload(
        image_file,
        folder="tiles/generated",
        resource_type="image"
    )

    print("CLOUDINARY RESULT:")
    print(result)

    return result["secure_url"]


# ─────────── HOME ───────────

def home(request):
    countries = Country.objects.all()[:10]
    categories = TileCategory.objects.all()
    total_tiles = TileProduct.objects.filter(is_active=True).count()
    total_locations = Village.objects.count() + City.objects.count() + State.objects.count()
    return render(request, 'tiles/home.html', {
        'countries': countries,
        'categories': categories,
        'total_tiles': total_tiles,
        'total_locations': total_locations,
        'total_countries': countries.count(),
    })


# ─────────── LOCATION BROWSING ───────────

def countries_list(request):
    countries = Country.objects.all().annotate(state_count=Count('states'))
    breadcrumbs = _build_breadcrumbs([('All Countries', None)])
    return render(request, 'tiles/locations/countries.html', {
        'countries': countries, 'breadcrumbs': breadcrumbs,
    })


def states_list(request, country_slug):
    country = get_object_or_404(Country, slug=country_slug)
    states = country.states.all().annotate(annotated_city_count=Count('cities'))
    tiles = _get_tiles_for_country(country)[:12]
    breadcrumbs = _build_breadcrumbs([
        ('All Countries', '/locations/'),
        (country.name, None),
    ])
    return render(request, 'tiles/locations/states.html', {
        'country': country, 'states': states, 'tiles': tiles, 'breadcrumbs': breadcrumbs,
    })


def cities_list(request, country_slug, state_slug):
    country = get_object_or_404(Country, slug=country_slug)
    state = get_object_or_404(State, slug=state_slug, country=country)
    cities = state.cities.all().annotate(annotated_village_count=Count('villages'))
    tiles = _get_tiles_for_country(country)[:12]
    breadcrumbs = _build_breadcrumbs([
        ('All Countries', '/locations/'),
        (country.name, f'/locations/{country.slug}/'),
        (state.name, None),
    ])
    return render(request, 'tiles/locations/cities.html', {
        'country': country, 'state': state, 'cities': cities,
        'tiles': tiles, 'breadcrumbs': breadcrumbs,
    })


def villages_list(request, country_slug, state_slug, city_slug):
    country = get_object_or_404(Country, slug=country_slug)
    state = get_object_or_404(State, slug=state_slug, country=country)
    city = get_object_or_404(City, slug=city_slug, state=state)
    villages = city.villages.all()
    tiles = _get_tiles_for_country(country)
    breadcrumbs = _build_breadcrumbs([
        ('All Countries', '/locations/'),
        (country.name, f'/locations/{country.slug}/'),
        (state.name, f'/locations/{country.slug}/{state.slug}/'),
        (city.name, None),
    ])
    return render(request, 'tiles/locations/villages.html', {
        'country': country, 'state': state, 'city': city,
        'villages': villages, 'tiles': tiles, 'village': None,
        'showrooms': [], 'breadcrumbs': breadcrumbs,
    })


def village_tiles(request, country_slug, state_slug, city_slug, village_slug):
    country = get_object_or_404(Country, slug=country_slug)
    state = get_object_or_404(State, slug=state_slug, country=country)
    city = get_object_or_404(City, slug=city_slug, state=state)
    village = get_object_or_404(Village, slug=village_slug, city=city)

    tiles = _get_tiles_for_country(country)
    showrooms = village.showrooms.filter(is_active=True)

    breadcrumbs = _build_breadcrumbs([
        ('All Countries', '/locations/'),
        (country.name, None),
        (state.name, None),
        (city.name, None),
        (village.name, None),
    ])

    return render(
        request,
        'tiles/locations/villages.html',
        {
            'country': country,
            'state': state,
            'city': city,
            'village': village,
            'villages': [],
            'tiles': tiles,
            'showrooms': showrooms,
            'breadcrumbs': breadcrumbs,
        }
    )


# ─────────── TILE CATALOG ───────────

def tile_catalog(request):
    form = TileSearchForm(request.GET or None)

    tiles = TileProduct.objects.filter(
        is_active=True
    ).select_related(
        'category'
    ).prefetch_related(
        'effects',
        'finishes',
        'sizes',
        'countries'
    )

    query = request.GET.get('query', '')
    cat_slug = request.GET.get('category', '')
    tile_type = request.GET.get('tile_type', '')
    country_slug = request.GET.get('country', '')
    usage_type = request.GET.get('usage_type', '')

    if usage_type:
        tiles = tiles.filter(category__usage_type=usage_type)

    if query:
        tiles = tiles.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(material__icontains=query) |
            Q(effects__name__icontains=query)
        ).distinct()

    if cat_slug:
        tiles = tiles.filter(category__slug=cat_slug)

    if tile_type:
        tiles = tiles.filter(category__tile_type=tile_type)

    if country_slug:
        tiles = tiles.filter(countries__slug=country_slug).distinct()

    breadcrumbs = _build_breadcrumbs([
        ('Tile Catalog', None)
    ])

    return render(
        request,
        'tiles/tiles/catalog.html',
        {
            'tiles': tiles,
            'form': form,
            'query': query,
            'total': tiles.count(),
            'breadcrumbs': breadcrumbs,
        }
    )
def tile_detail(request, slug):
    tile = get_object_or_404(TileProduct, slug=slug, is_active=True)
    related = TileProduct.objects.filter(
        category=tile.category, is_active=True
    ).exclude(pk=tile.pk)[:8]
    breadcrumbs = _build_breadcrumbs([
        ('Tile Catalog', '/tiles/'),
        (tile.name, None),
    ])
    return render(request, 'tiles/tiles/detail.html', {
        'tile': tile, 'related': related, 'breadcrumbs': breadcrumbs,
    })


# ─────────── TILE IMAGE GENERATION ───────────

@login_required
def generate_single_tile_image(request, slug):
    tile = get_object_or_404(TileProduct, slug=slug, is_active=True)

    if not image_gen_service.is_configured():
        messages.error(request, 'Cloudflare AI not configured. Set CF_ACCOUNT_ID and CF_API_TOKEN in .env')
        return redirect('tiles:tile_detail', slug=slug)

    prompt = _build_tile_prompt(tile)
    result = image_gen_service.generate(prompt)

    if result['success'] and result['image_file']:
        # Upload to Cloudinary and get the URL
        image_url = upload_to_cloudinary(result['image_file'])

        # Save the Cloudinary URL to the database
        tile.image = image_url
        tile.save(update_fields=['image'])

        messages.success(request, f'Design generated for {tile.name}!')
    else:
        messages.error(
            request,
            result.get('error', 'Generation failed. Check Cloudflare credentials.')
        )

    # CRITICAL: Must redirect back to the page at the end
    return redirect('tiles:tile_detail', slug=slug)


@login_required
def generate_all_tile_images(request):
    if not image_gen_service.is_configured():
        messages.error(request, 'Cloudflare AI not configured. Set CF_ACCOUNT_ID and CF_API_TOKEN in .env')
        return redirect('tiles:tile_catalog')

    if request.method == 'POST':
        products = TileProduct.objects.filter(is_active=True)

        if request.POST.get('category'):
            products = products.filter(category__slug=request.POST.get('category'))
        if request.POST.get('force') != 'on':
            products = products.filter(image__isnull=True)

        limit = int(request.POST.get('limit', 0))
        if limit > 0:
            products = products[:limit]

        total = products.count()
        if total == 0:
            messages.info(request, 'No tiles need generation.')
            return redirect('tiles:generate_all_images')

        generated = 0
        failed = 0
        for tile in products:
            prompt = _build_tile_prompt(tile)
            result = image_gen_service.generate(prompt)
            
            if result['success'] and result['image_file']:
                # Upload to Cloudinary instead of saving locally
                image_url = upload_to_cloudinary(result['image_file'])
                
                # Save the URL
                tile.image = image_url
                tile.save(update_fields=['image'])
                generated += 1
            else:
                failed += 1
            time.sleep(1)

        messages.success(request, f'Generated {generated} designs, {failed} failed (of {total} total)')
        return redirect('tiles:generate_all_images')

    categories = TileCategory.objects.all()
    missing_count = TileProduct.objects.filter(is_active=True, image__isnull=True).count()
    total = TileProduct.objects.filter(is_active=True).count()
    with_image = total - missing_count
    tiles_without_images = TileProduct.objects.filter(is_active=True, image__isnull=True)[:30]

    breadcrumbs = _build_breadcrumbs([
        ('Tile Catalog', '/tiles/'),
        ('Generate Designs', None),
    ])
    return render(request, 'tiles/tiles/generate_designs.html', {
        'categories': categories,
        'missing': missing_count,
        'total': total,
        'with_image': with_image,
        'tiles_without_images': tiles_without_images,
        'breadcrumbs': breadcrumbs,
    })


# ─────────── AI CHAT ───────────

@csrf_exempt
@login_required(login_url='accounts:login')
def chat_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id', '')
        except json.JSONDecodeError:
            data = request.POST
            message = data.get('message', '').strip()
            session_id = data.get('session_id', '')

        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        if not session_id:
            session_id = str(uuid.uuid4())
            session = ChatSession.objects.create(session_id=session_id, title=message[:100])
        else:
            session, _ = ChatSession.objects.get_or_create(session_id=session_id)
            if not session.title:
                session.title = message[:100]
                session.save()

        ChatMessage.objects.create(session=session, role='user', content=message)

        chat_history_qs = list(session.messages.all()[:11])
        history = [
            {"role": m.role, "content": m.content}
            for m in chat_history_qs[:-1]
        ]

        result = chat_service.chat(message, history)
        print("=" * 60)
        print("CHAT RESULT")
        print(result)
        print("=" * 60)

        if result["success"]:
            response = result.get("response")
            if not response:
                response = "Sorry, AI returned an empty response."

            ChatMessage.objects.create(
                session=session,
                role="assistant",
                content=response
            )

            return JsonResponse({
                "success": True,
                "response": response,
                "session_id": session_id
            })
        else:
            error_msg = result.get("error", "Sorry, something went wrong while generating a response.")
            return JsonResponse({
                "success": False,
                "error": error_msg,
                "session_id": session_id
            }, status=502)

    breadcrumbs = _build_breadcrumbs([('AI Chat', None)])
    return render(request, 'tiles/chat.html', {'form': ChatForm(), 'breadcrumbs': breadcrumbs})


# ─────────── IMAGE GENERATION ───────────

@login_required(login_url='accounts:login')
def generate_image_view(request):
    images = GeneratedImage.objects.filter(user=request.user)
    form = ImageGenerateForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            prompt = form.cleaned_data.get('prompt')
            style = form.cleaned_data.get('style', 'realistic')

            result = image_gen_service.generate(prompt, style)

            if result['success'] and result.get('image_file'):
                # Upload to Cloudinary
                image_url = upload_to_cloudinary(result['image_file'])

                # Save URL to database
                GeneratedImage.objects.create(
                    user=request.user,
                    prompt=f"[{style}] {prompt}",
                    image=image_url,
                    model_used=image_gen_service.model,
                )

                messages.success(request, 'Tile design generated successfully!')
                return redirect('tiles:generate_image')
            else:
                messages.error(request, result.get('error', 'Generation failed'))

    breadcrumbs = _build_breadcrumbs([('Generate Image', None)])

    return render(
        request,
        'tiles/generate_image.html',
        {
            'form': form,
            'generated_images': images,
            'breadcrumbs': breadcrumbs,
        }
    )


# ─────────── LOCATION SEARCH API ───────────

def location_search(request):
    q = request.GET.get('q', '')
    if not q or len(q) < 2:
        return JsonResponse({'results': []})
    results = []
    for v in Village.objects.filter(name__icontains=q)[:8]:
        results.append({
            'type': 'village', 'name': v.name,
            'path': f"/locations/{v.country.slug}/{v.state.slug}/{v.city.slug}/{v.slug}/",
            'parent': f"{v.city.name}, {v.state.name}, {v.country.flag_emoji} {v.country.name}"
        })
    for c in City.objects.filter(name__icontains=q)[:8]:
        results.append({
            'type': 'city', 'name': c.name,
            'path': f"/locations/{c.country.slug}/{c.state.slug}/{c.slug}/",
            'parent': f"{c.state.name}, {c.country.flag_emoji} {c.country.name}"
        })
    for s in State.objects.filter(name__icontains=q)[:5]:
        results.append({
            'type': 'state', 'name': s.name,
            'path': f"/locations/{s.country.slug}/{s.slug}/",
            'parent': f"{s.country.flag_emoji} {s.country.name}"
        })
    return JsonResponse({'results': results})



#-------------Download IMages----------------

from io import BytesIO

import requests
from PIL import Image

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required


@login_required
def download_generated_image(request, pk):
    image = get_object_or_404(
        GeneratedImage,
        id=pk,
        user=request.user
    )

    response = requests.get(image.image)

    if response.status_code != 200:
        return HttpResponse("Image not found.", status=404)

    # Settings from modal
    width = int(request.GET.get("width", 1200))
    height = int(request.GET.get("height", 1200))
    dpi = int(request.GET.get("dpi", 300))
    fmt = request.GET.get("format", "png").lower()
    quality = int(request.GET.get("quality", 100))
    filename = request.GET.get("filename", f"tile-{pk}")

    # Open image
    img = Image.open(BytesIO(response.content)).convert("RGB")

    # Resize
    img = img.resize((width, height), Image.LANCZOS)

    output = BytesIO()

    if fmt == "jpg":
        img.save(
            output,
            format="JPEG",
            quality=quality,
            dpi=(dpi, dpi),
            optimize=True,
        )
        content_type = "image/jpeg"
        extension = "jpg"

    elif fmt == "webp":
        img.save(
            output,
            format="WEBP",
            quality=quality,
            method=6,
        )
        content_type = "image/webp"
        extension = "webp"

    else:
        img.save(
            output,
            format="PNG",
            dpi=(dpi, dpi),
        )
        content_type = "image/png"
        extension = "png"

    output.seek(0)

    download = HttpResponse(output.getvalue(), content_type=content_type)
    download["Content-Disposition"] = (
        f'attachment; filename="{filename}.{extension}"'
    )

    return download