import psycopg2
from psycopg2 import sql

# Connect to your PostgreSQL database
conn = psycopg2.connect(
    dbname="Fabrico2",
    user="Fabrico2",
    password="password",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

# Read the image file as binary data
with open("D:/Workspace/fabrico2/app/static/Logo.png", "rb") as file:
    image_data = file.read()

# Define the SQL query to insert data into the FabricDefects table
insert_query = sql.SQL("""
    INSERT INTO public."FabricDefects" (fabric_id, defect, defectimage) 
    VALUES (%s, %s, %s)
""")

# Define the values to be inserted
values = ("FAB002", "Line", psycopg2.Binary(image_data))

try:
    # Execute the SQL query
    cursor.execute(insert_query, values)
    print("Data inserted successfully.")
except psycopg2.Error as e:
    print("Error executing SQL statement:", e)

# Commit the transaction
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
