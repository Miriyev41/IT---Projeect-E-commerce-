VIZJA-TECH E-commerce Store
A professional Django-based e-commerce platform featuring product management, a shopping cart system, and order processing.

🚀 Features
• User Interface: Custom user model (`Account`) with email-based login.

• Store: Category and Product management with stock tracking.

• Cart: Add/remove items and quantity management.

• Checkout: Order placement with detailed billing information.

• Admin Dashboard: Seller interface to manage products and orders.

---

💻 Developer Cheat Sheet (New Owner Setup)
1. Environment Management

To activate your virtual environment (Run this first):

source env/Scripts/activate

```

2. Install Dependencies

To install Django and all necessary libraries on a new computer:

pip install -r requirements.txt

```

3. Database Migrations

To create the database tables and structure for the first time:

python manage.py migrate

```

4. Create Superuser

To create your Admin/Seller account to access the dashboard:

python manage.py createsuperuser

```

5. Run Server

To start the local development server:

python manage.py runserver

```

6. Django Shell

To enter the backend console for manual data management:

python manage.py shell

```


📁 Project Structure
📂 Accounts

`accounts/`: Custom user models, registration logic, and login authentication.

📂 Carts

`carts/`: Shopping cart logic, including adding items and session management.

📂 Category

`category/`: Database models for grouping products into searchable categories.

📂 Store

`store/`: The main catalog, product detail pages, and search functionality.

📂 Orders

`orders/`: Checkout processing, payment records, and order fulfillment.

📂 Media

`media/`: Folder containing all uploaded product images and assets.

📂 Templates

`templates/`: Global HTML files, including the base layout, navbar, and footer.
