"""Populate the database with realistic AquaCare sample data.

Usage:  python manage.py seed_data
The command is idempotent - running it twice will not duplicate records.
"""

from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import CompanyInfo, FAQ, Statistic, Testimonial
from products.models import Category, Product
from services.models import AMCPlan, Service, Technician

CATEGORIES = [
    ("RO Water Purifiers", "domestic", "bi-droplet-fill",
     "Reverse osmosis purifiers that reduce dissolved salts, heavy metals and hardness."),
    ("UV Water Purifiers", "domestic", "bi-lightbulb",
     "Ultraviolet purifiers that deactivate bacteria and viruses in low-TDS water."),
    ("RO + UV + UF Purifiers", "domestic", "bi-layers",
     "Multi-stage purification combining RO, UV and ultrafiltration for all-round safety."),
    ("Alkaline RO Purifiers", "domestic", "bi-star",
     "RO systems with mineral and alkaline cartridges that restore essential minerals."),
    ("Commercial RO Systems", "commercial", "bi-building",
     "High-output purification for offices, restaurants, schools and clinics."),
    ("Industrial RO Plants", "industrial", "bi-gear-wide-connected",
     "Skid-mounted industrial reverse osmosis plants and treatment systems."),
    ("Water Dispensers", "dispenser", "bi-cup-hot",
     "Hot, cold and normal water dispensers for homes and workplaces."),
]

PRODUCTS = [
    dict(name="AquaCare Pure 7 RO+UV", cat="RO + UV + UF Purifiers", sku="AC-PU7-001",
         tech="RO+UV+UF", price="14990", discount="12490", capacity="12 LPH",
         storage="7 L", dim="36 x 22 x 47 cm", weight="8.5 kg",
         warranty="1 Year Comprehensive Warranty", stock=24, featured=True,
         short="Compact 7-litre RO + UV + UF purifier for small families and apartments.",
         desc="The AquaCare Pure 7 is built for city households on municipal or mixed "
              "water supply. A seven-stage process removes sediment, chlorine taste, "
              "dissolved salts and microbes, while the food-grade tank keeps 7 litres "
              "ready at all times. A low-noise booster pump and auto shut-off valve keep "
              "running costs and water wastage down.",
         features="7-stage RO + UV + UF purification\nFood-grade 7 litre storage tank\n"
                  "Auto shut-off and low-pressure protection\nSuitable up to 2000 ppm TDS\n"
                  "Wall-mount or counter-top installation"),
    dict(name="AquaCare Pure 10 Alkaline RO", cat="Alkaline RO Purifiers", sku="AC-ALK10-002",
         tech="ALKALINE", price="21990", discount="18990", capacity="15 LPH",
         storage="10 L", dim="38 x 24 x 52 cm", weight="10.2 kg",
         warranty="1 Year Warranty + 1 Year Free Service", stock=16, featured=True,
         short="Alkaline RO with mineral cartridge that restores pH balance after purification.",
         desc="After reverse osmosis strips dissolved salts, the AquaCare Pure 10 passes "
              "water through a mineral and alkaline cartridge that reintroduces calcium "
              "and magnesium and lifts pH to a mildly alkaline range. The result is water "
              "that is both safe and pleasant to drink, with a 10-litre reserve for larger "
              "families.",
         features="Alkaline and mineral enrichment cartridge\n10 litre transparent storage\n"
                  "Copper-infused post carbon filter\nTDS controller for balanced taste\n"
                  "Digital filter-change indicator"),
    dict(name="AquaCare Shield UV Slim", cat="UV Water Purifiers", sku="AC-UVS-003",
         tech="UV", price="8990", discount="7490", capacity="60 LPH",
         storage="Direct flow", dim="40 x 14 x 30 cm", weight="4.1 kg",
         warranty="1 Year Warranty", stock=30, featured=True,
         short="High-flow UV purifier for low-TDS municipal water with no storage needed.",
         desc="Where the incoming water is already low in dissolved solids, reverse "
              "osmosis is unnecessary. The Shield UV Slim uses a high-output ultraviolet "
              "chamber and sediment-carbon pre-filtration to deactivate bacteria and "
              "viruses at 60 litres per hour without wasting a drop of reject water.",
         features="High-output 11W UV lamp\nZero water wastage\nUV fail alarm\n"
                  "Sediment and carbon pre-filters\nSlim wall-mount design"),
    dict(name="AquaCare Guard UF Gravity", cat="UV Water Purifiers", sku="AC-UFG-004",
         tech="UF", price="4990", discount=None, capacity="10 LPH",
         storage="14 L", dim="30 x 30 x 50 cm", weight="3.4 kg",
         warranty="1 Year Warranty", stock=40, featured=False,
         short="Electricity-free ultrafiltration purifier ideal for areas with power cuts.",
         desc="The Guard UF Gravity needs neither electricity nor plumbing. Hollow-fibre "
              "ultrafiltration membranes block bacteria and cysts while retaining natural "
              "minerals, making it a dependable backup for homes, hostels and sites with "
              "an unreliable power supply.",
         features="Works without electricity\nHollow-fibre UF membrane\n14 litre total capacity\n"
                  "Retains natural minerals\nEasy-clean detachable tank"),
    dict(name="AquaCare Prime 12 RO+UV Copper", cat="RO Water Purifiers", sku="AC-PR12-005",
         tech="RO+UV", price="24990", discount="21490", capacity="15 LPH",
         storage="12 L", dim="40 x 26 x 54 cm", weight="11.4 kg",
         warranty="2 Year Comprehensive Warranty", stock=12, featured=True,
         short="Premium copper-infused RO + UV purifier for high-TDS borewell water.",
         desc="Designed for borewell and tanker supply up to 3000 ppm TDS, the Prime 12 "
              "pairs a high-rejection membrane with in-tank UV sterilisation and a copper "
              "infusion chamber. A smart display reports purification status, filter life "
              "and tank level at a glance.",
         features="Handles up to 3000 ppm TDS\nIn-tank UV sterilisation\nCopper infusion technology\n"
                  "Smart LED status display\n12 litre storage with level indicator"),
    dict(name="AquaCare OfficePro 50 LPH RO", cat="Commercial RO Systems", sku="AC-OP50-006",
         tech="RO+UV", price="64990", discount="58990", capacity="50 LPH",
         storage="100 L external tank", dim="80 x 40 x 120 cm", weight="62 kg",
         warranty="1 Year Warranty on system, 6 months on membrane", stock=6, featured=True,
         short="50 LPH commercial RO system for offices and small institutions.",
         desc="The OfficePro 50 delivers purified water for up to 150 people per day. A "
              "stainless-steel frame, industrial membrane housing and pressure gauges make "
              "servicing straightforward, while an auto-flush cycle extends membrane life "
              "in hard-water locations.",
         features="50 litres per hour output\nStainless-steel frame and housings\n"
                  "Automatic membrane flushing\nPressure gauges and low-pressure cut-off\n"
                  "Optional chiller integration"),
    dict(name="AquaCare DineFresh 100 LPH RO", cat="Commercial RO Systems", sku="AC-DF100-007",
         tech="RO", price="98990", discount="89990", capacity="100 LPH",
         storage="200 L external tank", dim="95 x 45 x 140 cm", weight="88 kg",
         warranty="1 Year Warranty", stock=4, featured=False,
         short="100 LPH RO plant built for restaurants, canteens and banquet kitchens.",
         desc="Kitchens need purified water for cooking, ice and beverages throughout "
              "service hours. The DineFresh 100 provides a continuous 100 LPH supply with "
              "a dosing provision for anti-scalant, making it suitable for hard municipal "
              "lines and heavy daily duty cycles.",
         features="100 litres per hour continuous output\nAnti-scalant dosing provision\n"
                  "Multiport valve with softener option\nFood-safe piping throughout\n"
                  "Service-friendly modular layout"),
    dict(name="AquaCare CampusPure 250 LPH RO", cat="Commercial RO Systems", sku="AC-CP250-008",
         tech="RO+UV", price="164990", discount=None, capacity="250 LPH",
         storage="500 L external tank", dim="140 x 60 x 165 cm", weight="180 kg",
         warranty="1 Year Warranty with quarterly service visits", stock=3, featured=False,
         short="250 LPH purification system for schools, colleges and hostels.",
         desc="CampusPure supplies safe drinking water to multiple dispensing points "
              "across a campus. Dual media filtration protects the membrane bank, and UV "
              "post-treatment guards the storage loop so water stays safe between peak "
              "usage periods.",
         features="250 litres per hour output\nDual media pre-filtration\n"
                  "UV post-treatment on storage loop\nMulti-point distribution ready\n"
                  "Quarterly preventive service included"),
    dict(name="AquaCare IndusFlow 1000 LPH RO Plant", cat="Industrial RO Plants", sku="AC-IF1000-009",
         tech="OTHER", price="489000", discount=None, capacity="1000 LPH",
         storage="Customer tank", dim="Skid 200 x 90 x 180 cm", weight="520 kg",
         warranty="1 Year Warranty with AMC options", stock=2, featured=True,
         short="Skid-mounted 1000 LPH industrial RO plant with PLC control.",
         desc="IndusFlow is engineered around your feed-water analysis. The skid includes "
              "multigrade and activated carbon filtration, antiscalant dosing, a high "
              "pressure pump and a membrane bank, all managed by a PLC with online "
              "conductivity monitoring and data logging.",
         features="1000 LPH design output\nPLC control with online conductivity monitoring\n"
                  "Multigrade and activated carbon pre-treatment\nAntiscalant dosing system\n"
                  "Custom-engineered to your water report"),
    dict(name="AquaCare ChillPure Hot & Cold Dispenser", cat="Water Dispensers", sku="AC-CD-010",
         tech="OTHER", price="17990", discount="15490", capacity="Hot 5 L/h, Cold 3 L/h",
         storage="Bottle-fed 20 L", dim="32 x 34 x 98 cm", weight="16 kg",
         warranty="1 Year Warranty on compressor", stock=18, featured=False,
         short="Floor-standing hot, cold and normal water dispenser with child lock.",
         desc="ChillPure serves boiling-hot, chilled and ambient water from a single "
              "20-litre bottle. A compressor-based cooling system keeps output steady "
              "through the day and the hot tap includes a child-safety lock, making it "
              "suitable for offices, clinics and family homes.",
         features="Hot, cold and ambient taps\nCompressor cooling for steady output\n"
                  "Child-safety lock on hot tap\nStainless-steel internal tanks\n"
                  "Removable drip tray"),
    dict(name="AquaCare DeskFlow Tabletop Dispenser", cat="Water Dispensers", sku="AC-TD-011",
         tech="OTHER", price="9990", discount="8490", capacity="Hot 4 L/h, Cold 2 L/h",
         storage="Bottle-fed 20 L", dim="30 x 32 x 52 cm", weight="9.5 kg",
         warranty="1 Year Warranty", stock=22, featured=False,
         short="Compact tabletop dispenser for cabins, reception desks and small kitchens.",
         desc="Where floor space is scarce, the DeskFlow fits on a counter and still "
              "delivers hot and chilled water from a standard 20-litre bottle. Quiet "
              "operation and a low standby draw make it well suited to cabins and "
              "consulting rooms.",
         features="Fits on any counter top\nQuiet low-power operation\nHot and cold taps\n"
                  "Standard 20 litre bottle compatible\nEasy-clean removable tray"),
    dict(name="AquaCare EcoSave RO+UV 8L", cat="RO Water Purifiers", sku="AC-ES8-012",
         tech="RO+UV", price="16990", discount="13990", capacity="12 LPH",
         storage="8 L", dim="37 x 23 x 49 cm", weight="9.1 kg",
         warranty="1 Year Warranty", stock=28, featured=False,
         short="Water-saving RO + UV purifier that recovers up to 60% of input water.",
         desc="Conventional domestic RO systems reject two to three litres for every "
              "litre purified. EcoSave uses a recovery pump and optimised flow restrictor "
              "to lift recovery to around 60%, cutting both your water bill and the volume "
              "sent to drain.",
         features="Up to 60% water recovery\nRecovery booster pump\n8 litre storage tank\n"
                  "RO + UV double purification\nReject-water reuse outlet"),
]

# Sample product photos shipped in static/images/products/ so the catalogue looks
# complete on a fresh install. They are copied into MEDIA_ROOT when seeding.
PRODUCT_IMAGES = {
    "AC-PU7-001": "domestic-ro.jpg",
    "AC-ALK10-002": "alkaline-ro.jpg",
    "AC-UVS-003": "uv-slim.jpg",
    "AC-UFG-004": "uf-gravity.jpg",
    "AC-PR12-005": "domestic-ro.jpg",
    "AC-OP50-006": "commercial-ro.jpg",
    "AC-DF100-007": "commercial-ro.jpg",
    "AC-CP250-008": "commercial-ro.jpg",
    "AC-IF1000-009": "industrial-ro.jpg",
    "AC-CD-010": "dispenser-floor.jpg",
    "AC-TD-011": "dispenser-table.jpg",
    "AC-ES8-012": "alkaline-ro.jpg",
}

SERVICES = [
    ("Water Purifier Installation", "bi-wrench-adjustable", "499",
     "Professional installation, plumbing connection and commissioning of your purifier.",
     "Our technician mounts the unit, connects the inlet and drain lines, flushes the "
     "membrane, verifies output TDS and demonstrates daily use and filter care. "
     "Installation of AquaCare products purchased from us is free of charge."),
    ("Repair & Breakdown Service", "bi-tools", "399",
     "Fast diagnosis and repair for leakage, low flow, noise or taste problems.",
     "We diagnose the fault on site, quote the repair before starting work and carry "
     "common spares on the service van so most issues are resolved on the first visit."),
    ("Periodic Maintenance", "bi-calendar-check", "599",
     "Scheduled servicing with filter inspection, sanitisation and performance testing.",
     "Preventive maintenance keeps output quality and flow rate stable. Each visit "
     "includes pre-filter cleaning, tank sanitisation, membrane performance testing and "
     "a written service report."),
    ("Filter & Membrane Replacement", "bi-funnel", "899",
     "Genuine filter cartridges and RO membranes replaced by trained technicians.",
     "We stock original sediment, carbon, UF and RO components for every AquaCare model, "
     "along with popular third-party sizes. Replacement includes flushing and a post-"
     "service TDS check."),
    ("Annual Maintenance Contract", "bi-shield-check", "2499",
     "Yearly coverage with scheduled visits, priority support and discounted spares.",
     "An AMC converts unpredictable repair bills into a single yearly cost and gives you "
     "priority in the service queue. Choose Basic, Standard or Premium depending on how "
     "much coverage you need."),
]

AMC_PLANS = [
    ("Basic AMC", 12, "2499", 2, False, False, False,
     "Essential yearly cover with two scheduled service visits and labour included.",
     "2 preventive service visits\nLabour charges included\nPhone and WhatsApp support\n"
     "10% discount on spare parts"),
    ("Standard AMC", 12, "4499", 3, True, False, True,
     "Our most popular plan — three visits with standard filter replacement included.",
     "3 preventive service visits\nSediment and carbon filters included\nLabour charges included\n"
     "Priority scheduling within 48 hours\n15% discount on other spares"),
    ("Premium AMC", 12, "6999", 4, True, True, False,
     "Complete peace of mind with four visits, all filters and emergency breakdown cover.",
     "4 preventive service visits\nAll filters including RO membrane\nUnlimited breakdown visits\n"
     "Same-day emergency response\n20% discount on out-of-scope parts"),
]

TESTIMONIALS = [
    ("Priya Nair", "Homemaker", "Kochi", 5,
     "Our borewell water was very hard and the old purifier gave up within a year. The "
     "AquaCare Prime 12 has been running for eighteen months without a single complaint, "
     "and the service reminders actually arrive on time."),
    ("Rahul Menon", "Restaurant Owner", "Bengaluru", 5,
     "We installed the DineFresh 100 in our kitchen. It keeps up with lunch and dinner "
     "service easily, and the engineer who installed it still handles our servicing — "
     "that continuity makes a real difference."),
    ("Dr. Anita Sharma", "Clinic Director", "Pune", 4,
     "Reliable water quality matters in a clinic. The OfficePro 50 was commissioned in a "
     "day and the quarterly service reports give us documentation we can show during audits."),
    ("Suresh Patel", "Facility Manager", "Ahmedabad", 5,
     "Managing purifiers across four floors used to mean chasing vendors. With the AMC and "
     "the online tracking, I raise a request and can see exactly which technician is "
     "assigned and when the job is closed."),
    ("Meera Krishnan", "School Administrator", "Chennai", 5,
     "CampusPure serves over six hundred students daily. Installation was planned around "
     "our holidays, and the team trained our maintenance staff on basic checks."),
]

FAQS = [
    ("Which purifier should I choose for my water?",
     "It depends on your source. If the TDS of your supply is below about 200 ppm, a UV or "
     "UF purifier is usually sufficient. Between 200 and 2000 ppm, an RO or RO + UV system "
     "is recommended. Above that, we suggest a survey before selecting the system. Send us "
     "your water report through the quote form and we will recommend a specific model."),
    ("Is installation included when I buy a purifier?",
     "Yes. Standard installation of any AquaCare product purchased from us is free and is "
     "normally completed within 48 hours of delivery. Extra plumbing, additional piping or "
     "custom mounting is quoted separately and confirmed with you before work begins."),
    ("How often should the filters be changed?",
     "Sediment and carbon pre-filters typically last six to twelve months depending on the "
     "input water quality. RO membranes usually last two to three years in domestic use. "
     "Our service visits include a performance test that tells you exactly when a component "
     "needs replacement rather than guessing by calendar."),
    ("What does an AMC cover?",
     "Every AMC includes scheduled preventive visits and labour charges. Standard and "
     "Premium plans add filter replacement, and Premium also covers unlimited breakdown "
     "visits with a same-day response commitment. Full inclusions are listed on each plan."),
    ("How quickly do you respond to a breakdown?",
     "Requests logged before 5 PM are normally attended within 48 hours, and Premium AMC "
     "customers receive same-day response in serviceable areas. You can track the status of "
     "your request at any time from your dashboard or the tracking page."),
    ("Do you serve commercial and industrial customers?",
     "Yes. We design, manufacture, install and maintain systems from 50 LPH commercial "
     "units to 1000+ LPH industrial RO plants, including effluent and water treatment "
     "systems engineered around your feed water analysis."),
]

STATS = [
    ("Happy customers", 25000, "+", "bi-people", 1),
    ("Systems installed", 32000, "+", "bi-droplet", 2),
    ("Service engineers", 120, "+", "bi-person-badge", 3),
    ("Cities served", 45, "+", "bi-geo-alt", 4),
]

TECHNICIANS = [
    ("Arun Kumar", "9876500011", "arun@aquacare.example", "South Zone", "Domestic RO & UV", 8),
    ("Vikas Rane", "9876500022", "vikas@aquacare.example", "Central Zone", "Commercial RO systems", 6),
    ("Imran Sheikh", "9876500033", "imran@aquacare.example", "North Zone", "Industrial plants", 11),
]


class Command(BaseCommand):
    help = "Seed the database with realistic AquaCare sample data."

    @transaction.atomic
    def handle(self, *args, **options):
        # ---- Company info ------------------------------------------------
        company = CompanyInfo.get_solo()
        company.name = "AquaCare"
        company.tagline = "Pure Water. Better Life."
        company.about_short = (
            "AquaCare designs, manufactures and services advanced water purification "
            "systems for homes, offices and industries — backed by certified technicians "
            "and genuine spare parts."
        )
        company.address = "AquaCare Water Systems\nPlot 14, Industrial Estate\nBengaluru 560058"
        company.phone = "+91 98765 43210"
        company.alternate_phone = "+91 80 4000 1234"
        company.whatsapp = "919876543210"
        company.email = "support@aquacare.example"
        company.business_hours = "Mon - Sat: 9:00 AM to 7:00 PM"
        company.map_embed_url = "https://www.google.com/maps?q=Bengaluru&output=embed"
        company.save()
        self.stdout.write(self.style.SUCCESS("Company info ready"))

        # ---- Categories --------------------------------------------------
        cat_map = {}
        for order, (name, segment, icon, desc) in enumerate(CATEGORIES, start=1):
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={"segment": segment, "icon": icon,
                          "description": desc, "order": order},
            )
            cat_map[name] = cat
        self.stdout.write(self.style.SUCCESS(f"{len(cat_map)} categories ready"))

        # ---- Products ----------------------------------------------------
        image_dir = Path(settings.BASE_DIR) / "static" / "images" / "products"
        for p in PRODUCTS:
            product, created = Product.objects.get_or_create(
                sku=p["sku"],
                defaults={
                    "name": p["name"],
                    "category": cat_map[p["cat"]],
                    "technology": p["tech"],
                    "price": Decimal(p["price"]),
                    "discount_price": Decimal(p["discount"]) if p["discount"] else None,
                    "capacity": p["capacity"],
                    "storage_capacity": p["storage"],
                    "dimensions": p["dim"],
                    "weight": p["weight"],
                    "warranty": p["warranty"],
                    "stock_quantity": p["stock"],
                    "is_featured": p["featured"],
                    "short_description": p["short"],
                    "description": p["desc"],
                    "features": p["features"],
                    "meta_description": p["short"],
                },
            )
            # Attach a sample photo the first time the product is created.
            filename = PRODUCT_IMAGES.get(p["sku"])
            if created and filename and not product.image:
                source = image_dir / filename
                if source.exists():
                    with source.open("rb") as fh:
                        product.image.save(f"{p['sku'].lower()}.jpg", File(fh), save=True)
        self.stdout.write(self.style.SUCCESS(f"{len(PRODUCTS)} products ready"))

        # ---- Services ----------------------------------------------------
        for order, (name, icon, price, short, desc) in enumerate(SERVICES, start=1):
            Service.objects.get_or_create(
                name=name,
                defaults={"icon": icon, "starting_price": Decimal(price),
                          "short_description": short, "description": desc, "order": order},
            )
        self.stdout.write(self.style.SUCCESS(f"{len(SERVICES)} services ready"))

        # ---- AMC plans -----------------------------------------------------
        for order, (name, months, price, visits, filters, emergency, popular,
                    desc, features) in enumerate(AMC_PLANS, start=1):
            AMCPlan.objects.get_or_create(
                name=name,
                defaults={"duration_months": months, "price": Decimal(price),
                          "number_of_services": visits, "filter_replacement": filters,
                          "emergency_service": emergency, "is_popular": popular,
                          "description": desc, "features": features, "order": order},
            )
        self.stdout.write(self.style.SUCCESS(f"{len(AMC_PLANS)} AMC plans ready"))

        # ---- Testimonials / FAQs / stats / technicians ----------------------
        for order, (name, role, city, rating, msg) in enumerate(TESTIMONIALS, start=1):
            Testimonial.objects.get_or_create(
                name=name, defaults={"designation": role, "city": city,
                                     "rating": rating, "message": msg, "order": order},
            )
        for order, (q, a) in enumerate(FAQS, start=1):
            FAQ.objects.get_or_create(question=q, defaults={"answer": a, "order": order})
        for label, value, suffix, icon, order in STATS:
            Statistic.objects.get_or_create(
                label=label, defaults={"value": value, "suffix": suffix,
                                       "icon": icon, "order": order},
            )
        for name, phone, email, area, spec, years in TECHNICIANS:
            Technician.objects.get_or_create(
                name=name, defaults={"phone": phone, "email": email, "area": area,
                                     "specialization": spec, "experience_years": years},
            )

        self.stdout.write(self.style.SUCCESS(
            "Sample data loaded. Create an admin with: python manage.py createsuperuser"
        ))
