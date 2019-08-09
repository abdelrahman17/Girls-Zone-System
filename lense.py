from Utilities import DatabaseManager
import pyodbc
from datetime import datetime
from time import sleep
from collections import namedtuple


class Color:
    def __init__(self, lense_id, color_id, name, quantity):
        self.lense_id = lense_id
        self.color_id = color_id
        self.name = name
        self.quantity = quantity

    @classmethod
    def save(cls, lense_id, name, quantity):
        try:
            with DatabaseManager() as db:
                db.execute('insert into ColorsTable (lenseID, name, quantity) values(?, ?, ?)',
                           (lense_id, name, quantity))
                db.commit()
                db.execute('select top 1 color_id from ColorsTable order by color_id desc')
                color_id = db.fetchone()[0]
            return Color(lense_id, color_id, name, quantity)
        except pyodbc.Error as err:
            print('Error while adding new color to the database')
            print(err)

    def delete(self):
        try:
            with DatabaseManager() as db:
                db.execute("update ColorsTable set flag = 'deleted' where lenseID = ? and color_id = ?",
                           (self.lense_id, self.color_id))
                db.commit()
        except pyodbc.Error:
            print('Error while deleting color from the database')

    def edit(self, name, quantity):
        try:
            with DatabaseManager() as db:
                db.execute('update ColorsTable set name = ?, quantity = ? where lenseID = ? and color_id = ?',
                          (name, quantity, self.lense_id, self.color_id))
                db.commit()
            self.name = name
            self.quantity = quantity
        except pyodbc.Error as err:
            print('Error while updating color data in the database')
            print(err)

    def __repr__(self):
        return f"Color({self.lense_id}, {self.color_id}, '{self.name}', {self.quantity})"


class Lense:
    lenses = []

    def __init__(self, ID, name, diameter, colors):
        self.ID = ID
        self.name = name
        self.diameter = diameter
        self.colors = colors
        self.wholesale_price, self.selling_price = self.get_prices()

    @classmethod
    def new(cls, name, wholesale_price, selling_price, diameter, colors: list):  # colors is a list of colornamedtuple objects
        colors_list = []
        current_date, max_date = cls.get_dates()
        try:
            with DatabaseManager() as db:
                db.execute('insert into LensesTable (name, diameter) values(?, ?)',
                           (name, diameter))
                db.commit()
                db.execute('select top 1 lense_id from LensesTable order by lense_id desc')
                id_ = db.fetchone()[0]
            for color in colors:
                colors_list.append(Color.save(id_, color.name, color.quantity))
            with DatabaseManager() as db:
                db.execute(f"insert into PriceDetails (lense_id, wholesale_price, selling_price, start_date, end_date) values(?, ?, ?, ?, ?)",
                           (id_, wholesale_price, selling_price, current_date, max_date))
                db.commit()
            cls.load_lenses()
            return Lense(id_, name, diameter, colors_list)
        except pyodbc.Error as err:
            print('Error while adding new lense to the database')
            print(err)

    def edit(self, name, diameter):
        # we will just edit the lenses data and the colors will be updated separately
        try:
            with DatabaseManager() as db:
                db.execute('update LensesTable set name = ?, diameter = ? where lense_id = ?',
                           (name, diameter, self.ID))
                db.commit()
            self.name = name
            self.diameter = diameter
        except pyodbc.Error as err:
            print('Error while updating lense data in the database')
            print(err)

    def delete(self):
        try:
            with DatabaseManager() as db:
                db.execute("update LensesTable set flag = 'deleted' where lense_id = ?", self.ID)
                db.commit()
            self.load_lenses()
        except pyodbc.Error:
            print('Error while deleting Lense from the database')

    def get_prices(self):
        current_datetime = datetime.now()
        try:
            with DatabaseManager() as db:
                db.execute('select wholesale_price, selling_price from PriceDetails where ? between start_date and end_date and lense_id = ?',
                           (current_datetime, self.ID))
                prices = db.fetchone()
            if prices:
                return prices
            else:
                return None, None
        except pyodbc.Error:
            print('Error while fetching the price from the database')

    def update_prices(self, wholesale_price, selling_price):
        current_date, max_date = self.get_dates()
        with DatabaseManager() as db:
            db.execute('update PriceDetails set end_date = ? where end_date = ?', (current_date, max_date))
            db.commit()
            sleep(1)
            current_date, max_date = self.get_dates()
            db.execute('insert into PriceDetails (lense_id, wholesale_price, selling_price, start_date, end_date) values(?, ?, ?, ?, ?)',
                       self.ID, wholesale_price, selling_price,current_date, max_date)
            db.commit()
            self.wholesale_price = wholesale_price
            self.selling_price = selling_price

    @classmethod
    def load_lenses(cls):
        cls.lenses.clear()
        try:
            with DatabaseManager() as db:
                db.execute("select lense_id, name, diameter from LensesTable where flag = 'live'")
                lenses_data = db.fetchall()
                for row in lenses_data:
                    colors = cls.load_colors(row[0])
                    lense = Lense(*row, colors)
                    if lense.wholesale_price is not None and lense.selling_price is not None:
                        cls.lenses.append(lense)

        except pyodbc.Error as err:
            print('Error while loading lenses data from the database', err, sep='\n')

    @classmethod
    def load_colors(cls, lense_id):
        colors_list = []
        try:
            with DatabaseManager() as db:
                db.execute("select * from ColorsTable where lenseID = ? and flag = 'live'", lense_id)
                colors_data = db.fetchall()
            for row in colors_data:
                colors_list.append(Color(*row[:-1]))
            return colors_list
        except pyodbc.Error as err:
            print('Error while loading colors data from the database', err, sep='\n')

    @classmethod
    def get_dates(cls):
        current_date = str(datetime.now())
        current_date = current_date[:current_date.index('.')]
        max_date = str(datetime.max)
        max_date = max_date[:max_date.index('.')]
        return current_date, max_date

    @classmethod
    def get_lense_by_name(cls, name):
        cls.load_lenses()
        for lense in cls.lenses:
            if lense.name == name:
                return lense

    @classmethod
    def get_lense_by_id(cls, ID):
        cls.load_lenses()
        for lense in cls.lenses:
            if lense.ID == ID:
                return lense

    def get_color_by_id(self, ID):
        self.load_colors(self.ID)
        for color in self.colors:
            if color.color_id == ID:
                return color

    def get_color_by_name(self, name):
        self.load_colors(self.ID)
        for color in self.colors:
            if color.name == name:
                return color

    def __repr__(self):
        return f"Lense({self.ID}, '{self.name}', {self.diameter}, {self.colors})"

    def __str__(self):
        return f"Lense({self.ID}, '{self.name}', {self.wholesale_price}, {self.selling_price}, {self.diameter}, {self.colors})"
