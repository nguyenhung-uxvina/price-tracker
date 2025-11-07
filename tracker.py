#!/usr/bin/env python3
"""
Product Price Tracker
Track prices from e-commerce sites with historical data, trends, and alerts.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import re


# Configuration
DATA_FILE = "tracked_products.json"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Colors and formatting (basic ANSI codes for cross-platform support)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @staticmethod
    def disable():
        """Disable colors for Windows compatibility if needed"""
        Colors.HEADER = ''
        Colors.BLUE = ''
        Colors.CYAN = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.RED = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''
        Colors.END = ''

# Try to enable colors on Windows
try:
    import os
    if os.name == 'nt':
        os.system('color')
except:
    Colors.disable()


class PriceTracker:
    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self.products = self._load_data()

    def _load_data(self) -> Dict:
        """Load tracked products from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {self.data_file} is corrupted. Starting fresh.")
                return {}
        return {}

    def _save_data(self):
        """Save tracked products to JSON file."""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)

    def add_product(self, url: str, name: str) -> bool:
        """Add a new product to track."""
        if name in self.products:
            print(f"Error: Product '{name}' already exists.")
            return False

        # Try to fetch initial price
        print(f"Adding product '{name}'...")
        price = self._scrape_price(url)

        if price is None:
            print(f"Warning: Could not fetch initial price, but product will be added.")

        self.products[name] = {
            "name": name,
            "url": url,
            "prices": []
        }

        # Add initial price if available
        if price is not None:
            self._add_price_entry(name, price)
            print(f"[+] Added '{name}' with current price: ${price:.2f}")
        else:
            print(f"[+] Added '{name}' (price will be fetched on next check)")

        self._save_data()
        return True

    def _add_price_entry(self, name: str, price: float):
        """Add a price entry with timestamp to a product."""
        timestamp = datetime.now().isoformat()
        self.products[name]["prices"].append({
            "date": timestamp,
            "price": price
        })

    def _scrape_price(self, url: str) -> Optional[float]:
        """Scrape price from URL. Supports Amazon and general e-commerce sites."""
        try:
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Try different selectors based on site
            if "amazon" in url.lower():
                return self._scrape_amazon(soup)
            else:
                return self._scrape_generic(soup)

        except requests.RequestException as e:
            print(f"Error fetching URL: {e}")
            return None
        except Exception as e:
            print(f"Error parsing price: {e}")
            return None

    def _scrape_amazon(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from Amazon product page."""
        # Amazon price selectors (they change frequently)
        selectors = [
            'span.a-price-whole',
            'span.a-offscreen',
            'span#priceblock_ourprice',
            'span#priceblock_dealprice',
            'span.a-color-price',
        ]

        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                price_text = element.get_text().strip()
                price = self._extract_price_from_text(price_text)
                if price is not None:
                    return price

        return None

    def _scrape_generic(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from generic e-commerce site."""
        # Common price selectors
        selectors = [
            '[class*="price"]',
            '[id*="price"]',
            '[class*="Price"]',
            'span.price',
            'div.price',
            'p.price',
        ]

        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                price_text = element.get_text().strip()
                price = self._extract_price_from_text(price_text)
                if price is not None:
                    return price

        return None

    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """Extract numeric price from text string."""
        # Remove common currency symbols and clean text
        text = text.replace('$', '').replace('£', '').replace('€', '')
        text = text.replace(',', '').strip()

        # Find price pattern (e.g., 123.45 or 123)
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass

        return None

    def check_all(self) -> int:
        """Check and update prices for all tracked products."""
        if not self.products:
            print("No products being tracked.")
            return 0

        print(f"Checking {len(self.products)} product(s)...")
        updated = 0

        for name, product in self.products.items():
            print(f"\nChecking '{name}'...")
            price = self._scrape_price(product["url"])

            if price is not None:
                self._add_price_entry(name, price)

                # Show price change if we have previous data
                if len(product["prices"]) > 1:
                    old_price = product["prices"][-2]["price"]
                    change = price - old_price
                    change_pct = (change / old_price) * 100

                    if change > 0:
                        print(f"  Current: ${price:.2f} (UP ${change:.2f}, +{change_pct:.1f}%)")
                    elif change < 0:
                        print(f"  Current: ${price:.2f} (DOWN ${abs(change):.2f}, {change_pct:.1f}%)")
                    else:
                        print(f"  Current: ${price:.2f} (no change)")
                else:
                    print(f"  Current: ${price:.2f}")

                updated += 1
            else:
                print(f"  Failed to fetch price")

        self._save_data()
        print(f"\n[+] Updated {updated}/{len(self.products)} product(s)")
        return updated

    def list_products(self):
        """List all tracked products with latest prices."""
        if not self.products:
            print(f"\n{Colors.YELLOW}No products being tracked.{Colors.END}")
            print(f"Use '{Colors.CYAN}python tracker.py add <url> <name>{Colors.END}' to add a product.\n")
            return

        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{'Product':<35} {'Price':<15} {'Entries':<12} {'Trend':<10}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}")

        for name, product in self.products.items():
            if product["prices"]:
                latest_price = product["prices"][-1]["price"]
                price_str = f"${latest_price:.2f}"
                entries = len(product["prices"])
                trend = self._calculate_trend(product["prices"])

                # Color code the trend
                if trend == "Rising":
                    trend_colored = f"{Colors.RED}{trend}{Colors.END}"
                elif trend == "Falling":
                    trend_colored = f"{Colors.GREEN}{trend}{Colors.END}"
                else:
                    trend_colored = f"{Colors.CYAN}{trend}{Colors.END}"

                # Color code the price
                price_colored = f"{Colors.BOLD}{Colors.YELLOW}{price_str}{Colors.END}"
            else:
                price_colored = f"{Colors.YELLOW}N/A{Colors.END}"
                entries = 0
                trend_colored = f"{Colors.YELLOW}N/A{Colors.END}"

            print(f"{name:<35} {price_colored:<24} {entries:<12} {trend_colored:<19}")

        print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}\n")

    def show_history(self, name: str):
        """Show price history for a specific product."""
        if name not in self.products:
            print(f"Error: Product '{name}' not found.")
            return

        product = self.products[name]
        print(f"\nPrice History for: {name}")
        print(f"URL: {product['url']}")
        print("\n" + "=" * 60)

        if not product["prices"]:
            print("No price history available.")
            return

        print(f"{'Date':<25} {'Price':<15} {'Change':<15}")
        print("-" * 60)

        for i, entry in enumerate(product["prices"]):
            date_str = datetime.fromisoformat(entry["date"]).strftime("%Y-%m-%d %H:%M:%S")
            price = entry["price"]

            if i > 0:
                prev_price = product["prices"][i-1]["price"]
                change = price - prev_price
                change_pct = (change / prev_price) * 100

                if change > 0:
                    change_str = f"UP ${change:.2f} (+{change_pct:.1f}%)"
                elif change < 0:
                    change_str = f"DOWN ${abs(change):.2f} ({change_pct:.1f}%)"
                else:
                    change_str = "No change"
            else:
                change_str = "Initial"

            print(f"{date_str:<25} ${price:<14.2f} {change_str:<15}")

        # Show summary
        print("\n" + "=" * 60)
        trend = self._calculate_trend(product["prices"])
        print(f"Trend: {trend}")

        if len(product["prices"]) >= 2:
            first_price = product["prices"][0]["price"]
            latest_price = product["prices"][-1]["price"]
            total_change = latest_price - first_price
            total_change_pct = (total_change / first_price) * 100

            print(f"Overall Change: ${total_change:+.2f} ({total_change_pct:+.1f}%)")

    def _calculate_trend(self, prices: List[Dict]) -> str:
        """Calculate trend from price history."""
        if len(prices) < 2:
            return "Insufficient data"

        # Calculate trend over last 3 entries (or all if less)
        window = min(3, len(prices))
        recent_prices = [p["price"] for p in prices[-window:]]

        # Check if prices are rising, falling, or stable
        increases = sum(1 for i in range(1, len(recent_prices)) if recent_prices[i] > recent_prices[i-1])
        decreases = sum(1 for i in range(1, len(recent_prices)) if recent_prices[i] < recent_prices[i-1])

        if increases > decreases:
            return "Rising"
        elif decreases > increases:
            return "Falling"
        else:
            return "Stable"

    def show_stats(self, name: Optional[str] = None):
        """Show detailed statistics for a product or all products."""
        if name:
            # Stats for single product
            if name not in self.products:
                print(f"\n{Colors.RED}Error: Product '{name}' not found.{Colors.END}\n")
                return

            self._show_product_stats(name, self.products[name])
        else:
            # Stats for all products
            if not self.products:
                print(f"\n{Colors.YELLOW}No products being tracked.{Colors.END}\n")
                return

            print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}")
            print(f"{Colors.BOLD}PRICE TRACKER STATISTICS{Colors.END}")
            print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}\n")

            for product_name, product in self.products.items():
                self._show_product_stats(product_name, product)
                print()

    def _show_product_stats(self, name: str, product: Dict):
        """Show statistics for a single product."""
        print(f"{Colors.BOLD}{Colors.CYAN}{name}{Colors.END}")
        print(f"URL: {Colors.BLUE}{product['url']}{Colors.END}")

        if not product["prices"]:
            print(f"  {Colors.YELLOW}No price data available{Colors.END}\n")
            return

        prices = [p["price"] for p in product["prices"]]
        first_price = prices[0]
        latest_price = prices[-1]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)

        # Calculate changes
        total_change = latest_price - first_price
        total_change_pct = (total_change / first_price) * 100 if first_price != 0 else 0

        # Find best and worst prices with dates
        min_idx = prices.index(min_price)
        max_idx = prices.index(max_price)
        min_date = datetime.fromisoformat(product["prices"][min_idx]["date"]).strftime("%Y-%m-%d")
        max_date = datetime.fromisoformat(product["prices"][max_idx]["date"]).strftime("%Y-%m-%d")

        # Calculate volatility (standard deviation)
        if len(prices) > 1:
            variance = sum((p - avg_price) ** 2 for p in prices) / len(prices)
            volatility = variance ** 0.5
            volatility_pct = (volatility / avg_price) * 100 if avg_price != 0 else 0
        else:
            volatility_pct = 0

        # Display stats
        print(f"  {Colors.BOLD}Price Range:{Colors.END}")
        print(f"    Current:  {Colors.YELLOW}${latest_price:.2f}{Colors.END}")
        print(f"    Average:  ${avg_price:.2f}")
        print(f"    Lowest:   {Colors.GREEN}${min_price:.2f}{Colors.END} (on {min_date})")
        print(f"    Highest:  {Colors.RED}${max_price:.2f}{Colors.END} (on {max_date})")

        print(f"\n  {Colors.BOLD}Price Changes:{Colors.END}")
        change_color = Colors.GREEN if total_change < 0 else Colors.RED if total_change > 0 else Colors.CYAN
        print(f"    Overall:  {change_color}${total_change:+.2f} ({total_change_pct:+.1f}%){Colors.END}")
        print(f"    Spread:   ${max_price - min_price:.2f} ({((max_price - min_price) / min_price * 100):.1f}%)")

        print(f"\n  {Colors.BOLD}Statistics:{Colors.END}")
        print(f"    Data Points:  {len(prices)}")
        print(f"    Volatility:   {volatility_pct:.1f}%")
        print(f"    Trend:        {self._format_trend(self._calculate_trend(product['prices']))}")

        # First and last recorded dates
        first_date = datetime.fromisoformat(product["prices"][0]["date"]).strftime("%Y-%m-%d %H:%M")
        last_date = datetime.fromisoformat(product["prices"][-1]["date"]).strftime("%Y-%m-%d %H:%M")
        print(f"    First Check:  {first_date}")
        print(f"    Last Check:   {last_date}")

    def _format_trend(self, trend: str) -> str:
        """Format trend with color."""
        if trend == "Rising":
            return f"{Colors.RED}{trend}{Colors.END}"
        elif trend == "Falling":
            return f"{Colors.GREEN}{trend}{Colors.END}"
        else:
            return f"{Colors.CYAN}{trend}{Colors.END}"

    def check_alerts(self, drop_threshold: float):
        """Check for price drops exceeding threshold percentage."""
        if not self.products:
            print("No products being tracked.")
            return

        print(f"\nChecking for price drops > {drop_threshold}%...")
        alerts = []

        for name, product in self.products.items():
            if len(product["prices"]) < 2:
                continue

            latest_price = product["prices"][-1]["price"]
            previous_price = product["prices"][-2]["price"]

            drop = ((previous_price - latest_price) / previous_price) * 100

            if drop >= drop_threshold:
                alerts.append({
                    "name": name,
                    "previous": previous_price,
                    "current": latest_price,
                    "drop": drop
                })

        if alerts:
            print("\n[!] PRICE DROP ALERTS:")
            print("=" * 70)
            for alert in alerts:
                print(f"Product: {alert['name']}")
                print(f"  Previous: ${alert['previous']:.2f}")
                print(f"  Current:  ${alert['current']:.2f}")
                print(f"  Drop:     {alert['drop']:.1f}%")
                print()
        else:
            print("No significant price drops detected.")


def show_help():
    """Display detailed help information with examples."""
    help_text = f"""
{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}
{Colors.BOLD}PRODUCT PRICE TRACKER - Help{Colors.END}
{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}

{Colors.BOLD}DESCRIPTION:{Colors.END}
  Track product prices from e-commerce sites with historical data,
  trend analysis, and price drop alerts.

{Colors.BOLD}COMMANDS:{Colors.END}

  {Colors.CYAN}add{Colors.END} <url> <name>
      Add a new product to track
      Example: python tracker.py add "https://amazon.com/dp/B08N5WRWNW" "AirPods Pro"

  {Colors.CYAN}check{Colors.END}
      Update prices for all tracked products
      Example: python tracker.py check

  {Colors.CYAN}list{Colors.END}
      Display all tracked products with latest prices and trends
      Example: python tracker.py list

  {Colors.CYAN}history{Colors.END} <name>
      Show complete price history for a product
      Example: python tracker.py history "AirPods Pro"

  {Colors.CYAN}stats{Colors.END} [name]
      Show detailed statistics (avg, min, max, volatility, etc.)
      Example: python tracker.py stats
      Example: python tracker.py stats "AirPods Pro"

  {Colors.CYAN}alert{Colors.END} --drop <percentage>
      Check for price drops exceeding threshold
      Example: python tracker.py alert --drop 10

  {Colors.CYAN}help{Colors.END}
      Display this help message
      Example: python tracker.py help

{Colors.BOLD}WORKFLOW:{Colors.END}
  1. Add products you want to track
  2. Run 'check' regularly (daily recommended) to build price history
  3. Use 'list' to see current prices and trends
  4. Use 'history' to view detailed price changes
  5. Use 'stats' for comprehensive analytics
  6. Use 'alert' to find good deals

{Colors.BOLD}TIPS:{Colors.END}
  - Amazon URLs work best: https://amazon.com/dp/PRODUCT_ID
  - Schedule 'check' command daily for best results
  - Green = falling prices (good for buying!)
  - Red = rising prices (missed opportunity?)
  - Data stored in: {Colors.YELLOW}tracked_products.json{Colors.END}

{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}
"""
    print(help_text)


def main():
    parser = argparse.ArgumentParser(
        description="Product Price Tracker - Track prices from e-commerce sites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tracker.py add "https://amazon.com/product" "Product Name"
  python tracker.py check
  python tracker.py list
  python tracker.py stats
  python tracker.py history "Product Name"
  python tracker.py alert --drop 10
  python tracker.py help
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Help command
    subparsers.add_parser('help', help='Show detailed help and usage examples')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a product to track')
    add_parser.add_argument('url', help='Product URL')
    add_parser.add_argument('name', help='Product name')

    # Check command
    subparsers.add_parser('check', help='Update prices for all tracked products')

    # List command
    subparsers.add_parser('list', help='List all tracked products')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show detailed statistics')
    stats_parser.add_argument('name', nargs='?', default=None, help='Product name (optional)')

    # History command
    history_parser = subparsers.add_parser('history', help='Show price history for a product')
    history_parser.add_argument('name', help='Product name')

    # Alert command
    alert_parser = subparsers.add_parser('alert', help='Check for price drop alerts')
    alert_parser.add_argument('--drop', type=float, required=True,
                            help='Alert if price dropped more than this percentage')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'help':
        show_help()
        return

    tracker = PriceTracker()

    if args.command == 'add':
        tracker.add_product(args.url, args.name)

    elif args.command == 'check':
        tracker.check_all()

    elif args.command == 'list':
        tracker.list_products()

    elif args.command == 'stats':
        tracker.show_stats(args.name)

    elif args.command == 'history':
        tracker.show_history(args.name)

    elif args.command == 'alert':
        tracker.check_alerts(args.drop)


if __name__ == '__main__':
    main()
