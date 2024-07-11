import pandas as pd
from django.core.management.base import BaseCommand
from DataProcessor.models import Insurer, Category, Month, Products

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # Load Excel file
        file_path = 'media/master_file/master.xlsx'
        xls = pd.ExcelFile(file_path)

        # Load data into Category model
        category_df = pd.read_excel(xls, 'category') 
        for _, row in category_df.iterrows():
            Category.objects.update_or_create(
                clubbed_name=row['clubbed_name'],
                defaults={'category': row['category']}
            )
        
        # Load data into Insurer model
        insurer_df = pd.read_excel(xls, 'name') 
        for _, row in insurer_df.iterrows():
            # Find or create the corresponding Category object
            category = Category.objects.get(clubbed_name=row['clubbed_name'])
            Insurer.objects.update_or_create(
                insurer=row['insurer'],
                defaults={'name': row['name'], 'clubbed_name': category}
            )
        #load data into Products table
        product_df = pd.read_excel(xls, 'lob') 
        for _, row in product_df.iterrows():
            Products.objects.update_or_create(
                Product=row['Product'],
            )

        # Load data into Month model
        month_df = pd.read_excel(xls, 'month') 
        for _, row in month_df.iterrows():
            Month.objects.update_or_create(
                month=row['month'],
                defaults={'month_num': row['month_num']}
            )

        self.stdout.write(self.style.SUCCESS('Successfully loaded data from master Excel file'))
