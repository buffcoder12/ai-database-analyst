CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    stock INTEGER DEFAULT 0
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30) NOT NULL
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

INSERT INTO customers (name, email, city) 
VALUES 
('Rahul Sharma', '[rahul@example.com]', 'Delhi'),
('Priya Verma', '[priya@example.com]', 'Mumbai'),
('Amit Singh', '[amit@example.com]', 'Pune'),
('Neha Gupta', '[neha@example.com]', 'Banglore'),
('Rohan Mehta', '[rohan@example.com]', 'Jaipur');

INSERT INTO products (name, category, price, stock)
values
('Laptop', 'Electronics', 85000, 15),
('Wireless Mouse', 'Accessories', 1000, 30),
('Mechanical Keyboard', 'Accessories', 500, 100),
('4k Monitor', 'Electronics', 25000, 30),
('USB Hub', 'Accessories', 200, 50);

INSERT INTO orders (customer_id, order_date, status)
VALUES
(1, '2026-07-01', 'Shipped'),
(2, '2026-07-10', 'Pending'),
(3, '2026-07-13', 'Delivered'),
(4, '2026-07-20', 'Shipped'),
(5, '2026-07-26', 'Pending'),
(1, '2026-08-02', 'Delivered');

INSERT INTO order_items (order_id, product_id, quantity, unit_price)      
VALUES
(1, 1, 1, 85000),
(1, 2, 2, 1000),
(2, 4, 1, 25000),
(3, 3, 2, 500),
(4, 5, 2, 200),
(5, 2, 3, 1000),
(6, 2, 1, 85000);