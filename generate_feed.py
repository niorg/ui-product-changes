import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime

# Path to the local JSON file
local_json_path = 'public.json'

# Paths for saved product IDs and the RSS feed
saved_products_path = 'saved_products.json'
rss_feed_path = 'product_feed.xml'

# Load the current JSON data from the local file
with open(local_json_path, 'r') as file:
    data = json.load(file)

# Extract product IDs and details from the current data
current_products = {product['id']: product for product in data['devices']}

# Load previously saved product IDs
if os.path.exists(saved_products_path):
    with open(saved_products_path, 'r') as file:
        saved_products = json.load(file)
else:
    saved_products = {}

# Determine new products that are not in the saved list
new_products = {product_id: details for product_id, details in current_products.items() if product_id not in saved_products}

if new_products:
    # Generate the RSS feed
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = 'New Ubiquiti Products'
    ET.SubElement(channel, 'link').text = 'https://static.ui.com/fingerprint/ui/'
    ET.SubElement(channel, 'description').text = 'Latest additions to the Ubiquiti product line.'
    ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %Z')
    
    for product_id, product in new_products.items():
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = product['product']['name']
        ET.SubElement(item, 'link').text = f"https://static.ui.com/fingerprint/ui/images/{product_id}/default/{product['images']['default']}.png"
        ET.SubElement(item, 'description').text = f"{product['product']['name']} ({product['sku']})"
        ET.SubElement(item, 'guid').text = product_id
        ET.SubElement(item, 'pubDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %Z')

    # Write RSS feed to file
    tree = ET.ElementTree(rss)
    with open(rss_feed_path, 'wb') as file:
        tree.write(file, encoding='utf-8', xml_declaration=True)
    
    print("RSS feed created with new products.")

# Save the current product IDs for future comparison
with open(saved_products_path, 'w') as file:
    json.dump(current_products, file)

print(f"Saved {len(current_products)} products for future comparison.")
