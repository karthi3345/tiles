"""
Populate latitude/longitude for all seeded City records.

Usage:
    python manage.py seed_coordinates
"""
from django.core.management.base import BaseCommand
from tiles.models import City


# Real-world coordinates for every city in the seed data.
# Format: "City Name": (latitude, longitude)
CITY_COORDS = {
    # ── Brazil ──
    "Belo Horizonte": (-19.9167, -43.9345),
    "Campinas": (-22.9099, -47.0626),
    "Criciuma": (-28.6772, -49.3717),
    "Joinville": (-26.3045, -48.8487),
    "Orleans": (-28.3547, -49.3000),
    "Petropolis": (-22.5050, -43.1786),
    "Rio de Janeiro": (-22.9068, -43.1729),
    "Sao Paulo": (-23.5505, -46.6333),
    "Sorocaba": (-23.5015, -47.4526),
    "Tubarao": (-28.4667, -49.0067),
    "Uberlandia": (-18.9186, -48.2772),

    # ── China ──
    "Chengdu": (30.5728, 104.0668),
    "Deyang": (31.1270, 104.3980),
    "Dongguan": (23.0207, 113.7518),
    "Foshan": (23.0218, 113.1219),
    "Guangzhou": (23.1291, 113.2644),
    "Hangzhou": (30.2741, 120.1551),
    "Jinan": (36.6512, 117.1201),
    "Jingdezhen": (29.2687, 117.1784),
    "Jinjiang": (24.7817, 118.5539),
    "Nanchang": (28.6820, 115.8579),
    "Qingdao": (36.0671, 120.3826),
    "Quanzhou": (24.8741, 118.6757),
    "Shenzhen": (22.5431, 114.0579),
    "Wenzhou": (27.9938, 120.6993),
    "Xiamen": (24.4798, 118.0894),
    "Zhaoqing": (23.0515, 112.4658),
    "Zibo": (36.8131, 118.0548),

    # ── India ──
    "Agra": (27.1767, 78.0081),
    "Ahmedabad": (23.0225, 72.5714),
    "Bangalore": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Coimbatore": (11.0168, 76.9558),
    "Hubli": (15.3647, 75.1240),
    "Hyderabad": (17.3850, 78.4867),
    "Jaipur": (26.9124, 75.7873),
    "Jodhpur": (26.2389, 73.0243),
    "Kishangarh": (26.5728, 74.9700),
    "Kochi": (9.9312, 76.2673),
    "Kozhikode": (11.2588, 75.7804),
    "Lucknow": (26.8467, 80.9462),
    "Madurai": (9.9252, 78.1198),
    "Morbi": (22.8167, 70.8333),
    "Mumbai": (19.0760, 72.8777),
    "Mysore": (12.2958, 76.6394),
    "Nagpur": (21.1458, 79.0882),
    "Nashik": (19.9975, 73.7898),
    "Noida": (28.5355, 77.3910),
    "Pune": (18.5204, 73.8567),
    "Rajkot": (22.3039, 70.8022),
    "Salem": (11.6643, 78.1460),
    "Surat": (21.1702, 72.8311),
    "Thiruvananthapuram": (8.5241, 76.9366),
    "Udaipur": (24.5854, 73.7125),
    "Vadodara": (22.3072, 73.1812),
    "Varanasi": (25.3176, 82.9739),
    "Warangal": (17.9689, 79.5941),

    # ── Indonesia ──
    "Bandung": (-6.9175, 107.6191),
    "Bekasi": (-6.2383, 106.9756),
    "Bogor": (-6.5950, 106.8166),
    "Depok": (-6.4025, 106.7942),
    "Gresik": (-7.1567, 112.6547),
    "Jakarta Barat": (-6.1600, 106.7700),
    "Jakarta Pusat": (-6.1800, 106.8300),
    "Jakarta Selatan": (-6.2700, 106.8200),
    "Malang": (-7.9666, 112.6326),
    "Semarang": (-6.9667, 110.4167),
    "Serang": (-6.1200, 106.1500),
    "Solo (Surakarta)": (-7.5755, 110.8243),
    "Surabaya": (-7.2575, 112.7521),
    "Tangerang": (-6.1700, 106.6400),

    # ── Italy ──
    "Bergamo": (45.6983, 9.6773),
    "Bologna": (44.4949, 11.3426),
    "Florence": (43.7696, 11.2558),
    "Milan": (45.4642, 9.1900),
    "Prato": (43.8797, 11.0967),
    "Reggio Emilia": (44.6989, 10.6308),
    "Sassuolo": (44.5800, 10.7800),
    "Treviso": (45.6669, 12.2436),
    "Verona": (45.4384, 10.9916),

    # ── Mexico ──
    "Guadalajara": (20.6597, -103.3496),
    "Monterrey": (25.6866, -100.3161),
    "Puebla": (19.0414, -98.2063),
    "San Nicolas de los Garza": (25.7420, -100.3020),
    "Tlaquepaque": (20.6400, -103.2900),
    "Veracruz": (19.1810, -96.1341),
    "Xalapa": (19.5438, -96.9102),
    "Zapopan": (20.7167, -103.4000),

    # ── Spain ──
    "Alicante": (38.3452, -0.4810),
    "Barcelona": (41.3851, 2.1734),
    "Castellon de la Plana": (39.9864, -0.0513),
    "Malaga": (36.7213, -4.4214),
    "Seville": (37.3891, -5.9845),
    "Tarragona": (41.1189, 1.2445),
    "Valencia": (39.4699, -0.3763),

    # ── Turkey ──
    "Bilecik Merkez": (40.1426, 29.9793),
    "Bozuyuk": (39.9080, 29.9250),
    "Istanbul Asian Side": (41.0082, 29.0400),
    "Istanbul European Side": (41.0420, 28.9700),
    "Izmir Merkez": (38.4237, 27.1428),
    "Kutahya Merkez": (39.4242, 29.9833),
    "Sogut": (40.0230, 30.1830),
    "Tavsanli": (39.5450, 29.4870),

    # ── United States ──
    "Austin": (30.2672, -97.7431),
    "Chicago": (41.8781, -87.6298),
    "Dallas": (32.7767, -96.7970),
    "Houston": (29.7604, -95.3698),
    "Jersey City": (40.7178, -74.0431),
    "Los Angeles": (34.0522, -118.2437),
    "Miami": (25.7617, -80.1918),
    "New York City": (40.7128, -74.0060),
    "Newark": (40.7357, -74.1723),
    "Orlando": (28.5383, -81.3792),
    "San Diego": (32.7157, -117.1611),
    "San Francisco": (37.7749, -122.4194),

    # ── Vietnam ──
    "Bien Hoa": (10.9430, 106.8240),
    "Binh Thanh": (10.8100, 106.7000),
    "Cau Giay": (21.0285, 105.7820),
    "Di An": (10.8700, 106.8500),
    "District 1": (10.7731, 106.7026),
    "District 7": (10.7320, 106.7210),
    "Ha Dong": (20.9600, 105.7600),
    "Hoan Kiem": (21.0285, 105.8542),
    "Long Khanh": (10.9500, 107.2400),
    "Tan Uyen": (11.0500, 106.7500),
    "Thu Dau Mot": (10.9800, 106.6500),
}


class Command(BaseCommand):
    help = 'Populate latitude/longitude coordinates for all seeded cities'

    def handle(self, *args, **options):
        updated = 0
        skipped = 0
        missing = []

        for city in City.objects.select_related('state__country').all():
            coords = CITY_COORDS.get(city.name)
            if coords:
                city.latitude = coords[0]
                city.longitude = coords[1]
                city.save(update_fields=['latitude', 'longitude'])
                updated += 1
            else:
                missing.append(f"{city.name}, {city.state.country.name}")
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'Coordinates updated for {updated} cities.'
        ))
        if skipped:
            self.stdout.write(self.style.WARNING(
                f'{skipped} cities had no coordinate mapping:'
            ))
            for m in missing:
                self.stdout.write(f'  - {m}')
