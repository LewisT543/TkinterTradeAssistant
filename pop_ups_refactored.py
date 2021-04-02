# Base imports for all pop_up Classes
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Separator

# Pandastable for displaying database contents (ShowTradesDisplay)
from pandastable import Table, TableModel

# Dateparser for (AddTradeDisplay)
from dateutil.parser import parse
import datetime


# This is a base class, from which all other popups are derived. It takes only a parent argument, defaulting to None.
class PopUpBlueprint(tk.Frame):
    def __init__(self, parent=None):
        self.is_showing = True
        self.parent = parent
        tk.Frame.__init__(self)
        self.window = tk.Toplevel(parent)
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        self.window.protocol('WM_DELETE_WINDOW', self.on_closing)

    # Callback designed to show/hide a hidden/shown widget on clicking the 'X' button. Also destroys the window.
    def on_closing(self):
        self.is_showing = not self.is_showing
        self.window.destroy()

    # Validate and Set Geometry and title for popup
    def setup_popup(self, geometry, title):
        if self.validate_geometry(geometry):
            self.window.geometry(geometry)
        if self.validate_title(title):
            self.window.title(title)
    
    # Allow only 'nnn(n)xnnn(n)'
    @staticmethod
    def validate_geometry(geometry_string):
        try:
            str_list = geometry_string.split(sep='x', maxsplit=1)
            print(str_list)
            for str in str_list:
                if 2 < len(str) < 5 and str.isdigit():
                    continue
                else:
                    return False
            return True
        except Exception as e:
            print('Error Validating geometry string.')

    # Allow only type(str) and length < 50 chars
    @staticmethod
    def validate_title(title_string):
        if isinstance(title_string, str) and len(title_string) < 50:
            return True
        else:
            return False


# Trades Window display
class MyTradesWindow(PopUpBlueprint):
    def __init__(self, parent=None, dataframe=None, geometry=None, title=None):
        super.__init__(parent)
        self.df = dataframe
        self.setup_popup(geometry, title)
        self.table = pt = Table(self.main_frame, dataframe=self.df, showtoolbar=True, showstatusbar=True)
        pt.show()


# Add Trade Window display
class AddTradeWindow(PopUpBlueprint):
    def __init__(self, parent=None, entries_list=None, db_con=None, geometry=None, title=None):
        super.__init__(parent)
        self.entries_list = entries_list
        self.db_con = db_con
        self.setup_popup(geometry, title)
        self.vars_entries_labels_setup()

    # Create the main widgets and layout of said widgets.    
    def vars_entries_labels_setup(self):
        self.entries_frame = tk.LabelFrame(self.window, text='Enter Trade Details: ', width=400, height=500)
        self.entries_frame.place(x=0,y=0)
        # Three vars to hold stringvars, entry widgets and entry labels.
        self.stringvars = {}
        self.entries = {}
        self.entry_labels = {}
        # Use enumerate to: 1. Create the stringVars; 2. Create entries; 3. Create entry labels; 4. Grid entry labels using index.
        for index, entry in enumerate(self.entries_list):
            # Create String Variables, store them in self.stringvars{entry: StringVar}
            self.stringvars[entry] = tk.StringVar()
            # Create Entries, store them in self.entries{entry: Entry Widget}, place using grid
            self.entries[entry] = tk.Entry(self.entries_frame, textvariable=self.stringvars[entry], width=40)
            self.entries[entry].grid(row=index, column=2, padx=2, pady=2)
            # Create Entry Labels, store them in self.entry_labels{entry: Label Widget}, place using grid
            # Split entries into 2 groups, active and passive, creating the passive ones in disabled state and a slightly different text
            if entry in ['cost', 'exit_total', 'profit_loss', 'pct_gain_loss']:
                self.entry_labels[entry] = tk.Label(self.entries_frame, text=f'{entry.capitalize()}: ')
                self.entries[entry].config(state=tk.DISABLED)
            else:
                self.entry_labels[entry] = tk.Label(self.entries_frame, text=f'Enter {entry.capitalize()}: ')
            self.entry_labels[entry].grid(row=index, column=1, ipadx=2, ipady=2, padx=2, pady=2)
        # Adding trace variables to required fields.
        self.stringvars['long_short'].trace_add('write', self.format_long_short)
        # Submit button
        self.submit_button = tk.Button(self.entries_frame, text='Save to Database', command=self.submit)
        self.submit_button.grid(row=(len(self.entries_list)+2), column=2, padx=5, pady=5)
        # Calculate button
        self.calc_button = tk.Button(self.entries_frame, text='Calculate Fields', command=self.calculate)
        self.calc_button.grid(row=(len(self.entries_list) + 2), column=1, padx=5, pady=5)

    # Gets all values from Entry fields/StringVars, validates the data within them and calculates the missing values, adding them in.
    def calculate(self):
        # Create mapping to add data to and get the data from self.stringvars{}
        data_fields = {'price': None, 'quantity': None, 'exit_price': None}
        for key in data_fields.keys():
            data_fields[key] = self.stringvars[key].get()
            if data_fields[key] == None:
                messagebox.showerror(f'Empty field: {key}.\nPlease enter:\n\tPrice\n\tQuantity\n\tExit price')
                break
        # Force float type
        try:
            cost = float(data_fields['price']) * float(data_fields['quantity'])
            exit_total = float(data_fields['quantity']) * float(data_fields['exit_price'])               
        except TypeError:
            print('Cannot calculate cost or exit total, data is not of type: Float.')
        # Sort out the long/shorts
        long_or_short = self.stringvars['long_short'].get()
        if long_or_short == 'Long':
            profit_loss = exit_total - cost
        elif long_or_short == 'Short':
            profit_loss = cost - exit_total
        else:
            messagebox.showerror('Empty Field', 'Please enter valid long/short representation.\n\tUse: [long, short, Long, Short, l, s, 1, -1]')  
        # Format data into dictionary, calculating blank data fields
        output_data = {'cost': cost, 'exit_total': exit_total, 'profit_loss': profit_loss, 
                        'pct_gain_loss': round((profit_loss / cost) * 100, 2)}
        # Add data to blank data fields
        for key in output_data:
            self.stringvars[key].set(output_data[key]) 
    
    # Verify all Entry fields (StringVars), throwing an error if not all present and correct
    def submit(self):
        # Iterate through stringvars and get data for all
        item_dict = {}
        for key in self.stringvars:
            item = self.stringvars[key].get()
            # Tackle empty fields
            if item == '':
                # Shows an error if an item is left empty, sets focus back to popup main window after
                messagebox.showerror('Error', 'Empty Field %s'.format(key))
                self.window.focus_set()
                break
            # Verify each field and add to item_dict:
            # Verify all strings
            if key in ['counterparty', 'base_asset', 'asset', 'long_short', 'strategy'] and self.verify_string(item):
                item_dict[key] = item
            # Verify and format all dates
            elif key in ['open_date', 'close_date'] and self.verify_date(item):
                item = self.format_date(item)
                item_dict[key] = item
            # Verify floats
            elif self.verify_float(item):
                item_dict[key] = item
        # Submit the finished information, mapped into a dictionary, break the operation if any values are None.
        for val in item_dict:
            if val == None:
                return 
        # Call add_to_database to submit cleaned data to db                
        self.db_con.add_item(item_dict)

    @staticmethod
    def verify_string(string):
        if string.isalnum() and len(string) < 256:
            return True
    
    @staticmethod
    def verify_float(string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    @staticmethod        
    def verify_date(string, fuzzy=False):
        try:
            parse(string, fuzzy=fuzzy)
            return True
        except ValueError:
            return False
    
    @staticmethod 
    def format_date(string):
        try:
            my_datetime = parse(string, fuzzy=False)
            my_date = datetime.date.strftime(my_datetime, '%d/%m/%Y')
            return my_date
        except ValueError:
            return None

    @staticmethod 
    def verify_long_short(string):
        if string in ['1', '-1', 'long', 'short', 'l', 's', 'Long', 'Short']:
            return True
    
    # Callback command for long_short 'w' Tracer, normalises representations of long/short. Using *args to unpack all arguments sent
    # by the event handler. Not that we actually use them. *args = [x, y, event_widget, z]
    def format_long_short(self, *args):
        if self.stringvars['long_short'].get() in ['1', 'long', 'l', 'Long']:
            self.stringvars['long_short'].set('Long')
        elif self.stringvars['long_short'].get() in ['-1', 'short', 's', 'Short']:
            self.stringvars['long_short'].set('Short')


class PositionSizingWindow(PopUpBlueprint):

    inputs = {'Balance': (1, 1), 'Risk %': (1, 3), 'Price': (2, 1), 'ATR': (2, 3), 'Quantity': (3, 3), 
                    'LongTP': (4, 1), 'LongSL': (5, 1), 'ShortTP': (4, 3), 'ShortSL': (5, 3)}
    font = ('Ariel', 14)

    def __init__(self, parent=None, geometry=None, title=None):
        super.__init__(parent)
        self.setup_popup(geometry, title)
        self.vars_entries_labels_setup()

    # Definitely potential to inherit some form of this function for more polymorphic implementation of widget 
        # creation and placement
    def vars_entries_labels_setup(self):
        # Labelframe to hold it all
        self.entries_frame = tk.LabelFrame(self.window, text='Enter Trade Details')
        self.entries_frame.place(x=0, y=0)
        # Three vars to hold stringvars, entry widgets and entry labels.
        self.stringvars = {}
        self.entries = {}
        self.entry_labels = {}
        # Use for loop to: 1. Create the stringVars; 2. Create entries; 3. Create entry labels; 4. Grid entries based on co-ordinate tuple.
        for entry in PositionSizingWindow.inputs:
            self.stringvars[entry] = tk.StringVar() 
            self.stringvars[entry].trace_add('write', self.validate_entry)
            vcmd = (self.register(self.validate_entry))
            self.entries[entry] = tk.Entry(self.entries_frame, textvariable=self.stringvars[entry], width=8, font=PositionSizingWindow.font, 
                                            validate='all', validatecommand=(vcmd, '%P'))
            self.entries[entry].grid(row=PositionSizingWindow.inputs[entry][0], column=PositionSizingWindow.inputs[entry][1] + 1, 
                                        padx=5, pady=5)
            self.entry_labels[entry] = tk.Label(self.entries_frame, text=entry, font=PositionSizingWindow.font)
            self.entry_labels[entry].grid(row=PositionSizingWindow.inputs[entry][0], column=PositionSizingWindow.inputs[entry][1], 
                                        padx=5, pady=5)
        # Calculate Button
        self.calc_button = tk.Button(self.entries_frame, text='Calculate Fields', command=self.calculate)
        self.calc_button.grid(row=3, column=2, padx=10, pady=10)
    
    # Calculate all missing values in 
    def calculate(self, *args):
        # Sort all the calcs out, only firing when all are not-none
        get_fields = {'Balance': None, 'Price': None, 'Risk %': None, 'ATR': None}
        for entry in get_fields:
            get_fields[entry] = self.stringvars[entry].get()
            if get_fields[entry] == None:
                messagebox.showerror('Error', 'Invalid field, please have values for:\n\tBalance\n\tPrice\n\tRisk %\n\tATR')
        # Do calcs here

        
        # Update the entry fields

    # Active validator used for entering chars into any field in PositionSizingWindow. Does not allow any typing other than digits.
    def validate_entry(self, P, *args):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False

    

