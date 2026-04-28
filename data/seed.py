import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "northwind.db")


def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS Categories (
        CategoryID   INTEGER PRIMARY KEY,
        CategoryName TEXT NOT NULL,
        Description  TEXT
    );

    CREATE TABLE IF NOT EXISTS Suppliers (
        SupplierID   INTEGER PRIMARY KEY,
        CompanyName  TEXT NOT NULL,
        Country      TEXT,
        City         TEXT
    );

    CREATE TABLE IF NOT EXISTS Products (
        ProductID       INTEGER PRIMARY KEY,
        ProductName     TEXT NOT NULL,
        SupplierID      INTEGER REFERENCES Suppliers(SupplierID),
        CategoryID      INTEGER REFERENCES Categories(CategoryID),
        UnitPrice       REAL DEFAULT 0,
        UnitsInStock    INTEGER DEFAULT 0,
        Discontinued    INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS Customers (
        CustomerID   TEXT PRIMARY KEY,
        CompanyName  TEXT NOT NULL,
        Country      TEXT,
        City         TEXT
    );

    CREATE TABLE IF NOT EXISTS Employees (
        EmployeeID  INTEGER PRIMARY KEY,
        FirstName   TEXT NOT NULL,
        LastName    TEXT NOT NULL,
        Title       TEXT,
        HireDate    TEXT
    );

    CREATE TABLE IF NOT EXISTS Orders (
        OrderID      INTEGER PRIMARY KEY,
        CustomerID   TEXT REFERENCES Customers(CustomerID),
        EmployeeID   INTEGER REFERENCES Employees(EmployeeID),
        OrderDate    TEXT,
        ShipCountry  TEXT
    );

    CREATE TABLE IF NOT EXISTS OrderDetails (
        OrderDetailID INTEGER PRIMARY KEY,
        OrderID       INTEGER REFERENCES Orders(OrderID),
        ProductID     INTEGER REFERENCES Products(ProductID),
        UnitPrice     REAL,
        Quantity      INTEGER,
        Discount      REAL DEFAULT 0
    );
    """)

    cur.executemany("INSERT OR IGNORE INTO Categories VALUES (?,?,?)", [
        (1, "Beverages",    "Soft drinks, coffees, teas, beers, and ales"),
        (2, "Condiments",   "Sweet and savory sauces, relishes, spreads, and seasonings"),
        (3, "Confections",  "Desserts, candies, and sweet breads"),
        (4, "Dairy Products", "Cheeses"),
        (5, "Grains/Cereals", "Breads, crackers, pasta, and cereal"),
        (6, "Meat/Poultry", "Prepared meats"),
        (7, "Produce",      "Dried fruit and bean curd"),
        (8, "Seafood",      "Seaweed and fish"),
    ])

    cur.executemany("INSERT OR IGNORE INTO Suppliers VALUES (?,?,?,?)", [
        (1, "Exotic Liquids",          "UK",      "London"),
        (2, "New Orleans Cajun Delights", "USA",  "New Orleans"),
        (3, "Grandma Kelly's Homestead",  "USA",  "Ann Arbor"),
        (4, "Tokyo Traders",           "Japan",   "Tokyo"),
        (5, "Cooperativa de Quesos",   "Spain",   "Oviedo"),
        (6, "Mayumi's",                "Japan",   "Osaka"),
        (7, "Pavlova Ltd.",            "Australia","Melbourne"),
        (8, "Specialty Biscuits Ltd.", "UK",      "Manchester"),
    ])

    cur.executemany("INSERT OR IGNORE INTO Products VALUES (?,?,?,?,?,?,?)", [
        (1,  "Chai",                  1, 1, 18.00,  39, 0),
        (2,  "Chang",                 1, 1, 19.00,  17, 0),
        (3,  "Aniseed Syrup",         1, 2, 10.00,  13, 0),
        (4,  "Chef Anton's Cajun",    2, 2, 22.00,  53, 0),
        (5,  "Grandma's Boysenberry", 3, 2, 25.00,  0,  1),
        (6,  "Uncle Bob's Organic",   3, 7, 30.00,  15, 0),
        (7,  "Queso Cabrales",        5, 4, 21.00,  22, 0),
        (8,  "Queso Manchego",        5, 4, 38.00,  86, 0),
        (9,  "Konbu",                 6, 8, 6.00,   24, 0),
        (10, "Tofu",                  6, 7, 23.25,  35, 0),
        (11, "Genen Shouyu",          6, 2, 15.50,  39, 0),
        (12, "Grandma's Cranberry",   3, 2, 40.00,  0,  1),
        (13, "Konbu Dried",           6, 8, 6.00,   24, 0),
        (14, "Tofu Silken",           6, 7, 23.25,  35, 0),
        (15, "Ikura",                 4, 8, 31.00,  31, 0),
        (16, "Pavlova",               7, 3, 17.45, 129, 0),
        (17, "Alice Mutton",          7, 6, 39.00,  0,  1),
        (18, "Carnarvon Tigers",      7, 8, 62.50,  42, 0),
        (19, "Teatime Choc Biscuits", 8, 3,  9.20,  25, 0),
        (20, "Sir Rodney's Marmalade",8, 3, 81.00,  40, 0),
    ])

    cur.executemany("INSERT OR IGNORE INTO Customers VALUES (?,?,?,?)", [
        ("ALFKI", "Alfreds Futterkiste",       "Germany", "Berlin"),
        ("ANATR", "Ana Trujillo Emparedados",  "Mexico",  "México D.F."),
        ("ANTON", "Antonio Moreno Taquería",   "Mexico",  "México D.F."),
        ("AROUT", "Around the Horn",           "UK",      "London"),
        ("BERGS", "Berglunds snabbköp",        "Sweden",  "Luleå"),
        ("BLAUS", "Blauer See Delikatessen",   "Germany", "Mannheim"),
        ("BLONP", "Blondesddsl père et fils",  "France",  "Strasbourg"),
        ("BOLID", "Bólido Comidas preparadas", "Spain",   "Madrid"),
        ("BONAP", "Bon app'",                  "France",  "Marseille"),
        ("BOTTM", "Bottom-Dollar Markets",     "Canada",  "Tsawassen"),
        ("BSBEV", "B's Beverages",             "UK",      "London"),
        ("CACTU", "Cactus Comidas para llevar","Argentina","Buenos Aires"),
        ("CENTC", "Centro comercial Moctezuma","Mexico",  "México D.F."),
        ("CHOPS", "Chop-suey Chinese",         "Switzerland","Bern"),
        ("COMMI", "Comércio Mineiro",          "Brazil",  "São Paulo"),
    ])

    cur.executemany("INSERT OR IGNORE INTO Employees VALUES (?,?,?,?,?)", [
        (1, "Nancy",   "Davolio",   "Sales Representative",    "1992-05-01"),
        (2, "Andrew",  "Fuller",    "Vice President, Sales",   "1992-08-14"),
        (3, "Janet",   "Leverling", "Sales Representative",    "1992-04-01"),
        (4, "Margaret","Peacock",   "Sales Representative",    "1993-05-03"),
        (5, "Steven",  "Buchanan",  "Sales Manager",           "1993-10-17"),
        (6, "Michael", "Suyama",    "Sales Representative",    "1993-10-17"),
        (7, "Robert",  "King",      "Sales Representative",    "1994-01-02"),
        (8, "Laura",   "Callahan",  "Inside Sales Coordinator","1994-03-05"),
        (9, "Anne",    "Dodsworth", "Sales Representative",    "1994-11-15"),
    ])

    import random, datetime
    random.seed(42)
    customers = ["ALFKI","ANATR","ANTON","AROUT","BERGS","BLAUS","BLONP",
                 "BOLID","BONAP","BOTTM","BSBEV","CACTU","CENTC","CHOPS","COMMI"]
    countries = ["Germany","UK","France","USA","Mexico","Brazil","Spain","Sweden"]
    orders = []
    order_id = 1
    base = datetime.date(2022, 1, 1)
    for _ in range(120):
        cid = random.choice(customers)
        eid = random.randint(1, 9)
        days = random.randint(0, 730)
        odate = (base + datetime.timedelta(days=days)).isoformat()
        ship  = random.choice(countries)
        orders.append((order_id, cid, eid, odate, ship))
        order_id += 1

    cur.executemany("INSERT OR IGNORE INTO Orders VALUES (?,?,?,?,?)", orders)

    details = []
    detail_id = 1
    for order in orders:
        oid = order[0]
        n_items = random.randint(1, 5)
        chosen_products = random.sample(range(1, 21), n_items)
        for pid in chosen_products:
            price    = round(random.uniform(5, 80), 2)
            qty      = random.randint(1, 30)
            discount = random.choice([0, 0, 0, 0.05, 0.1, 0.15])
            details.append((detail_id, oid, pid, price, qty, discount))
            detail_id += 1

    cur.executemany("INSERT OR IGNORE INTO OrderDetails VALUES (?,?,?,?,?,?)", details)

    conn.commit()
    conn.close()
    print(f"Database seeded at {DB_PATH}")


if __name__ == "__main__":
    seed()
