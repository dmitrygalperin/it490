# Walcart

Walcart is an open-source product tracking service built around the Walmart Product API. Users can register an account and begin tracking a product's price and availability status. Walcart regularly polls the Walmart Product API for updated price information and provides users with a graph of a tracked product's price history.

## Architecture

Walcart is written written entirely in Python, and makes use of the RabbitMQ message broker for all inter-server communications.

The system's architecture is comprised of a 4 server stack consisting of the following:

1. RabbitMQ
	* Handles all messaging between servers	
2. Database
	* Processes all CRUD operations to the database
	* Uses SQLAlchemy Core and ORM to process queries
3. Backend
	* Handles all business logic between the frontend and database
	* Regularly polls Walmart Product API to maintain accurate price data
4. Frontend
	* Handles all forward-facing user interactions

## Core Dependencies

* Python 3.5.2
* MySQL
* Flask
* SQLAlchemy
* Pika

## Usage

Configure all networking and API settings in lib/config.py.

### Server entry points:

backend/backend.py

database/dbserv.py

frontend/app.py
