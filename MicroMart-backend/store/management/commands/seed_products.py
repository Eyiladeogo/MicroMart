import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from faker import Faker

from store.models import Product


class Command(BaseCommand):
    help = "Seeds the database with dummy product data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--num_products",
            type=int,
            default=50,  # Default to 50 products
            help="The number of dummy products to create.",
        )
        parser.add_argument(
            "--clear_existing",
            action="store_true",  # This argument doesn't take a value, just its presence is true
            help="Clear all existing products before seeding.",
        )

    def handle(self, *args, **options):
        num_products = options["num_products"]
        clear_existing = options["clear_existing"]
        fake = Faker()  # Initialize Faker for realistic-looking data

        self.stdout.write(self.style.NOTICE(f"Starting product seeding process..."))

        if clear_existing:
            self.stdout.write(self.style.WARNING("Clearing all existing products..."))
            Product.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing products cleared."))

        products_created = 0
        for i in range(num_products):
            try:
                # Generate unique product name (using Faker and a random number)
                product_name = f"{fake.word().capitalize()} {fake.word().capitalize()} {random.randint(100, 999)}"
                # Ensure uniqueness if there's a rare collision, though unlikely with random suffix
                while Product.objects.filter(name=product_name).exists():
                    product_name = f"{fake.word().capitalize()} {fake.word().capitalize()} {random.randint(100, 999)}"

                # Generate random image URL using picsum.photos for random, realistic images
                image_url = f"https://placehold.co/600*400/C0C0C0/333333?text={slugify(product_name).replace('-', '+')}"  # Use slugified name as seed for consistent image for same product name

                with transaction.atomic():
                    Product.objects.create(
                        name=product_name,
                        description=fake.paragraph(
                            nb_sentences=3, variable_nb_sentences=True
                        ),
                        price=round(
                            random.uniform(5.00, 1000.00), 2
                        ),  # Price between 5 and 1000, 2 decimal places
                        stock=random.randint(0, 200),  # Stock between 0 and 200
                        image=image_url,
                    )
                    products_created += 1
                    if (i + 1) % 10 == 0:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Created {products_created} products so far..."
                            )
                        )

            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Error creating product {i+1}: {e}")
                )
                # Continue even if one product fails, but log the error

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully seeded {products_created} dummy products."
            )
        )
