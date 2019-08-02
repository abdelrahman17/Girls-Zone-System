from Utilities import DatabaseManager
from collections import namedtuple
import pyodbc

Color = namedtuple('Color', ['id', 'name', 'quantity'])


class Lense:
    lenses = []

    def __init__(self, ID, name, wholesome_price, selling_price, diameter=None, colors=None):  # colors: namedtuple
        self.ID = ID
        self.name = name
        self.wholesome_price = wholesome_price
        self.selling_price = selling_price
        self.diameter = diameter
        self.colors = colors

    def add(self):
        try:
            # We need to add lenses table
            with DatabaseManager() as db:
                db.execute('insert into LensesTable (name, wholesale_price, selling_price, diameter) values(?, ?, ?, ?)',
                           (self.name, self.wholesome_price, self.selling_price, self.diameter))
                db.commit()
            with DatabaseManager() as db:
                db.execute('select lense_id from LensesTable where name = ?', self.name)
                self.ID = db.fetchone()[0]

        # add the colors to the colors table
            for color in self.colors:
                print(color)
                print(color.id, color.name, color.quantity)
                with DatabaseManager() as db:
                    db.execute('insert into ColorsTable (lenseID, name, quantity) values(?, ?, ?)',
                               (self.ID, color.name, color.quantity))
                    db.commit()
            self.load_lenses()
        except pyodbc.Error:
            print('Error while adding the lense to the database')

    def edit(self,):
        pass

    @classmethod
    def load_lenses(cls):
        cls.lenses.clear()
        try:
            with DatabaseManager() as db:
                db.execute('select * from LensesTable')
                rows = db.fetchall()
            for row in rows:
                lense = Lense(*row)
                lense.load_colors()
                cls.lenses.append(lense)
        except pyodbc.Error:
            print('Error while loading lenses')

    def load_colors(self):
        try:
            with DatabaseManager() as db:
                db.execute('select color_id, name, quantity from ColorsTable where lenseID = ?', self.ID)
                rows = db.fetchall()
            colors = []
            for row in rows:
                colors.append(Color(*row))
                self.colors = colors
            return colors
        except pyodbc.Error:
            print('Error while loading lenses colors')

    def __repr__(self):
        return f"Lense({self.ID}, {self.name}, {self.wholesome_price}, {self.selling_price}, {self.diameter}, {self.colors})"
