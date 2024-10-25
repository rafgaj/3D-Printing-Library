import sqlite3

connection = sqlite3.connect("3Dprint.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
        username VARCHAR(20) NOT NULL, 
        email TEXT NOT NULL, 
        password TEXT NOT NULL
    )
""")


cursor.execute("""
    CREATE TABLE Models (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        filename VARCHAR(120) NOT NULL,
        thumbnail TEXT, 
        desc TEXT, 
        filepath TEXT NOT NULL, 
        private BLOB NOT NULL, 
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
        FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
    )
""")


release_users = [
    (1, "raf", "rafalg@gmail.com", "password"),
    (2, "abc", "abc@gmail.com", "password"),
    (3, "bcd", "bcd@gmail.com", "password"),
]


#cursor.executemany("INSERT INTO Users VALUES (?, ?, ?, ?)", release_users)
#cursor.executemany("INSERT INTO models VALUES (?, ?, ?, ?, ?, ?, ?)", release_models)

connection.commit()
connection.close()