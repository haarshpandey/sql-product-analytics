"""
Seed a sample e-commerce SQLite database for the product analytics case study.

Generates a deterministic (seeded) dataset: customers, products, orders,
order items, and a marketing-funnel event log over 12 months.

The data is SYNTHETIC — built to look like a small D2C store so the SQL
analysis queries have something realistic to chew on.

Run:  python seed.py   -> creates store.db
"""

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "store.db"
SEED = 42
N_CUSTOMERS = 2000

PRODUCTS = [
    # (name, category, price)
    ("Trailhead Backpack", "Outdoor", 89.0),
    ("Summit Water Bottle", "Outdoor", 24.0),
    ("Merino Base Layer", "Apparel", 65.0),
    ("Ridgeline Jacket", "Apparel", 149.0),
    ("Campfire Mug", "Home", 18.0),
    ("Basecamp Tent 2P", "Outdoor", 229.0),
    ("Everyday Tote", "Apparel", 45.0),
    ("Insulated Lunch Box", "Home", 32.0),
]

CHANNELS = ["organic", "paid_search", "social", "email", "referral"]


def main() -> None:
    rng = random.Random(SEED)
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.executescript("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            acquired_date DATE NOT NULL,
            channel TEXT NOT NULL,
            country TEXT NOT NULL
        );
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        );
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
            order_date DATE NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        CREATE TABLE order_items (
            order_id INTEGER NOT NULL REFERENCES orders(order_id),
            product_id INTEGER NOT NULL REFERENCES products(product_id),
            quantity INTEGER NOT NULL,
            PRIMARY KEY (order_id, product_id)
        );
        CREATE TABLE funnel_events (
            event_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
            event_date DATE NOT NULL,
            event_type TEXT NOT NULL  -- page_view, add_to_cart, checkout, purchase
        );
    """)

    cur.executemany(
        "INSERT INTO products (product_id, name, category, price) VALUES (?, ?, ?, ?)",
        [(i + 1, n, c, p) for i, (n, c, p) in enumerate(PRODUCTS)],
    )

    start = date(2024, 1, 1)
    customers, orders, items, events = [], [], [], []
    order_id = 1
    event_id = 1

    for cid in range(1, N_CUSTOMERS + 1):
        acquired = start + timedelta(days=rng.randint(0, 364))
        channel = rng.choices(CHANNELS, weights=[30, 25, 20, 15, 10])[0]
        country = rng.choices(["US", "CA", "UK", "DE"], weights=[70, 10, 12, 8])[0]
        customers.append((cid, acquired.isoformat(), channel, country))

        # Funnel: everyone views; conversion decays down the funnel
        d = acquired + timedelta(days=rng.randint(0, 30))
        events.append((event_id, cid, d.isoformat(), "page_view")); event_id += 1
        if rng.random() < 0.55:
            d += timedelta(days=rng.randint(0, 3))
            events.append((event_id, cid, d.isoformat(), "add_to_cart")); event_id += 1
            if rng.random() < 0.65:
                d += timedelta(days=rng.randint(0, 2))
                events.append((event_id, cid, d.isoformat(), "checkout")); event_id += 1
                if rng.random() < 0.80:
                    events.append((event_id, cid, d.isoformat(), "purchase")); event_id += 1
                    # Orders: 1 + chance of repeats (loyal customers buy more)
                    n_orders = 1 + (1 if rng.random() < 0.35 else 0) + (1 if rng.random() < 0.12 else 0)
                    for _ in range(n_orders):
                        od = d + timedelta(days=rng.randint(0, 300))
                        if od > date(2024, 12, 31):
                            break
                        orders.append((order_id, cid, od.isoformat()))
                        for pid in rng.sample(range(1, 9), k=rng.randint(1, 3)):
                            items.append((order_id, pid, rng.randint(1, 2)))
                        order_id += 1

    cur.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", customers)
    cur.executemany("INSERT INTO orders VALUES (?, ?, ?)", orders)
    cur.executemany("INSERT INTO order_items VALUES (?, ?, ?)", items)
    cur.executemany("INSERT INTO funnel_events VALUES (?, ?, ?, ?)", events)
    con.commit()

    n_orders = cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    revenue = cur.execute(
        "SELECT ROUND(SUM(oi.quantity * p.price), 2) FROM order_items oi JOIN products p USING (product_id)"
    ).fetchone()[0]
    print(f"customers={len(customers):,} orders={n_orders:,} revenue=${revenue:,.0f} events={len(events):,}")
    con.close()


if __name__ == "__main__":
    main()
