from django.core.management.base import BaseCommand
from billing.models import Product

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        Product.objects.all().delete()
        
        products = [
            {'name': 'Product A', 'product_id': 'PA01', 'available_stocks': 100, 'price': 10.0, 'tax_percentage': 5.0},
            {'name': 'Product B', 'product_id': 'PB02', 'available_stocks': 50, 'price': 20.0, 'tax_percentage': 8.0},
            {'name': 'Product C', 'product_id': 'PC03', 'available_stocks': 75, 'price': 5.5, 'tax_percentage': 2.0},
            {'name': 'Product D', 'product_id': 'PD04', 'available_stocks': 200, 'price': 15.0, 'tax_percentage': 12.0},
            {'name': 'Product E', 'product_id': 'PE05', 'available_stocks': 30, 'price': 50.0, 'tax_percentage': 18.0},
            {'name': 'Product F', 'product_id': 'PF06', 'available_stocks': 120, 'price': 8.0, 'tax_percentage': 3.0},
            {'name': 'Product G', 'product_id': 'PG07', 'available_stocks': 60, 'price': 25.0, 'tax_percentage': 10.0},
            {'name': 'Product H', 'product_id': 'PH08', 'available_stocks': 90, 'price': 12.0, 'tax_percentage': 6.0},
            {'name': 'Product I', 'product_id': 'PI09', 'available_stocks': 150, 'price': 4.0, 'tax_percentage': 0.0},
            {'name': 'Product J', 'product_id': 'PJ10', 'available_stocks': 40, 'price': 100.0, 'tax_percentage': 20.0},
        ]
        
        for p_data in products:
            Product.objects.create(**p_data)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully saved {len(products)} products'))
