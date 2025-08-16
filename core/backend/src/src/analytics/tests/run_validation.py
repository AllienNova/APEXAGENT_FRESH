#!/usr/bin/env python3
"""
Validation runner for the Advanced Analytics system.

This script provides a standalone runner for the validation suite,
ensuring proper import paths and execution environment.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add the parent directory to sys.path to allow absolute imports
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the necessary modules using absolute imports
from analytics.analytics import AdvancedAnalytics
from analytics.tests.validation import AnalyticsValidator

def run_validation():
    """
    Run the validation suite and save the results to a file.
    
    Returns:
        Dict containing the validation results
    """
    logger.info("Initializing Advanced Analytics system for validation")
    analytics = AdvancedAnalytics()
    
    logger.info("Creating validator")
    validator = AnalyticsValidator(analytics)
    
    logger.info("Running comprehensive validation")
    results = validator.validate_all()
    
    # Generate timestamp for the report filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"analytics_validation_report_{timestamp}.json"
    report_path = os.path.join(os.path.dirname(__file__), report_filename)
    
    # Save results to file
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Validation results saved to {report_path}")
    
    # Print summary
    summary = results["summary"]
    logger.info(f"Validation complete: {summary['passed_tests']}/{summary['total_tests']} tests passed")
    logger.info(f"Success rate: {summary['success_rate'] * 100:.2f}%")
    logger.info(f"Overall status: {summary['status']}")
    
    return results

if __name__ == "__main__":
    run_validation()
