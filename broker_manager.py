"""
Broker Manager - Support for multiple brokers (Angel One, Zerodha, 5Paisa, etc.)
Phase 2: Multi-broker connectivity and management
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
import os


class BrokerType(Enum):
    """Supported broker types"""
    ANGEL_ONE = "angel_one"
    ZERODHA = "zerodha"
    FIVEPAISA = "5paisa"
    SHOONYA = "shoonya"
    ALICEBLUE = "aliceblue"
    TRADINGTODAY = "tradingtoday"


class BrokerConfig:
    """Broker configuration and credentials"""

    BROKER_DETAILS = {
        BrokerType.ANGEL_ONE: {
            "name": "Angel One",
            "display_name": "Angel One (SmartAPI)",
            "logo": "https://cdn.angel-broking.com/angel-one-logo.png",
            "required_fields": ["api_key", "client_code", "pin"],
            "optional_fields": ["totp_secret"],
            "base_url": "https://api.angelbroking.com",
            "supports": ["live_prices", "order_placement", "portfolio", "options"],
            "max_connections": 1,
            "documentation": "https://smartapi.angelbroking.com/docs"
        },
        BrokerType.ZERODHA: {
            "name": "Zerodha",
            "display_name": "Zerodha (Kite)",
            "logo": "https://zerodha.com/static/images/logo.svg",
            "required_fields": ["api_key", "api_secret"],
            "optional_fields": ["user_id"],
            "base_url": "https://api.kite.trade",
            "supports": ["live_prices", "order_placement", "portfolio", "options"],
            "max_connections": 1,
            "documentation": "https://kite.trade/docs/connect/v3/"
        },
        BrokerType.FIVEPAISA: {
            "name": "5Paisa",
            "display_name": "5Paisa Capital",
            "logo": "https://www.5paisa.com/assets/5paisa_logo.png",
            "required_fields": ["client_code", "password", "dob"],
            "optional_fields": [],
            "base_url": "https://api.5paisa.com",
            "supports": ["live_prices", "order_placement", "portfolio"],
            "max_connections": 1,
            "documentation": "https://5paisa.com/api-documentation"
        },
        BrokerType.SHOONYA: {
            "name": "Shoonya",
            "display_name": "Shoonya (ShoonyaAPI)",
            "logo": "https://shoonya.finvasia.com/assets/shoonya-logo.png",
            "required_fields": ["userid", "password"],
            "optional_fields": ["api_key"],
            "base_url": "https://api.shoonya.com",
            "supports": ["live_prices", "order_placement", "portfolio"],
            "max_connections": 1,
            "documentation": "https://shoonya.finvasia.com/api-docs"
        }
    }

    @staticmethod
    def get_broker_info(broker_type: BrokerType) -> Dict:
        """Get broker configuration"""
        return BrokerConfig.BROKER_DETAILS.get(broker_type)

    @staticmethod
    def get_required_fields(broker_type: BrokerType) -> List[str]:
        """Get required fields for broker"""
        config = BrokerConfig.get_broker_info(broker_type)
        return config.get("required_fields", []) if config else []

    @staticmethod
    def validate_credentials(broker_type: BrokerType, credentials: Dict) -> tuple:
        """Validate broker credentials format"""
        required = BrokerConfig.get_required_fields(broker_type)

        for field in required:
            if field not in credentials or not credentials[field]:
                return False, f"Missing required field: {field}"

        # Additional validations
        if broker_type == BrokerType.ANGEL_ONE:
            if len(credentials.get("pin", "")) != 4:
                return False, "PIN must be 4 digits"

        if broker_type == BrokerType.FIVEPAISA:
            if len(credentials.get("dob", "")) != 10:  # DD-MM-YYYY
                return False, "DOB format must be DD-MM-YYYY"

        return True, "Valid"


class BrokerConnection:
    """Manage broker connections"""

    def __init__(self, broker_type: BrokerType, credentials: Dict):
        self.broker_type = broker_type
        self.credentials = credentials
        self.is_authenticated = False
        self.last_tested = None
        self.last_error = None

    def connect(self) -> bool:
        """Establish connection with broker"""
        try:
            # Validate credentials first
            is_valid, msg = BrokerConfig.validate_credentials(self.broker_type, self.credentials)
            if not is_valid:
                self.last_error = msg
                return False

            # Route to appropriate broker handler
            if self.broker_type == BrokerType.ANGEL_ONE:
                return self._connect_angel_one()
            elif self.broker_type == BrokerType.ZERODHA:
                return self._connect_zerodha()
            elif self.broker_type == BrokerType.FIVEPAISA:
                return self._connect_5paisa()
            elif self.broker_type == BrokerType.SHOONYA:
                return self._connect_shoonya()

            self.last_error = "Broker not supported"
            return False

        except Exception as e:
            self.last_error = str(e)
            return False

    def _connect_angel_one(self) -> bool:
        """Connect to Angel One broker"""
        try:
            # Import and initialize Angel One connection
            from market_data import AngelOneMarketData

            api_key = self.credentials.get("api_key")
            client_code = self.credentials.get("client_code")
            pin = self.credentials.get("pin")
            totp_secret = self.credentials.get("totp_secret", "")

            market = AngelOneMarketData(api_key, client_code, pin, totp_secret)
            self.is_authenticated = market.is_authenticated()
            self.last_tested = datetime.utcnow()

            if self.is_authenticated:
                self.last_error = None
                return True
            else:
                self.last_error = "Authentication failed"
                return False

        except Exception as e:
            self.last_error = str(e)
            return False

    def _connect_zerodha(self) -> bool:
        """Connect to Zerodha Kite API"""
        try:
            # Placeholder for Zerodha connection
            # In production, use: from kiteconnect import KiteConnect
            self.last_error = "Zerodha integration coming in Q3 2026"
            return False
        except Exception as e:
            self.last_error = str(e)
            return False

    def _connect_5paisa(self) -> bool:
        """Connect to 5Paisa API"""
        try:
            # Placeholder for 5Paisa connection
            self.last_error = "5Paisa integration coming in Q3 2026"
            return False
        except Exception as e:
            self.last_error = str(e)
            return False

    def _connect_shoonya(self) -> bool:
        """Connect to Shoonya API"""
        try:
            # Placeholder for Shoonya connection
            self.last_error = "Shoonya integration coming in Q3 2026"
            return False
        except Exception as e:
            self.last_error = str(e)
            return False

    def disconnect(self):
        """Close broker connection"""
        self.is_authenticated = False

    def test_connection(self) -> bool:
        """Test broker connectivity"""
        return self.connect()

    def get_status(self) -> Dict:
        """Get connection status"""
        return {
            "broker": self.broker_type.value,
            "is_connected": self.is_authenticated,
            "last_tested": self.last_tested.isoformat() if self.last_tested else None,
            "last_error": self.last_error
        }


class BrokerManager:
    """Manage user's broker connections"""

    def __init__(self):
        self.connections = {}

    def add_connection(self, broker_type: BrokerType, credentials: Dict, name: str = None) -> tuple:
        """Add new broker connection"""
        try:
            connection = BrokerConnection(broker_type, credentials)
            is_connected = connection.connect()

            if not is_connected:
                return False, connection.last_error

            key = name or broker_type.value
            self.connections[key] = connection

            return True, f"Connected to {broker_type.value}"

        except Exception as e:
            return False, str(e)

    def get_connection(self, broker_type: BrokerType) -> Optional[BrokerConnection]:
        """Get active connection for broker"""
        key = broker_type.value
        connection = self.connections.get(key)

        if connection and connection.is_authenticated:
            return connection

        return None

    def list_connections(self) -> List[Dict]:
        """List all connections"""
        return [
            {
                "broker": conn.broker_type.value,
                "status": conn.get_status()
            }
            for conn in self.connections.values()
        ]

    def remove_connection(self, broker_type: BrokerType) -> bool:
        """Remove broker connection"""
        key = broker_type.value
        if key in self.connections:
            self.connections[key].disconnect()
            del self.connections[key]
            return True
        return False

    def get_primary_broker(self) -> Optional[BrokerConnection]:
        """Get primary broker connection (Angel One preferred)"""
        # Check Angel One first
        connection = self.get_connection(BrokerType.ANGEL_ONE)
        if connection:
            return connection

        # Return any active connection
        for conn in self.connections.values():
            if conn.is_authenticated:
                return conn

        return None


class BrokerAPIFactory:
    """Factory for broker-specific API implementations"""

    @staticmethod
    def get_market_data_api(broker_type: BrokerType, credentials: Dict):
        """Get market data API for broker"""
        if broker_type == BrokerType.ANGEL_ONE:
            from market_data import AngelOneMarketData
            return AngelOneMarketData(
                credentials.get("api_key"),
                credentials.get("client_code"),
                credentials.get("pin"),
                credentials.get("totp_secret", "")
            )

        # Other brokers would return their respective API implementations
        raise NotImplementedError(f"Market data API not implemented for {broker_type.value}")

    @staticmethod
    def get_order_api(broker_type: BrokerType, credentials: Dict):
        """Get order execution API for broker"""
        # Order API implementations would go here
        raise NotImplementedError(f"Order API not implemented for {broker_type.value}")

    @staticmethod
    def get_portfolio_api(broker_type: BrokerType, credentials: Dict):
        """Get portfolio management API for broker"""
        # Portfolio API implementations would go here
        raise NotImplementedError(f"Portfolio API not implemented for {broker_type.value}")


class BrokerStats:
    """Track broker usage and performance"""

    @staticmethod
    def get_broker_list() -> List[Dict]:
        """Get list of supported brokers"""
        brokers = []
        for broker_type, config in BrokerConfig.BROKER_DETAILS.items():
            brokers.append({
                "id": broker_type.value,
                "name": config["display_name"],
                "logo": config["logo"],
                "supports": config["supports"],
                "documentation": config["documentation"],
                "available": True if broker_type == BrokerType.ANGEL_ONE else False
            })
        return brokers

    @staticmethod
    def get_broker_support() -> Dict:
        """Get supported brokers with features"""
        return {
            "total_supported": len(BrokerType),
            "brokers": BrokerStats.get_broker_list(),
            "roadmap": {
                "phase_2": ["zerodha", "5paisa"],
                "phase_3": ["shoonya", "aliceblue", "tradingtoday"]
            }
        }


if __name__ == "__main__":
    print("✅ Broker manager module ready")
    print("\nSupported Brokers:")
    for broker in BrokerStats.get_broker_list():
        status = "✅" if broker["available"] else "⏳"
        print(f"  {status} {broker['name']}")
