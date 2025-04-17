import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
import datetime
import schedule
from urllib.parse import urlparse
import hashlib
import re

# User agents to rotate through to avoid blocking
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
]

# Configuration - target sites by category with CSS selectors for the content
SITES = {
    "news": [
        {
            "url": "https://www.the-star.co.ke/",
            "article_selector": "article.article-box",
            "title_selector": "h4.article-title",
            "summary_selector": "div.article-summary",
            "link_selector": "a.article-link",
            "image_selector": "img.article-image",
            "date_selector": "span.article-date"
        },
        {
            "url": "https://nation.africa/kenya/news",
            "article_selector": ".card--article",
            "title_selector": ".card__title",
            "summary_selector": ".card__summary",
            "link_selector": ".card__link",
            "image_selector": ".card__image img",
            "date_selector": ".card__date"
        },
        {
            "url": "https://www.standardmedia.co.ke/news",
            "article_selector": "article.article",
            "title_selector": "h3.article-title",
            "summary_selector": "p.article-summary",
            "link_selector": "a.article-link",
            "image_selector": "img.article-image",
            "date_selector": "span.article-date"
        }
    ],
    "tech": [
        {
            "url": "https://techweez.com/",
            "article_selector": "article.post",
            "title_selector": "h2.entry-title",
            "summary_selector": ".entry-content p",
            "link_selector": "h2.entry-title a",
            "image_selector": ".post-thumbnail img",
            "date_selector": ".entry-date"
        },
        {
            "url": "https://africabusinesscommunities.com/tech/",
            "article_selector": ".blogpost",
            "title_selector": "h2 a",
            "summary_selector": ".blogpost-content p",
            "link_selector": "h2 a",
            "image_selector": ".blogpost-thumb img",
            "date_selector": ".blogpost-date"
        }
    ],
    "business": [
        {
            "url": "https://www.businessdailyafrica.com/bd/corporate",
            "article_selector": ".article-card",
            "title_selector": ".article-card__title",
            "summary_selector": ".article-card__summary",
            "link_selector": ".article-card__link",
            "image_selector": ".article-card__image img",
            "date_selector": ".article-card__date"
        },
        {
            "url": "https://kenyanwallstreet.com/",
            "article_selector": "article.post",
            "title_selector": "h2.entry-title a",
            "summary_selector": ".entry-content p",
            "link_selector": "h2.entry-title a",
            "image_selector": ".post-thumbnail img",
            "date_selector": ".entry-date"
        }
    ],
    "gaming": [
        {
            "url": "https://www.paxfulkenya.com/blog/category/gaming/",
            "article_selector": "article.post",
            "title_selector": "h2.entry-title",
            "summary_selector": ".entry-content p",
            "link_selector": "h2.entry-title a",
            "image_selector": ".post-thumbnail img",
            "date_selector": ".entry-date"
        },
        {
            "url": "https://gadgets-africa.com/category/gaming/",
            "article_selector": "article.post",
            "title_selector": "h2.entry-title",
            "summary_selector": ".entry-content p",
            "link_selector": "h2.entry-title a",
            "image_selector": ".post-thumbnail img",
            "date_selector": ".entry-date"
        }
    ],
    "events": [
        {
            "url": "https://allevents.in/nairobi",
            "article_selector": ".item",
            "title_selector": ".event-title",
            "summary_selector": ".event-description",
            "link_selector": "a.event-link",
            "image_selector": ".event-banner img",
            "date_selector": ".event-date"
        },
        {
            "url": "https://nairobinow.wordpress.com/",
            "article_selector": "article.post",
            "title_selector": "h2.entry-title",
            "summary_selector": ".entry-content p",
            "link_selector": "h2.entry-title a",
            "image_selector": ".post-thumbnail img",
            "date_selector": ".entry-date"
        }
    ],
    "trending": [
        {
            "url": "https://www.standardmedia.co.ke/",
            "article_selector": ".trending-article",
            "title_selector": "h3.article-title",
            "summary_selector": "p.article-summary",
            "link_selector": "a.article-link",
            "image_selector": "img.article-image",
            "date_selector": "span.article-date"
        },
        {
            "url": "https://www.kenyans.co.ke/news",
            "article_selector": ".article-box",
            "title_selector": "h2.article-title",
            "summary_selector": "p.article-summary",
            "link_selector": "a.article-link",
            "image_selector": "img.article-image",
            "date_selector": "span.article-date"
        }
    ],
    "ai": [
        {
            "url": "https://africa.businessinsider.com/tech",
            "article_selector": ".teaser",
            "title_selector": "h2.headline",
            "summary_selector": "p.excerpt",
            "link_selector": "a.headline-link",
            "image_selector": ".teaser-img img",
            "date_selector": ".date"
        },
        {
            "url": "https://techcrunch.com/category/artificial-intelligence/",
            "article_selector": "article.post",
            "title_selector": "h2.post-title",
            "summary_selector": "div.post-excerpt",
            "link_selector": "a.post-link",
            "image_selector": "img.post-image",
            "date_selector": "time.post-time"
        }
    ],
    "soccer": [
        {
            "url": "https://www.goal.com/en-ke",
            "article_selector": "article.card",
            "title_selector": "h3.card-title",
            "summary_selector": "p.card-text",
            "link_selector": "a.card-link",
            "image_selector": ".card-image img",
            "date_selector": ".card-date"
        },
        {
            "url": "https://www.standardmedia.co.ke/sports/football",
            "article_selector": ".article",
            "title_selector": "h3.article-title",
            "summary_selector": "p.article-summary",
            "link_selector": "a.article-link",
            "image_selector": "img.article-image",
            "date_selector": "span.article-date"
        },
        {
            "url": "https://futaa.com/",
            "article_selector": "article.article",
            "title_selector": "h2.article-title",
            "summary_selector": "p.article-summary",
            "link_selector": "a.article-link",
            "image_selector": "img.article-image",
            "date_selector": "span.article-date"
        }
    ]
}

# Storage file
DATA_FILE = "blog_data.json"

# Fallback images if no image found
FALLBACK_IMAGES = {
    "news": "https://static.vecteezy.com/system/resources/thumbnails/000/295/608/small/4.jpg",
    "tech": "https://static.vecteezy.com/system/resources/thumbnails/023/944/577/small/technology-background-circuit-board-electronic-system-digital-tech-design-vector.jpg",
    "business": "https://static.vecteezy.com/system/resources/thumbnails/004/893/886/small/investment-and-stock-market-business-graph-data-concept-financial-data-on-a-monitor-as-financial-figures-forex-charts-for-financial-business-concepts-3d-illustration-vector.jpg",
    "gaming": "https://static.vecteezy.com/system/resources/thumbnails/010/454/513/small/game-controller-icon-joystick-gamepad-icon-video-game-symbol-free-vector.jpg",
    "events": "https://static.vecteezy.com/system/resources/thumbnails/026/775/025/small/the-concept-of-event-management-with-a-calendar-pencil-and-checklist-on-the-form-vector.jpg",
    "trending": "https://static.vecteezy.com/system/resources/thumbnails/018/930/750/small/social-media-marketing-colorful-icon-png.png",
    "ai": "https://static.vecteezy.com/system/resources/thumbnails/022/841/114/small/ai-generated-digital-brain-in-blue-background-artificial-intelligence-deep-learning-automation-intelligence-background-free-photo.jpg",
    "soccer": "https://static.vecteezy.com/system/resources/thumbnails/000/554/695/small/football_1.jpg"
}

def get_random_user_agent():
    """Return a random user agent from the list"""
    return random.choice(USER_AGENTS)

def clean_text(text):
    """Clean up text content"""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove special characters
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
    return text

def make_absolute_url(base_url, url):
    """Convert relative URL to absolute"""
    if url.startswith('http'):
        return url
    
    domain = urlparse(base_url).netloc
    scheme = urlparse(base_url).scheme
    
    if url.startswith('//'):
        return f"{scheme}:{url}"
    elif url.startswith('/'):
        return f"{scheme}://{domain}{url}"
    else:
        path = '/'.join(urlparse(base_url).path.split('/')[:-1])
        return f"{scheme}://{domain}{path}/{url}"

def scrape_site(site_config):
    """Scrape a single site based on the provided configuration"""
    url = site_config["url"]
    user_agent = get_random_user_agent()
    headers = {'User-Agent': user_agent}
    
    try:
        # Allow for insecure connection when needed (for some sites with SSL issues)
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select(site_config["article_selector"])
        
        results = []
        for article in articles[:5]:  # Limit to 5 articles per site
            try:
                # Extract article details with more robust error handling
                title_element = article.select_one(site_config["title_selector"])
                title = title_element.get_text().strip() if title_element else "No title available"
                
                summary_element = article.select_one(site_config["summary_selector"])
                summary = clean_text(summary_element.get_text()) if summary_element else "No summary available"
                
                link_element = article.select_one(site_config["link_selector"])
                link = link_element.get('href') if link_element else ""
                
                # Handle relative URLs
                if link and not (link.startswith('http://') or link.startswith('https://')):
                    base_url = urlparse(url)
                    link = f"{base_url.scheme}://{base_url.netloc}{link}"
                
                # Skip if link is invalid
                if not link or link.startswith('javascript:') or link == '#':
                    continue
                
                image_element = article.select_one(site_config["image_selector"])
                image = image_element.get('src') if image_element and image_element.get('src') else ""
                
                # Handle data-src for lazy-loaded images
                if not image and image_element:
                    for attr in ['data-src', 'data-lazy-src', 'data-original']:
                        if image_element.get(attr):
                            image = image_element.get(attr)
                            break
                
                # Handle relative image URLs
                if image and not (image.startswith('http://') or image.startswith('https://')):
                    base_url = urlparse(url)
                    image = f"{base_url.scheme}://{base_url.netloc}{image if image.startswith('/') else '/' + image}"
                
                date_element = article.select_one(site_config["date_selector"])
                date = date_element.get_text().strip() if date_element else "Recent"
                
                # Create post ID using hash of link
                post_id = hashlib.md5(link.encode()).hexdigest()
                
                # Get category from current iteration
                category = next((cat for cat, sites in SITES.items() if any(s['url'] == site_config['url'] for s in sites)), "news")
                
                # Only add articles with at least a title and link
                if title and link:
                    results.append({
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "image": image or FALLBACK_IMAGES.get(category, FALLBACK_IMAGES.get("news")),
                        "date": date,
                        "source": urlparse(url).netloc,
                        "category": category,
                        "id": post_id
                    })
            except Exception as e:
                print(f"Error extracting article details: {e}")
                continue
                
        return results
    
    except requests.exceptions.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return []
    
    except Exception as e:
        print(f"Unexpected error scraping {url}: {e}")
        return []

def create_sample_data():
    """Create sample data to use if scraping fails"""
    sample_data = {
        "news": [
            {
                "title": "Kenyan Economic Growth Surpasses Expectations",
                "link": "https://www.nation.africa/kenya/news/economy-growth",
                "summary": "Kenya's economy has shown remarkable resilience with growth exceeding analyst predictions for the second quarter...",
                "date": "2023-10-15",
                "image": FALLBACK_IMAGES.get("news"),
                "source": "nation.africa",
                "category": "news",
                "id": "sample001"
            },
            {
                "title": "New Infrastructure Projects Announced for Nairobi",
                "link": "https://www.the-star.co.ke/news/infrastructure",
                "summary": "The government has unveiled plans for major infrastructure developments in the capital city aimed at easing congestion...",
                "date": "2023-10-12",
                "image": FALLBACK_IMAGES.get("news"),
                "source": "the-star.co.ke",
                "category": "news",
                "id": "sample002"
            }
        ],
        "tech": [
            {
                "title": "Safaricom Launches New 5G Services Across Major Cities",
                "link": "https://techweez.com/2023/5g-network-expansion",
                "summary": "Kenya's largest telecom provider is expanding high-speed connectivity options to more Kenyans with new infrastructure...",
                "date": "2023-10-14",
                "image": FALLBACK_IMAGES.get("tech"),
                "source": "techweez.com",
                "category": "tech",
                "id": "sample003"
            },
            {
                "title": "Kenyan Startups Attract Record Foreign Investment",
                "link": "https://www.businessdailyafrica.com/bd/corporate/technology",
                "summary": "Tech startups in Kenya have secured unprecedented funding rounds from international investors seeking to tap into the growing innovation hub...",
                "date": "2023-10-10",
                "image": FALLBACK_IMAGES.get("tech"),
                "source": "businessdailyafrica.com",
                "category": "tech",
                "id": "sample004"
            }
        ],
        "business": [
            {
                "title": "Kenya Shilling Shows Strong Recovery Against Dollar",
                "link": "https://kenyanwallstreet.com/currency-market",
                "summary": "The local currency has recorded significant gains in recent weeks, improving economic outlook for importers and consumers...",
                "date": "2023-10-13",
                "image": FALLBACK_IMAGES.get("business"),
                "source": "kenyanwallstreet.com",
                "category": "business",
                "id": "sample005"
            },
            {
                "title": "Nairobi Securities Exchange Hits 3-Year High",
                "link": "https://www.businessdailyafrica.com/bd/markets/capital-markets",
                "summary": "Investor confidence continues to grow as the Nairobi bourse records impressive performance across multiple sectors...",
                "date": "2023-10-11",
                "image": FALLBACK_IMAGES.get("business"),
                "source": "businessdailyafrica.com",
                "category": "business",
                "id": "sample006"
            }
        ],
        "gaming": [
            {
                "title": "The Future of Gaming in Kenya: Rise of Mobile Gaming",
                "link": "https://gadgets-africa.com/2023/10/mobile-gaming-kenya-rise",
                "summary": "Mobile gaming is taking Kenya by storm, with over 12 million active players across the country. Local developers are creating culturally relevant games...",
                "date": "2023-10-15",
                "image": FALLBACK_IMAGES.get("gaming"),
                "source": "gadgets-africa.com",
                "category": "gaming",
                "id": "sample007"
            },
            {
                "title": "Esports Tournament Draws Record Viewers in Nairobi",
                "link": "https://www.paxfulkenya.com/blog/category/gaming/esports-tournament",
                "summary": "Competitive gaming continues to gain popularity with the latest championship event attracting unprecedented audience numbers...",
                "date": "2023-10-09",
                "image": FALLBACK_IMAGES.get("gaming"),
                "source": "paxfulkenya.com",
                "category": "gaming",
                "id": "sample008"
            }
        ],
        "events": [
            {
                "title": "Nairobi International Jazz Festival 2023",
                "link": "https://allevents.in/nairobi/jazz-festival",
                "summary": "Experience the world's finest jazz musicians at Kenya's premier music event, featuring both local and international artists...",
                "date": "2023-10-20",
                "image": FALLBACK_IMAGES.get("events"),
                "source": "allevents.in",
                "category": "events",
                "id": "sample009"
            },
            {
                "title": "Tech Summit Africa Coming to KICC Next Month",
                "link": "https://nairobinow.wordpress.com/tech-summit-africa",
                "summary": "Leading technology innovators and entrepreneurs will gather for the continent's largest tech conference focused on emerging market solutions...",
                "date": "2023-10-08",
                "image": FALLBACK_IMAGES.get("events"),
                "source": "nairobinow.wordpress.com",
                "category": "events",
                "id": "sample010"
            }
        ],
        "trending": [
            {
                "title": "Kenya's Tech Revolution: How Startups Are Changing the Economy",
                "link": "https://www.standardmedia.co.ke/business/article/tech-revolution",
                "summary": "Kenya's tech startup ecosystem continues to grow, with investments reaching record levels in the first quarter of 2023...",
                "date": "2023-10-14",
                "image": FALLBACK_IMAGES.get("trending"),
                "source": "standardmedia.co.ke",
                "category": "trending",
                "id": "sample011"
            },
            {
                "title": "Government Announces Major Policy Changes",
                "link": "https://www.kenyans.co.ke/news/policy-changes",
                "summary": "New regulatory framework aims to streamline business operations and improve investment climate across multiple sectors...",
                "date": "2023-10-12",
                "image": FALLBACK_IMAGES.get("trending"),
                "source": "kenyans.co.ke",
                "category": "trending",
                "id": "sample012"
            }
        ],
        "ai": [
            {
                "title": "How AI is Transforming Healthcare in East Africa",
                "link": "https://africa.businessinsider.com/tech/ai-healthcare-east-africa",
                "summary": "AI-powered diagnostic tools are helping bridge the healthcare gap in rural Kenya, with mobile applications that can detect common illnesses...",
                "date": "2023-10-10",
                "image": FALLBACK_IMAGES.get("ai"),
                "source": "businessinsider.com",
                "category": "ai",
                "id": "sample013"
            },
            {
                "title": "Kenyan Startup Launches AI-Powered Agricultural Assistant",
                "link": "https://techcrunch.com/category/artificial-intelligence/kenyan-agritech",
                "summary": "New technology aims to help farmers optimize crop yields and reduce resource wastage through advanced data analysis and recommendations...",
                "date": "2023-10-08",
                "image": FALLBACK_IMAGES.get("ai"),
                "source": "techcrunch.com",
                "category": "ai",
                "id": "sample014"
            }
        ],
        "soccer": [
            {
                "title": "Kenyan Premier League: Title Race Heats Up",
                "link": "https://www.goal.com/en-ke/news/kenyan-premier-league",
                "summary": "With just five games remaining, three teams are separated by just two points at the top of the Kenyan Premier League...",
                "date": "2023-10-15",
                "image": FALLBACK_IMAGES.get("soccer"),
                "source": "goal.com",
                "category": "soccer",
                "id": "sample015"
            },
            {
                "title": "Harambee Stars Announce Squad for World Cup Qualifiers",
                "link": "https://futaa.com/article/harambee-stars-squad",
                "summary": "Kenya's national team coach has revealed the selection of players for the upcoming crucial international fixtures...",
                "date": "2023-10-09",
                "image": FALLBACK_IMAGES.get("soccer"),
                "source": "futaa.com",
                "category": "soccer",
                "id": "sample016"
            }
        ]
    }
    return sample_data

def scrape_all_sites():
    """Scrape all configured sites and ensure data persistence."""
    all_posts = {}
    
    # Initialize or load existing data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                all_posts = json.load(f)
            # Basic validation: Ensure it's a dict
            if not isinstance(all_posts, dict):
                print(f"Warning: Data in {DATA_FILE} is not a dictionary. Initializing fresh.")
                all_posts = {category: [] for category in SITES.keys()}
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {DATA_FILE}. Initializing fresh.")
            all_posts = {category: [] for category in SITES.keys()}
        except Exception as e:
            print(f"Warning: Error loading {DATA_FILE}: {e}. Initializing fresh.")
            all_posts = {category: [] for category in SITES.keys()}
    else:
        print(f"Data file {DATA_FILE} not found. Initializing fresh.")
        all_posts = {category: [] for category in SITES.keys()}
    
    # Ensure all expected categories exist
    for category in SITES.keys():
        if category not in all_posts or not isinstance(all_posts.get(category), list):
            all_posts[category] = []

    # Process each category: Scrape and merge
    for category, sites in SITES.items():
        new_posts_for_category = []
        print(f"--- Processing category: {category} ---")
        for site_config in sites:
            print(f"Scraping {site_config['url']} for {category}...")
            try:
                site_posts = scrape_site(site_config)
                if site_posts:
                    new_posts_for_category.extend(site_posts)
                    print(f"  Found {len(site_posts)} posts.")
                else:
                    print(f"  No posts found.")
            except Exception as e:
                print(f"  Error scraping site {site_config['url']}: {e}")
            # Be nice to servers
            time.sleep(random.uniform(1, 3)) # Add slight random delay
        
        # Combine with existing posts for the category, remove duplicates
        existing_ids = {post['id'] for post in all_posts.get(category, [])}
        filtered_new_posts = [post for post in new_posts_for_category if post.get('id') and post['id'] not in existing_ids]
        
        print(f"  Added {len(filtered_new_posts)} new unique posts for {category}.")
        
        # Prepend new posts and keep top 20
        all_posts[category] = filtered_new_posts + all_posts.get(category, [])
        all_posts[category] = all_posts[category][:20]

    # Add sample data ONLY if a category is still empty AFTER scraping
    sample_data = create_sample_data()
    for category in SITES.keys():
        if not all_posts.get(category): # Check if list is empty or category missing
            print(f"Category '{category}' still empty after scraping. Adding sample data.")
            all_posts[category] = sample_data.get(category, [])[:1] # Add max 1 sample post
        elif len(all_posts[category]) < 1:
             print(f"Category '{category}' has less than 1 post after scraping. Topping up with sample data.")
             existing_ids = {post['id'] for post in all_posts.get(category, [])}
             sample_posts_needed = [p for p in sample_data.get(category, []) if p['id'] not in existing_ids]
             all_posts[category].extend(sample_posts_needed)
             all_posts[category] = all_posts[category][:1] # Ensure only 1 post total

    # Save updated data
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(all_posts, f, indent=2)
        print(f"Data saved successfully to {DATA_FILE}.")
    except Exception as e:
        print(f"Error saving data to {DATA_FILE}: {e}")

    return all_posts

def generate_html():
    """Generate HTML with the latest posts"""
    all_posts = {}
    # Load data generated by scrape_all_sites
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                all_posts = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {DATA_FILE}. Check the file content.")
            return # Stop if data file is corrupted
        except Exception as e:
            print(f"Error loading {DATA_FILE}: {e}")
            return # Stop if file cannot be loaded
    else:
        print(f"Error: Data file {DATA_FILE} not found. Run scraper first.")
        return # Stop if data file doesn't exist

    # Read the existing HTML template
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print("Error: index.html template not found.")
        return
    except Exception as e:
        print(f"Error reading index.html: {e}")
        return

    # Find where to inject the posts
    start_marker = '<main id="blog-posts">'
    end_marker = '</main>'

    start_idx = html_content.find(start_marker) + len(start_marker)
    end_idx = html_content.find(end_marker)

    if start_idx == -1 + len(start_marker) or end_idx == -1:
        print("Error: Couldn't find start/end markers in index.html")
        return

    # Generate HTML for posts
    posts_html = ""

    # Function to create HTML for a single post
    def create_post_html(post):
        # Add default values for all fields to prevent KeyErrors
        title = post.get('title', 'No Title Available').replace('"', '&quot;')
        summary = post.get('summary', 'No summary available').replace('"', '&quot;')
        link = post.get('link', '#')
        image = post.get('image', FALLBACK_IMAGES.get('news'))
        date = post.get('date', 'Recent')
        source = post.get('source', 'Unknown')
        category = post.get('category', 'news')  # Default to 'news' if category is missing
        
        return f"""
        <article class="post" data-title="{title}" data-content="{summary}" data-category="{category}">
            <img src="{image}" alt="{title}" class="post-image">
            <div class="post-content">
                <span class="category-tag {category}">{category.title()}</span>
                <div class="post-date">{date} • Source: {source}</div>
                <h2 class="post-title">{title}</h2>
                <p class="post-excerpt">{summary}</p>
                <a href="{link}" class="read-more" target="_blank">Read more →</a>
                
                <div class="share-buttons">
                    <a href="https://twitter.com/intent/tweet?url={link}&text={title}" class="share-button twitter" target="_blank" aria-label="Share on Twitter">
                        <i class="fab fa-twitter"></i>
                    </a>
                    <a href="https://www.facebook.com/sharer/sharer.php?u={link}" class="share-button facebook" target="_blank" aria-label="Share on Facebook">
                        <i class="fab fa-facebook-f"></i>
                    </a>
                    <a href="https://www.linkedin.com/shareArticle?mini=true&url={link}&title={title}" class="share-button linkedin" target="_blank" aria-label="Share on LinkedIn">
                        <i class="fab fa-linkedin-in"></i>
                    </a>
                </div>
            </div>
        </article>
        """
    
    # Generate 1 post for each category
    if isinstance(all_posts, dict):
        for category in all_posts.keys():
            # Ensure the category exists and has posts before trying to access index 0
            if category in all_posts and isinstance(all_posts[category], list) and all_posts[category]:
                posts = all_posts[category][:1]  # Get only the top 1 post
                for post in posts:
                    posts_html += create_post_html(post)
            else:
                print(f"Skipping category {category} - no posts found or data malformed.")
    else:
        print(f"Error: Expected all_posts to be a dictionary, but got {type(all_posts)}")
        return

    # Update the HTML file
    new_html = html_content[:start_idx] + posts_html + html_content[end_idx:]

    # Write to a new file first (safer)
    try:
        with open('index_new.html', 'w', encoding='utf-8') as f:
            f.write(new_html)
        # If successful, replace the original
        os.replace('index_new.html', 'index.html')
        print(f"Blog HTML updated successfully at {datetime.datetime.now()}")
    except Exception as e:
        print(f"Error writing or replacing index.html: {e}")

def update_blog():
    """Main function to update the blog"""
    print("Scraping sites for new content...")
    scrape_all_sites()
    print("Generating HTML...")
    generate_html()

# Suppress only the single InsecureRequestWarning from urllib3
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Allow running as a script or being imported
if __name__ == "__main__":
    # Run immediately once
    update_blog()

    # Schedule to run every 30 minutes (changed from 12 hours)
    schedule.every(30).minutes.do(update_blog)

    print("Web scraper running. Blog will update every 30 minutes.")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute 