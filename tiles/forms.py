from django import forms


class ChatForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 1, 'placeholder': 'Ask about tiles, markets, locations...',
        'class': 'w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 resize-none'
    }), label='')


class ImageGenerateForm(forms.Form):
    prompt = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 3, 'placeholder': 'Describe tile design... e.g., "White marble porcelain tile with grey veins, glossy, 600x600mm"',
        'class': 'w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 resize-none'
    }), label='')
    style = forms.ChoiceField(choices=[
        ('realistic', 'Realistic'), ('artistic', 'Artistic'),
        ('minimalist', 'Minimalist'), ('luxury', 'Luxury'), ('industrial', 'Industrial'),
    ], widget=forms.Select(attrs={
        'class': 'w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20'
    }), label='Style', required=False)


from django import forms


class TileSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search tiles by name, material, effect...',
            'class': 'w-full rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20'
        }),
        label=''
    )

    category = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories')],
        widget=forms.Select(attrs={
            'class': 'rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20'
        }),
        label=''
    )

    country = forms.ChoiceField(
        required=False,
        choices=[('', 'All Countries')],
        widget=forms.Select(attrs={
            'class': 'rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20'
        }),
        label=''
    )

    tile_type = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Types'),
            ('floor', 'Floor Tiles'),
            ('wall', 'Wall Tiles'),
            ('both', 'Floor & Wall'),
            ('special', 'Special Purpose'),
        ],
        widget=forms.Select(attrs={
            'class': 'rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20'
        }),
        label=''
    )

    usage_type = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Usage'),
            ('residential', 'Residential'),
            ('commercial', 'Commercial'),
        ],
        widget=forms.Select(attrs={
            'class': 'rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20'
        }),
        label=''
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        from .models import TileCategory, Country

        # Load categories
        self.fields['category'].choices = [
            ('', 'All Categories')
        ] + [
            (c.slug, c.name) for c in TileCategory.objects.all()
        ]

        # Load countries
        self.fields['country'].choices = [
            ('', 'All Countries')
        ] + [
            (c.slug, c.name) for c in Country.objects.all()
        ]

from django import forms
from .models import UserProfile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["profile_picture"]