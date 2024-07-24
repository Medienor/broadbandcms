import requests
from weds import webflow_bearer_token
from datetime import datetime
import locale

# Set locale for Norwegian date format
locale.setlocale(locale.LC_TIME, 'nb_NO.UTF-8')

def get_collection_items(url, headers, offset=0, limit=100):
    params = {
        "offset": offset,
        "limit": limit
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def analyze_items(collection_id, speed_field, speed_values):
    url = f"https://api.webflow.com/v2/collections/{collection_id}/items"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {webflow_bearer_token}"
    }

    total_items = 0
    offset = 0
    max_offset = 500

    prices = {speed: [] for speed in speed_values}

    while offset <= max_offset:
        data = get_collection_items(url, headers, offset)
        items = data.get("items", [])
        total_items += len(items)

        for item in items:
            field_data = item.get("fieldData", {})
            speed = field_data.get(speed_field)
            pris = field_data.get("pris")

            if pris and speed:
                pris = float(pris)
                speed = int(speed)

                if speed in speed_values:
                    prices[speed].append(pris)

        if len(items) < 100:  # If we get less than 100 items, we've reached the end
            break
        
        offset += 100

    return total_items, prices

def calculate_average(prices):
    return round(sum(prices) / len(prices)) if prices else 0  # Rounded to nearest integer

def print_results(title, total_items, avg_prices):
    print(f"\n=== {title} ===")
    print(f"Total number of items in the collection: {total_items}")
    for speed, avg in avg_prices.items():
        print(f"Average price for products with {title.lower()} = {speed}: {avg}")

# Analyze Fiber Internett
fiber_total, fiber_prices = analyze_items("6669de2ff0ef9f9dcbb75e1b", "nedlastning-2", [100, 250, 500])
fiber_avg_prices = {speed: calculate_average(prices) for speed, prices in fiber_prices.items()}

# Analyze Trådløst Bredbånd
tradlost_total, tradlost_prices = analyze_items("666c52def5fd5c40c4921034", "nedlastning", [100, 250, 500])
tradlost_avg_prices = {speed: calculate_average(prices) for speed, prices in tradlost_prices.items()}

# Analyze Mobilt Bredbånd
mobilt_total, mobilt_prices = analyze_items("6670854ae5dd5e1a19b7333b", "datamengde-2", [50, 100, 200])
mobilt_avg_prices = {speed: calculate_average(prices) for speed, prices in mobilt_prices.items()}

# Print results
print_results("FIBER INTERNETT", fiber_total, fiber_avg_prices)
print_results("TRÅDLØST BREDBÅND", tradlost_total, tradlost_avg_prices)
print_results("MOBILT BREDBÅND", mobilt_total, mobilt_avg_prices)

# Prepare data for Webflow update
update_data = {
    "fieldData": {
        "name": "bredband stats",
        "slug": "bredband-stats",
        "fiber-avg-100": str(fiber_avg_prices[100]),
        "fiber-avg-250": str(fiber_avg_prices[250]),
        "fiber-avg-500": str(fiber_avg_prices[500]),
        "mbb-avg-100": str(mobilt_avg_prices[100]),
        "mbb-avg-200": str(mobilt_avg_prices[200]),
        "mbb-avg-50": str(mobilt_avg_prices[50]),
        "sist-oppdatert": datetime.now().strftime("%d. %B %Y"),
        "tradlast-avg-100": str(tradlost_avg_prices[100]),
        "tradlast-avg-250": str(tradlost_avg_prices[250]),
        "tradlast-avg-500": str(tradlost_avg_prices[500])
    }
}

# Update Webflow item
url = "https://api.webflow.com/v2/collections/669f96a8afae4ace41107d19/items/669fdbe3b5b8cd79868612c8/live"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {webflow_bearer_token}"
}
response = requests.patch(url, headers=headers, json=update_data)

# Print response code and content
print(f"\nWebflow API Response Code: {response.status_code}")
print(f"Webflow API Response Content: {response.text}")