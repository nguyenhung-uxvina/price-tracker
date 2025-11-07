# Product Price Tracker 📊

A powerful command-line tool to track product prices from e-commerce sites with historical data, advanced statistics, trend analysis, and price drop alerts. Never miss a great deal again!

![Price Tracker](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🛒 **Multi-Site Support** - Track products from Amazon and generic e-commerce sites
- 📈 **Historical Data** - Store complete price history with timestamps in JSON
- 🤖 **Automatic Scraping** - Smart price extraction with BeautifulSoup
- 📊 **Advanced Statistics** - Average prices, volatility, price ranges, and more
- 🎯 **Trend Detection** - Automatic identification of rising/falling/stable trends
- 🔔 **Price Drop Alerts** - Customizable threshold alerts for great deals
- 🎨 **Beautiful Output** - Color-coded, formatted display for easy reading
- 💡 **Comprehensive Help** - Built-in help system with examples

## 🚀 Quick Start

### Installation

1. **Clone or download** this repository
2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Basic Usage

```bash
# Get help
python tracker.py help

# Add a product to track
python tracker.py add "https://www.amazon.com/dp/B08N5WRWNW" "Apple AirPods Pro"

# Check/update all prices
python tracker.py check

# View all tracked products
python tracker.py list

# View detailed statistics
python tracker.py stats

# Check for price drops > 10%
python tracker.py alert --drop 10
```

## 📖 Commands Reference

### 1️⃣ Add Product

Add a new product to your tracking list:

```bash
python tracker.py add <URL> <Name>
```

**Example:**
```bash
python tracker.py add "https://www.amazon.com/dp/B08N5WRWNW" "Apple AirPods Pro"
```

**Output:**
```
Adding product 'Apple AirPods Pro'...
[+] Added 'Apple AirPods Pro' with current price: $249.99
```

---

### 2️⃣ Check Prices

Update prices for all tracked products:

```bash
python tracker.py check
```

**Output:**
```
Checking 3 product(s)...

Checking 'Apple AirPods Pro'...
  Current: $239.99 (DOWN $10.00, -4.0%)

[+] Updated 3/3 product(s)
```

---

### 3️⃣ List Products

Display all tracked products with a beautiful formatted table:

```bash
python tracker.py list
```

**Output:**
```
================================================================================
Product                             Price           Entries      Trend
================================================================================
Apple AirPods Pro                   $239.99         5            Falling
Wireless Mouse                      $23.99          8            Falling
Mechanical Keyboard                 $104.99         8            Rising
================================================================================
```

**Color Guide:**
- 🟡 Yellow = Prices
- 🟢 Green = Falling (good for buying!)
- 🔴 Red = Rising (prices going up)

---

### 4️⃣ View Statistics

Show comprehensive statistics for all products or a specific product:

```bash
# All products
python tracker.py stats

# Specific product
python tracker.py stats "Apple AirPods Pro"
```

**Output:**
```
Apple AirPods Pro
URL: https://www.amazon.com/dp/B08N5WRWNW

  Price Range:
    Current:  $239.99
    Average:  $245.80
    Lowest:   $234.99 (on 2025-11-05)
    Highest:  $249.99 (on 2025-10-31)

  Price Changes:
    Overall:  $-10.00 (-4.0%)
    Spread:   $15.00 (6.4%)

  Statistics:
    Data Points:  5
    Volatility:   2.3%
    Trend:        Falling
    First Check:  2025-10-31 10:30
    Last Check:   2025-11-07 10:30
```

**Statistics Explained:**
- **Average**: Mean price across all data points
- **Lowest/Highest**: Best and worst prices with dates
- **Spread**: Difference between highest and lowest prices
- **Volatility**: Price variation (standard deviation) - higher = more unstable
- **Data Points**: Number of price checks recorded

---

### 5️⃣ Price History

View complete price history for a product:

```bash
python tracker.py history "Product Name"
```

**Example:**
```bash
python tracker.py history "Apple AirPods Pro"
```

**Output:**
```
Price History for: Apple AirPods Pro
URL: https://www.amazon.com/dp/B08N5WRWNW

============================================================
Date                      Price           Change
------------------------------------------------------------
2025-10-31 10:30:00       $249.99         Initial
2025-11-01 10:30:00       $249.99         No change
2025-11-02 10:30:00       $244.99         DOWN $5.00 (-2.0%)
2025-11-03 10:30:00       $239.99         DOWN $5.00 (-2.0%)
============================================================
Trend: Falling
Overall Change: $-10.00 (-4.0%)
```

---

### 6️⃣ Price Alerts

Check for significant price drops:

```bash
python tracker.py alert --drop <percentage>
```

**Example:**
```bash
python tracker.py alert --drop 5
```

**Output:**
```
Checking for price drops > 5.0%...

[!] PRICE DROP ALERTS:
======================================================================
Product: Wireless Mouse
  Previous: $29.99
  Current:  $23.99
  Drop:     20.0%
======================================================================
```

---

### 7️⃣ Help

Display comprehensive help with all commands:

```bash
python tracker.py help
```

## Data Storage

All tracked products and price history are stored in `tracked_products.json`:

```json
{
  "Product Name": {
    "name": "Product Name",
    "url": "https://example.com/product",
    "prices": [
      {
        "date": "2025-01-15T10:30:00",
        "price": 99.99
      },
      {
        "date": "2025-01-16T10:30:00",
        "price": 89.99
      }
    ]
  }
}
```

## Supported Sites

### Tested
- **Amazon** - Full support with multiple price selector fallbacks

### Generic Support
The tracker attempts to find prices on any e-commerce site using common price selectors:
- Elements with "price" in class or id
- Common price HTML tags

You may need to test with specific sites to ensure compatibility.

## How Price Scraping Works

1. Sends HTTP request with browser-like User-Agent
2. Parses HTML with BeautifulSoup
3. Searches for price using site-specific or generic selectors
4. Extracts numeric price from text (handles currency symbols)
5. Stores price with timestamp in JSON

## 🧠 How It Works

### Price Scraping Process

1. **HTTP Request** - Sends request with browser-like User-Agent to avoid basic blocking
2. **HTML Parsing** - Uses BeautifulSoup to parse page content
3. **Smart Extraction** - Tries multiple selectors (site-specific then generic)
4. **Price Parsing** - Extracts numeric value from text (handles $, £, €, commas)
5. **Storage** - Saves to JSON with ISO timestamp

### Trend Detection Algorithm

Trends are calculated using the **last 3 price entries** with a sliding window approach:

- **Rising** 🔴 - More increases than decreases (prices going up)
- **Falling** 🟢 - More decreases than increases (good for buying!)
- **Stable** 🔵 - Equal increases and decreases (no clear direction)

**Example:**
```
Prices: $100 → $105 → $110 → $108
Last 3: $105 → $110 (up) → $108 (down)
Result: 1 increase, 1 decrease = Stable
```

### Statistics Calculations

- **Average**: Mean of all recorded prices
- **Volatility**: Standard deviation as percentage (measures price stability)
  - Low volatility (< 5%) = Stable pricing
  - High volatility (> 10%) = Unpredictable pricing
- **Spread**: Range between highest and lowest prices
- **Overall Change**: Difference between first and latest price

## 🌐 Supported Sites

### ✅ Tested & Working
- **Amazon** - Full support with multiple price selector fallbacks
  - Best URL format: `https://www.amazon.com/dp/PRODUCT_ID`

### 🔄 Generic Support
The tracker uses intelligent selectors for any e-commerce site:
- Elements with "price" in class or id attributes
- Common HTML price containers
- Site-specific patterns (expandable)

**Note:** Some sites have anti-scraping measures. Test your target site first!

## 💡 Pro Tips

### Getting Best Results

1. **Schedule Regular Checks**
   ```bash
   # Windows (Task Scheduler)
   # Linux/Mac (cron - daily at 9 AM)
   0 9 * * * cd /path/to/tracker && python tracker.py check
   ```

2. **Use Clean Product URLs**
   - ✅ Good: `https://amazon.com/dp/B08N5WRWNW`
   - ❌ Bad: `https://amazon.com/product/...?ref=xyz&tag=abc`

3. **Meaningful Product Names**
   - ✅ Good: "AirPods Pro 2nd Gen"
   - ❌ Bad: "Product1"

4. **Monitor Trends**
   - Check `stats` weekly to identify best buying windows
   - Set alerts slightly above expected discounts (e.g., 8% if expecting 10%)

5. **Backup Your Data**
   ```bash
   # Backup tracked_products.json regularly
   cp tracked_products.json tracked_products_backup.json
   ```

## 🔧 Troubleshooting

### Price Not Detected

**Problem:** "Failed to fetch price" message

**Solutions:**
- ✅ Verify URL works in browser
- ✅ Check if site requires login/region (some Amazon items are region-locked)
- ✅ Site may have anti-scraping (try different product)
- ✅ Use clean URL without tracking parameters

### Request Blocked

**Problem:** HTTP 403/429 errors

**Solutions:**
- ✅ Add delays between checks (don't check too frequently)
- ✅ Some sites block datacenter IPs
- ✅ User-Agent is already set, but some sites need more headers
- ✅ Consider using demo data for testing

### Unicode Errors (Windows)

**Problem:** Character encoding errors

**Solution:** Already fixed! The tool uses ASCII-safe characters for Windows compatibility.

## 📊 Example Workflow

### Day 1: Setup
```bash
python tracker.py add "https://amazon.com/dp/B08N5WRWNW" "AirPods Pro"
python tracker.py add "https://amazon.com/dp/B0CHWRXH8B" "Echo Dot"
python tracker.py list
```

### Daily: Check Prices
```bash
python tracker.py check
python tracker.py alert --drop 5
```

### Weekly: Review Analytics
```bash
python tracker.py stats
python tracker.py history "AirPods Pro"
```

### When You See a Deal
```bash
# Check if it's a good price
python tracker.py stats "AirPods Pro"
# Look at lowest price in history
# If current is at/near lowest, it's a good deal!
```

## 🚧 Limitations

- **Anti-Scraping**: Some sites actively block automated access
- **Dynamic Content**: Sites using JavaScript for prices may not work (requires Selenium)
- **Regional Restrictions**: Some products only available in certain regions
- **Rate Limiting**: Frequent checks may get temporarily blocked
- **Selector Changes**: Sites may update HTML structure (selectors need updates)

## 🔮 Future Enhancements

Planned features:
- [ ] Multi-currency support
- [ ] Price charts/visualization
- [ ] Email/SMS notifications
- [ ] Browser extension
- [ ] Database support (SQLite/PostgreSQL)
- [ ] Export to CSV/Excel
- [ ] More e-commerce sites (eBay, Walmart, Best Buy)
- [ ] Selenium support for JavaScript-heavy sites
- [ ] Docker container
- [ ] Web dashboard

## 📝 License

MIT License - Free to use, modify, and distribute.

## 🤝 Contributing

Contributions welcome! Feel free to:
- Add support for new e-commerce sites
- Improve price selectors
- Add new features
- Fix bugs
- Improve documentation

## ⚠️ Disclaimer

This tool is for personal use only. Please:
- Respect website Terms of Service
- Don't overload sites with requests
- Use reasonable check intervals
- Comply with robots.txt
- Consider legal implications in your jurisdiction

**Note:** Web scraping legality varies by jurisdiction. Use responsibly and ethically.
