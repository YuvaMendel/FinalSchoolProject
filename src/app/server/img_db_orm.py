import sqlite3
import os
import uuid
from PIL import Image
import io

image_limit = 100


class ImagesORM:
    def __init__(self, db_path='images.db', image_dir='saved_images'):
        self.db_path = db_path
        self.image_dir = image_dir
        self.conn = None
        self.cursor = None
        os.makedirs(self.image_dir, exist_ok=True)

    def open_DB(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close_DB(self):
        if self.conn:
            self.conn.close()

    def commit(self):
        self.conn.commit()

    def create_tables(self):
        self.open_DB()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Images (
            image_id TEXT PRIMARY KEY,
            digit TEXT,
            path TEXT,
            confidence REAL
        )
        ''')
        self.commit()
        self.close_DB()

    def save_image_file(self, image_bytes, max_size=256):
        img = Image.open(io.BytesIO(image_bytes))

        img = img.convert("RGB")

        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        output = io.BytesIO()
        img.save(output, format='PNG')
        resized_bytes = output.getvalue()
        image_id = str(uuid.uuid4())
        filename = f"{image_id}.png"
        path = os.path.join(self.image_dir, filename)
        with open(path, 'wb') as f:
            f.write(resized_bytes)
        return image_id, path

    def insert_image(self, image_id, digit, path, confidence):
        self.open_DB()
        self.cursor.execute('''
        INSERT INTO Images (image_id, digit, path, confidence)
        VALUES (?, ?, ?, ?)
        ''', (image_id, digit, path, confidence))

        # Prune database to last 100 entries by rowid
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

    def process_and_store(self, image_bytes, digit, confidence):
        image_id, path = self.save_image_file(image_bytes)
        self.insert_image(image_id, digit, path, confidence)
        self.delete_old_files()



    def get_all_images_files(self):
        self.open_DB()
        self.cursor.execute('SELECT * FROM Images ORDER BY rowid DESC')
        rows = self.cursor.fetchall()
        self.close_DB()
        files = get_files_by_rows(rows)
        return files

    def get_image_by_digit_files(self, digit):
        self.open_DB()
        self.cursor.execute('SELECT * FROM Images WHERE digit = ?', (digit,))
        rows = self.cursor.fetchall()
        self.close_DB()
        files = get_files_by_rows(rows)
        return files


def get_files_by_rows(rows):
    files = []
    for row in rows:
        image_id, digit, path, confidence = row
        if os.path.exists(path):
            with open(path, 'rb') as f:
                image_bytes = f.read()
            files.append((image_id, image_bytes, digit, confidence))
    return files