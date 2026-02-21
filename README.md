# 📡 Nexus Bridge – Offline Local Network File Sharing System

Nexus Bridge is an offline file sharing system that allows file transfer between:

Laptop ↔ Phone  
PC ↔ Phone  
Laptop ↔ Laptop  
PC ↔ PC  

using a local network (Wi-Fi / Hotspot) and a web browser.

It does NOT use:
❌ Internet  
❌ Bluetooth  
❌ USB cable  

It works using a Python-based local server and a browser interface.

---

## 🎯 Project Objective

To design and implement an offline file sharing system that:
- Works without internet
- Uses local network (LAN)
- Allows browsing and downloading files from another device
- Supports folder navigation
- Provides a simple web interface
- Is platform independent (Windows, Android, Linux)

---

## 🧠 Problem Statement

Traditional file sharing methods such as USB cables and Bluetooth are:
- Slow
- Require physical connection
- Limited by OS compatibility
- Not suitable for fast large file sharing

There is a need for a:
- Wireless
- Offline
- Simple
- Secure
file sharing solution for nearby devices.

---

## 💡 Proposed Solution

Nexus Bridge creates a local web server on one device (laptop/PC).  
Other devices (phone or PC) connect through a browser using the IP address.

Features:
- File browsing
- File download
- Folder access
- ZIP folder download
- Login authentication
- Works fully offline

---

## ⚙️ Technologies Used

- Python 3
- HTTP Server
- HTML, CSS
- Local Wi-Fi / Hotspot
- Browser (Chrome, Edge, etc.)

---

## 🧩 System Architecture

Sender Device (Laptop / PC):
- Runs Python server
- Shares a selected folder/drive

Receiver Device (Phone / PC):
- Connects using browser
- Enters IP address
- Downloads required files

Communication uses:
- HTTP protocol
- Local IP address
- TCP sockets

---

## 🚀 How to Run the Project

### Step 1: Install Python
Install Python 3 from:
https://www.python.org

---

### Step 2: Run the server

Double click your Python file  
OR  
Right click → Open with Python

It will ask:
Enter drive or folder to share  
Example:
C:/Users  
D:/ (Any folder) 
E:/ " " " " " "

---

### Step 3: Get IP Address

The program will show something like:
http://192.168.1.5:8000

---

### Step 4: Connect from phone or other PC

1. Connect both devices to same Wi-Fi or hotspot
2. Open browser in phone
3. Type:
http://<laptop-ip>:8000  
Example:
http://192.168.1.5:8000

---

## 🔐 Login Details

Default login:
Username: admin  
Password: nexus123  

---

## 📂 Features Implemented

✔ Folder browsing  
✔ File downloading  
✔ ZIP folder download  
✔ Login authentication  
✔ QR code for quick access  
✔ Responsive UI  
✔ Works without internet 
✔ Drive selection  
✔ Multi-device access  

---

## 📊 Comparison with Existing Apps

| Feature | ShareIt / Xender | Nexus Bridge |
|--------|------------------|--------------|
| Internet needed | Sometimes | ❌ No |
| App install | Required | ❌ No (browser) |
| Works on PC | Limited | ✔ Yes |
| Offline mode | Partial | ✔ Full |
| Platform independent | ❌ | ✔ |
| Customizable | ❌ | ✔ |

---

## 🆕 Uniqueness of the Project

- Browser-based file sharing
- No third-party app required
- Fully offline
- Cross-device support
- Simple Python backend
- Educational implementation

---

## 🔮 Future Enhancements

- File upload from phone to laptop
- Drag and drop upload
- Multi-file download
- Encryption
- Progress bar
- Android app wrapper
- QR code auto connect
- Device list auto detect

---

## 📜 License

MIT License  
You are free to:
- Use
- Modify
- Share
- Improve

---

## 🧑‍💻 Developer

Name: Sri Mano Bala N  
Project: Nexus Bridge  
Type: Academic Project  
Category: Networking / File Sharing  

---

## 📌 Project Status

Current Stage:
Laptop → Phone file access completed  

Next Stage:
Phone → Laptop  
Phone → Phone  
PC → PC  

---

## 🏁 Conclusion

Nexus Bridge demonstrates how local network and browser technology can be used to build a fast, offline, cross-platform file sharing system without relying on internet or proprietary apps.

It is suitable for:
- Students
- Offline environments
- Labs
- File sharing in classrooms
- Emergency data transfer

---

⭐ If you like this project, give it a star on GitHub!
