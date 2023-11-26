import requests
from bs4 import BeautifulSoup

def convert_to_integer(s):
    i = ""

    for ch in [c for c in s]:
        if ch == "." and i:
            break

        if not ch.isdigit():
            continue

        i += ch

    return int(i)

def get_html_code(url, headers={}):
    resp = requests.get(url, headers=headers)

    while resp.status_code != 200:
        resp = requests.get(url, headers=headers)

    return resp.text

def scrape_from_html(html, data):
    soup = BeautifulSoup(html, "html.parser")
    sr = soup.find_all(
        *data["item-query"][0],
        **data["item-query"][1]
    )

    output = []

    for r in sr:
        result_name = r.find(
            *data["item-name"][0],
            **data["item-name"][1]
        )

        result_price = r.find(
            *data["item-price"][0],
            **data["item-price"][1]
        )

        result_link = r.find(
            "a",
            href=True
        )

        if not all([result_name, result_price, result_link]):
            continue

        output.append({
            "source": data["source"],
            "name": result_name.get_text(),
            "price": result_price.get_text(),
            "link": result_link.href
        })
    
    return output

def scrape_from_website(url, headers, scrape_data):
    html = get_html_code(url, headers)
    output = scrape_from_html(html, scrape_data)

    return output

def search_item(item, websites, headers):
    output = []

    for w in websites:
        output.extend(
            scrape_from_website(
                w["url"] + item,
                headers,
                w["scrape_data"]
            )
        )
    
    output.sort(key=lambda r: convert_to_integer(r["price"]))
    
    return output

def display_results(results):
    for result in results:
        results_name = result["name"][:35]
        
        results_price = convert_to_integer(result["price"])
        results_price = f"Rs. {results_price}"

        results_source = result["source"]

        out = f"{results_name:<35} - {results_price:>15} - {results_source}"

        print(out)

def cli_mode(websites, headers):
    item = input("Search for: ")
    if not item:
        return False
    
    results = search_item(item, websites, headers)
    display_results(results)

    return True

if __name__ == "__main__":
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    websites_data = [
        {
            "url": "https://amazon.in/s?k=",
            "scrape_data": {
                "item-query": [
                    ["div"],
                    {"class": "s-result-item"}
                ],
                "item-name": [
                    ["span"],
                    {"class": "a-text-normal"}
                ],
                "item-price": [
                    ["span"],
                    {"class": "a-offscreen"}
                ],
                "source": "Amazon"
            }
        },
        {
            "url": "https://snapdeal.com/search?keyword=",
            "scrape_data": {
                "item-query": [
                    ["div"],
                    {"class": "product-tuple-listing"}
                ],
                "item-name": [
                    ["p"],
                    {"class": "product-title"}
                ],
                "item-price": [
                    ["span"],
                    {"class": "product-price"}
                ],
                "source": "Snapdeal"
            }
        },
        {
            "url": "https://www.pepperfry.com/site_product/search?q=",
            "scrape_data": {
                "item-query": [
                    ["div"],
                    {"class": "clip-product-card-wrapper"}
                ],
                "item-name": [
                    ["h3"],
                    {"class": "product-name"}
                ],
                "item-price": [
                    ["span"],
                    {"class": "product-offer-price"}
                ],
                "source": "Pepperfry"
            }
        }
    ]

    while cli_mode(websites_data, headers):
        pass
