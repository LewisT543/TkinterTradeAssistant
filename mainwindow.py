# Libraries
import tkinter as tk
import pandas as pd

# Local imports
from trades_database import SQLiteDatabase
from notes_handler_refactored import NoteHandler
from pop_ups_refactored import *

geometry = (600, 600)
window = tk.Tk()
window.title('My Trade Hub')
window.geometry(f'{geometry[0]}x{geometry[1]}')

class MainWindow:
    def __init__(self, parent):
        self.menu_buttons = {
            '1). Show Trades': lambda: self.show_my_trades_window(parent), 
            '2). Add Trade': lambda: self.show_add_trade_window(parent), 
            '3). Search Trades': None, 
            '4). Position Size Calc.': lambda: self.show_pos_size_calc_window(parent), 
            '5). extra_button_2': None,
            '6). extra_button_3': None,
            '7). extra_button_4': None, 
            '8). extra_button_5': None
        }
        self.db = SQLiteDatabase()
        self.note_handler = NoteHandler()
        self.base_frame = tk.Frame(parent, width=geometry[0], height=geometry[1])
        self.base_frame.place(x=0,y=0)
        self.windows_open = {}
        for name in self.menu_buttons:
            self.windows_open[name] = None 
            # Specifically need a new dict full of None
        self.welcome_screen(parent)
    
    # SETUP Methods:
    def make_buttons(self, menu_buttons):
        self.button_frame = tk.LabelFrame(self.base_frame, text='Options', width=(geometry[0]-20), 
                                                    height=(geometry[1]-10), bg='black', fg='white')
        self.button_frame.place(x=10, y=430)
        row, counter = 0, 0
        # Dict to store {name_of_button: Button object}
        self.main_menu_items = {}
        for button_name in menu_buttons:
            self.main_menu_items[button_name] = tk.Button(self.button_frame, text=button_name, width=19, height=4)
            self.main_menu_items[button_name].grid(row=row, column=counter)
            counter += 1
            if counter == 4:
                row += 1
                counter = 0
            self.main_menu_items[button_name].config(command=menu_buttons[button_name])
    
    def welcome_screen(self, parent):
        # Create Tk objects, load text from 'notes.txt', set: tk.text(textvariable=text from .txt file)
        self.make_buttons(self.menu_buttons)
        self.balance_label = tk.Label(parent, text='Welcome to My Trade Tracker!', font=('Ariel', 20))
        self.balance_label.place(x=15, y=10)
        self.noteframe = tk.LabelFrame(parent, text='My Notes', font=('Ariel', 16))
        self.noteframe.place(x=10, y=50)
        loaded_text = self.note_handler.get_text_from_file()
        text_var = tk.StringVar()
        self.notes_text = TextExtension(self.noteframe, textvariable=text_var, height=15, width=51, font=('Ariel', 14), bd=0, wrap=tk.WORD)
        self.notes_text.pack(fill=tk.BOTH)
        text_var.set(loaded_text)

    def show_my_trades_window(self, parent):
        def make_window():
            df = pd.read_sql_query('SELECT * FROM trades', self.db.connection)
            self.windows_open['1). Show Trades'] = MyTradesWindow(parent=parent, dataframe=df, geometry='900x500', title='My Trades')
        try:
            if self.windows_open['1). Show Trades'].window.state() == 'normal':
                self.windows_open['1). Show Trades'].window.focus()
        except Exception as e:
            make_window()

    def show_add_trade_window(self, parent):
        def make_window():
            self.windows_open['2). Add Trade'] = AddTradeWindow(parent=parent, entries_list=SQLiteDatabase.trade_column_names[1:], 
                                                                db_con=self.db, geometry='390x520', title='Add Trade')
        try:
            if self.windows_open['2). Add Trade'].window.state() == 'normal':
                self.windows_open['2). Add Trade'].window.focus()
        except Exception as e:
            make_window()


    # def show_search_trades_window(self, parent):
    #     def make_window():
    #         self.windows_open['3). Search Trades'] = SearchTradesWindow(parent=parent, entries_list=SQLiteDatabase.trade_column_names[:1], 
    #                                                             db_con=self.db, geometry='390x520', title='Add Trade')
    #     try:
    #         if self.windows_open['3). Search Trades'].is_showing():
    #             self.windows_open['3). Search Trades'].focus_set()
    #         else:
    #             make_window()
    #     except:
    #         make_window()

    def show_pos_size_calc_window(self, parent):
        def make_window():
            self.windows_open['4). Position Size Calc'] = PositionSizingWindow(parent=parent, geometry='420x220', 
                                                                                title='Position Size Calculator')
        try:
            if self.windows_open['4). Position Size Calc'].window.state() == 'normal':
                self.windows_open['4). Position Size Calc'].window.focus()
        except Exception as e:
            make_window()


if __name__ == '__main__':
    my_window = MainWindow(window)
    window.resizable(False, False)
    window.mainloop()


