-- MySQL Database Initialization Script
-- Creates tables for claim verification system

CREATE DATABASE IF NOT EXISTS claim_verification;
USE claim_verification;

-- Videos table
CREATE TABLE IF NOT EXISTS videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    video_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500),
    source VARCHAR(100),
    url TEXT,
    duration_seconds INT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_video_id (video_id)
);

-- Claims table
CREATE TABLE IF NOT EXISTS claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    video_id VARCHAR(255) NOT NULL,
    claim_text TEXT NOT NULL,
    claim_type VARCHAR(50),
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(video_id),
    INDEX idx_video_id (video_id),
    INDEX idx_created_at (created_at)
);

-- Verifications table
CREATE TABLE IF NOT EXISTS verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    claim_id INT NOT NULL,
    label VARCHAR(50),
    confidence FLOAT,
    explanation TEXT,
    citations JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES claims(id),
    INDEX idx_claim_id (claim_id),
    INDEX idx_label (label)
);

-- Evidence table
CREATE TABLE IF NOT EXISTS evidence (
    id INT AUTO_INCREMENT PRIMARY KEY,
    claim_id INT NOT NULL,
    source_title VARCHAR(500),
    source_url TEXT,
    snippet TEXT,
    relevance_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES claims(id),
    INDEX idx_claim_id (claim_id)
);

-- Transcripts table
CREATE TABLE IF NOT EXISTS transcripts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    video_id VARCHAR(255) UNIQUE NOT NULL,
    transcript_text LONGTEXT,
    language VARCHAR(10),
    duration_seconds INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(video_id),
    INDEX idx_video_id (video_id)
);

-- Processing logs table
CREATE TABLE IF NOT EXISTS processing_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    video_id VARCHAR(255),
    component VARCHAR(100),
    status VARCHAR(50),
    message TEXT,
    latency_ms FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_video_id (video_id),
    INDEX idx_component (component),
    INDEX idx_created_at (created_at)
);

-- Evaluation metrics table
CREATE TABLE IF NOT EXISTS evaluation_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    metric_name VARCHAR(100),
    metric_value FLOAT,
    metric_type VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_metric_name (metric_name),
    INDEX idx_created_at (created_at)
);

-- Create indexes for common queries
CREATE INDEX idx_claims_video_type ON claims(video_id, claim_type);
CREATE INDEX idx_verifications_label ON verifications(label, confidence);
