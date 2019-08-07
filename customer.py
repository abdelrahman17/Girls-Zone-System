from Utilities import DatabaseManager
import pyodbc


class Customer:
    customers = []

    def __init__(self, ID: int, name: str, phone: str, address: str):
        self.ID = ID
        self.name = name
        self.phone = phone
        self.address = address

    def edit(self, new_name, new_phone, new_address):
        try:
            with DatabaseManager() as db:
                # db.execute('update CustomerTable set name = ?, phone = ?, address = ? where customer_id = ?',
                #            (new_name, new_phone, new_address, self.ID))
                db.execute(f"update CustomerTable set name = N'{new_name}', phone = N'{new_phone}', address = N'{new_address}' where customer_id = {self.ID}")
                db.commit()
                self.name = new_name
                self.phone = new_phone
                self.address = new_address
        except pyodbc.Error as err:
            print('error while editing the customer data')
            print(str(err))

    def delete(self):
        try:
            with DatabaseManager() as db:
                db.execute('update CustomerTable set flag = ? where customer_id = ?',('deleted' ,self.ID))
                db.commit()
            self.load_cutomers()
        except pyodbc.Error:
            print('Error while deleting customer from the database')

    @classmethod
    def new_customer(cls, name, phone, address) -> 'Customer':
        try:
            with DatabaseManager() as db:
                # db.execute("insert into CustomerTable (name, phone, address) values(?, ?, ?)",
                #            (name, phone, address))
                db.execute(f"insert into CustomerTable (name, phone, address) values(N'{name}', N'{phone}', N'{address}')")
                db.commit()
            cls.load_cutomers()
        except pyodbc.Error as err:
            print('Error while adding new customer data to the database')
            print(err)
        finally:
            return cls.get_by_phone(phone)

    @classmethod
    def get_by_id(cls, ID):
        for customer in cls.customers:
            if customer.ID == ID:
                return customer

    @classmethod
    def get_by_phone(cls, phone):
        for customer in cls.customers:
            if customer.phone == phone:
                return customer

    @classmethod
    def load_cutomers(cls):
        cls.customers.clear()
        try:
            with DatabaseManager() as db:
                db.execute("select * from CustomerTable where flag = 'live'")
                rows = db.fetchall()
            for row in rows:
                cls.customers.append(Customer(*row[:-1]))
        except pyodbc.Error:
            print('Error while loading customers')
            # print(err)

    def __repr__(self):
        return f"Customer({self.ID}, {self.name}, {self.phone}, {self.address})"
