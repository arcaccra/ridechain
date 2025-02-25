# RideChain - Decentralized Carpooling Platform

RideChain is a decentralized carpooling platform built using Django Rest Framework, leveraging Cardano's blockchain to create a transparent, secure, and flexible ride-sharing experience. It empowers users to interact directly without intermediaries, ensuring affordable transportation options tailored for cost-conscious economies like Ghana.

---
## 🌟 Features
- **Decentralized Carpooling**: Eliminate intermediaries with blockchain-powered direct interactions.
- **Driver Autonomy**: Drivers control routes, pricing, and schedules.
- **Passenger Flexibility**: Passengers select trips based on convenience and budget.
- **Transparent Pricing and Payments**: Smart contract-based payments ensure no hidden fees.
- **Blockchain-Powered Security**: Decentralized Identity (DID) solutions for secure user verification.
- **Low-Cost Transactions Using ADA**: Fast payments with minimal fees using Cardano's ADA token.

---
## 🌐 Architecture Overview
RideChain is designed using a microservices architecture to ensure scalability, security, and maintainability. The backend is developed using Django Rest Framework, integrated with Cardano blockchain for decentralized payments and smart contracts. The platform leverages Cardano's Plutus and Marlowe smart contracts for secure payment automation and DID (Decentralized Identity) for user verification.

### Key Components:
- **Backend (Django Rest Framework)**: Manages APIs, authentication, and business logic.
- **Blockchain Layer (Cardano)**: Facilitates decentralized payments, smart contracts, and identity verification.
- **Smart Contracts (Plutus and Marlowe)**: Ensure transparent and automated payments and reputation management.
- **Decentralized Identity (DID)**: Used for secure user authentication and verification.
- **Frontend (React/Next.js)**: User-facing interfaces for drivers and passengers (planned future integration).
- **Database (PostgreSQL)**: Stores user data, trip details, and transaction records.
- **Hosting (AWS/Heroku)**: For deployment, ensuring scalability and security.

---
## 🚀 Tech Stack
- **Backend**: Django Rest Framework
- **Blockchain Integration**: Cardano Blockchain
- **Smart Contracts**: Plutus and Marlowe
- **Security**: Decentralized Identity (DID)
- **Payment System**: Cardano's native ADA token

---
## 📁 Project Structure
The project is structured following Django's best practices, with a modular architecture to support scalability and maintainability.

```
ridechain/
│   manage.py             # Django management script
│   README.md              # Project Documentation
│   requirements.txt       # Python dependencies
│   .env                   # Environment variables (API keys, secrets)
│   .gitignore             # Git ignore settings
│
├── core/
│   ├── settings.py        # Django settings including Cardano integration
│   ├── urls.py            # URL routing for the platform
│   ├── wsgi.py            # WSGI configuration for deployment
│   └── asgi.py            # ASGI configuration for WebSockets (future expansion)
│
├── users/
│   ├── models.py          # User models including DID integration
│   ├── serializers.py     # Data serialization for API responses
│   ├── views.py           # API views for user actions (Registration, Login, DID Verification)
│   ├── urls.py            # User-specific URL routes
│   └── tests.py           # Unit tests for user-related features
│
├── trips/
│   ├── models.py          # Trip and booking models
│   ├── serializers.py     # Serialization for trip-related data
│   ├── views.py           # APIs for trip creation, booking, and payment
│   ├── urls.py            # URL routes for trip management
│   └── tests.py           # Unit tests for trip functionalities
│
└── payments/
    ├── models.py          # Payment and escrow models
    ├── serializers.py     # Data serialization for payment processes
    ├── views.py           # APIs for payment handling using Cardano's ADA
    ├── urls.py            # URL routes for payment and transaction management
    └── smart_contracts/   # Smart contracts for decentralized payments
```

The modular structure allows easy expansion, particularly with future plans to integrate real-time updates and WebSocket support.

---
```
ridechain/
│   manage.py
│   README.md
│   requirements.txt
│
├── core/
│   ├── settings.py      # Django settings including Cardano integration
│   ├── urls.py          # URL routing for the platform
│   └── wsgi.py          # WSGI configuration for deployment
│
├── users/
│   ├── models.py        # User models including DID integration
│   ├── serializers.py   # Data serialization for API responses
│   ├── views.py         # API views for user actions
│   └── urls.py          # User-specific URL routes
│
└── trips/
    ├── models.py        # Trip and booking models
    ├── serializers.py   # Serialization for trip-related data
    ├── views.py         # APIs for trip creation, booking, and payment
    └── urls.py          # URL routes for trip management
```

---
## 🔧 Installation & Setup
1. **Clone the Repository:**
```
git clone https://github.com/your-username/ridechain.git
cd ridechain
```
2. **Create and Activate Virtual Environment:**
```
python3 -m venv env
source env/bin/activate
```
3. **Install Dependencies:**
```
pip install -r requirements.txt
```
4. **Run Migrations:**
```
python manage.py makemigrations
python manage.py migrate
```
5. **Start Development Server:**
```
python manage.py runserver
```
6. **Access the platform:**
```
http://127.0.0.1:8000/
```

---
## 📄 API Documentation
The RideChain platform provides a comprehensive set of RESTful APIs built with Django Rest Framework. Detailed API documentation is available through the built-in browsable API interface and Swagger UI at `/api/docs/`.

### User Endpoints:
- **POST `/api/users/register/`** - Register a new user with DID integration.
- **POST `/api/users/login/`** - Authenticate users with secure DID verification.
- **GET `/api/users/profile/`** - Retrieve user profile data.
- **PUT `/api/users/profile/update/`** - Update user profile details.

### Trip Endpoints:
- **POST `/api/trips/create/`** - Create a new carpooling trip.
- **GET `/api/trips/list/`** - Browse available trips by location, time, and pricing.
- **POST `/api/trips/book/`** - Book a ride using ADA tokens.
- **PUT `/api/trips/update/`** - Update trip details (by driver only).
- **DELETE `/api/trips/cancel/`** - Cancel a booking or trip.

### Payment Endpoints:
- **POST `/api/payments/initiate/`** - Initiate payment with smart contract escrow.
- **GET `/api/payments/status/`** - Check payment status on Cardano blockchain.
- **POST `/api/payments/complete/`** - Complete payment upon trip completion.

### Security & Decentralized Identity (DID):
- **Decentralized Identity (DID)**: Secure authentication mechanism ensuring user privacy.
- **Smart Contract Escrow**: Funds are securely held in smart contracts until trip completion, ensuring transparent and trustworthy transactions.

Comprehensive API documentation and usage examples are available in the `docs/` directory.

---
- **User Endpoints**:
  - Registration, Login, DID Verification
  - User Profile Management
- **Trip Endpoints**:
  - Trip Creation, Listing, and Booking
  - Payment Integration using Cardano ADA
- **Payment and Security**:
  - Smart contract-based escrow payments
  - Decentralized Identity (DID) for secure user verification

API documentation is available through Django Rest Framework's browsable API interface at `/api/`.

---
## 📜 License
This project is licensed under the MIT License.

---
## 🤝 Contributing
We welcome contributions! Please read `CONTRIBUTING.md` for guidelines.

---
## 👥 Team & Acknowledgments
- **Project Lead**: [Your Name](https://linkedin.com)
- **Backend Developer**: Django Rest Framework & Cardano Integration
- **Blockchain Developer**: Smart Contracts & Security
- **Operations Manager**: Community Engagement & Local Support
- **Special Thanks**: Accra Resource Center for local support and user onboarding

---
## 📞 Contact
For any inquiries, please reach out to [Your Email].
