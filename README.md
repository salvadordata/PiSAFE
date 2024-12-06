# PiSafe: A Raspberry Pi-Based Emergency Alert System

**PiSafe** is a robust, feature-rich **Emergency Alert System (EAS)** built for the Raspberry Pi platform. Designed to deliver critical alerts across multiple communication channels, PiSafe ensures that your emergency notifications are timely, reliable, and versatile.

---

## 🌟 Key Features

### 📡 Multi-Channel Alert Delivery
- **SMS Alerts**: Notify users instantly via text messages (Twilio).
- **Email Notifications**: Deliver alerts directly to inboxes (SMTP or SendGrid).
- **Push Notifications**: Send browser/mobile alerts via Firebase Cloud Messaging (FCM).
- **Voice Calls**: Automated emergency announcements via Twilio.
- **Social Media Integration**: Post alerts to Twitter and Facebook.
- **Desktop Alerts**: Broadcast notifications across a local network.

### 🖥️ Modern User Interface
- **Admin Dashboard**:
  - Real-time analytics (alert history, user activity, system uptime).
  - Centralized control panel for managing users and settings.
- **Responsive Design**:
  - Optimized for desktop, mobile, and tablet displays.
  - Built with Bootstrap 5 for a clean and modern look.
- **Customizable Themes**:
  - Light and dark modes.
  - Multi-language support (English, Spanish, French).

### 🛠️ Advanced System Management
- **Role-Based Access Control**:
  - Granular permissions for admin and user roles.
- **Audit Logs**:
  - Comprehensive tracking of user activity and triggered alerts.
- **Scheduled Alerts**:
  - Automate tests and drills in advance.
- **System Health Monitoring**:
  - Track uptime, CPU usage, and system performance metrics.

### 🔒 Security and Resilience
- **End-to-End Encryption**:
  - HTTPS-secured communication with SSL certificates.
- **IP Whitelisting**:
  - Restrict system access to specific trusted networks.
- **Incident Escalation**:
  - Unacknowledged alerts are automatically escalated to higher authorities.

---

## 📦 Installation

### Prerequisites
1. **Raspberry Pi 5 (32GB)** or equivalent hardware.
2. **Python 3.9+** installed on your system.
3. **Twilio Account** (for SMS and voice alerts).
4. **SMTP Server Credentials** (for email notifications).

### Steps
1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/PiSafe.git
   cd PiSafe

	2.	Install required libraries:

pip install -r requirements.txt


	3.	Generate SSL certificates:

openssl req -x509 -newkey rsa:2048 -keyout certs/server.key -out certs/server.crt -days 365 -nodes


	4.	Configure .env file:

TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_email_password
FCM_SERVER_KEY=your_firebase_key


	5.	Start the application:

python flask_server.py


	6.	Access the system in your browser:
	•	URL: https://<your-pi-ip>:5000

📖 Documentation

Visit our GitHub Pages site for detailed guides, examples, and API references:
	•	URL: https://.github.io/PiSafe/

🛠️ Contributing

We welcome contributions! Please follow our guidelines in CONTRIBUTING.md.
	1.	Fork this repository.
	2.	Create a new branch:

git checkout -b feature/your-feature


	3.	Submit a pull request.

⚖️ License

This project is licensed under the MIT License.

---

## **Additional Files**

### **1. GitHub Actions Workflow (`.github/workflows/deploy.yml`)**

```yaml
