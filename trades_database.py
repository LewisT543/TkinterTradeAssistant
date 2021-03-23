import sqlite3
from datetime import date

class SQLiteDatabase:
    def __init__(self):
        self.connection = sqlite3.connect('trades.db')
        self.c = self.connection.cursor()

    trade_column_names = ["id", "counterparty", "base_asset", "asset", "risk_pct", 
                        "risk_amount", "open_date", "price", "quantity", "cost", "close_date", 
                        "exit_price", "exit_total", "profit_loss", "pct_gain_loss", "strategy"]

    def create_trades_table(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY,
                    counterparty VARCHAR(255) NOT NULL,
                    base_asset VARCHAR(255) NOT NULL,
                    asset VARCHAR(255) NOT NULL,
                    risk_pct FLOAT NOT NULL,
                    risk_amount FLOAT NOT NULL,
                    open_date TEXT NOT NULL,
                    price FLOAT NOT NULL,
                    quantity FLOAT NOT NULL,
                    cost FLOAT NOT NULL,
                    close_date TEXT NOT NULL,
                    exit_price FLOAT NOT NULL,
                    exit_total FLOAT NOT NULL,
                    profit_loss FLOAT NOT NULL,
                    pct_gain_loss FLOAT NOT NULL,
                    strategy VARCHAR(255)
                    );''')    

    def add_item(self, item_dict):
        query = '''
        INSERT INTO trades ("counterparty", "base_asset", "asset", 
        "risk_pct", "risk_amount", "open_date", "price", "quantity", "cost", "close_date", 
        "exit_price", "exit_total", "profit_loss", "pct_gain_loss", "strategy") 
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''

        if [*item_dict] != SQLiteDatabase.trade_column_names[1:]:
            print([*item_dict])
            print(SQLiteDatabase.trade_column_names[1:])
            raise Exception('Item dict keys doesnt match database column names')
            
        else:
            values_list = list(item_dict.values())
        self.c.execute(query, (values_list))
        self.connection.commit()
    
    def alter_strategy(self, id, new_strat):
        query = 'UPDATE trades SET strategy = ? WHERE id = ?'
        self.c.execute(query, (new_strat, id))
        self.connection.commit()
    
    def delete_trade(self, item_id):
        query = 'DELETE FROM trades WHERE id = ?'
        self.c.execute(query, (item_id,))
        self.connection.commit()
    
    def print_all_rows(self):
        for row in self.c.execute('SELECT * FROM trades'):
            print(row)

    def all_search(self, search):
        for row in self.c.execute('SELECT * FROM trades'):
            if search in row:
                return row
        return None
    
    def id_search(self, id):
        for row in self.c.execute('SELECT * FROM trades WHERE id = ?', (id, )):
            return row
        return None

    def get_todays_trades(self):
        query = 'SELECT * FROM trades WHERE close_date = ?'
        todays_date = str(date.today().strftime("%d/%m/%Y"))
        print(todays_date)
        for row in self.c.execute(query, (todays_date, )):
            print(row)
    
    def delete_all(self):
        query = 'DELETE FROM trades'
        self.c.execute(query)

item = {"counterparty": 'Binance', "base_asset": 'USDT', "asset": 'BTC', "risk_pct": 3, 
        "risk_amount": 100, "open_date": '18/03/2021', "price": 55000, "quantity": 0.1, 
        "cost": 5500, "close_date": '23/03/2021', 'exit_price': 57000, 'exit_total': 5700, 
        "profit_loss": 200, "pct_gain_loss": 3.64, "strategy": 'basic'}

my_db = SQLiteDatabase()
my_db.create_trades_table()
my_db.add_item(item)
my_db.print_all_rows()
my_db.get_todays_trades()
my_db.delete_all()
my_db.print_all_rows()