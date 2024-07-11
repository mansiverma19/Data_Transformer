import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import UploadFileForm
from .File_transformation import Transformation
from urllib.parse import quote, unquote
import os

# Function to handle uploaded files and return the list of file paths
def handle_uploaded_files(files):
    try:
        file_paths = []
        for key, file in files.items():
            if isinstance(file, list):
                for f in file:
                    file_path = os.path.join('media/upload/', f.name)
                    with open(file_path, 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)
                    file_paths.append(file_path)
            else:
                file_path = os.path.join('media/upload/', file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                file_paths.append(file_path)
        return file_paths
    except Exception as e:
        raise IOError(f"Error saving files: {str(e)}")

# Django view for uploading and transforming files
def upload_file(request):
    error_message = None
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file_paths = handle_uploaded_files(request.FILES)
                print("Uploaded file paths:", file_paths)
                # Redirect to transform view with encoded file paths
                return redirect(reverse('transform', kwargs={'file_paths': ';'.join(quote(os.path.basename(path)) for path in file_paths)}))
            except Exception as e:
                error_message = f"File upload error: {str(e)}"
        else:
            # Print form errors to debug
            print(form.errors)
            error_message = "Form is not valid. Please check your files."
    else:
        form = UploadFileForm()
    return render(request, 'transform/upload.html', {'form': form, 'error_message': error_message})

def transform(request, file_paths):
    error_message = None
    paths = []
    plot1_base64 = None
    plot2_base64 = None

    try:
        for file_name in unquote(file_paths).split(';'):
            file_path = 'media/upload/' + file_name
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Input file not found at path: {file_path}")
            
            o_path = Transformation(file_path)
            paths.append(o_path)


        # Perform transformation for each file and concatenate results
        all_output_dfs = []
        for path in paths:
            output_df = pd.read_excel(path)
            all_output_dfs.append(output_df)

        # Concatenate all dataframes
        combined_df = pd.concat(all_output_dfs, ignore_index=True)
        combined_df = combined_df.sort_values(by='clubbed_name')
        output_file_path = os.path.join('media/outputs/', 'Output.xlsx')
        combined_df.to_excel(output_file_path, index=False)

        # Plot 1: Total Value by Product
        plt.figure(figsize=(9, 4))
        combined_df.groupby('Product')['Value'].sum().plot(kind='bar')
        plt.title('Total Value by Product')
        plt.xlabel('Product')
        plt.ylabel('Value')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Saving plot 1 to a BytesIO buffer
        buf1 = io.BytesIO()
        plt.savefig(buf1, format='png')
        buf1.seek(0)
        plot1_base64 = base64.b64encode(buf1.getvalue()).decode('utf-8')
        buf1.close()

        # Plot 2: Total Value by Year and Product
        plt.figure(figsize=(12, 4))
        combined_df.pivot_table(index='Year', columns='Product', values='Value', aggfunc='sum').plot(kind='bar', stacked=True)
        plt.title('Total Value by Year and Product')
        plt.xlabel('Year')
        plt.ylabel('Value')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Saving plot 2 to a BytesIO buffer
        buf2 = io.BytesIO()
        plt.savefig(buf2, format='png')
        buf2.seek(0)
        plot2_base64 = base64.b64encode(buf2.getvalue()).decode('utf-8')
        buf2.close()

    except FileNotFoundError as e:
        error_message = f"File not found: {str(e)}"
    except Exception as e:
        error_message = f"Error during transformation: {str(e)}"

    return render(request, 'transform/result.html', {
        'path': output_file_path,
        'error_message': error_message,
        'plot1': plot1_base64,
        'plot2': plot2_base64
    })
