import pandas as pd
import numpy as np
import os
from django.shortcuts import get_object_or_404
from .models import Category, Insurer, Month



def read_and_prepare_sheet(sheet, year, month):
    sheet.columns = sheet.iloc[0]
    sheet = sheet[1:].reset_index(drop=True)
    sheet = sheet.rename(columns={np.nan: 'insurer'})
    sheet['Year'] = year
    sheet['Month'] = month
    sheet.loc[sheet['insurer'] == 'Previous Year', 'Year'] -= 1
    sheet['clubbed_name'] = np.nan
    sheet['category'] = np.nan
    return sheet

def get_clubbed_name_and_category(insurer_name):
    insurer = get_object_or_404(Insurer, insurer=insurer_name)
    category = insurer.clubbed_name
    return {'clubbed_name': category.clubbed_name, 'category': category.category}

def extract_data(sheet, products, output):
    for index, row in sheet.iterrows():
        if row['insurer'] == 'Previous Year':
            for product in products:
                if product in sheet.columns:
                    new_row = {
                        'Year': row['Year'],
                        'Month': row['Month'],
                        'category': row['category'],
                        'clubbed_name': row['clubbed_name'],
                        'Product': product,
                        'Value': int(row[product])*10
                    }
                    output = pd.concat([output, pd.DataFrame(new_row, index=[0])], ignore_index=True)
    return output

def Transformation(file_path):
    print("________________________START")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input File not found: {file_path}")

    # Converting the excel sheet into DataFrame
    sheet = pd.read_excel(file_path, sheet_name=None)
    sheet1_df = sheet['Segmentwise Report']
    sheet2_df = sheet['Miscellaneous portfolio']
    sheet3_df = sheet['Health Portfolio']
    print("________________________1")
    
    # Extracting the month and year from the DataFrame
    date_lst = sheet1_df.columns[0].split('UPTO')[1].split()
    month = date_lst[0][:3]
    year = int(date_lst[1])

    # Preparing sheets
    sheet1_df = read_and_prepare_sheet(sheet1_df, year, month)
    sheet2_df = read_and_prepare_sheet(sheet2_df, year, month)
    sheet3_df = read_and_prepare_sheet(sheet3_df, year, month)
    print("________________________2")
    dct_insurer = {}
    sheet_lst = [sheet1_df,sheet2_df,sheet3_df]

    # Adding clubbed_name and category to sheets
    for sheet in sheet_lst:
        for index, row in sheet.iterrows():
            insurer_name = row['insurer']
            if insurer_name not in dct_insurer:
                try:
                    result = get_clubbed_name_and_category(insurer_name)
                    dct_insurer[insurer_name] = result
                except:
                    continue
            sheet.at[index, 'clubbed_name'] = dct_insurer[insurer_name]['clubbed_name']
            sheet.at[index, 'category'] = dct_insurer[insurer_name]['category']
            sheet.at[index+1, 'clubbed_name'] = dct_insurer[insurer_name]['clubbed_name']
            sheet.at[index+1, 'category'] = dct_insurer[insurer_name]['category']

    print("________________________3")
    products = [
        "All Other miscellaneous", "Aviation", "Credit Guarantee", "Crop Insurance", "Engineering", 
        "Fire", "Health-Government schemes", "Health-Group", "Health-Retail", "Liability", 
        "Marine Cargo", "Marine Hull", "Motor OD", "Motor TP", "Overseas Medical", "P.A."
    ]

    # Creating the output DataFrame in the desired form  
    output = pd.DataFrame(columns=['Year', 'Month', 'category', 'clubbed_name', 'Product', 'Value'])

    output = extract_data(sheet1_df, products, output)
    output = extract_data(sheet2_df, products, output)
    output = extract_data(sheet3_df, products, output)
    print("________________________4")
    # Sorting the output DataFrame on the clubbed_name
    output = output.sort_values(by='clubbed_name')
    output_dir = 'media/outputs/'
    os.makedirs(output_dir, exist_ok=True)
    nm = file_path.split('.')[0][-1]
    output_file_path = os.path.join(output_dir, 'file'+nm+'.xlsx')
    output.to_excel(output_file_path, index=False)
    print("________________________STOP",output_file_path)

    return output_file_path

