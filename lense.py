from Utilities import DatabaseManager
from collections import namedtuple
import pyodbc

Color = namedtuple('Color', ['id', 'name', 'quantity'])


class Lense:
    lenses = []

    def __init__(self, ID, name, wholesale_price, selling_price, diameter=None, colors=None):  # colors: namedtuple
        self.ID = ID
        self.name = name
        self.wholesale_price = wholesale_price
        self.selling_price = selling_price
        self.diameter = diameter
        self.colors = colors

    @classmethod
    def new_lense(cls, name, wholesale_pirce, selling_price, diameter=None, colors=None): # colors is a namedtuple
        try:
            # first we update the lenses table
            with DatabaseManager() as db:
                db.execute('insert into LensesTable (name, wholesale_price, selling_price, diameter) values(?, ?, ?, ?)',
                           (name, wholesale_pirce, selling_price, diameter))
                db.commit()
            # get the id
            with DatabaseManager() as db:
                db.execute('select lense_id from LensesTable where name = ?', name)
                id_ = db.fetchone()[0]
            # second we update the colors table
            for color in colors:
                with DatabaseManager() as db:
                    db.execute('insert into ColorsTable (lenseID, name, quantity) values(?, ?, ?)',
                               (id_, color.name, color.quantity))
                    db.commit()
            cls.load_lenses()
            return cls.get_by_name(name)
        except pyodbc.Error as err:
            print('Error while saving lense to the database')
            print(err)

    def edit(self, new_name, new_wholesale_price, new_selling_price, new_diameter, new_colors):
        try:
            with DatabaseManager() as db:
                db.execute('update LensesTable set name = ?, wholesale_price = ?, selling_price = ?, diameter = ? where lense_id = ?',
                           (new_name, new_wholesale_price, new_selling_price, new_diameter, self.ID))
                db.commit()

            for color in new_colors:
                with DatabaseManager() as db:
                    db.execute('update ColorsTable set name = ?, quantity = ? where lenseID = ? and color_id = ?',
                               (color.name, color.quantity, self.ID, color.id))
                    db.commit()
            self.load_lenses()
            self.name = new_name
            self.wholesale_price = new_wholesale_price
            self.selling_price = new_selling_price
            self.diameter = new_diameter
            self.colors = new_colors
        except pyodbc.Error as err:
            print('Error while updating lense data in the database')
            print(err)

    def delete(self):
        try:
            with DatabaseManager() as db:
                db.execute('delete from LensesTable where lense_id = ?', self.ID)
                db.commit()
            self.load_lenses()
        except pyodbc.Error:
            print('Error while deleting lense from the database')

    def delete_color(self, color_id):
        try:
            with DatabaseManager() as db:
                db.execute('delete from ColorsTable where lenseID = ? and color_id = ?', (self.ID, color_id))
                db.commit()
            self.load_lenses()
            self.colors = self.get_by_name(self.name).colors
        except pyodbc.Error:
            print('Error while deleting color from the database')

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

    @classmethod
    def get_by_name(cls, name) -> 'Lense':
        for lense in cls.lenses:
            if lense.name == name:
                return lense

    def __repr__(self):
        return f"Lense({self.ID}, {self.name}, {self.wholesale_price}, {self.selling_price}, {self.diameter}, {self.colors})"
