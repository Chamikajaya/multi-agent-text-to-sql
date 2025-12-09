"""
Database Schema Definition

Contains the detailed schema documentation used by SQL generation agents
to understand the database structure and relationships.
"""

# Database schema with detailed table and column descriptions
SCHEMA_DEFINITION = """
TABLE: PRODUCTS
Description: Catalog of items available for sale.
COLUMNS:
- id (INTEGER): PK. Unique identifier for the product.
- cost (REAL): The cost to manufacture or acquire the item (not the sale price).
- category (TEXT): High-level product category (e.g., 'Accessories', 'Outerwear').
- name (TEXT): The commercial name of the product.
- brand (TEXT): The brand manufacturer.
- retail_price (REAL): The suggested MSRP or list price of the item.
- department (TEXT): Gender or demographic target (e.g., 'Men', 'Women').
- sku (TEXT): Stock Keeping Unit code.
- distribution_center_id (INTEGER): FK. Links to DISTRIBUTION_CENTERS table (location where stocked).

TABLE: USERS
Description: Registered customers and their demographic data.
COLUMNS:
- id (INTEGER): PK. Unique identifier for the user.
- first_name (TEXT): User's first name.
- last_name (TEXT): User's last name.
- email (TEXT): User's email address.
- age (INTEGER): User's age.
- gender (TEXT): User's gender (M/F).
- state (TEXT): State of residence.
- street_address (TEXT): Street address.
- postal_code (TEXT): Zip/Postal code.
- city (TEXT): City of residence.
- country (TEXT): Country of residence.
- latitude (REAL): GPS latitude of user address.
- longitude (REAL): GPS longitude of user address.
- traffic_source (TEXT): Marketing channel that acquired the user (e.g., 'Search', 'Organic').
- created_at (TIMESTAMP): Date and time the account was created.

TABLE: ORDERS
Description: Summary of a purchase event (basket level).
COLUMNS:
- order_id (INTEGER): PK. Unique identifier for the order.
- user_id (INTEGER): FK. Links to USERS table.
- status (TEXT): Current state of the order (e.g., 'Complete', 'Cancelled', 'Returned').
- gender (TEXT): Gender associated with the order items (often redundant with User gender).
- created_at (TIMESTAMP): Timestamp when the order was placed.
- returned_at (TIMESTAMP): Timestamp if/when the order was returned.
- shipped_at (TIMESTAMP): Timestamp when the order left the warehouse.
- delivered_at (TIMESTAMP): Timestamp when the order reached the customer.
- num_of_item (INTEGER): Total count of items in this order.

TABLE: ORDER_ITEMS
Description: Individual line items within an order. Use this for revenue calculations.
COLUMNS:
- id (INTEGER): PK. Unique identifier for the line item.
- order_id (INTEGER): FK. Links to ORDERS table.
- user_id (INTEGER): FK. Links to USERS table.
- product_id (INTEGER): FK. Links to PRODUCTS table.
- inventory_item_id (INTEGER): FK. Links to INVENTORY_ITEMS table (specific stock instance).
- status (TEXT): Status of this specific item (e.g., 'Returned', 'Complete').
- created_at (TIMESTAMP): Purchase timestamp.
- shipped_at (TIMESTAMP): Shipping timestamp.
- delivered_at (TIMESTAMP): Delivery timestamp.
- returned_at (TIMESTAMP): Return timestamp.
- sale_price (REAL): The actual price the user paid for this item (Revenue).

TABLE: INVENTORY_ITEMS
Description: Historical log of every specific physical item in the warehouse.
COLUMNS:
- id (INTEGER): PK. Unique identifier for the inventory unit.
- product_id (INTEGER): FK. Links to PRODUCTS table.
- created_at (TIMESTAMP): When the item arrived in inventory.
- sold_at (TIMESTAMP): When the item was sold (NULL if currently in stock).
- cost (REAL): Cost of this specific inventory batch.
- product_category (TEXT): Redundant snapshot of product category.
- product_name (TEXT): Redundant snapshot of product name.
- product_brand (TEXT): Redundant snapshot of brand.
- product_retail_price (REAL): Redundant snapshot of retail price.
- product_department (TEXT): Redundant snapshot of department.
- product_sku (TEXT): Redundant snapshot of SKU.
- product_distribution_center_id (INTEGER): FK. Links to DISTRIBUTION_CENTERS table.

TABLE: DISTRIBUTION_CENTERS
Description: Physical warehouse locations.
COLUMNS:
- id (INTEGER): PK. Unique identifier for the distribution center.
- name (TEXT): Name of the facility (e.g., 'Memphis TN').
- latitude (REAL): GPS latitude of the facility.
- longitude (REAL): GPS longitude of the facility.

TABLE: EVENTS
Description: Web traffic logs (views, clicks, interactions).
COLUMNS:
- id (INTEGER): PK. Unique identifier for the event log.
- user_id (REAL): FK. Links to USERS (can be NULL for guest visitors).
- sequence_number (INTEGER): Order of events within a session.
- session_id (TEXT): Unique ID for the browsing session.
- created_at (TIMESTAMP): Timestamp of the event.
- ip_address (TEXT): User's IP address.
- city (TEXT): Estimated city based on IP.
- state (TEXT): Estimated state based on IP.
- postal_code (TEXT): Estimated zip code based on IP.
- browser (TEXT): Browser used (e.g., 'Chrome', 'Safari').
- traffic_source (TEXT): Marketing source for this session.
- uri (TEXT): The specific URL path visited.
- event_type (TEXT): Type of interaction (e.g., 'product', 'department', 'cart', 'purchase').
"""
