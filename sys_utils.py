# -*- coding: utf-8 -*-
#
# quantsumore - finance api client
# https://github.com/cedricmoorejr/quantsumore/
#
# Copyright 2023-2024 Cedric Moore Jr.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



import sqlite3
import os
import json
import pandas as pd
from datetime import datetime, timedelta
import re
import string
import atexit
import shutil
import errno
import os
import _io
from random import Random as RandomGenerator


def add_flag_if_available(flag_name, base_flags):
    return base_flags | getattr(os, flag_name, 0)

base_flags = os.O_RDWR | os.O_CREAT | os.O_EXCL # Base flags for opening files
text_file_open_flags = add_flag_if_available('O_NOFOLLOW', base_flags) # Text file flags, optionally add O_NOFOLLOW
binary_file_open_flags = add_flag_if_available('O_BINARY', text_file_open_flags) # Binary file flags, start from text file flags and optionally add O_BINARY
MAX_TEMP_TRIES = getattr(os, 'TMP_MAX', 10000) # Define maximum attempts for temporary file naming, default to 10000


class RandomNameGenerator:
    characters = "abcdefghijklmnopqrstuvwxyz0123456789_"
    @property
    def random_instance(self):
        current_pid = os.getpid()
        if current_pid != getattr(self, '_pid_bound_random', None):
            self._random = RandomGenerator()
            self._pid_bound_random = current_pid
        return self._random

    def __iter__(self):
        return self

    def __next__(self):
        allowed_chars = self.characters
        choose_random = self.random_instance.choice
        random_name = [choose_random(allowed_chars) for _ in range(8)]
        return ''.join(random_name)


def get_potential_temp_dirs():
    temp_dirs = []
    for env_var in 'TMPDIR', 'TEMP', 'TMP':
        env_dir = os.getenv(env_var)
        if env_dir:
            temp_dirs.append(env_dir)

    if os.name == 'nt':
        temp_dirs.extend([
            os.path.expanduser(r'~\AppData\Local\Temp'),
            os.path.expandvars(r'%SYSTEMROOT%\Temp'),
            r'c:\temp', r'c:\tmp', r'\temp', r'\tmp'
        ])
    else:
        temp_dirs.extend(['/tmp', '/var/tmp', '/usr/tmp'])

    try:
        temp_dirs.append(os.getcwd())
    except (AttributeError, OSError):
        temp_dirs.append(os.curdir)

    return temp_dirs


def find_default_temp_dir():
    name_generator = RandomNameGenerator()
    potential_temp_dirs = get_potential_temp_dirs()

    for directory in potential_temp_dirs:
        if directory != os.curdir:
            directory = os.path.abspath(directory)
        for attempt in range(100):
            temp_name = next(name_generator)
            temp_file_path = os.path.join(directory, temp_name)
            try:
                file_descriptor = os.open(temp_file_path, binary_file_open_flags, 0o600)
                try:
                    try:
                        with _io.open(file_descriptor, 'wb', closefd=False) as temp_file:
                            temp_file.write(b'temp_data')
                    finally:
                        os.close(file_descriptor)
                finally:
                    os.unlink(temp_file_path)
                return directory
            except FileExistsError:
                pass
            except PermissionError:
                if (os.name == 'nt' and os.path.isdir(directory) and
                    os.access(directory, os.W_OK)):
                    continue
                break 
            except OSError:
                break 
    raise FileNotFoundError(errno.ENOENT, "No usable temporary directory found in %s" % potential_temp_dirs)


class TempDirectory:
    """
    A class for creating and managing temporary directories.

    Attributes:
        base_temp_dir (str): The base directory where temporary directories will be created.

    Methods:
        Dir():
            Creates a temporary directory with a random name and registers it for cleanup.
            Returns the path of the created temporary directory.

        Omit(path):
            Deletes a specified temporary directory and prints a message about the deletion.

        Clean():
            Cleans up all temporary directories created by this class in the base_temp_dir.

        DirFile(filename, extension):
            Creates a file with a specified name and extension in the temporary directory.
            Returns the path of the temporary directory containing the new file.

    Example Usage:
        temp_dir_creator = TempDirectory()
        temp_dir_with_file = temp_dir_creator.DirFile("sample", "txt")
        print(f"Temporary directory with file created at: {temp_dir_with_file}")        
    """
    
    def __init__(self):
        """
        Initializes the TempDirectory instance.

        It checks for the existence of the TEMP or TMP environment variable and sets
        base_temp_dir accordingly. Raises an exception if no temporary directory
        environment variable is found.
        """
        self.base_temp_dir = find_default_temp_dir()
        if not self.base_temp_dir:
            raise Exception("No temporary directory environment variable found.")

    def Dir(self):
        """
        Creates a temporary directory and registers it for cleanup.

        Returns:
            str: The path of the created temporary directory.
        """
        rng = RandomGenerator()
        parts = []
        for part_length in [8, 4, 4, 4, 7]:
            part = ''.join(rng.choices(string.ascii_letters + string.digits, k=part_length))
            parts.append(part)

        temp_dir_name = "quantsumore-" + "-".join(parts)
        temp_dir_path = os.path.join(self.base_temp_dir, temp_dir_name)

        os.makedirs(temp_dir_path, exist_ok=True)
        atexit.register(self.Omit, temp_dir_path)

        return temp_dir_path 

    def Omit(self, path):
        """
        Deletes a specified temporary directory and prints a message about the deletion.

        Args:
            path (str): The path of the temporary directory to be deleted.
        """
        shutil.rmtree(path, ignore_errors=True)
        print(f"Temporary directory {path} has been deleted.")

    def DirFile(self, filename, extension):
        """
        Creates a file with a specified name and extension in the temporary directory.
        Automatically removes a leading '.' from the extension if present.
        If the extension is 'xlsx', a blank Excel workbook is created.

        Args:
            filename (str): The name of the file to be created.
            extension (str): The file extension, with or without a leading '.'.

        Returns:
            str: The full path of the newly created file.
        """
        temp_dir_path = self.Dir()
        extension = extension.lstrip('.')
        full_file_path = os.path.join(temp_dir_path, f"{filename}.{extension}")
        with open(full_file_path, 'w') as file:
            pass
        return full_file_path
    
    def Clean(self):
        """
        Cleans up all temporary directories created by this class in the base_temp_dir.
        """
        for item in os.listdir(self.base_temp_dir):
            if "quantsumore-" in item:
                path = os.path.join(self.base_temp_dir, item)
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)




class FilePathFinder:
    """Handles finding, reading, writing, and modifying file paths and contents."""	
    
    class fPath:
        """Nested class to manage file path finding within a project structure marked by a unique identifier."""
        def __init__(self, temp_dir):
            self.temporary_directory = temp_dir

        def _find_file(self, file_name):
            """Searches for a file within the given directory."""
            if not os.path.splitext(file_name)[1]:
                file_name += '.py'
            for dirpath, dirnames, filenames in os.walk(self.temporary_directory):
                if file_name in filenames:
                    return os.path.join(dirpath, file_name)
            return None

        def _find_directory(self, target_directory):
            """Searches for a directory within the given root directory."""
            for dirpath, dirnames, _ in os.walk(self.temporary_directory):
                if target_directory in dirnames:
                    return os.path.join(dirpath, target_directory)
            return None

        def return_path(self, file=None, directory=None):
            """Find either a file or directory based on input."""
            if file and not directory:
                return self._find_file(file_name=file)
            elif directory and not file:
                return self._find_directory(target_directory=directory)
            else:
                return None
    
    def __init__(self, temp_dir, encoding='utf-8'):
        self.encoding = encoding
        self.path_handler = self.fPath(temp_dir)
        self.directory = self.path_handler.temporary_directory
       
                
    def trace(self, file=None, directory=None):
        """Retrieves the path for a specified file or directory.

        Args:
            file (str, optional): The name of the file to find.
            directory (str, optional): The name of the directory to find.

        Returns:
            str: The path to the file or directory if found, otherwise None.
        """    	
        return self.path_handler.return_path(file=file, directory=directory)       

    def inscribe(self, file, s, overwrite=True):
        """Writes data to a file, with the option to overwrite or append.

        Args:
            file (str): The file path to write to.
            s (str or pandas.DataFrame): The data to write to the file.
            overwrite (bool): True to overwrite the file, False to append.
        """    	
        mode = 'w' if overwrite else 'a'
        if isinstance(s, pd.DataFrame):
            header = True if overwrite else False
            s.to_csv(file, mode=mode, encoding=self.encoding, index=False, header=header)
        else:            
            with open(file, mode, encoding=self.encoding) as compose:
                compose.write(s)
                
    def extend(self, file, s):
        """Appends data to a file, creating the file if it does not exist.

        Args:
            file (str): The file path to append data to.
            s (str): The data to append.
        """    	
        if not os.path.exists(file):
            self.inscribe(file, s)
        with open(file, 'a', encoding=self.encoding) as compose:
            compose.write(s)

    def inject(self, file, s, line):
        """Inserts data into a specific line of a file.

        Args:
            file (str): The file path where data is to be inserted.
            s (str): The data to insert.
            line (int): The line number at which to insert the data.
        """    	
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
        """Reads the contents of a file.

        Args:
            file (str): The file path to read from.
            silent (bool): If True, returns an empty string instead of raising an error when the file is not found.

        Returns:
            str: The contents of the file or an empty string if silent is True and the file does not exist.
        """    	
        if not os.path.exists(file):
            if silent:
                return ''
            else:
                raise FileNotFoundError(str(file))
        with open(file, encoding=self.encoding) as skim:
            return skim.read()

    def alter(self, file, new, old=None, pattern=None):
        """Replaces occurrences of an old string or pattern in a file with a new string.

        Args:
            file (str): The file path for the replacement operation.
            new (str): The new string to replace with.
            old (str, optional): The old string to replace.
            pattern (str, optional): A regex pattern to match and replace.
        """    	
        if old is None and pattern is None:
            raise ValueError("Either 'old' or 'pattern' must be provided for replacement.")
        s = self.extract(file)
        if old is not None:
            s = s.replace(old, new)
        if pattern is not None:
            s = re.sub(pattern, new, s)
        self.inscribe(file, s)


tempDir = TempDirectory()
directory = tempDir.Dir()
filePaths = FilePathFinder(directory)

class JSON:
    def __init__(self, filename=None, directory=directory, json_data=None):
        self.json_data = json_data
        if json_data is None:
            if filename is None:
                raise ValueError("Either filename or json_data must be provided.")
            self.filename = filename
            self.json_dir = directory
            if self.json_dir is None:
                raise FileNotFoundError(f"Directory '{directory}' not found in the expected paths.")
            self.json_path = os.path.join(self.json_dir, self.filename)
        else:
            self.filename = filename if filename else "data.json"
            self.json_path = None
    
    def save(self, data, force_save_to_file=False):
        if force_save_to_file or self.json_path:
            if self.json_path is None:
                raise ValueError("File path not set. Provide a filename and directory for file operations.")
            try:
                with open(self.json_path, 'w', encoding='utf-8') as json_file:
                    if isinstance(data, dict):
                        json.dump(data, json_file, indent=4)
                    else:
                        json_file.write(data)
            except Exception as e:
                print(f"An error occurred while saving data to {self.json_path}: {e}")
        else:
            self.json_data = data
    
    def load(self, from_file=False, key=None):
        if from_file and self.json_path:
            try:
                with open(self.json_path, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    if key:
                        data = data.get(key, None)  # Safely fetch the key if it exists
                    self.json_data = data
                    return data
            except FileNotFoundError:
                print(f"No such file: '{self.json_path}'")
            except json.JSONDecodeError:
                print(f"Error decoding JSON from the file: '{self.json_path}'")
            except Exception as e:
                print(f"An error occurred while loading data from {self.json_path}: {e}")
        elif self.json_data:
            data = self.json_data
            if key:
                data = data.get(key, None)  # Safely fetch the key if it exists
            return data
        else:
            raise ValueError("No data available to load. Provide json_data or enable file loading.")

    def flatten(self, initial_path, keys, data=None):
        """ Flatten the JSON data based on the provided path and keys. """
        data = data if data is not None else self.json_data        
        try:
            for part in initial_path.split('.'):
                if part.isdigit():
                    data = data[int(part)]
                else:
                    data = data[part]
        except KeyError as e:
            raise KeyError(f"Path error: {e}")
        flattened = {}
        try:
            for key in keys:
                parts = key.split('.')
                ref = data
                for part in parts:
                    if part.isdigit():
                        ref = ref[int(part)]
                    else:
                        ref = ref[part]
                flattened[key.replace('.', '_')] = ref
        except KeyError as e:
            print(f"Flattening error on key {key}: {e}")
            flattened[key.replace('.', '_')] = None

        self.flattened_json_data = flattened
        return flattened
    
    def dataframe(self, data=None, rename_columns=None, column_order=None, data_types=None):
        """ Creates a DataFrame from data which may contain scalar values or lists."""
        data = data if data is not None else self.flattened_json_data        
        if isinstance(data, dict):
            if all(not isinstance(v, (list, tuple, set, dict)) for v in data.values()):
                data = {k: [v] for k, v in data.items()}
        df = pd.DataFrame(data)

        if rename_columns and isinstance(rename_columns, dict):
            df.rename(columns=rename_columns, inplace=True, errors='ignore')

        if column_order and isinstance(column_order, list):
            filtered_columns = [col for col in column_order if col in df.columns]
            df = df[filtered_columns]

        if data_types and isinstance(data_types, dict):
            valid_data_types = {k: v for k, v in data_types.items() if k in df.columns}
            df = df.astype(valid_data_types, errors='ignore')

        self.dataframe_json_data = df

        return df

    def clear_json(self):
        """ Resets the json_data, flattened_json_data, and dataframe_json_data attributes to None."""
        self.json_data = None
        self.flattened_json_data = None
        self.dataframe_json_data = None
        print("All data has been cleared.")
       
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
    def __init__(self, filename, directory=directory, json_data=None):
        self.filename = filename
        self.db_dir = directory
        self.db_path = os.path.join(self.db_dir, self.filename)
        self.path = self.Path()        
        self.conn = None
        self.cursor = None
        self.json_data = json_data        

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

    def parse_json(self):
        """Parse JSON content to prepare for database insertion."""
        data = self.json_data
        data = data["cryptos"]
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

    def save(self):
        """Process JSON content and save to the database."""
        try:
            self.connect()
            self.ensure_database()
            transformed_data = self.parse_json()
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








def __dir__():
    return ['JSON', 'SQLiteDBHandler', 'filePaths']

__all__ = ['JSON', 'SQLiteDBHandler', 'filePaths']





