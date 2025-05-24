import sqlite3
import os
import uuid
import hashlib
import secrets
from PIL import Image
import io

image_limit = 100


class ImagesORM:
    """A class to handle image storage and retrieval using SQLite ORM."""
    def __init__(self, db_path='images.db', image_dir='saved_images'):
        self.db_path = db_path
        self.image_dir = image_dir
        self.conn = None
        self.cursor = None
        os.makedirs(self.image_dir, exist_ok=True)

    def open_DB(self):
        """Open a connection to the SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close_DB(self):
        """Close the database connection if it is open."""
        if self.conn:
            self.conn.close()

    def commit(self):
        """Commit the current transaction to the database."""
        self.conn.commit()

    def create_tables(self):
        """Create the necessary tables in the database if they do not exist."""
        self.open_DB()

        # Create Users table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            salt TEXT
        )
        ''')

        # Create Images table with user_id column
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Images (
            image_id TEXT PRIMARY KEY,
            digit TEXT,
            path TEXT,
            confidence REAL,
            hash TEXT UNIQUE,
            user_id TEXT
        )
        ''')

        self.commit()
        self.close_DB()

    def register_user(self, username, password):
        """Register a new user with a username and password, returning the user_id if successful."""
        self.open_DB()
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        user_id = str(uuid.uuid4())

        try:
            self.cursor.execute('''
            INSERT INTO Users (user_id, username, password_hash, salt)
            VALUES (?, ?, ?, ?)
            ''', (user_id, username, password_hash, salt))
            self.commit()
        except sqlite3.IntegrityError:
            user_id = None  # Username already exists
        self.close_DB()
        return user_id

    def authenticate_user(self, username, password):
        """Authenticate a user by checking the username and password against the database."""
        self.open_DB()
        self.cursor.execute('SELECT user_id, password_hash, salt FROM Users WHERE username = ?', (username,))
        result = self.cursor.fetchone()
        self.close_DB()

        if result:
            user_id, stored_hash, salt = result
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            if computed_hash == stored_hash:
                return user_id
        return None

    def save_image_file(self, image_bytes, max_size=256):
        """Resize an image, compute its SHA-256 hash, and save it to the disk."""
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert("RGB")
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        output = io.BytesIO()
        img.save(output, format='PNG')
        resized_bytes = output.getvalue()

        # Compute SHA-256 hash of resized image
        hash_val = hashlib.sha256(resized_bytes).hexdigest()

        image_id = str(uuid.uuid4())
        filename = f"{image_id}.png"
        path = os.path.join(self.image_dir, filename)

        with open(path, 'wb') as f:
            f.write(resized_bytes)

        return image_id, path, hash_val

    def insert_image(self, image_id, digit, path, confidence, hash_val, user_id):
        """Insert an image record into the database, checking for duplicates based on hash."""
        self.open_DB()

        # Check for duplicate based on hash
        self.cursor.execute('SELECT image_id, path FROM Images WHERE hash = ?', (hash_val,))
        result = self.cursor.fetchone()

        if result:
            existing_image_id, existing_path = result
            if not os.path.exists(existing_path):
                # File is missing, remove old database record
                self.cursor.execute('DELETE FROM Images WHERE image_id = ?', (existing_image_id,))
            else:
                self.close_DB()
                return  # File exists, skip insertion

        self.cursor.execute('''
        INSERT INTO Images (image_id, digit, path, confidence, hash, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (image_id, digit, path, confidence, hash_val, user_id))

        # Keep only the most recent `image_limit` entries
        self.cursor.execute('''
        DELETE FROM Images
        WHERE image_id NOT IN (
            SELECT image_id FROM Images
            ORDER BY rowid DESC
            LIMIT ?
        )
        ''', (image_limit,))

        self.commit()
        self.close_DB()

    def delete_old_files(self):
        """Delete old image files that are not in the most recent `image_limit` entries."""
        self.open_DB()
        self.cursor.execute('SELECT image_id, path FROM Images ORDER BY rowid DESC LIMIT ?', (image_limit,))
        rows = self.cursor.fetchall()
        self.close_DB()

        recent_paths = set()
        missing_image_ids = []

        for image_id, path in rows:
            if os.path.exists(path):
                recent_paths.add(path)
            else:
                missing_image_ids.append(image_id)

        all_paths = set(os.path.join(self.image_dir, f) for f in os.listdir(self.image_dir))
        to_delete = all_paths - recent_paths

        for path in to_delete:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass

        if missing_image_ids:
            self.open_DB()
            self.cursor.executemany('DELETE FROM Images WHERE image_id = ?',
                                    [(img_id,) for img_id in missing_image_ids])
            self.commit()
            self.close_DB()

    def process_and_store(self, image_bytes, digit, confidence, user_id):
        """Process an image, resize it, compute its hash, and store it in the database."""
        image_id, path, hash_val = self.save_image_file(image_bytes)
        self.insert_image(image_id, digit, path, confidence, hash_val, user_id)
        self.delete_old_files()

    def get_all_images_files(self):
        """Retrieve all image files from the database."""
        self.open_DB()
        self.cursor.execute('SELECT image_id, digit, path, confidence FROM Images ORDER BY rowid DESC')
        rows = self.cursor.fetchall()
        self.close_DB()
        files = Files(rows)
        return files

    def get_image_by_digit_files(self, digit):
        """Retrieve image files by digit from the database."""
        self.open_DB()
        self.cursor.execute('SELECT image_id, digit, path, confidence FROM Images WHERE digit = ?', (digit,))
        rows = self.cursor.fetchall()
        self.close_DB()
        files = Files(rows)
        return files


def get_files_by_rows(rows):
    """Retrieve image files based on database rows."""
    files = []
    for row in rows:
        image_id, digit, path, confidence = row
        if os.path.exists(path):
            with open(path, 'rb') as f:
                image_bytes = f.read()
            files.append((image_id, image_bytes, digit, confidence))
    return files


class Files:
    """A class to handle a collection of image files stored in a database."""
    def __init__(self, rows):
        self.rows = rows
        self.index = 0

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index >= len(self.rows):
            raise StopIteration
        file_path = self.rows[self.index][2]
        self.index += 1
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
            return self.rows[self.index - 1][0], image_bytes, self.rows[self.index - 1][1], self.rows[self.index - 1][3]
        return None
