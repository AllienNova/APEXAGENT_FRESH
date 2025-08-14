"""
Real-time Threat Detection and Monitoring System
Advanced threat detection with machine learning and behavioral analysis
"""

import logging
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict, deque
import redis
import hashlib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatDetectionEngine:
    """Advanced threat detection with machine learning and behavioral analysis"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=3, decode_responses=True)
        self.threat_patterns = self._load_threat_patterns()
        self.behavioral_baselines = {}
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        self.threat_scores = defaultdict(float)
        self.monitoring_active = True
        self.alert_thresholds = {
            'LOW': 0.3,
            'MEDIUM': 0.6,
            'HIGH': 0.8,
            'CRITICAL': 0.95
        }
        self.recent_events = deque(maxlen=10000)
        self._initialize_ml_models()
        self._start_monitoring_thread()
    
    def _load_threat_patterns(self) -> Dict[str, Any]:
        """Load comprehensive threat detection patterns"""
        return {
            'brute_force': {
                'failed_logins_threshold': 5,
                'time_window': 300,  # 5 minutes
                'severity': 'HIGH'
            },
            'dos_attack': {
                'requests_threshold': 1000,
                'time_window': 60,  # 1 minute
                'severity': 'CRITICAL'
            },
            'port_scanning': {
                'unique_ports_threshold': 10,
                'time_window': 60,
                'severity': 'HIGH'
            },
            'data_exfiltration': {
                'data_volume_threshold': 100 * 1024 * 1024,  # 100MB
                'time_window': 300,
                'severity': 'CRITICAL'
            },
            'privilege_escalation': {
                'admin_attempts_threshold': 3,
                'time_window': 600,
                'severity': 'CRITICAL'
            },
            'anomalous_behavior': {
                'deviation_threshold': 3.0,  # Standard deviations
                'severity': 'MEDIUM'
            }
        }
    
    def _initialize_ml_models(self):
        """Initialize machine learning models for anomaly detection"""
        try:
            # Try to load existing model
            model_path = '/tmp/aideon_anomaly_model.joblib'
            if os.path.exists(model_path):
                self.anomaly_detector = joblib.load(model_path)
                logger.info("Loaded existing anomaly detection model")
            else:
                # Create new model
                self.anomaly_detector = IsolationForest(
                    contamination=0.1,
                    random_state=42,
                    n_estimators=100
                )
                logger.info("Created new anomaly detection model")
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {str(e)}")
            self.anomaly_detector = None
    
    def _start_monitoring_thread(self):
        """Start background monitoring thread"""
        def monitor():
            while self.monitoring_active:
                try:
                    self._perform_periodic_analysis()
                    time.sleep(30)  # Run every 30 seconds
                except Exception as e:
                    logger.error(f"Monitoring thread error: {str(e)}")
                    time.sleep(60)  # Wait longer on error
        
        monitoring_thread = threading.Thread(target=monitor, daemon=True)
        monitoring_thread.start()
        logger.info("Started threat monitoring thread")
    
    def analyze_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze security event for threats
        
        Args:
            event: Security event to analyze
            
        Returns:
            Threat analysis results
        """
        analysis = {
            'event_id': event.get('id', hashlib.md5(str(event).encode()).hexdigest()[:8]),
            'timestamp': datetime.utcnow().isoformat(),
            'threat_detected': False,
            'threat_level': 'LOW',
            'threat_score': 0.0,
            'threat_types': [],
            'recommendations': [],
            'requires_action': False
        }
        
        try:
            # Add event to recent events
            self.recent_events.append(event)
            
            # Analyze different threat types
            brute_force_score = self._analyze_brute_force(event)
            dos_score = self._analyze_dos_attack(event)
            port_scan_score = self._analyze_port_scanning(event)
            data_exfil_score = self._analyze_data_exfiltration(event)
            privilege_esc_score = self._analyze_privilege_escalation(event)
            anomaly_score = self._analyze_behavioral_anomaly(event)
            
            # Calculate overall threat score
            threat_scores = {
                'brute_force': brute_force_score,
                'dos_attack': dos_score,
                'port_scanning': port_scan_score,
                'data_exfiltration': data_exfil_score,
                'privilege_escalation': privilege_esc_score,
                'behavioral_anomaly': anomaly_score
            }
            
            # Find maximum threat score
            max_score = max(threat_scores.values())
            analysis['threat_score'] = max_score
            
            # Determine threat level
            if max_score >= self.alert_thresholds['CRITICAL']:
                analysis['threat_level'] = 'CRITICAL'
                analysis['threat_detected'] = True
                analysis['requires_action'] = True
            elif max_score >= self.alert_thresholds['HIGH']:
                analysis['threat_level'] = 'HIGH'
                analysis['threat_detected'] = True
                analysis['requires_action'] = True
            elif max_score >= self.alert_thresholds['MEDIUM']:
                analysis['threat_level'] = 'MEDIUM'
                analysis['threat_detected'] = True
            elif max_score >= self.alert_thresholds['LOW']:
                analysis['threat_level'] = 'LOW'
            
            # Identify specific threat types
            for threat_type, score in threat_scores.items():
                if score > 0.3:  # Threshold for reporting
                    analysis['threat_types'].append({
                        'type': threat_type,
                        'score': score,
                        'severity': self._get_threat_severity(threat_type, score)
                    })
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(threat_scores, event)
            
            # Store analysis results
            self._store_threat_analysis(analysis)
            
            # Trigger alerts if necessary
            if analysis['requires_action']:
                self._trigger_security_alert(analysis, event)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Threat analysis error: {str(e)}")
            analysis['error'] = str(e)
            return analysis
    
    def _analyze_brute_force(self, event: Dict[str, Any]) -> float:
        """Analyze for brute force attack patterns"""
        try:
            if event.get('event_type') != 'login_failed':
                return 0.0
            
            source_ip = event.get('source_ip')
            if not source_ip:
                return 0.0
            
            # Count failed logins from this IP in time window
            current_time = datetime.utcnow()
            time_window = timedelta(seconds=self.threat_patterns['brute_force']['time_window'])
            
            failed_count = 0
            for recent_event in self.recent_events:
                if (recent_event.get('event_type') == 'login_failed' and
                    recent_event.get('source_ip') == source_ip):
                    
                    event_time = datetime.fromisoformat(recent_event.get('timestamp', ''))
                    if current_time - event_time <= time_window:
                        failed_count += 1
            
            threshold = self.threat_patterns['brute_force']['failed_logins_threshold']
            score = min(failed_count / threshold, 1.0)
            
            return score
            
        except Exception as e:
            logger.error(f"Brute force analysis error: {str(e)}")
            return 0.0
    
    def _analyze_dos_attack(self, event: Dict[str, Any]) -> float:
        """Analyze for DoS attack patterns"""
        try:
            source_ip = event.get('source_ip')
            if not source_ip:
                return 0.0
            
            # Count requests from this IP in time window
            current_time = datetime.utcnow()
            time_window = timedelta(seconds=self.threat_patterns['dos_attack']['time_window'])
            
            request_count = 0
            for recent_event in self.recent_events:
                if recent_event.get('source_ip') == source_ip:
                    event_time = datetime.fromisoformat(recent_event.get('timestamp', ''))
                    if current_time - event_time <= time_window:
                        request_count += 1
            
            threshold = self.threat_patterns['dos_attack']['requests_threshold']
            score = min(request_count / threshold, 1.0)
            
            return score
            
        except Exception as e:
            logger.error(f"DoS analysis error: {str(e)}")
            return 0.0
    
    def _analyze_port_scanning(self, event: Dict[str, Any]) -> float:
        """Analyze for port scanning patterns"""
        try:
            if event.get('event_type') != 'connection_attempt':
                return 0.0
            
            source_ip = event.get('source_ip')
            if not source_ip:
                return 0.0
            
            # Count unique ports accessed from this IP
            current_time = datetime.utcnow()
            time_window = timedelta(seconds=self.threat_patterns['port_scanning']['time_window'])
            
            unique_ports = set()
            for recent_event in self.recent_events:
                if (recent_event.get('event_type') == 'connection_attempt' and
                    recent_event.get('source_ip') == source_ip):
                    
                    event_time = datetime.fromisoformat(recent_event.get('timestamp', ''))
                    if current_time - event_time <= time_window:
                        port = recent_event.get('destination_port')
                        if port:
                            unique_ports.add(port)
            
            threshold = self.threat_patterns['port_scanning']['unique_ports_threshold']
            score = min(len(unique_ports) / threshold, 1.0)
            
            return score
            
        except Exception as e:
            logger.error(f"Port scanning analysis error: {str(e)}")
            return 0.0
    
    def _analyze_data_exfiltration(self, event: Dict[str, Any]) -> float:
        """Analyze for data exfiltration patterns"""
        try:
            if event.get('event_type') != 'data_transfer':
                return 0.0
            
            user_id = event.get('user_id')
            if not user_id:
                return 0.0
            
            # Calculate data volume transferred by user in time window
            current_time = datetime.utcnow()
            time_window = timedelta(seconds=self.threat_patterns['data_exfiltration']['time_window'])
            
            total_bytes = 0
            for recent_event in self.recent_events:
                if (recent_event.get('event_type') == 'data_transfer' and
                    recent_event.get('user_id') == user_id):
                    
                    event_time = datetime.fromisoformat(recent_event.get('timestamp', ''))
                    if current_time - event_time <= time_window:
                        bytes_transferred = recent_event.get('bytes_transferred', 0)
                        total_bytes += bytes_transferred
            
            threshold = self.threat_patterns['data_exfiltration']['data_volume_threshold']
            score = min(total_bytes / threshold, 1.0)
            
            return score
            
        except Exception as e:
            logger.error(f"Data exfiltration analysis error: {str(e)}")
            return 0.0
    
    def _analyze_privilege_escalation(self, event: Dict[str, Any]) -> float:
        """Analyze for privilege escalation attempts"""
        try:
            if event.get('event_type') != 'privilege_request':
                return 0.0
            
            user_id = event.get('user_id')
            if not user_id:
                return 0.0
            
            # Count privilege escalation attempts by user
            current_time = datetime.utcnow()
            time_window = timedelta(seconds=self.threat_patterns['privilege_escalation']['time_window'])
            
            escalation_count = 0
            for recent_event in self.recent_events:
                if (recent_event.get('event_type') == 'privilege_request' and
                    recent_event.get('user_id') == user_id):
                    
                    event_time = datetime.fromisoformat(recent_event.get('timestamp', ''))
                    if current_time - event_time <= time_window:
                        escalation_count += 1
            
            threshold = self.threat_patterns['privilege_escalation']['admin_attempts_threshold']
            score = min(escalation_count / threshold, 1.0)
            
            return score
            
        except Exception as e:
            logger.error(f"Privilege escalation analysis error: {str(e)}")
            return 0.0
    
    def _analyze_behavioral_anomaly(self, event: Dict[str, Any]) -> float:
        """Analyze for behavioral anomalies using machine learning"""
        try:
            if not self.anomaly_detector:
                return 0.0
            
            # Extract features from event
            features = self._extract_event_features(event)
            if not features:
                return 0.0
            
            # Normalize features
            features_array = np.array(features).reshape(1, -1)
            
            # Check if we have enough data to scale
            if hasattr(self.scaler, 'scale_'):
                features_scaled = self.scaler.transform(features_array)
            else:
                # Not enough data for scaling yet
                features_scaled = features_array
            
            # Get anomaly score
            anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
            
            # Convert to 0-1 scale (lower scores are more anomalous)
            normalized_score = max(0, min(1, (anomaly_score + 0.5) / 1.0))
            
            # Invert so higher scores indicate more anomalous behavior
            return 1.0 - normalized_score
            
        except Exception as e:
            logger.error(f"Behavioral anomaly analysis error: {str(e)}")
            return 0.0
    
    def _extract_event_features(self, event: Dict[str, Any]) -> Optional[List[float]]:
        """Extract numerical features from event for ML analysis"""
        try:
            features = []
            
            # Time-based features
            timestamp = event.get('timestamp')
            if timestamp:
                dt = datetime.fromisoformat(timestamp)
                features.extend([
                    dt.hour,  # Hour of day
                    dt.weekday(),  # Day of week
                    dt.minute  # Minute of hour
                ])
            else:
                features.extend([0, 0, 0])
            
            # Event type encoding
            event_types = {
                'login_success': 1,
                'login_failed': 2,
                'logout': 3,
                'api_request': 4,
                'file_access': 5,
                'data_transfer': 6,
                'privilege_request': 7,
                'connection_attempt': 8
            }
            event_type = event.get('event_type', 'unknown')
            features.append(event_types.get(event_type, 0))
            
            # Numerical features
            features.append(event.get('response_time', 0))
            features.append(event.get('bytes_transferred', 0))
            features.append(event.get('status_code', 0))
            
            # User behavior features
            user_id = event.get('user_id')
            if user_id:
                user_baseline = self.behavioral_baselines.get(user_id, {})
                features.append(user_baseline.get('avg_requests_per_hour', 0))
                features.append(user_baseline.get('avg_session_duration', 0))
            else:
                features.extend([0, 0])
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction error: {str(e)}")
            return None
    
    def _get_threat_severity(self, threat_type: str, score: float) -> str:
        """Get threat severity based on type and score"""
        base_severity = self.threat_patterns.get(threat_type, {}).get('severity', 'LOW')
        
        if score >= 0.9:
            return 'CRITICAL'
        elif score >= 0.7:
            return 'HIGH'
        elif score >= 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_recommendations(self, threat_scores: Dict[str, float], event: Dict[str, Any]) -> List[str]:
        """Generate security recommendations based on threat analysis"""
        recommendations = []
        
        # Brute force recommendations
        if threat_scores['brute_force'] > 0.5:
            recommendations.extend([
                "Implement account lockout policies",
                "Enable multi-factor authentication",
                "Monitor failed login attempts",
                f"Consider blocking IP: {event.get('source_ip')}"
            ])
        
        # DoS attack recommendations
        if threat_scores['dos_attack'] > 0.5:
            recommendations.extend([
                "Implement rate limiting",
                "Deploy DDoS protection",
                "Scale infrastructure capacity",
                f"Block suspicious IP: {event.get('source_ip')}"
            ])
        
        # Port scanning recommendations
        if threat_scores['port_scanning'] > 0.5:
            recommendations.extend([
                "Review firewall rules",
                "Disable unnecessary services",
                "Implement intrusion detection",
                "Monitor network traffic"
            ])
        
        # Data exfiltration recommendations
        if threat_scores['data_exfiltration'] > 0.5:
            recommendations.extend([
                "Review data access permissions",
                "Implement data loss prevention",
                "Monitor large data transfers",
                "Audit user activities"
            ])
        
        # Privilege escalation recommendations
        if threat_scores['privilege_escalation'] > 0.5:
            recommendations.extend([
                "Review privilege assignments",
                "Implement least privilege principle",
                "Monitor administrative actions",
                "Require approval for privilege changes"
            ])
        
        # Behavioral anomaly recommendations
        if threat_scores['behavioral_anomaly'] > 0.5:
            recommendations.extend([
                "Investigate user behavior",
                "Review recent account activity",
                "Consider additional authentication",
                "Monitor user sessions"
            ])
        
        return list(set(recommendations))  # Remove duplicates
    
    def _store_threat_analysis(self, analysis: Dict[str, Any]):
        """Store threat analysis results"""
        try:
            key = f"threat_analysis:{analysis['event_id']}"
            self.redis_client.setex(key, 86400, json.dumps(analysis))  # Store for 24 hours
        except Exception as e:
            logger.error(f"Failed to store threat analysis: {str(e)}")
    
    def _trigger_security_alert(self, analysis: Dict[str, Any], event: Dict[str, Any]):
        """Trigger security alert for high-priority threats"""
        try:
            alert = {
                'alert_id': f"alert_{int(time.time())}",
                'timestamp': datetime.utcnow().isoformat(),
                'threat_level': analysis['threat_level'],
                'threat_score': analysis['threat_score'],
                'threat_types': analysis['threat_types'],
                'event': event,
                'recommendations': analysis['recommendations'],
                'status': 'ACTIVE'
            }
            
            # Store alert
            alert_key = f"security_alert:{alert['alert_id']}"
            self.redis_client.setex(alert_key, 604800, json.dumps(alert))  # Store for 7 days
            
            # Log critical alert
            logger.critical(f"SECURITY ALERT: {json.dumps(alert)}")
            
            # In production, this would trigger notifications (email, SMS, etc.)
            
        except Exception as e:
            logger.error(f"Failed to trigger security alert: {str(e)}")
    
    def _perform_periodic_analysis(self):
        """Perform periodic threat analysis and model updates"""
        try:
            # Update behavioral baselines
            self._update_behavioral_baselines()
            
            # Retrain anomaly detection model if needed
            if len(self.recent_events) > 100:
                self._update_anomaly_model()
            
            # Clean up old data
            self._cleanup_old_data()
            
        except Exception as e:
            logger.error(f"Periodic analysis error: {str(e)}")
    
    def _update_behavioral_baselines(self):
        """Update user behavioral baselines"""
        try:
            # Group events by user
            user_events = defaultdict(list)
            for event in self.recent_events:
                user_id = event.get('user_id')
                if user_id:
                    user_events[user_id].append(event)
            
            # Calculate baselines for each user
            for user_id, events in user_events.items():
                if len(events) >= 10:  # Minimum events for baseline
                    baseline = self._calculate_user_baseline(events)
                    self.behavioral_baselines[user_id] = baseline
            
        except Exception as e:
            logger.error(f"Baseline update error: {str(e)}")
    
    def _calculate_user_baseline(self, events: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate behavioral baseline for a user"""
        try:
            # Calculate various metrics
            timestamps = []
            response_times = []
            bytes_transferred = []
            
            for event in events:
                if event.get('timestamp'):
                    timestamps.append(datetime.fromisoformat(event['timestamp']))
                if event.get('response_time'):
                    response_times.append(event['response_time'])
                if event.get('bytes_transferred'):
                    bytes_transferred.append(event['bytes_transferred'])
            
            baseline = {}
            
            # Calculate requests per hour
            if len(timestamps) >= 2:
                time_span = (max(timestamps) - min(timestamps)).total_seconds() / 3600
                if time_span > 0:
                    baseline['avg_requests_per_hour'] = len(events) / time_span
            
            # Calculate average response time
            if response_times:
                baseline['avg_response_time'] = sum(response_times) / len(response_times)
            
            # Calculate average data transfer
            if bytes_transferred:
                baseline['avg_bytes_transferred'] = sum(bytes_transferred) / len(bytes_transferred)
            
            # Calculate session patterns
            baseline['avg_session_duration'] = self._calculate_avg_session_duration(timestamps)
            
            return baseline
            
        except Exception as e:
            logger.error(f"Baseline calculation error: {str(e)}")
            return {}
    
    def _calculate_avg_session_duration(self, timestamps: List[datetime]) -> float:
        """Calculate average session duration"""
        try:
            if len(timestamps) < 2:
                return 0.0
            
            # Simple heuristic: gaps > 30 minutes indicate new sessions
            timestamps.sort()
            session_durations = []
            session_start = timestamps[0]
            
            for i in range(1, len(timestamps)):
                gap = (timestamps[i] - timestamps[i-1]).total_seconds()
                if gap > 1800:  # 30 minutes
                    # End of session
                    session_duration = (timestamps[i-1] - session_start).total_seconds()
                    session_durations.append(session_duration)
                    session_start = timestamps[i]
            
            # Add final session
            final_duration = (timestamps[-1] - session_start).total_seconds()
            session_durations.append(final_duration)
            
            return sum(session_durations) / len(session_durations) if session_durations else 0.0
            
        except Exception as e:
            logger.error(f"Session duration calculation error: {str(e)}")
            return 0.0
    
    def _update_anomaly_model(self):
        """Update anomaly detection model with recent data"""
        try:
            # Extract features from recent events
            features_list = []
            for event in list(self.recent_events)[-1000:]:  # Use last 1000 events
                features = self._extract_event_features(event)
                if features:
                    features_list.append(features)
            
            if len(features_list) >= 50:  # Minimum for training
                features_array = np.array(features_list)
                
                # Fit scaler
                self.scaler.fit(features_array)
                features_scaled = self.scaler.transform(features_array)
                
                # Retrain model
                self.anomaly_detector.fit(features_scaled)
                
                # Save model
                model_path = '/tmp/aideon_anomaly_model.joblib'
                joblib.dump(self.anomaly_detector, model_path)
                
                logger.info(f"Updated anomaly model with {len(features_list)} samples")
            
        except Exception as e:
            logger.error(f"Model update error: {str(e)}")
    
    def _cleanup_old_data(self):
        """Clean up old data to prevent memory issues"""
        try:
            # Keep only recent events (already handled by deque maxlen)
            
            # Clean up old Redis keys
            current_time = datetime.utcnow()
            
            # Clean up old threat analyses (older than 7 days)
            pattern = "threat_analysis:*"
            for key in self.redis_client.scan_iter(match=pattern):
                try:
                    data = self.redis_client.get(key)
                    if data:
                        analysis = json.loads(data)
                        analysis_time = datetime.fromisoformat(analysis['timestamp'])
                        if current_time - analysis_time > timedelta(days=7):
                            self.redis_client.delete(key)
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
    
    def get_threat_report(self) -> Dict[str, Any]:
        """Generate comprehensive threat report"""
        try:
            current_time = datetime.utcnow()
            
            # Analyze recent events
            recent_threats = []
            threat_counts = defaultdict(int)
            
            for event in list(self.recent_events)[-100:]:  # Last 100 events
                analysis = self.analyze_event(event)
                if analysis['threat_detected']:
                    recent_threats.append(analysis)
                    for threat_type in analysis['threat_types']:
                        threat_counts[threat_type['type']] += 1
            
            # Get active alerts
            active_alerts = []
            pattern = "security_alert:*"
            for key in self.redis_client.scan_iter(match=pattern):
                try:
                    data = self.redis_client.get(key)
                    if data:
                        alert = json.loads(data)
                        if alert['status'] == 'ACTIVE':
                            active_alerts.append(alert)
                except:
                    pass
            
            return {
                'report_timestamp': current_time.isoformat(),
                'monitoring_status': 'ACTIVE' if self.monitoring_active else 'INACTIVE',
                'recent_threats': len(recent_threats),
                'active_alerts': len(active_alerts),
                'threat_types_detected': dict(threat_counts),
                'top_threats': sorted(recent_threats, key=lambda x: x['threat_score'], reverse=True)[:5],
                'system_health': {
                    'anomaly_model_status': 'ACTIVE' if self.anomaly_detector else 'INACTIVE',
                    'behavioral_baselines': len(self.behavioral_baselines),
                    'events_analyzed': len(self.recent_events)
                },
                'recommendations': self._get_system_recommendations(threat_counts)
            }
            
        except Exception as e:
            logger.error(f"Threat report generation error: {str(e)}")
            return {
                'error': str(e),
                'report_timestamp': datetime.utcnow().isoformat()
            }
    
    def _get_system_recommendations(self, threat_counts: Dict[str, int]) -> List[str]:
        """Get system-wide security recommendations"""
        recommendations = []
        
        if threat_counts.get('brute_force', 0) > 5:
            recommendations.append("Implement stronger authentication policies")
        
        if threat_counts.get('dos_attack', 0) > 3:
            recommendations.append("Deploy DDoS protection and rate limiting")
        
        if threat_counts.get('data_exfiltration', 0) > 2:
            recommendations.append("Review data access controls and monitoring")
        
        if threat_counts.get('privilege_escalation', 0) > 1:
            recommendations.append("Audit privilege assignments and access controls")
        
        if sum(threat_counts.values()) > 10:
            recommendations.append("Consider increasing security monitoring frequency")
        
        return recommendations

# Global threat detection engine
threat_detector = ThreatDetectionEngine()

