import requests
from bs4 import BeautifulSoup
from datetime import datetime
from requests.auth import HTTPBasicAuth

# WordPress API Configuration
WP_SITE_URL = os.environ.get('WP_SITE_URL')
WP_USER = os.environ.get('WP_USER')
WP_APP_PASSWORD = os.environ.get('WP_APP_PASSWORD')

# Telegram bot configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# URLs for NSE and BSE top gainers
url_nse = 'https://www.livemint.com/market/nse-top-gainers'
url_bse = 'https://www.livemint.com/market/bse-top-gainers'

def scrape_top_gainers(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'table table-hover'})
    top_gainers = []
    if table:
        rows = table.find_all('tr')[1:]  # Skip the header row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                stock_name = cols[0].find('a').text.strip()
                stock_price = cols[1].find('a').text.strip()
                stock_change = cols[2].find('a').text.strip()
                stock_percent_change = cols[3].find('a').text.strip()

                # Add symbols based on the percentage change
                if float(stock_percent_change.replace('%', '')) > 5:
                    symbol = '🚀'  # Rocket for significant gains
                elif float(stock_percent_change.replace('%', '')) > 2:
                    symbol = '📈'  # Chart with upwards trend for moderate gains
                else:
                    symbol = '💹'  # Chart with upwards trend and yen symbol for small gains

                top_gainers.append(f"{symbol} *{stock_name}*\n💰 Price: ₹{stock_price}\n📊 Change: ₹{stock_change} ({stock_percent_change})")
    return top_gainers

def get_current_date():
    """Return the current date formatted as DD-MM-YYYY."""
    return datetime.now().strftime("%d %B %Y"))

def create_wp_post_content(nse_gainers, bse_gainers):
    current_date = get_current_date()

    # Create the content for WordPress Post
    post_content = f"<h2>🔥 NSE Top Gainers (as of {current_date}) 🔥</h2>\n"
    post_content += "<ul>\n"
    for gainer in nse_gainers:
        post_content += f"<li>{gainer.replace('*', '<b>').replace('💰', '💰 Price: ').replace('📊', '📊 Change: ')}</li>\n"
    post_content += "</ul>\n"
    
    post_content += f"<h2>🔥 BSE Top Gainers (as of {current_date}) 🔥</h2>\n"
    post_content += "<ul>\n"
    for gainer in bse_gainers:
        post_content += f"<li>{gainer.replace('*', '<b>').replace('💰', '💰 Price: ').replace('📊', '📊 Change: ')}</li>\n"
    post_content += "</ul>\n"

    # Add promotional content
    post_content += "<p>💼 <b>Join our free channel for expert stock tips and market analysis!</b> 💼<br>"
    post_content += "🔗 <a href='https://t.me/currentadda'>Click here to subscribe</a></p>"

    post_content += "<p>📅 Date: " + current_date + "</p>"
    post_content += "<p>#StockMarket #TopGainers #NSE #BSE #DalalStreet</p>"

    return post_content

def post_to_wordpress(title, content):
    headers = {
        'Content-Type': 'application/json',
    }

    post_data = {
        'title': title,
        'content': content,
        'status': 'publish',  # Set the post status to publish directly
        'categories': [2]  # Assign post to category ID 2
    }

    response = requests.post(WP_SITE_URL, headers=headers, json=post_data,
                             auth=HTTPBasicAuth(WP_USER, WP_APP_PASSWORD))

    if response.status_code == 201:
        post_json = response.json()
        post_link = post_json.get('link', '')
        print("Post successfully created on WordPress.")
        return post_link
    else:
        print(f"Failed to create post: {response.content}")
        return None

def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.post(telegram_url, json=payload)
    
    if response.status_code == 200:
        print("Message sent successfully to Telegram.")
    else:
        print(f"Failed to send message to Telegram: {response.content}")

# Scrape data from NSE and BSE
nse_gainers = scrape_top_gainers(url_nse)[:10]  # Limit to top 10 gainers
bse_gainers = scrape_top_gainers(url_bse)[:10]  # Limit to top 10 gainers

# Generate post title and content
current_date = get_current_date()
post_title = f"Top 10 BSE-NSE gainers Stock of The {current_date}"
post_content = create_wp_post_content(nse_gainers, bse_gainers)

# Publish the post on WordPress
post_link = post_to_wordpress(post_title, post_content)

# If the WordPress post was successful, send the message to Telegram
if post_link:
    promo_message = "💼 *Join our premium channel for expert stock tips and market analysis!* 💼\n" \
                    "🔗 [Click here to subscribe](https://t.me/dalalstreetgujarati)"
    
    telegram_message = f"🔥 *Top 10 BSE-NSE gainers Stock of The {current_date}* 🔥\n\n"
    telegram_message += "\n\n".join(nse_gainers)
    telegram_message += "\n\n"
    telegram_message += "\n\n".join(bse_gainers)
    telegram_message += f"\n\n🔗 [Read full article here]({post_link})"
    telegram_message += f"\n\n{promo_message}"

    send_telegram_message(telegram_message)
