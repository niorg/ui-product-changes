import json
import os
import requests

# Define the URL of the remote JSON file
json_url = "https://static.ui.com/fingerprint/ui/public.json"

# Fetch the JSON data from the remote URL
response = requests.get(json_url)
data = response.json()

# Create a directory to store images if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

def download_image(product_id, image_id):
    # Construct image URL
    url = f"https://static.ui.com/fingerprint/ui/images/{product_id}/default/{image_id}.png"
    
    # Path to save the image
    image_path = os.path.join('images', f"{image_id}.png")
    
    # Download the image if not already downloaded
    if not os.path.exists(image_path):
        response = requests.get(url)
        if response.status_code == 200:
            with open(image_path, 'wb') as img_file:
                img_file.write(response.content)
    return image_path

# Start HTML document
html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ubiquiti Products</title>
    <style>
        table {border-collapse: collapse; width: 100%;}
        th, td {border: 1px solid #ccc; padding: 8px; text-align: left;}
        th {background-color: #f2f2f2;}
        img {max-width: 100px; height: auto;}
    </style>
</head>
<body>
    <h1>Ubiquiti Products</h1>
    <table>
        <tr>
            <th>Image</th>
            <th>Product Name</th>
            <th>SKU</th>
            <th>Abbreviation</th>
        </tr>
'''

# Process each product
for product in data['devices']:
    product_id = product['id']
    image_id = product['images']['default']
    
    # Download image and get the local path
    image_path = download_image(product_id, image_id)
    
    # Append product info to HTML content
    html_content += f'''
        <tr>
            <td><img src="{image_path}" alt="{product['product']['name']}"></td>
            <td>{product['product']['name']}</td>
            <td>{product['sku']}</td>
            <td>{product['product']['abbrev']}</td>
        </tr>
    '''

# End HTML document
html_content += '''
    </table>
</body>
</html>
'''

# Write HTML content to file
with open('products.html', 'w') as html_file:
    html_file.write(html_content)

print("HTML file 'products.html' and images have been created.")
