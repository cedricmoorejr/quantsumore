import sqlite3
import os
import json
from datetime import datetime, timedelta
from functools import lru_cache
import re


class FilePathFinder:
    class fPath:
        def __init__(self, unique_identifier="## -- quantsumore -- ##"):
            self.unique_identifier = unique_identifier

        @lru_cache(maxsize=None)
        def _root(self):
            """Finds the root directory marked by a unique identifier in its __init__.py."""
            current_directory = os.path.dirname(os.path.abspath(__file__))
            while current_directory != os.path.dirname(current_directory):
                init_file_path = os.path.join(current_directory, '__init__.py')
                if os.path.isfile(init_file_path):
                    with open(init_file_path, 'r') as f:
                        if self.unique_identifier in f.read():
                            return current_directory
                current_directory = os.path.dirname(current_directory)
            return None

        @lru_cache(maxsize=128)
        def _find_file(self, directory, file_name):
            """Searches for a file within the given directory."""
            if not os.path.splitext(file_name)[1]:
                file_name += '.py'
            for dirpath, dirnames, filenames in os.walk(directory):
                if file_name in filenames:
                    return os.path.join(dirpath, file_name)
            return None

        @lru_cache(maxsize=128)
        def _find_directory(self, root_directory, target_directory):
            """Searches for a directory within the given root directory."""
            for dirpath, dirnames, _ in os.walk(root_directory):
                if target_directory in dirnames:
                    return os.path.join(dirpath, target_directory)
            return None

        def return_path(self, file=None, directory=None):
            """Public method to find either a file or directory based on input."""
            if file and not directory:
                return self._find_file(directory=self._root(), file_name=file)
            elif directory and not file:
                return self._find_directory(root_directory=self._root(), target_directory=directory)
            else:
                return None
    
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding
        self.path_handler = self.fPath()
                
    def trace(self, file=None, directory=None):
        return self.path_handler.return_path(file=file, directory=directory)       

    def inscribe(self, file, s, overwrite=True):
        mode = 'w' if overwrite else 'a'
        with open(file, mode, encoding=self.encoding) as compose:
            compose.write(s)

    def extend(self, file, s):
        if not os.path.exists(file):
            self.inscribe(file, s)
        with open(file, 'a', encoding=self.encoding) as compose:
            compose.write(s)

    def inject(self, file, s, line):
        lines = []
        with open(file) as skim:
            lines = skim.readlines()
        if line == len(lines) or line == -1:
            lines.append(s + '\n')
        else:
            if line < 0:
                line += 1
            lines.insert(line, s + '\n')
        with open(file, 'w', encoding=self.encoding) as compose:
            compose.writelines(lines)

    def extract(self, file, silent=False):
        if not os.path.exists(file):
            if silent:
                return ''
            else:
                raise FileNotFoundError(str(file))
        with open(file, encoding=self.encoding) as skim:
            return skim.read()

    def alter(self, file, new, old=None, pattern=None):
        if old is None and pattern is None:
            raise ValueError("Either 'old' or 'pattern' must be provided for replacement.")
           
        s = self.extract(file)
        
        if old is not None:
            s = s.replace(old, new)
            
        if pattern is not None:
            s = re.sub(pattern, new, s)
            
        self.inscribe(file, s)





class JsonFileHandler:
    def __init__(self, filename, directory="configuration"):
        self.filename = filename
        self.json_dir = filePaths.trace(directory=directory)
        if self.json_dir is None:
            raise FileNotFoundError(f"Directory '{directory}' not found in the expected paths.")
        self.json_path = os.path.join(self.json_dir, self.filename)

    def save(self, data):
        try:
            if isinstance(data, str):
                with open(self.json_path, 'w', encoding='utf-8') as json_file:
                    json_file.write(data)
                
            elif isinstance(data, dict):
                with open(self.json_path, 'w', encoding='utf-8') as json_file:
                    json.dump(data, json_file, indent=4)
            
        except Exception as e:
            print(f"An error occurred while saving data to {self.json_path}: {e}")

    def load(self, key=None):
        try:
            with open(self.json_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)[key] if key else json.load(json_file)
            return data
        except FileNotFoundError:
            print(f"No such file: '{self.json_path}'")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the file: '{self.json_path}'")
        except Exception as e:
            print(f"An error occurred while loading data from {self.json_path}: {e}")
        return None
       
    def file_exists(self):
        """Check if the JSON file exists at the designated path."""
        return os.path.exists(self.json_path)
       
    def last_modified(self, as_string=False):
        """Return the last modification time of the JSON file."""
        if self.file_exists():
            timestamp = os.path.getmtime(self.json_path)
            if as_string:
                return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            return datetime.fromtimestamp(timestamp)
        else:
            return None      
           
    def is_outdated(self):
        """Check if the last modification of the file was more than a month ago."""
        if self.file_exists():
            last_modification_time = os.path.getmtime(self.json_path)
            last_modification_date = datetime.fromtimestamp(last_modification_time)
            if datetime.now() - last_modification_date > timedelta(days=30):
                return True
            else:
                return False
        return True




class SQLiteDBHandler:
    def __init__(self, filename, directory="configuration"):
        self.filename = filename
        self.db_dir = filePaths.trace(directory=directory)
        self.db_path = os.path.join(self.db_dir, self.filename)
        self.path = self.Path()        
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish a new database connection if one doesn't already exist."""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

    def close(self):
        """Properly close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def reset_database(self):
        """Deletes the existing database file if it exists."""
        if os.path.exists(self.db_path) and os.path.isfile(self.db_path):
            os.remove(self.db_path)

    def ensure_database(self):
        """Ensure the database and table exist."""
        self.connect()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cryptos (
                id INTEGER PRIMARY KEY,
                name TEXT,
                symbol TEXT,
                slug TEXT,
                is_active INTEGER,
                status INTEGER,
                rank INTEGER
            )
        ''')
        self.conn.commit()

    def parse_json(self, json_content):
        """Parse JSON content to prepare for database insertion."""
        data = JsonFileHandler(json_content).load(key="cryptos")
        return [(item['id'], item['name'], item['symbol'], item['slug'], item['is_active'], item['status'], item['rank']) for item in data.values()]

    def insert_data(self, transformed_data):
        """Inserts data into the database."""
        for item in transformed_data:
            self.cursor.execute('''
                INSERT INTO cryptos (id, name, symbol, slug, is_active, status, rank)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                symbol=excluded.symbol,
                slug=excluded.slug,
                is_active=excluded.is_active,
                status=excluded.status,
                rank=excluded.rank;
            ''', item)
        self.conn.commit()

    def save(self, json_content):
        """Process JSON content and save to the database."""
        try:
            self.connect()
            self.ensure_database()
            transformed_data = self.parse_json(json_content)
            self.insert_data(transformed_data)
        except Exception as e:
            print(f"An error occurred during the save process: {e}")
            self.conn.rollback()
        finally:
            self.close()

    def file_exists(self):
        """Check if the database file exists."""
        return os.path.exists(self.db_path)

    def Path(self):
        """Returns the database file path if it exists, otherwise notifies non-existence."""
        if os.path.exists(self.db_path) and os.path.isfile(self.db_path):
            return self.db_path
        else:
            return None

    def last_modified(self, as_string=False):
        """Return the last modification time of the database file."""
        if self.file_exists():
            timestamp = os.path.getmtime(self.db_path)
            if as_string:
                return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            return datetime.fromtimestamp(timestamp)
        else:
            return None 

    def is_outdated(self):
        """Check if the last modification of the file was more than a month ago."""
        if self.file_exists():
            last_modification_time = os.path.getmtime(self.db_path)
            last_modification_date = datetime.fromtimestamp(last_modification_time)
            if datetime.now() - last_modification_date > timedelta(days=30):
                return True
            else:
                return False
        return True



filePaths = FilePathFinder()


def __dir__():
    return ['JsonFileHandler', 'SQLiteDBHandler', 'filePaths']

__all__ = ['JsonFileHandler', 'SQLiteDBHandler', 'filePaths']





