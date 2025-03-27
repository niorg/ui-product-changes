import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime

# Path to the local JSON file
local_json_path = 'public.json'

# Paths for saved product IDs and the RSS feed
saved_products_path = 'rss/saved_products/saved_products.json'
rss_feed_path = 'rss/product_feed.xml'

# Load the current JSON data from the local file
with open(local_json_path, 'r') as file:
    data = json.load(file)

# Extract product IDs and details from the current data and add a discovery date if they are new
current_time = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
current_products = {
    product['id']: {
        **product,
        'first_discovered': current_time if product['id'] not in saved_products else saved_products[product['id']]['first_discovered']
    } for product in data['devices']
}

# Load previously saved product IDs with their first discovery date
if os.path.exists(saved_products_path):
    with open(saved_products_path, 'r') as file:
        saved_products = json.load(file)
else:
    saved_products = {}

# Merge new details back into saved products
updated_saved_products = {**saved_products, **current_products}

# Sort products by first discovery date to find the 30 most recent
sorted_products = sorted(updated_saved_products.items(), key=lambda item: datetime.strptime(item[1]['first_discovered'], '%a, %d %b %Y %H:%M:%S GMT'))
recent_products = dict(sorted_products[-30:])  # Keep only the last 30 products

# Generate the RSS feed
rss = ET.Element('rss', version='2.0')
channel = ET.SubElement(rss, 'channel')
ET.SubElement(channel, 'title').text = 'New Ubiquiti Products'
ET.SubElement(channel, 'link').text = 'https://static.ui.com/fingerprint/ui/'
ET.SubElement(channel, 'description').text = 'Latest additions to the Ubiquiti product line.'
ET.SubElement(channel, 'lastBuildDate').text = current_time

for product_id, product in recent_products.items():
    item = ET.SubElement(channel, 'item')
    ET.SubElement(item, 'title').text = product['product']['name']
    ET.SubElement(item, 'link').text = f"https://static.ui.com/fingerprint/ui/images/{product_id}/default/{product['images']['default']}.png"
    ET.SubElement(item, 'description').text = f"{product['product']['name']} ({product['sku']})"
    guid = ET.SubElement(item, 'guid', isPermaLink="false")
    guid.text = product_id
    ET.SubElement(item, 'pubDate').text = product['first_discovered']

    # Add image as enclosure
    ET.SubElement(item, 'enclosure', url=f"https://static.ui.com/fingerprint/ui/images/{product_id}/default/{product['images']['default']}.png", type="image/png")

# Write RSS feed to file
tree = ET.ElementTree(rss)
with open(rss_feed_path, 'wb') as file:
    tree.write(file, encoding='utf-8', xml_declaration=True)

print("RSS feed created with new products.")

# Save the current product IDs for future comparison and include the first discovery date
with open(saved_products_path, 'w') as file:
    json.dump(updated_saved_products, file)

print(f"Saved {len(recent_products)} products for future comparison.")
