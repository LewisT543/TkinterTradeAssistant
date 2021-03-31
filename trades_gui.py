
import tkinter as tk
from tkinter import messagebox
from trades_database import SQLiteDatabase
import datetime
from dateutil.parser import parse
import pandas as pd
from pandastable import Table, TableModel 
from pop_ups import *

window = tk.Tk()
window.title('My Trade Tracker')
window.geometry('600x600')


class TradesWindow:
    def __init__(self, master):
        # Setup database, building table(s) if absent
        self.database = SQLiteDatabase()
        # Setup tk.Toplevel window variables
        self.show_trades_window = None
        self.add_trade_window = None
        self.search_trade_window = None
        self.pos_calc_window = None
        # Building a base frame:
        self.base_frame = tk.Frame(master, width=600, height=600)
        self.base_frame.place(x=0,y=0)
        # Create a welcome screen:
        # self.welcome_screen(self.base_frame)
        # Create button_frame:    
        self.button_frame = tk.LabelFrame(self.base_frame, text='Options', width=580, height=190, bg='black', fg='white')
        self.button_frame.place(x=10, y=430)
        # Create buttons:
        self.main_menu_button_names = ['1). Show Trades', '2). Add Trade', '3). Search Trades', '4). Position Size Calc.', '5). extra_button_2', 
                                        '6). extra_button_3', '7). extra_button_4', '8). extra_button_5']    
        row, counter = 0, 0
        self.main_menu_items = {}
        for button_name in self.main_menu_button_names:
            # Make button and save to dictionary as its name.
            self.main_menu_items[button_name] = tk.Button(self.button_frame, text=button_name, width=19, height=4)
            # Grid the button
            self.main_menu_items[button_name].grid(row=row, column=counter)
            counter += 1
            if counter == 4:
                row += 1
                counter = 0
        
        self.main_menu_items['1). Show Trades'].config(command=lambda:self.show_trades(master))
        self.main_menu_items['2). Add Trade'].config(command=lambda:self.add_trade(master))

        self.main_menu_items['4). Position Size Calc.'].config(command=lambda:self.show_pos_calc(master))
        
    def welcome_screen(self, master):
        pass

    def show_trades(self, master):
        # if window exists, focus window
        # if window doesnt exist, create window and focus it        
        try:
            if self.show_trades_window.is_showing:
                self.show_trades_window.focus_set()
            else:
                df = pd.read_sql_query('SELECT * FROM trades', self.database.connection)
                self.show_trades_window = TradesDisplay(passed_dataframe=df, parent=master)
        except:
            df = pd.read_sql_query('SELECT * FROM trades', self.database.connection)
            self.show_trades_window = TradesDisplay(passed_dataframe=df, parent=master)

    def add_trade(self, master):
        try:
            if self.add_trade_window.is_showing:
                self.add_trade_window.focus_set()
            else:
                self.add_trade_window = AddTradeDisplay(master, entries_list=SQLiteDatabase.trade_column_names[1:], db_con=self.database)
        except:
            self.add_trade_window = AddTradeDisplay(master, entries_list=SQLiteDatabase.trade_column_names[1:], db_con=self.database)

    def show_pos_calc(self, master):
        try:
            if self.pos_calc_window.is_showing:
                self.pos_calc_window.focus_set()
            else:
                self.pos_calc_window = PositionSizingDisplay(master)
        except:
            self.pos_calc_window = PositionSizingDisplay(master)
        

if __name__ == '__main__':
    my_window = TradesWindow(window)
    window.resizable(False, False)
    window.mainloop()