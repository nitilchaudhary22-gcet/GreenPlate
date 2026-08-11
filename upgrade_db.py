import sqlite3

def upgrade_db():
    conn = sqlite3.connect(r'd:\Greenplate\instance\greenplate.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE food_donation ADD COLUMN ngo_id INTEGER REFERENCES user(id);")
        conn.commit()
        print("Database updated successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error updating database: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    upgrade_db()
