import sqlite3
import json
import os

def create_structured_data(db_path="real_estate.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Properties table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        city TEXT,
        area TEXT,
        bedrooms INTEGER,
        purpose TEXT,
        price INTEGER,
        amenities TEXT,
        agent_name TEXT,
        status TEXT
    )
    ''')

    # Mock Data
    properties = [
        ("Gulberg Greens Villa", "Islamabad", "Gulberg Greens", 4, "Sale", 65000000, "Pool, Garden, Security", "Ali Khan", "Available"),
        ("DHA Phase 8 Apartment", "Karachi", "DHA", 3, "Sale", 45000000, "Gym, Backup Generator", "Zara Ahmed", "Available"),
        ("Bahria Town House", "Lahore", "Bahria Town", 5, "Sale", 55000000, "Park facing, Mosque nearby", "Usman Tariq", "Available"),
        ("Blue Area Office Space", "Islamabad", "Blue Area", 0, "Rent", 250000, "Elevator, Parking", "Ali Khan", "Available"),
        ("Clifton Flat", "Karachi", "Clifton", 2, "Rent", 120000, "Sea view, Security", "Zara Ahmed", "Rented")
    ]

    cursor.executemany('''
    INSERT INTO properties (name, city, area, bedrooms, purpose, price, amenities, agent_name, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', properties)

    conn.commit()
    conn.close()
    print(f"Structured data saved to {db_path}")

def create_unstructured_data(file_path="brochures_faqs.json"):
    data = [
        {
            "id": "faq_001",
            "title": "Payment Plans for Overseas Pakistanis",
            "content": "Overseas Pakistanis can avail a special 3-year installment plan with a 20% down payment. Remittances sent via official banking channels qualify for a 2% discount on the total price. A valid NICOP is required for the booking process."
        },
        {
            "id": "faq_002",
            "title": "Transfer Fee Policy",
            "content": "The property transfer fee is typically 1% of the total property value or as per the society's current schedule of charges. This fee is payable by the buyer at the time of ownership transfer."
        },
        {
            "id": "brochure_001",
            "title": "Gulberg Greens Project Overview",
            "content": "Gulberg Greens Islamabad offers a luxurious lifestyle with lush green farmhouses. It features underground electricity, 24/7 security, wide carpeted roads, and easy access to the Islamabad Expressway. The project includes commercial blocks, schools, and a modern hospital."
        },
        {
            "id": "brochure_002",
            "title": "Bahria Town Lahore Amenities",
            "content": "Bahria Town Lahore is a city within a city. It boasts world-class amenities including the Grand Jamia Mosque, international standard schools, state-of-the-art hospitals, a theme park, and a golf course. Security is uncompromised with 24/7 surveillance."
        }
    ]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"Unstructured data saved to {file_path}")

if __name__ == "__main__":
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    # Generate DB in current directory
    create_structured_data("real_estate.db")
    create_unstructured_data("brochures_faqs.json")
