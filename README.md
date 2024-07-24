# Payment Processing System

This project is a comprehensive payment processing system that integrates multiple technologies such as FastAPI, Firebase, LiqPay and Aiogram to provide a seamless experience for handling payments and messages over Telegram.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [License](#license)

## Features
- **Payment Creation**: Users can create payments with specified amounts, currencies, and descriptions.
- **QR Code Generation**: Generate QR codes for payment using LiqPay.
- **Real-time Notifications**: Notify users via Telegram upon successful payment.
- **Payment Status Tracking**: Track and update payment statuses.
- **Firebase Integration**: Store and retrieve payment data using Firebase Firestore.

## Technologies Used
- **[FastAPI](https://fastapi.tiangolo.com/)**: A modern, fast (high-performance) web framework for building APIs with Python.
- **[Firebase](https://firebase.google.com/)**: A platform developed by Google for creating mobile and web applications, specifically Firestore for database and Firebase Storage for file storage.
- **[LiqPay](https://www.liqpay.ua/en)**: A payment platform for creating and managing payments, including QR code generation.
- **[Aiogram](https://docs.aiogram.dev/en/latest/)**: A framework for building Telegram bots with Python.

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/payment-processing-system.git
    cd payment-processing-system
    ```

2. Create a virtual environment and activate it:
    ```sh
    python3 -m venv env
    source env/bin/activate
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration
1. Create a `.env` file in the root directory and add the following environment variables:
    ```env
    TOKEN_TELEGRAM_BOT=your_telegram_bot_token
    FIREBASE_SERVICE_ACCOUNT_KEY=path_to_your_firebase_service_account_key.json
    STORAGE_BUCKET_URL=your_firebase_storage_bucket_url
    PUBLIC_LIQPAY_KEY=your_public_liqpay_key
    PRIVATE_LIQPAY_KEY=your_private_liqpay_key
    ```

2. Initialize Firebase with your service account key:
    ```python
    import firebase_admin
    from firebase_admin import credentials

    cred = credentials.Certificate("path/to/serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'your_storage_bucket_url'
    })
    ```

## Usage
1. Start the FastAPI server:
    ```sh
    uvicorn app.main:app --reload
    ```

2. Start the Telegram bot:
    ```sh
    python bot.py
    ```

## Endpoints

### Payment Endpoints
- **Get All Payments**: `GET /payments/all/info/`
- **Get Payment Details**: `GET /payments/info/{order_id}/detail/`
- **Create Payment**: `POST /payments/save/`
- **Webhook for Payment Status**: `POST /payments/webhook/`
- **Delete Payment**: `DELETE /payments/delete/{order_id}/`

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

### Example Usage with Aiogram

#### Bot Commands
- **/start**: Initiate the bot and provide a welcome message.
- **/create**: Start the payment creation process.
- **/cancel**: Cancel the current operation.

#### Creating a Payment
1. Use `/create` to start the payment creation process.
2. Enter the amount, currency, description, and QR code validity time when prompted.
3. The bot will generate a payment and provide a QR code link.

#### Payment Webhook
The webhook endpoint `/payments/webhook/` handles payment status updates from LiqPay and sends a notification via Telegram upon successful payment.

---

For more detailed information, refer to the source code.
