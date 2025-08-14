"""
Network Security and System Hardening Module
Comprehensive network protection and system security measures
"""

import socket
import ssl
import ipaddress
import logging
import hashlib
import hmac
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
import redis
import json
import re
import subprocess
import psutil
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import requests
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkSecurityManager:
    """Comprehensive network security and system hardening manager"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)
        self.blocked_ips = set()
        self.allowed_domains = set()
        self.suspicious_patterns = self._load_suspicious_patterns()
        self.firewall_rules = []
        self.ssl_context = self._create_ssl_context()
        self.intrusion_attempts = {}
        self.network_monitoring = True
        
    def _load_suspicious_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns that indicate network attacks"""
        return [
            # SQL Injection patterns
            {
                'pattern': r'(?i)(union|select|insert|update|delete|drop|create|alter|exec|execute)',
                'type': 'SQL_INJECTION',
                'severity': 'HIGH'
            },
            # XSS patterns
            {
                'pattern': r'(?i)(<script|javascript:|vbscript:|onload=|onerror=|onclick=)',
                'type': 'XSS_ATTEMPT',
                'severity': 'HIGH'
            },
            # Command injection patterns
            {
                'pattern': r'(?i)(;|\||&|`|\$\(|wget|curl|nc|netcat|bash|sh|cmd|powershell)',
                'type': 'COMMAND_INJECTION',
                'severity': 'CRITICAL'
            },
            # Directory traversal patterns
            {
                'pattern': r'(\.\.\/|\.\.\\\\|%2e%2e%2f|%2e%2e%5c)',
                'type': 'DIRECTORY_TRAVERSAL',
                'severity': 'HIGH'
            },
            # LDAP injection patterns
            {
                'pattern': r'(\*|\)|\(|%28|%29|%2a)',
                'type': 'LDAP_INJECTION',
                'severity': 'MEDIUM'
            },
            # XXE patterns
            {
                'pattern': r'(?i)(<!entity|<!doctype|system|public)',
                'type': 'XXE_ATTEMPT',
                'severity': 'HIGH'
            }
        ]
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create secure SSL context"""
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # Disable weak ciphers
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
        return context
    
    def validate_ip_address(self, ip_address: str) -> Dict[str, Any]:
        """
        Validate and analyze IP address for security threats
        
        Args:
            ip_address: IP address to validate
            
        Returns:
            Validation result with threat assessment
        """
        validation = {
            'is_valid': False,
            'is_private': False,
            'is_blocked': False,
            'threat_level': 'LOW',
            'country': None,
            'asn': None,
            'reputation': 'UNKNOWN',
            'warnings': []
        }
        
        try:
            # Parse IP address
            ip = ipaddress.ip_address(ip_address)
            validation['is_valid'] = True
            validation['is_private'] = ip.is_private
            
            # Check if IP is blocked
            if ip_address in self.blocked_ips:
                validation['is_blocked'] = True
                validation['threat_level'] = 'CRITICAL'
                validation['warnings'].append('IP address is blocked')
                return validation
            
            # Check against known threat lists
            threat_check = self._check_ip_reputation(ip_address)
            validation.update(threat_check)
            
            # Check for suspicious patterns in reverse DNS
            try:
                hostname = socket.gethostbyaddr(ip_address)[0]
                if self._is_suspicious_hostname(hostname):
                    validation['threat_level'] = 'HIGH'
                    validation['warnings'].append('Suspicious hostname detected')
            except:
                pass
            
            # Rate limiting check
            rate_limit = self._check_ip_rate_limit(ip_address)
            if not rate_limit['allowed']:
                validation['threat_level'] = 'HIGH'
                validation['warnings'].append('Rate limit exceeded')
            
            return validation
            
        except ValueError:
            validation['warnings'].append('Invalid IP address format')
            return validation
        except Exception as e:
            logger.error(f"IP validation error: {str(e)}")
            validation['warnings'].append('IP validation failed')
            return validation
    
    def _check_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """Check IP reputation against threat intelligence"""
        reputation_data = {
            'reputation': 'CLEAN',
            'threat_level': 'LOW',
            'country': None,
            'asn': None
        }
        
        try:
            # Check cached reputation
            cache_key = f'ip_reputation:{ip_address}'
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            # Simple reputation check (in production, use threat intelligence APIs)
            # This is a basic implementation - integrate with real threat feeds
            
            # Check against known malicious IP ranges
            malicious_ranges = [
                '10.0.0.0/8',    # Example - replace with real threat data
                '192.168.0.0/16'  # Example - replace with real threat data
            ]
            
            ip = ipaddress.ip_address(ip_address)
            for range_str in malicious_ranges:
                if ip in ipaddress.ip_network(range_str):
                    reputation_data['reputation'] = 'MALICIOUS'
                    reputation_data['threat_level'] = 'CRITICAL'
                    break
            
            # Cache result for 1 hour
            self.redis_client.setex(cache_key, 3600, json.dumps(reputation_data))
            
            return reputation_data
            
        except Exception as e:
            logger.warning(f"IP reputation check failed: {str(e)}")
            return reputation_data
    
    def _is_suspicious_hostname(self, hostname: str) -> bool:
        """Check if hostname appears suspicious"""
        suspicious_patterns = [
            r'.*\.onion$',  # Tor hidden services
            r'.*malware.*',
            r'.*botnet.*',
            r'.*phishing.*',
            r'.*spam.*',
            r'.*proxy.*',
            r'.*vpn.*'
        ]
        
        for pattern in suspicious_patterns:
            if re.match(pattern, hostname.lower()):
                return True
        
        return False
    
    def _check_ip_rate_limit(self, ip_address: str) -> Dict[str, Any]:
        """Check rate limiting for IP address"""
        try:
            current_time = datetime.utcnow()
            minute_key = f'ip_rate:{ip_address}:minute:{current_time.strftime("%Y%m%d%H%M")}'
            hour_key = f'ip_rate:{ip_address}:hour:{current_time.strftime("%Y%m%d%H")}'
            
            minute_count = int(self.redis_client.get(minute_key) or 0)
            hour_count = int(self.redis_client.get(hour_key) or 0)
            
            # Limits per IP
            minute_limit = 60  # 60 requests per minute
            hour_limit = 1000  # 1000 requests per hour
            
            if minute_count >= minute_limit or hour_count >= hour_limit:
                return {'allowed': False, 'reason': 'IP rate limit exceeded'}
            
            # Increment counters
            pipe = self.redis_client.pipeline()
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)
            pipe.execute()
            
            return {'allowed': True}
            
        except Exception as e:
            logger.warning(f"IP rate limit check failed: {str(e)}")
            return {'allowed': True}
    
    def validate_url(self, url: str) -> Dict[str, Any]:
        """
        Validate URL for security threats
        
        Args:
            url: URL to validate
            
        Returns:
            Validation result with security assessment
        """
        validation = {
            'is_safe': True,
            'parsed_url': None,
            'domain': None,
            'scheme': None,
            'threat_level': 'LOW',
            'warnings': [],
            'blocked_reason': None
        }
        
        try:
            # Parse URL
            parsed = urlparse(url)
            validation['parsed_url'] = parsed
            validation['domain'] = parsed.netloc
            validation['scheme'] = parsed.scheme
            
            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                validation['is_safe'] = False
                validation['blocked_reason'] = f'Unsafe URL scheme: {parsed.scheme}'
                return validation
            
            # Check for suspicious patterns in URL
            for pattern_info in self.suspicious_patterns:
                if re.search(pattern_info['pattern'], url):
                    validation['threat_level'] = pattern_info['severity']
                    validation['warnings'].append(f"{pattern_info['type']} pattern detected")
                    
                    if pattern_info['severity'] == 'CRITICAL':
                        validation['is_safe'] = False
                        validation['blocked_reason'] = f"Blocked due to {pattern_info['type']}"
            
            # Check domain reputation
            domain_check = self._check_domain_reputation(parsed.netloc)
            if not domain_check['is_safe']:
                validation['is_safe'] = False
                validation['blocked_reason'] = domain_check['reason']
            
            # Check for URL shorteners (potential phishing)
            url_shorteners = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly']
            if parsed.netloc.lower() in url_shorteners:
                validation['warnings'].append('URL shortener detected - potential phishing risk')
                validation['threat_level'] = 'MEDIUM'
            
            return validation
            
        except Exception as e:
            logger.error(f"URL validation error: {str(e)}")
            validation['is_safe'] = False
            validation['blocked_reason'] = 'URL validation failed'
            return validation
    
    def _check_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """Check domain reputation"""
        try:
            # Check cached reputation
            cache_key = f'domain_reputation:{domain}'
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            # Basic domain checks
            reputation = {'is_safe': True, 'reason': None}
            
            # Check against blocked domains
            blocked_domains = [
                'malware.com',  # Example - replace with real threat data
                'phishing.net'  # Example - replace with real threat data
            ]
            
            if domain.lower() in blocked_domains:
                reputation['is_safe'] = False
                reputation['reason'] = 'Domain in blocklist'
            
            # Check for suspicious TLDs
            suspicious_tlds = ['.tk', '.ml', '.ga', '.cf']
            for tld in suspicious_tlds:
                if domain.lower().endswith(tld):
                    reputation['reason'] = f'Suspicious TLD: {tld}'
                    break
            
            # Cache result for 1 hour
            self.redis_client.setex(cache_key, 3600, json.dumps(reputation))
            
            return reputation
            
        except Exception as e:
            logger.warning(f"Domain reputation check failed: {str(e)}")
            return {'is_safe': True, 'reason': None}
    
    def scan_request_for_threats(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive request scanning for security threats
        
        Args:
            request_data: Request data to scan
            
        Returns:
            Threat analysis results
        """
        scan_result = {
            'is_safe': True,
            'threat_level': 'LOW',
            'threats_detected': [],
            'warnings': [],
            'blocked_reason': None,
            'scan_timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Scan headers
            headers = request_data.get('headers', {})
            header_threats = self._scan_headers(headers)
            if header_threats:
                scan_result['threats_detected'].extend(header_threats)
            
            # Scan parameters
            params = request_data.get('params', {})
            param_threats = self._scan_parameters(params)
            if param_threats:
                scan_result['threats_detected'].extend(param_threats)
            
            # Scan body/payload
            body = request_data.get('body', '')
            body_threats = self._scan_body(body)
            if body_threats:
                scan_result['threats_detected'].extend(body_threats)
            
            # Determine overall threat level
            if scan_result['threats_detected']:
                threat_levels = [threat['severity'] for threat in scan_result['threats_detected']]
                
                if 'CRITICAL' in threat_levels:
                    scan_result['is_safe'] = False
                    scan_result['threat_level'] = 'CRITICAL'
                    scan_result['blocked_reason'] = 'Critical security threat detected'
                elif 'HIGH' in threat_levels:
                    scan_result['threat_level'] = 'HIGH'
                    scan_result['warnings'].append('High-risk content detected')
                elif 'MEDIUM' in threat_levels:
                    scan_result['threat_level'] = 'MEDIUM'
                    scan_result['warnings'].append('Medium-risk content detected')
            
            return scan_result
            
        except Exception as e:
            logger.error(f"Request threat scan error: {str(e)}")
            scan_result['is_safe'] = False
            scan_result['blocked_reason'] = 'Threat scan failed'
            return scan_result
    
    def _scan_headers(self, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scan HTTP headers for threats"""
        threats = []
        
        # Check User-Agent for suspicious patterns
        user_agent = headers.get('User-Agent', '').lower()
        suspicious_agents = ['sqlmap', 'nikto', 'nmap', 'burp', 'scanner', 'bot']
        
        for agent in suspicious_agents:
            if agent in user_agent:
                threats.append({
                    'type': 'SUSPICIOUS_USER_AGENT',
                    'severity': 'HIGH',
                    'description': f'Suspicious user agent: {agent}',
                    'location': 'headers'
                })
        
        # Check for injection attempts in headers
        for header_name, header_value in headers.items():
            for pattern_info in self.suspicious_patterns:
                if re.search(pattern_info['pattern'], header_value):
                    threats.append({
                        'type': pattern_info['type'],
                        'severity': pattern_info['severity'],
                        'description': f'Malicious pattern in header {header_name}',
                        'location': 'headers'
                    })
        
        return threats
    
    def _scan_parameters(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan request parameters for threats"""
        threats = []
        
        for param_name, param_value in params.items():
            param_str = str(param_value)
            
            # Check for injection patterns
            for pattern_info in self.suspicious_patterns:
                if re.search(pattern_info['pattern'], param_str):
                    threats.append({
                        'type': pattern_info['type'],
                        'severity': pattern_info['severity'],
                        'description': f'Malicious pattern in parameter {param_name}',
                        'location': 'parameters'
                    })
        
        return threats
    
    def _scan_body(self, body: str) -> List[Dict[str, Any]]:
        """Scan request body for threats"""
        threats = []
        
        if not body:
            return threats
        
        # Check for injection patterns in body
        for pattern_info in self.suspicious_patterns:
            if re.search(pattern_info['pattern'], body):
                threats.append({
                    'type': pattern_info['type'],
                    'severity': pattern_info['severity'],
                    'description': f'Malicious pattern in request body',
                    'location': 'body'
                })
        
        return threats
    
    def block_ip(self, ip_address: str, reason: str, duration: Optional[int] = None):
        """
        Block IP address
        
        Args:
            ip_address: IP to block
            reason: Reason for blocking
            duration: Block duration in seconds (None for permanent)
        """
        try:
            self.blocked_ips.add(ip_address)
            
            # Store in Redis
            block_data = {
                'ip': ip_address,
                'reason': reason,
                'blocked_at': datetime.utcnow().isoformat(),
                'duration': duration
            }
            
            key = f'blocked_ip:{ip_address}'
            if duration:
                self.redis_client.setex(key, duration, json.dumps(block_data))
            else:
                self.redis_client.set(key, json.dumps(block_data))
            
            logger.warning(f"IP blocked: {ip_address} - {reason}")
            
        except Exception as e:
            logger.error(f"Failed to block IP {ip_address}: {str(e)}")
    
    def unblock_ip(self, ip_address: str):
        """Unblock IP address"""
        try:
            self.blocked_ips.discard(ip_address)
            self.redis_client.delete(f'blocked_ip:{ip_address}')
            logger.info(f"IP unblocked: {ip_address}")
        except Exception as e:
            logger.error(f"Failed to unblock IP {ip_address}: {str(e)}")
    
    def get_system_security_status(self) -> Dict[str, Any]:
        """Get comprehensive system security status"""
        try:
            # System resource monitoring
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network connections
            connections = psutil.net_connections()
            listening_ports = [conn.laddr.port for conn in connections if conn.status == 'LISTEN']
            
            # Process monitoring
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                'system_health': {
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent,
                    'disk_usage': (disk.used / disk.total) * 100,
                    'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                'network_security': {
                    'blocked_ips_count': len(self.blocked_ips),
                    'listening_ports': listening_ports,
                    'active_connections': len(connections)
                },
                'process_monitoring': {
                    'total_processes': len(processes),
                    'high_cpu_processes': [p for p in processes if p['cpu_percent'] > 80],
                    'high_memory_processes': [p for p in processes if p['memory_percent'] > 80]
                },
                'security_status': 'SECURE',
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"System security status error: {str(e)}")
            return {
                'error': 'Failed to get system status',
                'security_status': 'UNKNOWN',
                'last_updated': datetime.utcnow().isoformat()
            }

# Global network security manager
network_security = NetworkSecurityManager()

def require_network_security(f):
    """Decorator to apply network security checks"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get client IP
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()
        
        # Validate IP
        ip_validation = network_security.validate_ip_address(client_ip)
        if ip_validation['is_blocked'] or ip_validation['threat_level'] == 'CRITICAL':
            logger.warning(f"Blocked request from {client_ip}: {ip_validation}")
            return jsonify({'error': 'Access denied'}), 403
        
        # Scan request for threats
        request_data = {
            'headers': dict(request.headers),
            'params': dict(request.args),
            'body': request.get_data(as_text=True) if request.data else ''
        }
        
        threat_scan = network_security.scan_request_for_threats(request_data)
        if not threat_scan['is_safe']:
            logger.warning(f"Threat detected from {client_ip}: {threat_scan}")
            return jsonify({
                'error': 'Security threat detected',
                'reason': threat_scan['blocked_reason']
            }), 403
        
        # Add security info to request context
        g.client_ip = client_ip
        g.ip_validation = ip_validation
        g.threat_scan = threat_scan
        
        return f(*args, **kwargs)
    
    return decorated_function

