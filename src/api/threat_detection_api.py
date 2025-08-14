"""
Flask API Backend for AI-Powered Threat Detection System
Provides REST endpoints for threat monitoring and tier management

Author: Aideon AI Team
Date: June 2025
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Import our threat detection system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.security.ai_threat_detection import (
    AIThreatDetectionEngine, 
    SecurityTier, 
    initialize_threat_detection,
    get_threat_engine
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global threat engine
threat_engine = None

@app.route('/api/security/initialize', methods=['POST'])
def initialize_security():
    """Initialize threat detection system with user tier"""
    global threat_engine
    
    try:
        data = request.get_json()
        tier_name = data.get('tier', 'basic').upper()
        
        # Validate tier
        try:
            tier = SecurityTier[tier_name]
        except KeyError:
            return jsonify({
                'error': f'Invalid tier: {tier_name}',
                'valid_tiers': [t.value for t in SecurityTier]
            }), 400
        
        # Initialize threat detection engine
        threat_engine = initialize_threat_detection(tier)
        
        return jsonify({
            'status': 'success',
            'message': f'Threat detection initialized with {tier.value} tier',
            'tier': tier.value,
            'features': threat_engine.get_tier_features()
        })
        
    except Exception as e:
        logger.error(f"Error initializing security: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/status', methods=['GET'])
def get_security_status():
    """Get current security system status"""
    global threat_engine
    
    if not threat_engine:
        return jsonify({'error': 'Threat detection not initialized'}), 400
    
    try:
        stats = threat_engine.get_threat_statistics()
        features = threat_engine.get_tier_features()
        
        return jsonify({
            'status': 'success',
            'statistics': stats,
            'features': features,
            'tier': threat_engine.user_tier.value
        })
        
    except Exception as e:
        logger.error(f"Error getting security status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/threats', methods=['GET'])
def get_threats():
    """Get recent threat detections"""
    global threat_engine
    
    if not threat_engine:
        return jsonify({'error': 'Threat detection not initialized'}), 400
    
    try:
        limit = request.args.get('limit', 10, type=int)
        threats = threat_engine.get_recent_threats(limit)
        
        # Convert threats to JSON-serializable format
        threats_data = []
        for threat in threats:
            threats_data.append({
                'threat_id': threat.threat_id,
                'threat_type': threat.threat_type.value,
                'threat_level': threat.threat_level.value,
                'file_path': threat.file_path,
                'process_name': threat.process_name,
                'network_connection': threat.network_connection,
                'description': threat.description,
                'confidence_score': threat.confidence_score,
                'timestamp': threat.timestamp.isoformat(),
                'status': threat.status,
                'mitigation_action': threat.mitigation_action,
                'metadata': threat.metadata
            })
        
        return jsonify({
            'status': 'success',
            'threats': threats_data,
            'count': len(threats_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting threats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/upgrade', methods=['POST'])
def upgrade_tier():
    """Upgrade user security tier"""
    global threat_engine
    
    if not threat_engine:
        return jsonify({'error': 'Threat detection not initialized'}), 400
    
    try:
        data = request.get_json()
        new_tier_name = data.get('tier', '').upper()
        
        # Validate tier
        try:
            new_tier = SecurityTier[new_tier_name]
        except KeyError:
            return jsonify({
                'error': f'Invalid tier: {new_tier_name}',
                'valid_tiers': [t.value for t in SecurityTier]
            }), 400
        
        old_tier = threat_engine.user_tier
        threat_engine.upgrade_tier(new_tier)
        
        return jsonify({
            'status': 'success',
            'message': f'Upgraded from {old_tier.value} to {new_tier.value}',
            'old_tier': old_tier.value,
            'new_tier': new_tier.value,
            'features': threat_engine.get_tier_features()
        })
        
    except Exception as e:
        logger.error(f"Error upgrading tier: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/tiers', methods=['GET'])
def get_tier_comparison():
    """Get comparison of all security tiers"""
    try:
        # Create temporary engines to get features for each tier
        tiers_comparison = {}
        
        for tier in SecurityTier:
            temp_engine = AIThreatDetectionEngine(tier)
            tiers_comparison[tier.value] = {
                'tier': tier.value,
                'features': temp_engine.get_tier_features(),
                'pricing': get_tier_pricing(tier)
            }
            temp_engine.stop_monitoring()
        
        return jsonify({
            'status': 'success',
            'tiers': tiers_comparison
        })
        
    except Exception as e:
        logger.error(f"Error getting tier comparison: {e}")
        return jsonify({'error': str(e)}), 500

def get_tier_pricing(tier: SecurityTier) -> Dict[str, Any]:
    """Get pricing information for a tier"""
    pricing = {
        SecurityTier.BASIC: {
            'monthly_price': 0,
            'annual_price': 0,
            'currency': 'USD',
            'trial_days': 0,
            'description': 'Free basic protection'
        },
        SecurityTier.PREMIUM: {
            'monthly_price': 9.99,
            'annual_price': 99.99,
            'currency': 'USD',
            'trial_days': 14,
            'description': 'Advanced AI-powered protection'
        },
        SecurityTier.ENTERPRISE: {
            'monthly_price': 29.99,
            'annual_price': 299.99,
            'currency': 'USD',
            'trial_days': 30,
            'description': 'Enterprise-grade security suite'
        }
    }
    
    return pricing.get(tier, pricing[SecurityTier.BASIC])

@app.route('/api/security/simulate-threat', methods=['POST'])
def simulate_threat():
    """Simulate a threat detection for demo purposes"""
    global threat_engine
    
    if not threat_engine:
        return jsonify({'error': 'Threat detection not initialized'}), 400
    
    try:
        data = request.get_json()
        threat_type = data.get('threat_type', 'malware')
        
        # This would trigger the detection system to simulate finding a threat
        # In a real system, this would be removed
        
        return jsonify({
            'status': 'success',
            'message': f'Simulated {threat_type} threat detection',
            'note': 'This is for demonstration purposes only'
        })
        
    except Exception as e:
        logger.error(f"Error simulating threat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Threat Detection API',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize with basic tier by default
    threat_engine = initialize_threat_detection(SecurityTier.BASIC)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)

