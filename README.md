# MicroMart: A Modern E-commerce Platform

MicroMart is a full-stack e-commerce application designed to deliver a seamless shopping experience. It features a robust Django REST Framework backend for managing products, user authentication, shopping carts, and orders, paired with a responsive Flutter frontend for mobile and web platforms.

## 🚀 Tech Stack

### Backend

- **Framework**: Django 5.x
- **API**: Django REST Framework (DRF)
- **Authentication**: DRF Simple JWT (JWT-based)
- **API Documentation**: drf-spectacular (OpenAPI 3 / Swagger UI)
- **Filtering & Searching**: django-filter
- **Database**: SQLite (development)
- **Environment Variables**: python-dotenv

### Frontend

- **Framework**: Flutter 3.x (Dart)
- **State Management**: Provider
- **Networking**: http package
- **JWT Handling**: jwt_decoder
- **Local Storage**: shared_preferences

## ✨ Features

- **User Authentication**: Secure registration, login, and JWT token management (access & refresh tokens).
- **Product Catalog**: Browse products with search, filtering (price, stock), and sorting options.
- **Admin Product Management**: Create, update, and delete products (admin-only).
- **Shopping Cart**: Add, adjust, remove, or clear items in a user-specific cart.
- **Order Management**: Place orders, view order history, and manage stock levels.
- **Responsive Design**: Adapts seamlessly across mobile and web platforms.
- **API Documentation**: Interactive Swagger UI for API exploration.

## ⚙️ Setup Instructions

Follow these steps to set up and run MicroMart locally.

### Prerequisites

- Python 3.9+
- Flutter SDK (Stable Channel)
- Git

### 📦 Backend Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Eyiladeogo/MicroMart
   cd MicroMart-backend
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   ```

   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:

   - Create a `.env` file from the `.env.example` in the `MicroMart-backend` directory:
     ```env
     # Your computer's local IP address (e.g., from `ipconfig` or `ifconfig`)
     # This is crucial for your physical mobile device to connect.
     DEVICE_IP=192.168.X.X
     ```
   - Replace `192.168.X.X` with your local IP (e.g., from `ipconfig` or `ifconfig`).

5. **Apply database migrations**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser** (for admin access):

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
   - API accessible at: `http://localhost:8000/api/v1/`

### 📱 Frontend Setup

1. **Navigate to the frontend directory**:

   ```bash
   cd ../micromart_frontend
   ```

2. **Install Flutter dependencies**:

   ```bash
   flutter pub get
   ```

3. **Configure base URL environment variable for Flutter**:

   - Create a `.env` file in the Flutter project root:

   ```
    # Your backend's base URL.
    # Use your computer's actual IP for physical devices.
    # Use 10.0.2.2 for Android Emulator.
    # Use localhost or 127.0.0.1 for iOS Simulator/Flutter Web.
    FLUTTER_BASE_URL=http://192.168.X.X:8000/api/v1
   ```

4. **Run the Flutter app**:
   ```bash
   flutter run
   ```
   _Note_: Ensure a device or emulator is connected.

## 📊 API Endpoints

Explore the API via Swagger UI at: `http://localhost:8000/api/schema/swagger-ui/`

### 1. Authentication

- **Register User**  
  `POST /api/v1/auth/register/`  
  Creates a new user account and returns JWT tokens.  
  **Request Body**:

  ```json
  {
    "username": "newuser",
    "email": "user@example.com",
    "password": "strongpassword123",
    "confirm_password": "strongpassword123",
    "first_name": "John",
    "last_name": "Doe"
  }
  ```

  **Response (201 Created)**:

  ```json
  {
    "username": "newuser",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "access": "eyJ...",
    "refresh": "eyJ..."
  }
  ```

- **Login User**  
  `POST /api/v1/auth/token/`  
  Authenticates a user and returns JWT tokens.  
  **Request Body**:

  ```json
  {
    "email": "user@example.com",
    "password": "strongpassword123"
  }
  ```

  **Response (200 OK)**:

  ```json
  {
    "access": "eyJ...",
    "refresh": "eyJ..."
  }
  ```

- **Refresh Token**  
  `POST /api/v1/auth/token/refresh/`  
  Obtains a new access token using a refresh token.  
  **Request Body**:
  ```json
  {
    "refresh": "eyJ..."
  }
  ```
  **Response (200 OK)**:
  ```json
  {
    "access": "eyJ..."
  }
  ```

### 2. Products

- **List Products**  
  `GET /api/v1/store/products/`  
  Retrieves a paginated product list with search, filtering, and sorting.  
  **Query Params**: `?page=1&page_size=10&search=laptop&ordering=-price`  
  **Response (200 OK)**:

  ```json
  {
    "count": 41,
    "next": "http://127.0.0.1:8000/api/v1/store/products/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Gaming Laptop",
        "description": "High-performance gaming laptop.",
        "price": "1500.00",
        "stock": 45,
        "image_url": "https://placehold.co/600x400/000000/FFFFFF?text=Laptop"
      }
    ]
  }
  ```

- **Retrieve Product**  
  `GET /api/v1/store/products/{id}/`  
  Fetches details for a specific product.  
  **Response (200 OK)**:

  ```json
  {
    "id": 1,
    "name": "Gaming Laptop",
    "description": "High-performance gaming laptop.",
    "price": "1500.00",
    "stock": 45,
    "image_url": "https://placehold.co/600x400/000000/FFFFFF?text=Laptop"
  }
  ```

- **Create Product** (Admin Only)  
  `POST /api/v1/store/products/`  
  Adds a new product.  
  **Request Body**:
  ```json
  {
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse.",
    "price": "25.99",
    "stock": 200,
    "image_url": "https://placehold.co/600x400/000000/FFFFFF?text=Mouse"
  }
  ```
  **Response (201 Created)**: (Same as request body with `id`)

### 3. Cart

- **Get Cart**  
  `GET /api/v1/store/cart/`  
  Retrieves the user’s cart with item details.  
  **Response (200 OK)**:

  ```json
  {
    "id": 3,
    "user": 4,
    "cart_items": [
      {
        "id": 6,
        "product_id": 23,
        "product_name": "Product A",
        "product_price": "120.00",
        "quantity": 1,
        "subtotal": "120.00"
      }
    ],
    "total_items": 1,
    "total_amount": "120.00",
    "created_at": "2025-07-31T13:13:44.992603Z",
    "updated_at": "2025-07-31T13:13:44.992603Z"
  }
  ```

- **Add/Update Cart Item**  
  `POST /api/v1/store/cart/add/`  
  Adds or updates a product in the cart.  
  **Request Body**:

  ```json
  {
    "product_id": 23,
    "quantity": 1
  }
  ```

  **Response (200 OK)**: (Updated cart object)

- **Adjust Cart Quantity**  
  `POST /api/v1/store/cart/adjust-quantity/`  
  Increments/decrements item quantity.  
  **Request Body**:

  ```json
  {
    "product_id": 23,
    "action": "increment", // or "decrement"
    "change_by": 1
  }
  ```

  **Response (200 OK)**:

  ```json
  {
    "message": "Quantity of Product A incremented to 2.",
    "cart": {
      /* Updated cart */
    }
  }
  ```

- **Remove Cart Item**  
  `PUT /api/v1/store/cart/remove/`  
  Removes a product from the cart.  
  **Request Body**:

  ```json
  {
    "product_id": 23
  }
  ```

  **Response (200 OK)**:

  ```json
  {
    "message": "Product A removed from cart.",
    "cart": {
      /* Updated cart */
    }
  }
  ```

- **Clear Cart**  
  `DELETE /api/v1/store/cart/clear/`  
  Empties the cart.  
  **Response (200 OK)**:
  ```json
  {
    "detail": "Cart cleared.",
    "cart": {
      /* Empty cart */
    }
  }
  ```

### 4. Orders

- **Place Order**  
  `POST /api/v1/store/orders/`  
  Creates an order from the cart, deducting stock.  
  **Request Body**: `{}` (Uses cart contents)  
  **Response (201 Created)**:

  ```json
  {
    "id": 1,
    "user": 4,
    "user_username": "testuser",
    "total_amount": "120.00",
    "status": "pending",
    "created_at": "2025-07-31T13:13:44.992603Z",
    "updated_at": "2025-07-31T13:13:44.992603Z",
    "order_items": [
      {
        "id": 1,
        "product": 23,
        "product_name": "Product A",
        "quantity": 1,
        "price_at_order": "120.00"
      }
    ]
  }
  ```

- **List Orders**  
  `GET /api/v1/store/orders/`  
  Lists user’s orders (all orders for admins).  
  **Response (200 OK)**: (Paginated order list)

- **Retrieve Order**  
  `GET /api/v1/store/orders/{id}/`  
  Fetches a specific order’s details.  
  **Response (200 OK)**: (Single order object)

## ⚠️ Known Limitations

- **Image Handling**: Uses placeholder URLs. No integrated image upload/storage solution.
- **Payment Gateway**: Order placement is simulated; no real payment integration.
- **User Roles**: Limited to admin (`is_staff`) and regular users. No granular RBAC.
