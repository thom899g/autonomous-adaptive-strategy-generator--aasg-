"""
Configuration module for AASG system with Firebase integration and exchange settings.
Architectural Choice: Centralized config with validation to prevent runtime errors.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

# Environment variable validation
class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class FirebaseConfig:
    """Firebase configuration with type safety"""
    project_id: str
    credentials_path: str
    firestore_collection: str = "aasg_strategies"
    realtime_database_url: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate Firebase configuration"""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Firebase credentials not found at {self.credentials_path}")
        if not self.project_id:
            raise ValueError("Firebase project ID is required")
        return True

@dataclass
class ExchangeConfig:
    """Exchange configuration with rate limiting"""
    name: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    rate_limit: int = 10  # requests per second
    symbols: list = field(default_factory=lambda: ["BTC/USDT", "ETH/USDT"])
    
    def validate(self) -> bool:
        """Validate exchange configuration"""
        valid_exchanges = ["binance", "coinbase", "kraken"]
        if self.name.lower() not in valid_exchanges:
            raise ValueError(f"Invalid exchange. Must be one of: {valid_exchanges}")
        return True

class AASGConfig:
    """Main configuration manager with error handling"""
    
    def __init__(self, env: str = "development"):
        self.env = Environment(env.lower())
        self.firebase: Optional[FirebaseConfig] = None
        self.exchanges: Dict[str, ExchangeConfig] = {}
        self.logging_level = logging.INFO
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize configuration from environment variables"""
        try:
            # Firebase configuration
            project_id = os.getenv("FIREBASE_PROJECT_ID")
            creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase_credentials.json")
            
            if not project_id:
                logging.warning("FIREBASE_PROJECT_ID not set. Firebase features disabled.")
            else:
                self.firebase = FirebaseConfig(
                    project_id=project_id,
                    credentials_path=creds_path
                )
                self.firebase.validate()
            
            # Exchange configurations
            exchange_names = os.getenv("EXCHANGES", "binance").split(",")
            for exchange in exchange_names:
                self.exchanges[exchange] = ExchangeConfig(name=exchange.strip())
                self.exchanges[exchange].validate()
            
            # Logging configuration
            log_level = os.getenv("LOG_LEVEL", "INFO").upper()
            self.logging_level = getattr(logging, log_level, logging.INFO)
            
            logging.info(f"AASG Config initialized for {self.env.value} environment")
            
        except Exception as e:
            logging.error(f"Configuration initialization failed: {str(e)}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return {
            "environment": self.env.value,
            "firebase": {
                "project_id": self.firebase.project_id if self.firebase else None,
                "credentials_path": self.firebase.credentials_path if self.firebase else None
            } if self.firebase else None,
            "exchanges": {name: config.__dict__ for name, config in self.exchanges.items()},
            "logging_level": self.logging_level
        }