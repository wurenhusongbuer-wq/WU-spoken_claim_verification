"""
Database Manager

Handles MySQL and InfluxDB connections and operations.

Author: Capstone Team
Date: 2024
"""

import os
import logging
import json
from typing import List, Dict, Optional, Any
from datetime import datetime

import mysql.connector
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger(__name__)


class MySQLManager:
    """Manages MySQL database operations."""
    
    def __init__(
        self,
        host: str = "localhost",
        user: str = "root",
        password: str = "",
        database: str = "claim_verification"
    ):
        """
        Initialize MySQL manager.
        
        Args:
            host: MySQL host
            user: MySQL user
            password: MySQL password
            database: Database name
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
        self.connect()
    
    def connect(self) -> bool:
        """
        Connect to MySQL database.
        
        Returns:
            True if connection successful
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            logger.info(f"Connected to MySQL database: {self.database}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MySQL database."""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from MySQL")
    
    def execute_query(self, query: str, params: tuple = None) -> bool:
        """
        Execute a query (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            logger.debug(f"Query executed successfully")
            return True
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            self.connection.rollback()
            return False
    
    def fetch_query(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Fetch results from a SELECT query.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            logger.debug(f"Fetched {len(results)} rows")
            return results
        except Exception as e:
            logger.error(f"Fetch query error: {str(e)}")
            return []
    
    def insert_claim(
        self,
        video_id: str,
        claim_text: str,
        claim_type: str,
        confidence: float
    ) -> Optional[int]:
        """
        Insert a claim into database.
        
        Args:
            video_id: Video identifier
            claim_text: Claim text
            claim_type: Type of claim
            confidence: Extraction confidence
            
        Returns:
            Claim ID or None if failed
        """
        query = """
        INSERT INTO claims (video_id, claim_text, claim_type, confidence, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (video_id, claim_text, claim_type, confidence, datetime.now())
        
        if self.execute_query(query, params):
            cursor = self.connection.cursor()
            cursor.execute("SELECT LAST_INSERT_ID()")
            claim_id = cursor.fetchone()[0]
            return claim_id
        return None
    
    def insert_verification(
        self,
        claim_id: int,
        label: str,
        confidence: float,
        explanation: str,
        citations: List[str]
    ) -> bool:
        """
        Insert verification result.
        
        Args:
            claim_id: Claim ID
            label: Verification label (true/false/uncertain)
            confidence: Verification confidence
            explanation: Explanation text
            citations: List of citations
            
        Returns:
            True if successful
        """
        query = """
        INSERT INTO verifications (claim_id, label, confidence, explanation, citations, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            claim_id,
            label,
            confidence,
            explanation,
            json.dumps(citations),
            datetime.now()
        )
        
        return self.execute_query(query, params)
    
    def get_claims_by_video(self, video_id: str) -> List[Dict]:
        """
        Get all claims for a video.
        
        Args:
            video_id: Video identifier
            
        Returns:
            List of claim dictionaries
        """
        query = "SELECT * FROM claims WHERE video_id = %s"
        return self.fetch_query(query, (video_id,))
    
    def get_verification_by_claim(self, claim_id: int) -> Optional[Dict]:
        """
        Get verification for a claim.
        
        Args:
            claim_id: Claim ID
            
        Returns:
            Verification dictionary or None
        """
        query = "SELECT * FROM verifications WHERE claim_id = %s"
        results = self.fetch_query(query, (claim_id,))
        return results[0] if results else None


class InfluxDBManager:
    """Manages InfluxDB operations for time-series metrics."""
    
    def __init__(
        self,
        url: str = "http://localhost:8086",
        token: str = "",
        org: str = "capstone",
        bucket: str = "metrics"
    ):
        """
        Initialize InfluxDB manager.
        
        Args:
            url: InfluxDB URL
            token: InfluxDB token
            org: Organization name
            bucket: Bucket name
        """
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client = None
        self.write_api = None
        
        self.connect()
    
    def connect(self) -> bool:
        """
        Connect to InfluxDB.
        
        Returns:
            True if connection successful
        """
        try:
            self.client = InfluxDBClient(
                url=self.url,
                token=self.token,
                org=self.org
            )
            self.write_api = self.client.write_api(write_type=SYNCHRONOUS)
            logger.info(f"Connected to InfluxDB: {self.url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from InfluxDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from InfluxDB")
    
    def write_metric(
        self,
        measurement: str,
        tags: Dict[str, str],
        fields: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Write a metric to InfluxDB.
        
        Args:
            measurement: Measurement name
            tags: Tag dictionary
            fields: Field dictionary
            timestamp: Optional timestamp
            
        Returns:
            True if successful
        """
        try:
            from influxdb_client.client.write_api import Point
            
            point = Point(measurement)
            
            for tag_key, tag_value in tags.items():
                point.tag(tag_key, tag_value)
            
            for field_key, field_value in fields.items():
                point.field(field_key, field_value)
            
            if timestamp:
                point.time(timestamp)
            
            self.write_api.write(bucket=self.bucket, record=point)
            logger.debug(f"Metric written: {measurement}")
            return True
        except Exception as e:
            logger.error(f"Error writing metric: {str(e)}")
            return False
    
    def write_latency_metric(
        self,
        component: str,
        latency_ms: float,
        status: str = "success"
    ) -> bool:
        """
        Write latency metric.
        
        Args:
            component: Component name
            latency_ms: Latency in milliseconds
            status: Status (success/error)
            
        Returns:
            True if successful
        """
        return self.write_metric(
            measurement="latency",
            tags={"component": component, "status": status},
            fields={"value": latency_ms}
        )
    
    def write_throughput_metric(
        self,
        component: str,
        items_processed: int
    ) -> bool:
        """
        Write throughput metric.
        
        Args:
            component: Component name
            items_processed: Number of items processed
            
        Returns:
            True if successful
        """
        return self.write_metric(
            measurement="throughput",
            tags={"component": component},
            fields={"items": items_processed}
        )
    
    def write_token_usage(
        self,
        service: str,
        input_tokens: int,
        output_tokens: int,
        cost: float
    ) -> bool:
        """
        Write token usage metric.
        
        Args:
            service: Service name (e.g., "gemini", "openai")
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            cost: Cost in USD
            
        Returns:
            True if successful
        """
        return self.write_metric(
            measurement="token_usage",
            tags={"service": service},
            fields={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost
            }
        )
