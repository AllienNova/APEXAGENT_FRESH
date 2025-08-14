#!/usr/bin/env python3
"""
Diagnostic script to inspect how data protection is applied to PII and payment data.
This script will help diagnose why the validation tests are failing.
"""

import sys
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path to import analytics modules
sys.path.append('/home/ubuntu/agent_project/src')

from analytics.analytics import AdvancedAnalytics
from analytics.core.core import SecurityClassification

def main():
    """Run diagnostic tests for data protection."""
    logger.info("Starting data protection diagnostic tests")
    
    # Initialize analytics system
    analytics = AdvancedAnalytics()
    
    # Test 1: PII Data Protection
    logger.info("=== Testing PII Data Protection ===")
    
    # Create test PII data
    pii_data = {
        "email": "user@example.com",
        "phone": "555-123-4567",
        "address": "123 Main St",
        "name": "Test User",
        "age": 30
    }
    
    logger.info(f"Original PII data: {json.dumps(pii_data, indent=2)}")
    
    # Record event with PII data
    event_id = analytics.record_event(
        event_type="user_profile_update",
        event_data=pii_data,
        user_id="test_user"
    )
    
    logger.info(f"Recorded PII event with ID: {event_id}")
    
    # Retrieve the event and check for PII masking
    events = analytics.search_events(
        event_types=["user_profile_update"],
        user_id="test_user",
        limit=1
    )
    
    if events and len(events) > 0:
        event = events[0]
        logger.info(f"Retrieved PII event: {json.dumps(event, indent=2)}")
        
        # Check if PII fields are protected
        if "event_data" in event:
            event_data = event["event_data"]
            logger.info("PII Protection Analysis:")
            
            for field in ["email", "phone", "address"]:
                if field not in event_data:
                    logger.info(f"  - {field}: PROTECTED (field removed)")
                elif event_data[field].startswith("[REDACTED:") or event_data[field].startswith("HASH:"):
                    logger.info(f"  - {field}: PROTECTED ({event_data[field]})")
                else:
                    logger.info(f"  - {field}: NOT PROTECTED ({event_data[field]})")
            
            # Check validation test condition
            data_protected = (
                "email" not in event_data or 
                not event_data.get("email", "").startswith("user@") or
                "phone" not in event_data or
                not event_data.get("phone", "").startswith("555-") or
                "address" not in event_data or
                not event_data.get("address", "").startswith("123")
            )
            
            logger.info(f"Validation test would pass: {data_protected}")
    else:
        logger.error("No PII events found")
    
    # Test 2: Payment Data Protection
    logger.info("\n=== Testing Payment Data Protection ===")
    
    # Create test payment data
    payment_data = {
        "card_number": "4111-1111-1111-1111",
        "cvv": "123",
        "expiry": "12/25",
        "amount": 99.99,
        "currency": "USD"
    }
    
    logger.info(f"Original payment data: {json.dumps(payment_data, indent=2)}")
    
    # Record event with payment data
    event_id = analytics.record_event(
        event_type="payment_processed",
        event_data=payment_data,
        user_id="test_user"
    )
    
    logger.info(f"Recorded payment event with ID: {event_id}")
    
    # Retrieve the event and check for payment data masking
    events = analytics.search_events(
        event_types=["payment_processed"],
        user_id="test_user",
        limit=1
    )
    
    if events and len(events) > 0:
        event = events[0]
        logger.info(f"Retrieved payment event: {json.dumps(event, indent=2)}")
        
        # Check if payment fields are protected
        if "event_data" in event:
            event_data = event["event_data"]
            logger.info("Payment Data Protection Analysis:")
            
            for field in ["card_number", "cvv"]:
                if field not in event_data:
                    logger.info(f"  - {field}: PROTECTED (field removed)")
                elif event_data[field].startswith("[REDACTED:") or event_data[field].startswith("HASH:"):
                    logger.info(f"  - {field}: PROTECTED ({event_data[field]})")
                else:
                    logger.info(f"  - {field}: NOT PROTECTED ({event_data[field]})")
            
            # Check validation test condition
            data_protected = (
                "card_number" not in event_data or 
                not event_data.get("card_number", "").startswith("4111") or
                "cvv" not in event_data
            )
            
            logger.info(f"Validation test would pass: {data_protected}")
    else:
        logger.error("No payment events found")
    
    # Test 3: Direct Data Protection Integration Test
    logger.info("\n=== Testing Data Protection Integration Directly ===")
    
    # Test PII data protection directly
    protected_pii = analytics.data_protection_integration.protect_sensitive_data(
        pii_data, 
        SecurityClassification.RESTRICTED
    )
    
    logger.info(f"Directly protected PII data: {json.dumps(protected_pii, indent=2)}")
    
    # Test payment data protection directly
    protected_payment = analytics.data_protection_integration.protect_sensitive_data(
        payment_data, 
        SecurityClassification.RESTRICTED
    )
    
    logger.info(f"Directly protected payment data: {json.dumps(protected_payment, indent=2)}")
    
    # Test verification
    logger.info("\n=== Testing Data Protection Verification ===")
    
    try:
        pii_verified = analytics.data_protection_integration.verify_data_protection(
            protected_pii,
            SecurityClassification.RESTRICTED
        )
        logger.info(f"PII data protection verified: {pii_verified}")
    except Exception as e:
        logger.error(f"PII verification error: {str(e)}")
    
    try:
        payment_verified = analytics.data_protection_integration.verify_data_protection(
            protected_payment,
            SecurityClassification.RESTRICTED
        )
        logger.info(f"Payment data protection verified: {payment_verified}")
    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")

if __name__ == "__main__":
    main()
