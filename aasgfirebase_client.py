"""
Firebase client for state management and real-time strategy tracking.
CRITICAL: This is the primary state management system per ecosystem constraints.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, db
    from firebase_admin.exceptions import FirebaseError
    FIREBASE_AVAILABLE = True
except ImportError:
    logging.warning("firebase_admin not available. Install with: pip install firebase-admin")
    FIREBASE_AVAILABLE = False

class FirebaseClient:
    """Firebase client for AASG state management"""
    
    def __init__(self, config):
        self.config = config
        self.app = None
        self.db = None
        self.firestore_client = None
        self._initialized = False
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize Firebase connection with error handling"""
        if not FIREBASE_AVAILABLE:
            logging.error("Firebase admin SDK not available")
            return
        
        if not self.config.firebase:
            logging.warning("Firebase config not provided")
            return
        
        try:
            # Initialize Firebase app
            cred = credentials.Certificate(self.config.firebase.credentials_path)
            self.app = firebase_admin.initialize_app(
                cred,
                {
                    'projectId': self.config.firebase.project_id,
                    'databaseURL': self.config.firebase.realtime_database_url
                } if self.config.firebase.realtime_database_url else None
            )
            
            # Initialize Firestore
            self.firestore_client = firestore.client()
            
            # Initialize Realtime Database if URL provided
            if self.config.firebase.realtime_database_url:
                self.db = db.reference('/')
            
            self._initialized = True
            logging.info("Firebase client initialized successfully")
            
        except FileNotFoundError as e: