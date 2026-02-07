## 🛠️ Database Setup Guide

Follow these steps to initialize the PostgreSQL environment for this project. This ensures the **Database**, **User**, and **Schema** match the connection string:

`postgresql+psycopg://postgres:postgres@localhost/planet`

### 1. Access the PostgreSQL Terminal

Open your terminal and log in as the default superuser:

```bash
psql -U postgres
```

### 2. Create the Database

Inside the `psql` prompt, run the following to create the "bucket":

```sql
CREATE DATABASE planet;
```

### 3. Connect to the New Database

You must be **inside** the `planet` database to create a schema for it. Use the `\c` (connect) command:

```sql
\c planet
```

### 4. Create the Schema

Your SQLAlchemy models are configured to use the `planet` schema. Create it now:

```sql
CREATE SCHEMA planet;
```

### 5. Verify the Setup

Run these commands to ensure everything is mapped correctly:

* `\l` : You should see the `planet` database.
* `\dn` : You should see the `planet` schema listed.

---

## 🚀 Initialize Migrations

Once the database is ready, return to your project root and run your initial migration:

```bash
alembic upgrade head
```
