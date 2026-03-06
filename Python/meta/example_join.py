"""
Example demonstrating JOIN functionality in the ORM.
"""
import logging
from orm import Model, DorisEngine, Session, StringField, IntegerField, JoinType

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


# Define models
class User(Model):
    __table__ = "users"
    id = IntegerField()
    name = StringField()
    age = IntegerField()


class Order(Model):
    __table__ = "orders"
    id = IntegerField()
    user_id = IntegerField()
    product = StringField()
    amount = IntegerField()


class Address(Model):
    __table__ = "addresses"
    id = IntegerField()
    user_id = IntegerField()
    city = StringField()
    street = StringField()


if __name__ == "__main__":
    # Example connection (adjust hosts and credentials as needed)
    hosts = ["localhost"]

    # Note: This is a demonstration. Actual execution requires a running database.
    # with DorisEngine(hosts, password="your_password").debug(True) as conn:
    #     with Session(conn).debug() as session:

    # Example 1: INNER JOIN
    # Joins users and orders tables
    # SQL: SELECT * FROM users INNER JOIN orders ON users.id = orders.user_id
    print("Example 1: INNER JOIN")
    print("session.query(User).join(Order, 'users.id = orders.user_id').all()")
    print()

    # Example 2: LEFT JOIN
    # Gets all users and their orders (if any)
    # SQL: SELECT * FROM users LEFT JOIN orders ON users.id = orders.user_id
    print("Example 2: LEFT JOIN")
    print("session.query(User).join(Order, 'users.id = orders.user_id', JoinType.LEFT).all()")
    print()

    # Example 3: RIGHT JOIN
    # Gets all orders and their users (if any)
    # SQL: SELECT * FROM users RIGHT JOIN orders ON users.id = orders.user_id
    print("Example 3: RIGHT JOIN")
    print("session.query(User).join(Order, 'users.id = orders.user_id', JoinType.RIGHT).all()")
    print()

    # Example 4: Multiple JOINs
    # Joins users with both orders and addresses
    # SQL: SELECT * FROM users
    #      INNER JOIN orders ON users.id = orders.user_id
    #      LEFT JOIN addresses ON users.id = addresses.user_id
    print("Example 4: Multiple JOINs")
    print("session.query(User)")
    print("    .join(Order, 'users.id = orders.user_id')")
    print("    .join(Address, 'users.id = addresses.user_id', JoinType.LEFT)")
    print("    .all()")
    print()

    # Example 5: JOIN with WHERE clause
    # Joins and filters results
    # SQL: SELECT * FROM users
    #      INNER JOIN orders ON users.id = orders.user_id
    #      WHERE users.age > 18
    print("Example 5: JOIN with WHERE clause")
    print("session.query(User)")
    print("    .join(Order, 'users.id = orders.user_id')")
    print("    .filter(User.age > 18)")
    print("    .all()")
    print()

    # Example 6: JOIN with ORDER BY and LIMIT
    # Joins and sorts results with pagination
    # SQL: SELECT * FROM users
    #      INNER JOIN orders ON users.id = orders.user_id
    #      WHERE orders.amount > 100
    #      ORDER BY users.name
    #      LIMIT 10 OFFSET 0
    print("Example 6: JOIN with ORDER BY and LIMIT")
    print("session.query(User)")
    print("    .join(Order, 'users.id = orders.user_id')")
    print("    .filter(Order.amount > 100)")
    print("    .order_by('users.name')")
    print("    .limit(10)")
    print("    .all()")
    print()

    # Example 7: Complex multi-table JOIN
    # Comprehensive example with all features
    # SQL: SELECT * FROM users
    #      LEFT JOIN orders ON users.id = orders.user_id
    #      INNER JOIN addresses ON users.id = addresses.user_id
    #      WHERE users.age > 18 AND addresses.city = 'New York'
    #      ORDER BY users.name, orders.amount DESC
    #      LIMIT 20 OFFSET 10
    print("Example 7: Complex multi-table JOIN")
    print("session.query(User)")
    print("    .join(Order, 'users.id = orders.user_id', JoinType.LEFT)")
    print("    .join(Address, 'users.id = addresses.user_id')")
    print("    .filter(User.age > 18, Address.city == 'New York')")
    print("    .order_by('users.name', 'orders.amount DESC')")
    print("    .limit(20)")
    print("    .offset(10)")
    print("    .all()")
    print()

    print("JOIN functionality is now available in the ORM!")
    print("Supported JOIN types: INNER (default), LEFT, RIGHT")
    print("Can be combined with filter(), order_by(), limit(), offset(), first(), etc.")
