from Utilities import DatabaseManager
import pyodbc


class Customer:
    customers = []

    def __init__(self, ID: int, name: str, phone: str, address: str):
        self.ID = ID
        self.name = name
        self.phone = phone
        self.address = address

    def add(self):
        try:
            with DatabaseManager() as db:
                db.execute('insert into CustomerTable (name, phone, address) values(?, ?, ?)',
                           (self.name, self.phone, self.address))
                db.commit()
            with DatabaseManager() as db:
                db.execute('select customer_id from CustomerTable where phone = ?', self.phone)
                self.ID = db.fetchone()[0]
            self.customers.append(self)
        except pyodbc.Error as sql_err:
            # Phone number is a unique value and already exists, update the current object with the saved data
            # print(sql_err)
            print("This phone number already exists in the database")
            with DatabaseManager() as db:
                db.execute('select * from CustomerTable where phone = ?', self.phone)
                row = db.fetchone()
                self.ID = row[0]
                self.name = row[1]
                self.phone = row[2]
                self.address = row[3]

    def edit(self, new_name: str, new_phone: str, new_address: str):
        try:
            with DatabaseManager() as db:
                db.execute('update CustomerTable set name = ?, phone = ?, address = ? where customer_id = ?',
                           (new_name, new_phone, new_address, self.ID))
                db.commit()
                self.name = new_name
                self.phone = new_phone
                self.address = new_address
        except pyodbc.Error as err:
            print('error while editing the customer data')
            print(str(err))


    def delete(self):
        with DatabaseManager() as db:
            db.execute('delete from CustomerTable where cutomer_id = ?', self.ID)

    @classmethod
    def get_by_id(cls, ID):
        for customer in cls.customers:
            if customer.ID == ID:
                return customer
        return None

    @classmethod
    def get_by_phone(cls, phone):
        for customer in cls.customers:
            if customer.phone == phone:
                return customer
        return None

    @classmethod
    def load_cutomers(cls):
        try:
            with DatabaseManager() as db:
                db.execute('select * from CustomerTable')
                rows = db.fetchall()
            for row in rows:
                cls.customers.append(Customer(*row))
        except pyodbc.Error as err:
            print('Error while loading customers')
            # print(err)

    def __repr__(self):
        return f"Customer({self.ID}, {self.name}, {self.phone}, {self.address})"
