# 📂 Rootine API Documentation

## 🔑 User Authentication

### **Sign Up / Registration**
**POST** `/api/users/register`
- Registers a new user by taking email and password.
- Creates a new user entry in the users collection.

### **Login**
**POST** `/api/users/login`
- Authenticates a user by checking the provided email and password.

### **Password Reset**
**POST** `/api/users/request-reset`
- Initiates a password reset process by verifying user email and sending a reset link.

**POST** `/api/users/reset-password`
- Resets the user's password using the link/token received in their email.

---

## 🌱 Plant Tracker

### **Plant Profile Creation**
**POST** `/api/new_plant`
- Creates a new plant profile linked to a user.

### **Update Plant Profile**
**PUT** `/api/plants/{plant_id}`
- Updates details of an existing plant profile.

### **Delete Plant Profile**
**DELETE** `/api/plants/{plant_id}`
- Deletes a plant profile.

### **List All Plants for a User**
**GET** `/api/users/{user_id}/plants`
- Retrieves all plant profiles associated with a user.

---

## 📊 Growth Tracking

### **Add Growth Metrics**
**POST** `/api/plants/{plant_id}/growth-metrics`
- Adds growth metric data to a plant profile.

---

## 🌿 Plant Disease Identifier

### **Image Upload and Disease Analysis**
**POST** `/api/plants/disease-analysis`
- Receives an image, processes it for disease identification, and returns possible issues and diagnoses.

### **Results Display**
**GET** `/api/plants/{plant_id}/diseases`
- Retrieves a list of diagnosed diseases for a specific plant.

---

## ⏰ Reminders

### **Set Reminder**
**POST** `/api/reminders`
- Creates a new reminder for a plant care task.

### **Update Reminder**
**PUT** `/api/reminders/{reminder_id}`
- Updates an existing reminder.

### **Delete Reminder**
**DELETE** `/api/reminders/{reminder_id}`
- Deletes a reminder.

### **List Reminders for a Plant**
**GET** `/api/plants/{plant_id}/reminders`
- Retrieves all reminders set for a specific plant.

---

## 🏡 Home Page

### **Home Page View**
**GET** `/api/users/{user_id}/home`
- Displays a summary view for the user's home page, including a list of plants and upcoming reminders.

---
