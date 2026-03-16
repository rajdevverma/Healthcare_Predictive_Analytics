-- Healthcare Predictive Analytics System - MySQL Schema
-- Ensure SQL Workbench compatible

CREATE DATABASE IF NOT EXISTS healthcare_db;
USE healthcare_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'doctor') DEFAULT 'doctor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Patients Table
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    medical_history TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX (created_by)
);

-- 3. Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20),
    patient_name VARCHAR(100),
    disease_type VARCHAR(50) NOT NULL,
    risk_percentage FLOAT NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    model_used VARCHAR(50) DEFAULT 'random_forest',
    input_features JSON NOT NULL,
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    predicted_by INT,
    FOREIGN KEY (predicted_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX (predicted_by),
    INDEX (patient_id)
);
