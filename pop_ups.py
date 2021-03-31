import tkinter as tk
from tkinter import messagebox
from pandastable import Table, TableModel
from dateutil.parser import parse
import datetime

class TradesDisplay(tk.Frame):
    # Display My Trades window
    def __init__(self, passed_dataframe=TableModel.getSampleData(), parent=None):
        self.is_showing = True
        self.parent = parent
        tk.Frame.__init__(self)
        self.main = tk.Toplevel(parent)
        self.main.geometry('1000x400+200+100')
        self.main.title('My Trades Table')
        self.main.protocol('WM_DELETE_WINDOW', self.on_closing)
        f = tk.Frame(self.main)
        f.pack(fill=tk.BOTH, expand=1)
        df = passed_dataframe
        self.table = pt = Table(f, dataframe=df, showtoolbar=True, showstatusbar=True)
        pt.show()
        return
    
    def on_closing(self):
        self.is_showing = not self.is_showing
        self.main.destroy()
    

class AddTradeDisplay(tk.Frame):
    # Display Add Trade window
    def __init__(self, parent=None, entries_list=None, db_con=None):
        self.is_showing = True
        self.parent = parent
        tk.Frame.__init__(self)
        self.main = tk.Toplevel(parent)
        self.main.geometry('390x520')
        self.main.title('Add Trade')
        self.main.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.db_con = db_con
        # Set-up and placing of StringVars, entries and entry_labels
        self.entries_frame = tk.LabelFrame(self.main, text='Enter Trade Details: ', width=400, height=500)
        self.entries_frame.place(x=0,y=0)
        self.trace_vars = {}
        self.entries = {}
        self.entry_labels = {}    
        for index, entry in enumerate(entries_list):
            self.trace_vars[entry] = tk.StringVar()
            self.entries[entry] = tk.Entry(self.entries_frame, textvariable=self.trace_vars[entry], width=40)
            self.entries[entry].grid(row=index, column=2, padx=2, pady=2)
            if entry in ['cost', 'exit_total', 'profit_loss', 'pct_gain_loss']:
                self.entry_labels[entry] = tk.Label(self.entries_frame, text=f'{entry.capitalize()}: ')
                self.entries[entry].config(state=tk.DISABLED)
            else:
                self.entry_labels[entry] = tk.Label(self.entries_frame, text=f'Enter {entry.capitalize()}: ')
            self.entry_labels[entry].grid(row=index, column=1, ipadx=2, ipady=2, padx=2, pady=2)
        # Sort out some exceptions to the mass_production of entries, labels and trace_vars
        self.trace_vars['long_short'].trace_add('write', self.format_long_short)
        # Submit button
        self.submit_button = tk.Button(self.entries_frame, text='Save to Database', command=self.submit)
        self.submit_button.grid(row=(len(entries_list)+2), column=2, padx=5, pady=5)
        # Calculate button
        self.calc_button = tk.Button(self.entries_frame, text='Calculate Fields', command=self.calculate)
        self.calc_button.grid(row=(len(entries_list) + 2), column=1, padx=5, pady=5)
    
    def calculate(self):
        # Create mapping to add data to
        data_fields = {'price': None, 'quantity': None, 'exit_price': None}
        for key in data_fields.keys():
            data_fields[key] = self.trace_vars[key].get()
            if data_fields[key] == None:
                messagebox.showerror(f'Empty field: {key}.\nPlease enter:\n\tPrice\n\tQuantity\n\tExit price')
                break
        # Force float type
        cost = float(data_fields['price']) * float(data_fields['quantity'])
        exit_total = float(data_fields['quantity']) * float(data_fields['exit_price'])               
        # Sort out the long/shorts
        long_or_short = self.trace_vars['long_short'].get()
        if long_or_short == 'Long':
            profit_loss = exit_total - cost
        elif long_or_short == 'Short':
            profit_loss = cost - exit_total
        else:
            messagebox.showerror('Empty Field', 'Please enter valid long/short representation.\n\tUse: [long, short, Long, Short, l, s, 1, -1]')  
        # Format data into dictionary
        output_data = {
            'cost': cost, 
            'exit_total': exit_total, 
            'profit_loss': profit_loss,   
            'pct_gain_loss': round((profit_loss / cost) * 100, 2)
        }
        # Add data to form
        for key in output_data:
            print(key, output_data[key])
            print(self.trace_vars[key].get())
            self.trace_vars[key].set(output_data[key])

    def submit(self):
        # Verify all the fields, throwing an error if not all present and correct
        item_dict = {}
        for key in self.trace_vars:
            item = self.trace_vars[key].get()
            # Tackle empty fields
            if item == '':
                messagebox.showerror('Error', 'Empty Field %s'.format(key))
                self.main.focus_set()
                break
            # Verify each field and add to item_dict:
                # Strings first
            if key in ['counterparty', 'base_asset', 'asset', 'long_short', 'strategy'] and self.verify_string(item):
                item_dict[key] = item
                # Then dates, converting them too
            elif key in ['open_date', 'close_date'] and self.verify_date(item):
                item = self.format_date(item)
                item_dict[key] = item
                # Then finally floats/numbers
            elif self.verify_float(item):
                item_dict[key] = item
        
        # Submit the finished information, mapped into a dictionary
        # Call add_to_database to submit cleaned data to db
        for val in item_dict:
            if val == None:
                return                 
        self.db_con.add_item(item_dict)

    
    def on_closing(self):
        self.is_showing = not self.is_showing
        self.main.destroy() 
    
    def clear_form(self):
        pass
    
    def verify_string(self, string):
        if string.isalnum() and len(string) < 256:
            return True
    
    def verify_float(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False
            
    def verify_date(self, string, fuzzy=False):
        try:
            parse(string, fuzzy=fuzzy)
            return True
        except ValueError:
            return False
    
    def format_date(self, string):
        try:
            my_datetime = parse(string, fuzzy=False)
            my_date = datetime.date.strftime(my_datetime, '%d/%m/%Y')
            return my_date
        except ValueError:
            return None

    def verify_long_short(self, string):
        if string in ['1', '-1', 'long', 'short', 'l', 's', 'Long', 'Short']:
            return True
    
    def format_long_short(self, *args):
        if self.trace_vars['long_short'].get() in ['1', 'long', 'l', 'Long']:
            self.trace_vars['long_short'].set('Long')
        elif self.trace_vars['long_short'].get() in ['-1', 'short', 's', 'Short']:
            self.trace_vars['long_short'].set('Short')


class PositionSizingDisplay(tk.Frame):
    # Display Position sizing calculator window
    def __init__(self, parent=None):
        self.is_showing = True
        self.parent = parent
        tk.Frame.__init__(self)
        self.main = tk.Toplevel(parent)
        self.main.geometry('420x200')
        self.main.title('Position Size Calculator')
        self.main.protocol('WM_DELETE_WINDOW', self.on_closing)
        f = tk.Frame(self.main)
        f.pack(fill=tk.BOTH, expand=1)
        self.trace_vars = {}
        self.entries = {}
        self.entry_labels = {}
        inputs = {'Balance': (1, 1), 'Risk %': (1, 3), 'Price': (2, 1), 'ATR': (2, 3), 'Quantity': (3, 3), 
                    'LongTP': (4, 1), 'LongSL': (5, 1), 'ShortTP': (4, 3), 'ShortSL': (5, 3)}
        font = ('Ariel', 14)

        self.calc_button = tk.Button(f, text='Calculate Fields', command=self.calculate)
        self.calc_button.grid(row=3, column=2, padx=10, pady=10)
        for entry in inputs:
            self.trace_vars[entry] = tk.StringVar() 
            self.trace_vars[entry].trace_add('write', self.validate_entry)
            vcmd = (self.register(self.validate_entry))
            self.entries[entry] = tk.Entry(f, textvariable=self.trace_vars[entry], width=8, font=font, 
                                            validate='all', validatecommand=(vcmd, '%P'))
            self.entries[entry].grid(row=inputs[entry][0], column=inputs[entry][1] + 1, padx=5, pady=5)
            self.entry_labels[entry] = tk.Label(f, text=entry, font=font)
            self.entry_labels[entry].grid(row=inputs[entry][0], column=inputs[entry][1], padx=5, pady=5)
     
    def on_closing(self):
        self.is_showing = not self.is_showing
        self.main.destroy()
        
    def validate_entry(self, P, *args):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False

    def calculate(self, *args):
        # Sort all the calcs out, only firing when all are not-none
        # Doesnt Do anything yet, not worth implementing the same shit over and over.
        get_fields = {'Balance': None, 'Price': None, 'Risk %': None, 'ATR': None}
        for entry in get_fields:
            get_fields[entry] = self.trace_vars[entry].get()
        return

    