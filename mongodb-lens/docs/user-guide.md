# MongoDB Lens MCP Server - User Guide

## Overview

MongoDB Lens provides a natural language interface to MongoDB databases through the Model Context Protocol (MCP). This guide will help you understand how to effectively use MongoDB Lens to work with your MongoDB databases.

```
+----------------+      +-------------------+      +------------------+
| MCP Client     |----->| MongoDB Lens MCP  |----->| MongoDB Database |
| (Claude, etc.) |<-----| Server            |<-----| Instance         |
+----------------+      +-------------------+      +------------------+
```

## Getting Started

### Basic Database Operations

1. **Listing Databases**
   ```
   "List all databases"
   "Show me the databases available"
   ```

2. **Selecting a Database**
   ```
   "Switch to the customers database"
   "Use database sales"
   ```

3. **Viewing Collections**
   ```
   "List all collections in this database"
   "What collections are available?"
   ```

4. **Examining Collection Structure**
   ```
   "Analyze the schema of the products collection"
   "Show me the structure of the orders collection"
   ```

## Querying Data

### Finding Documents

1. **Basic Queries**
   ```
   "Find the first 10 documents in the orders collection"
   "Show me orders with status 'pending'"
   ```

2. **Complex Queries**
   ```
   "Find customers from New York with more than 10 orders"
   "Get all products with price between $10 and $50 sorted by rating"
   ```

3. **Aggregation**
   ```
   "Calculate the average order amount by customer"
   "Group products by category and count them"
   ```

### Modifying Data

1. **Inserting Documents**
   ```
   "Insert a new product with name 'Wireless Headphones', price 99.99, and category 'Electronics'"
   ```

2. **Updating Documents**
   ```
   "Update all products in the 'Books' category to add a 'discount' field with value 0.1"
   ```

3. **Deleting Documents**
   ```
   "Delete all orders with status 'cancelled'"
   ```

## Advanced Features

### Performance Optimization

1. **Index Management**
   ```
   "Create an index on the email field in the customers collection"
   "List all indexes on the products collection"
   ```

2. **Query Optimization**
   ```
   "Explain the query to find orders with status 'pending'"
   "Analyze query patterns for the products collection"
   ```

### Special Queries

1. **Text Search**
   ```
   "Search for products containing 'wireless' in their description"
   ```

2. **Geospatial Queries**
   ```
   "Find stores within a 5km radius of coordinates [40.7128, -74.0060]"
   ```

## Example Workflows

### Data Analysis Workflow

```
+-----------------+     +-----------------+     +-----------------+
| List Collections|---->| Analyze Schema  |---->| Run Aggregation |
+-----------------+     +-----------------+     +-----------------+
                                |
                                v
                        +-----------------+
                        | Export Results  |
                        +-----------------+
```

1. "List all collections in the sales database"
2. "Analyze the schema of the transactions collection"
3. "Run an aggregation to calculate monthly sales by product category"
4. "Export the results as JSON"

### Database Maintenance Workflow

```
+-----------------+     +-----------------+     +-----------------+
| Check Statistics|---->| Analyze Queries |---->| Create Indexes  |
+-----------------+     +-----------------+     +-----------------+
                                |
                                v
                        +-----------------+
                        | Validate Results|
                        +-----------------+
```

1. "Get statistics for the customers collection"
2. "Analyze query patterns for the customers collection"
3. "Create an index on the lastName field in the customers collection"
4. "Explain a query for finding customers by lastName"

## Command Reference

### Database Commands

```
+------------------+------------------------------------------+
| Command          | Description                              |
+------------------+------------------------------------------+
| list-databases   | Show all available databases             |
+------------------+------------------------------------------+
| use-database     | Switch to a specific database            |
+------------------+------------------------------------------+
| create-database  | Create a new database                    |
+------------------+------------------------------------------+
| drop-database    | Delete a database                        |
+------------------+------------------------------------------+
```

### Collection Commands

```
+------------------+------------------------------------------+
| Command          | Description                              |
+------------------+------------------------------------------+
| list-collections | Show all collections in current DB       |
+------------------+------------------------------------------+
| create-collection| Create a new collection                  |
+------------------+------------------------------------------+
| drop-collection  | Delete a collection                      |
+------------------+------------------------------------------+
| validate-        | Check collection for inconsistencies     |
| collection       |                                          |
+------------------+------------------------------------------+
```

### Document Commands

```
+------------------+------------------------------------------+
| Command          | Description                              |
+------------------+------------------------------------------+
| find-documents   | Query documents in a collection          |
+------------------+------------------------------------------+
| count-documents  | Count documents matching criteria        |
+------------------+------------------------------------------+
| insert-document  | Add new document(s) to a collection      |
+------------------+------------------------------------------+
| update-document  | Modify existing documents                |
+------------------+------------------------------------------+
| delete-document  | Remove documents from a collection       |
+------------------+------------------------------------------+
```

## Tips and Best Practices

1. **Be Specific in Queries**
   - Include collection names
   - Specify fields when possible
   - Define limits for large collections

2. **Use Schema Analysis First**
   - Understand collection structure before querying
   - Use this information to formulate better queries

3. **Performance Considerations**
   - Use `explain-query` to understand performance
   - Create indexes for frequently queried fields
   - Use `count-documents` instead of loading all documents for simple counts
   - Set appropriate limits when not needing all results

4. **Working with Large Collections**
   - Always use limits and pagination
   - Consider using projections to return only needed fields
   - For bulk operations, process in batches

5. **Safety Practices**
   - Destructive operations (delete, drop) require confirmation
   - Use `validate-collection` to check for issues before critical operations
   - Consider creating indexes in the background for production databases
