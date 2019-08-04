from Utilities import DatabaseManager
import pyodbc
from customer import Customer


class OrderItem:
    def __init__(self, order_id, color_id, quantity):
        self.order_id = order_id
        self.color_id = color_id
        self.quantity = quantity

    def save(self, order_id):
        self.order_id = order_id
        try:
            with DatabaseManager() as db:
                db.execute('insert into OrderDetails (orderID, colorID, quantity) values(?, ?, ?)',
                           (self.order_id, self.color_id, self.quantity))
                db.commit()
        except pyodbc.Error:
            print('Error while adding order item to the database in add()')

    def delete(self):
        try:
            with DatabaseManager() as db:
                db.execute('delete from OrderDetails where orderID = ? and colorID = ?', (self.order_id, self.color_id))
                db.commit()
        except pyodbc.Error:
            print('Error while deleting order item from the database')

    def __repr__(self):
        return f"OrderItem({self.order_id}, {self.color_id}, {self.quantity})"


class Order:
    orders = []

    def __init__(self, ID, awm, customer_name, phone, address, delivery_fees, date_, status, note, order_items):
        self.ID = ID
        self.awm = awm
        self.customer_name = customer_name
        self.phone = phone
        self.address = address
        self.delivery_fees = delivery_fees
        self.date = date_
        self.status = status
        self.note = note
        self.order_itmes = order_items
        self.customer = Customer.get_by_phone(phone)

    @classmethod
    def make(cls, awm, customer_name, phone, address, delivery_fees, date_, status, note, order_items):  # order_items type: list of OrderItem
        try:
            customer = Customer.get_by_phone(phone)
            if customer is None:
                customer = Customer.new_customer(customer_name, phone, address)
            with DatabaseManager() as db:
                query = ("insert into OrderTable "
                         "(AWM, customerID, customer_name, address, phone, delivery_fees, date, status, note) "
                         "values(?, ?, ?, ?, ?, ?, ?, ?, ?)")
                db.execute(query, (awm, customer.ID, customer_name, address, phone, delivery_fees, str(date_), status, note))
                db.commit()
            with DatabaseManager() as db:
                db.execute('select top 1 order_id from OrderTable order by order_id desc')
                ID = db.fetchone()[0]
            for item in order_items:
                item.save(ID)
            order = Order(ID, awm, customer_name, phone, address, delivery_fees, date_, status, note, order_items)
            cls.orders.append(order)
            return order
        except pyodbc.Error as err:
            print('Error while saving order to the database')
            print(err)

    def __repr__(self):
        return (f"Order({self.ID}, {self.awm}, {self.customer_name}, {self.phone}, {self.address}, "
                f"{self.date}, {self.status}, {self.note}, {self.order_itmes})")
