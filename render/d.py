import pandas as pd

class Table:
    def __init__(self, data, custom_columns=None):
        """
        Initializes the Display class with generic data.
        """
        self.data = data
        self.custom_columns = custom_columns   
        self.struct()
        
        self.column_widths = {}
        self.calculate_column_widths()

    def create_data_structure(self, data, col_names=None):
        """ Creates or modifies a dictionary data structure with optional specified column names and associated data."""
        if isinstance(data, dict) and self.is_flat_dict(data):
            data = {key: [value] for key, value in data.items()}
        
        if self.check_data_structure(data):
            max_length = max(len(lst) for lst in data.values())
            for key in data:
                adjusted_list = []
                for item in data[key]:
                    if pd.isna(item) or (isinstance(item, str) and not item.strip()):
                        adjusted_list.append('--')
                    else:
                        adjusted_list.append(item)
                additional_length = max_length - len(adjusted_list)
                if additional_length > 0:
                    adjusted_list += ['--'] * additional_length
                data[key] = adjusted_list
            return data

        if col_names is None or len(col_names) != len(data):
            raise ValueError("Column names must be provided and match the number of data lists.")

        max_length = max(len(sublist) for sublist in data) if data else 0
        adjusted_data = []
        for sublist in data:
            adjusted_sublist = []
            for item in sublist:
                if pd.isna(item) or (isinstance(item, str) and not item.strip()):
                    adjusted_sublist.append('--')
                else:
                    adjusted_sublist.append(item)
            adjusted_sublist += ['--'] * (max_length - len(adjusted_sublist))
            adjusted_data.append(adjusted_sublist)
        return {col_name: data_list for col_name, data_list in zip(col_names, adjusted_data)}

    def check_data_structure(self, data):
        """ Checks if the given data structure is a dictionary where each value is a list. """ 
        if not isinstance(data, dict):
            return False        
        for value in data.values():
            if not isinstance(value, list):
                return False        
        return True

    def is_flat_dict(self, data):
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, (dict, list, tuple, set)):
                    return False
            return True
        return False

    def struct(self):
        data = self.data
        if self.check_data_structure(data) or self.is_flat_dict(data):
            self.data = self.create_data_structure(data, col_names=None)
        else:
            self.data = self.create_data_structure(data, col_names=self.custom_columns)

    def calculate_column_widths(self):
        """
        Calculate the maximum width for each column based on the data and header labels.
        """
        for key, values in self.data.items():
            max_value_length = max(len(str(value)) for value in values)
            self.column_widths[key] = max(max_value_length, len(key))

    def display(self):
        padding_right = 4 
        headers = list(self.data.keys())
        header_format = "| " + " | ".join([f"{{:<{self.column_widths[header] + padding_right}}}" for header in headers]) + " |"
        header_line = header_format.format(*headers)
        separator_line = "|" + "|".join(["-" * (self.column_widths[header] + padding_right + 2) for header in headers]) + "|"

        print(header_line)
        print(separator_line)

        num_rows = len(next(iter(self.data.values())))
        for i in range(num_rows):
            row_data = [self.data[header][i] for header in headers]
            print(header_format.format(*row_data))


class Border:
    def __init__(self, Title, Body, line_width=100):
        """
        Initializes the Display class with generic data.
        """
        self.Title = Title
        self.Body = Body   
        self.line_width = line_width         
        
    def display(self):
        title = self.Title
        body = self.Body
        name_line = f" {title} "
        max_line_length = max(len(name_line) - 2, self.line_width)
        
        top_border = "┌" + "─" * (max_line_length + 2) + "┐"
        horizontal_border = "├" + "─" * (max_line_length + 2) + "┤"
        bottom_border = "└" + "─" * (max_line_length + 2) + "┘"
        
        words = body.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 > max_line_length:
                lines.append(current_line)
                current_line = word
            else:
                if current_line:
                    current_line += " "
                current_line += word
        
        if current_line:
            lines.append(current_line)
        
        print(top_border)
        print(f"│{name_line.center(max_line_length + 2)}│")
        print(horizontal_border)
        
        for line in lines:
            print(f"│ {line.ljust(max_line_length)} │")
        print(bottom_border)




class Grid:
    def __init__(self, statistics, Title=None):
        """
        Initializes the Display class with generic data.
        """
        self.statistics = statistics
        self.Title = Title             
        
    def display(self):
        stats = self.statistics
        title = f" {self.Title} Statistics " if self.Title is not None else " Stock Statistics "
        max_key_len = max(len(key) for key in stats.keys())
        max_val_len = max(len(str(value)) for value in stats.values())

        total_width = max_key_len + max_val_len + 7 

        top_border = "╔" + "═" * (total_width - 2) + "╗"     
        title_line = f"║{title.center(total_width - 2)}║"

        print(top_border)
        print(title_line)
        print("╠" + "═" * (total_width - 2) + "╣")

        for key, value in stats.items():
            row = f"║ {key.ljust(max_key_len)} │ {str(value).ljust(max_val_len)} ║"
            print(row)
            print("╟" + "─" * (total_width - 2) + "╢")

        print("╚" + "═" * (total_width - 2) + "╝")



def __dir__():
    return ['Table', 'Border', 'Grid']

__all__ = ['Table', 'Border', 'Grid']




