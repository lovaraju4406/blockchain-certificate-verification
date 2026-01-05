🎓 Blockchain-Based Certificate Storage & Verification System

Welcome to the Blockchain-Based Certificate Storage & Verification System!
This project provides a secure and decentralized solution for issuing, storing, and verifying academic certificates using Blockchain (Ethereum) and IPFS, with a Django backend for application logic.

The system ensures certificate authenticity, prevents forgery, and allows instant verification using blockchain records.

--------------------------------------------------

✨ Features

🌟 Core Features:
- Secure Certificate Upload by Admin
- Certificate Storage on IPFS
- Blockchain-based Hash Storage (Ethereum)
- Public Certificate Verification
- Admin Control via Django Backend
- Media-based Certificate Management
- Web-based Interface using HTML Templates

--------------------------------------------------

🛠️ Tech Stack

Backend:
- Django (Python)
- SQLite (Development Database)

Blockchain:
- Ethereum (Local Test Network)
- Solidity (Smart Contracts)
- Truffle Framework
- Ganache

Decentralized Storage:
- IPFS (Helia)

Frontend:
- HTML
- CSS
- JavaScript

Tools:
- Node.js
- npm
- Conda (Python Environment)

--------------------------------------------------

🗂️ Project Folder Structure

project-root/
│
├── app/
│   ├── __pycache__/
│   ├── migrations/
│   ├── templates/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── logic.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── blocks/
│   ├── build/
│   │   └── contracts/
│   │       └── Store.json
│   ├── contracts/
│   │   └── Store.sol
│   ├── migrations/
│   │   └── 1_migrations.js
│   ├── test/
│   └── truffle-config.js
│
├── IPFS/
│   ├── node_modules/
│   ├── package.json
│   ├── package-lock.json
│   └── test.js
│
├── media/
│   └── certificates/
│       ├── cert_1_1766051890.pdf
│       ├── cert_2_1766056297.png
│       └── cert_3_1766056814.pdf
│
├── templates/
│   ├── base.html
│   └── index.html
│
├── .gitignore
├── db.sqlite3
└── manage.py

--------------------------------------------------

🚀 Quick Start Guide

Prerequisites:
- Git
- Python 3.9+
- Node.js
- npm
- Ganache
- Truffle
- Conda (recommended)

--------------------------------------------------

🔗 Step 1: Start Ganache

1. Open Ganache
2. Start a local Ethereum workspace
3. Keep Ganache running in the background

--------------------------------------------------

🖥️ Step 2: Run Django Backend (Terminal 1)

conda activate env
cd <PROJECT_ROOT_DIRECTORY>
pip install django web3
python manage.py runserver

Backend URL:
http://127.0.0.1:8000/

--------------------------------------------------

⛓️ Step 3: Compile & Deploy Smart Contracts

cd blocks
truffle compile
truffle migrate

--------------------------------------------------

🌐 Step 4: Run IPFS Server (Terminal 2)

cd <PROJECT_ROOT_DIRECTORY>/IPFS
npm install
node test.js

--------------------------------------------------

🔍 How Certificate Verification Works

1. Admin uploads a certificate
2. Certificate file is stored on IPFS
3. IPFS hash is generated
4. Hash is stored on Ethereum blockchain via smart contract
5. Transaction hash is saved in the system
6. Anyone can verify certificate authenticity using blockchain data

--------------------------------------------------

📌 Use Cases

- Universities & Colleges
- Educational Institutions
- Certification Authorities
- Employers for Background Verification

--------------------------------------------------

🔒 Advantages

- Eliminates certificate forgery
- Tamper-proof blockchain records
- Decentralized storage
- Transparent verification
- Secure and scalable system

--------------------------------------------------

📄 Future Enhancements

- QR-code based verification
- Public Ethereum deployment
- Role-based authentication
- React frontend integration
- Cloud deployment

--------------------------------------------------

📜 License

This project is developed for academic and educational purposes.
