import sqlite3
import json
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'service.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create vehicles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            plate_number TEXT PRIMARY KEY,
            owner_name TEXT NOT NULL,
            vehicle_type TEXT NOT NULL
        )
    ''')
    
    # Create service_tickets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT NOT NULL,
            last_service_date TEXT NOT NULL,
            current_odometer INTEGER NOT NULL,
            daily_distance INTEGER NOT NULL,
            complaints TEXT,
            diagnostic_results TEXT,
            next_oil_odometer INTEGER NOT NULL,
            next_oil_date TEXT NOT NULL,
            next_service_odometer INTEGER NOT NULL,
            next_service_date TEXT NOT NULL,
            estimated_cost INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (plate_number) REFERENCES vehicles (plate_number)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_ticket(plate_number, owner_name, vehicle_type, last_service_date, current_odometer, 
                daily_distance, complaints, diagnostic_results, next_oil_odometer, 
                next_oil_date, next_service_odometer, next_service_date, estimated_cost):
    
    # Normalize plate number (uppercase, remove extra spaces)
    plate_norm = "".join(plate_number.upper().split())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Insert or replace vehicle profile
        cursor.execute('''
            INSERT OR REPLACE INTO vehicles (plate_number, owner_name, vehicle_type)
            VALUES (?, ?, ?)
        ''', (plate_norm, owner_name, vehicle_type))
        
        # Serialize diagnostic results to JSON string
        diag_json = json.dumps(diagnostic_results)
        
        # Insert service ticket
        cursor.execute('''
            INSERT INTO service_tickets (
                plate_number, last_service_date, current_odometer, daily_distance, 
                complaints, diagnostic_results, next_oil_odometer, next_oil_date, 
                next_service_odometer, next_service_date, estimated_cost
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (plate_norm, last_service_date, current_odometer, daily_distance, 
              complaints, diag_json, next_oil_odometer, next_oil_date, 
              next_service_odometer, next_service_date, estimated_cost))
        
        ticket_id = cursor.lastrowid
        conn.commit()
        return ticket_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_history(plate_number):
    plate_norm = "".join(plate_number.upper().split())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Join tickets with vehicle info
    cursor.execute('''
        SELECT t.*, v.owner_name, v.vehicle_type 
        FROM service_tickets t
        JOIN vehicles v ON t.plate_number = v.plate_number
        WHERE t.plate_number = ?
        ORDER BY t.created_at DESC
    ''', (plate_norm,))
    
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        ticket = dict(row)
        # Deserialize JSON string
        try:
            ticket['diagnostic_results'] = json.loads(ticket['diagnostic_results'])
        except (TypeError, json.JSONDecodeError):
            ticket['diagnostic_results'] = []
        history.append(ticket)
        
    return history

def get_latest_ticket(plate_number):
    history = get_history(plate_number)
    return history[0] if history else None

if __name__ == '__main__':
    # Test initialization
    init_db()
    print("Database initialized successfully.")
