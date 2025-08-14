"""
Video and Visual Support Validation Runner

This script runs the comprehensive validation tests for the Dr. TARDIS
video and visual support components and generates a detailed report.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_video_validation import VideoSupportValidator

async def run_validation_with_report():
    """Run validation tests and generate a detailed report."""
    print("Starting comprehensive validation of Dr. TARDIS video and visual support components...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    start_time = time.time()
    
    # Create validator
    validator = VideoSupportValidator()
    
    try:
        # Run validation
        results = await validator.validate_all()
    except Exception as e:
        # Handle validation failures gracefully
        print(f"Validation failed with error: {str(e)}")
        results = {
            "success": False,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "success_rate": 0.0,
            "error": str(e),
            "components": {},
            "results": []
        }
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Ensure all required fields exist in results
    if "success" not in results:
        results["success"] = False
    if "total_tests" not in results:
        results["total_tests"] = 0
    if "passed_tests" not in results:
        results["passed_tests"] = 0
    if "failed_tests" not in results:
        results["failed_tests"] = 0
    if "success_rate" not in results:
        if results["total_tests"] > 0:
            results["success_rate"] = results["passed_tests"] / results["total_tests"]
        else:
            results["success_rate"] = 0.0
    if "components" not in results:
        results["components"] = {}
    if "results" not in results:
        results["results"] = []
    
    # Save results to JSON file
    results_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "video_validation_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate HTML report
    html_report = generate_html_report(results, duration)
    
    # Save HTML report
    report_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "video_validation_report.html")
    with open(report_file, "w") as f:
        f.write(html_report)
    
    # Print summary
    print("\nValidation Summary:")
    print(f"Total tests: {results['total_tests']}")
    print(f"Passed tests: {results['passed_tests']}")
    print(f"Failed tests: {results['failed_tests']}")
    print(f"Success rate: {results['success_rate']*100:.1f}%")
    print(f"Overall result: {'PASSED' if results['success'] else 'FAILED'}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"\nDetailed results saved to: {results_file}")
    print(f"HTML report saved to: {report_file}")
    print("-" * 80)
    
    return results, report_file

def generate_html_report(results, duration):
    """Generate an HTML report from validation results."""
    # Get timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create a simple HTML report
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Dr. TARDIS Video Support Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .success {{ color: green; font-weight: bold; }}
        .failure {{ color: red; font-weight: bold; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Dr. TARDIS Video Support Validation Report</h1>
    <p>Generated on: {timestamp}</p>
    
    <h2>Validation Summary</h2>
    <p><strong>Overall Result:</strong> 
       <span class="{'success' if results.get('success', False) else 'failure'}">
           {results.get('success_rate', 0.0)*100:.1f}% - {'PASSED' if results.get('success', False) else 'FAILED'}
       </span>
    </p>
    <p><strong>Total Tests:</strong> {results.get('total_tests', 0)}</p>
    <p><strong>Passed Tests:</strong> {results.get('passed_tests', 0)}</p>
    <p><strong>Failed Tests:</strong> {results.get('failed_tests', 0)}</p>
    <p><strong>Duration:</strong> {duration:.2f} seconds</p>
    
    <h2>Component Results</h2>
    <table>
        <tr>
            <th>Component</th>
            <th>Success Rate</th>
            <th>Passed/Total</th>
        </tr>
"""
    
    # Add component results
    for component_name, component_data in results.get('components', {}).items():
        total = component_data.get('total', 0)
        passed = component_data.get('passed', 0)
        success_rate = passed / total if total > 0 else 0
        html += f"""
        <tr>
            <td>{component_name}</td>
            <td class="{'success' if success_rate >= 0.95 else 'failure'}">{success_rate*100:.1f}%</td>
            <td>{passed}/{total}</td>
        </tr>"""
    
    html += """
    </table>
</body>
</html>
"""
    
    return html

if __name__ == "__main__":
    results, report_file = asyncio.run(run_validation_with_report())
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)
