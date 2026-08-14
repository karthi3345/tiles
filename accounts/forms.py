from django import forms
from tiles.models import UserProfile, Country, City


class ProfileForm(forms.ModelForm):
    country = forms.ModelChoiceField(
        queryset=Country.objects.all().order_by("name"),
        required=False,
        widget=forms.Select(attrs={"class": "profile-select"}),
        empty_label="Select your country",
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "profile-select"}),
        empty_label="Select your city",
    )

    class Meta:
        model = UserProfile
        fields = ["profile_picture", "country", "city"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit city choices to the selected country (or the instance's country)
        country = None
        if self.instance and self.instance.pk and self.instance.country:
            country = self.instance.country
        if "country" in self.data:
            try:
                country_id = int(self.data.get("country"))
                country = Country.objects.filter(pk=country_id).first()
            except (TypeError, ValueError):
                country = None
        if country:
            self.fields["city"].queryset = City.objects.filter(
                state__country=country
            ).select_related("state").order_by("state__name", "name")
        else:
            self.fields["city"].queryset = City.objects.select_related(
                "state__country"
            ).order_by("state__country__name", "name")
