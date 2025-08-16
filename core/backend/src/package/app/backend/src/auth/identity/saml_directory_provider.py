"""
SAML Integration module for ApexAgent.

This module provides integration with SAML identity providers,
enabling enterprise single sign-on capabilities.
"""

import os
import base64
import logging
import uuid
import hashlib
import secrets
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

import requests
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate

from src.core.error_handling.errors import AuthenticationError, ConfigurationError
from src.core.event_system.event_manager import EventManager
from src.auth.identity.identity_manager import IdentityProvider

logger = logging.getLogger(__name__)

class SAMLProvider(IdentityProvider):
    """
    Identity provider for SAML 2.0 integration.
    """
    def __init__(
        self,
        provider_id: str,
        name: str,
        config: Dict[str, Any],
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        super().__init__(
            provider_id=provider_id,
            name=name,
            provider_type="saml",
            config=config,
            is_active=is_active,
            metadata=metadata
        )
        
        # Validate required configuration
        required_fields = [
            "entity_id", 
            "assertion_consumer_service_url",
            "idp_metadata_url"
        ]
        for field in required_fields:
            if field not in self.config:
                raise ConfigurationError(f"Missing required configuration field: {field}")
        
        # Initialize SAML-specific properties
        self.entity_id = self.config["entity_id"]
        self.acs_url = self.config["assertion_consumer_service_url"]
        self.idp_metadata_url = self.config["idp_metadata_url"]
        
        # Optional configuration
        self.signing_cert = self.config.get("signing_certificate")
        self.signing_key = self.config.get("signing_private_key")
        self.want_assertions_signed = self.config.get("want_assertions_signed", True)
        self.want_response_signed = self.config.get("want_response_signed", True)
        self.name_id_format = self.config.get("name_id_format", "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress")
        
        # Cache for IdP metadata
        self.idp_metadata = None
        self.idp_metadata_last_updated = None
        
        # Pending authentication requests
        self.pending_requests: Dict[str, Dict[str, Any]] = {}
        
    def _load_idp_metadata(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Load IdP metadata from URL or cached version.
        
        Args:
            force_refresh: Whether to force a refresh of the metadata
            
        Returns:
            Dictionary containing IdP metadata
            
        Raises:
            ConfigurationError: If metadata cannot be loaded
        """
        # Check if we need to refresh metadata
        current_time = datetime.now()
        if (self.idp_metadata is None or 
            force_refresh or 
            self.idp_metadata_last_updated is None or 
            (current_time - self.idp_metadata_last_updated) > timedelta(hours=24)):
            
            try:
                # Fetch metadata from URL
                response = requests.get(self.idp_metadata_url, timeout=30)
                response.raise_for_status()
                
                # Parse XML metadata
                metadata_xml = response.text
                root = ET.fromstring(metadata_xml)
                
                # Extract IdP information
                ns = {
                    'md': 'urn:oasis:names:tc:SAML:2.0:metadata',
                    'ds': 'http://www.w3.org/2000/09/xmldsig#'
                }
                
                idp_descriptor = root.find('.//md:IDPSSODescriptor', ns)
                if idp_descriptor is None:
                    raise ConfigurationError("No IdP SSO Descriptor found in metadata")
                
                # Extract SSO URL
                sso_element = idp_descriptor.find('./md:SingleSignOnService[@Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"]', ns)
                if sso_element is None:
                    raise ConfigurationError("No HTTP-Redirect SSO service found in metadata")
                
                sso_url = sso_element.get('Location')
                
                # Extract certificate
                cert_element = idp_descriptor.find('.//ds:X509Certificate', ns)
                if cert_element is None:
                    raise ConfigurationError("No X509Certificate found in metadata")
                
                cert_data = cert_element.text.strip()
                cert_pem = f"-----BEGIN CERTIFICATE-----\n{cert_data}\n-----END CERTIFICATE-----"
                
                # Store metadata
                self.idp_metadata = {
                    "entity_id": root.get('entityID'),
                    "sso_url": sso_url,
                    "certificate": cert_pem,
                    "raw_xml": metadata_xml
                }
                
                self.idp_metadata_last_updated = current_time
                
            except Exception as e:
                logger.error(f"Error loading IdP metadata: {e}")
                raise ConfigurationError(f"Failed to load IdP metadata: {e}")
        
        return self.idp_metadata
    
    def _generate_saml_request(self) -> Tuple[str, str, Dict[str, Any]]:
        """
        Generate a SAML authentication request.
        
        Returns:
            Tuple of (encoded_request, relay_state, request_data)
            
        Raises:
            ConfigurationError: If request cannot be generated
        """
        try:
            # Load IdP metadata
            idp_metadata = self._load_idp_metadata()
            
            # Generate request ID and issue instant
            request_id = f"id{uuid.uuid4()}"
            issue_instant = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Generate relay state
            relay_state = secrets.token_urlsafe(32)
            
            # Build SAML request XML
            saml_request = f"""
            <samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                               xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                               ID="{request_id}"
                               Version="2.0"
                               IssueInstant="{issue_instant}"
                               Destination="{idp_metadata['sso_url']}"
                               AssertionConsumerServiceURL="{self.acs_url}"
                               ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
                <saml:Issuer>{self.entity_id}</saml:Issuer>
                <samlp:NameIDPolicy Format="{self.name_id_format}"
                                   AllowCreate="true" />
            </samlp:AuthnRequest>
            """
            
            # Compress and encode the request
            saml_request_bytes = saml_request.strip().encode('utf-8')
            compressed_request = saml_request_bytes  # In practice, you would compress this
            encoded_request = base64.b64encode(compressed_request).decode('utf-8')
            
            # Store request data
            request_data = {
                "request_id": request_id,
                "relay_state": relay_state,
                "issue_instant": issue_instant,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(minutes=15)).isoformat()
            }
            
            # Store in pending requests
            self.pending_requests[request_id] = request_data
            
            return encoded_request, relay_state, request_data
            
        except Exception as e:
            logger.error(f"Error generating SAML request: {e}")
            raise ConfigurationError(f"Failed to generate SAML request: {e}")
    
    def get_login_url(self, **kwargs) -> Dict[str, Any]:
        """
        Get the URL for SAML login.
        
        Returns:
            Dictionary containing login URL and related data
            
        Raises:
            ConfigurationError: If login URL cannot be generated
        """
        try:
            # Load IdP metadata
            idp_metadata = self._load_idp_metadata()
            
            # Generate SAML request
            encoded_request, relay_state, request_data = self._generate_saml_request()
            
            # Build redirect URL
            redirect_url = f"{idp_metadata['sso_url']}?SAMLRequest={requests.utils.quote(encoded_request)}&RelayState={requests.utils.quote(relay_state)}"
            
            return {
                "login_url": redirect_url,
                "relay_state": relay_state,
                "request_id": request_data["request_id"],
                "expires_at": request_data["expires_at"]
            }
            
        except Exception as e:
            logger.error(f"Error generating login URL: {e}")
            raise ConfigurationError(f"Failed to generate login URL: {e}")
    
    def process_saml_response(self, saml_response: str, relay_state: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Process a SAML response from the IdP.
        
        Args:
            saml_response: Base64-encoded SAML response
            relay_state: Relay state from the request
            
        Returns:
            Tuple of (success, user_info, error_message)
            
        Raises:
            AuthenticationError: If response is invalid
        """
        try:
            # Decode SAML response
            decoded_response = base64.b64decode(saml_response).decode('utf-8')
            
            # Parse XML response
            root = ET.fromstring(decoded_response)
            
            # Define namespaces
            ns = {
                'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
                'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
                'ds': 'http://www.w3.org/2000/09/xmldsig#'
            }
            
            # Extract response ID and status
            response_id = root.get('ID')
            status_element = root.find('.//samlp:StatusCode', ns)
            status_value = status_element.get('Value') if status_element is not None else None
            
            # Check status
            if status_value != 'urn:oasis:names:tc:SAML:2.0:status:Success':
                status_message = root.find('.//samlp:StatusMessage', ns)
                message = status_message.text if status_message is not None else "Unknown error"
                return False, None, f"SAML authentication failed: {message}"
            
            # Extract InResponseTo to match with a pending request
            in_response_to = root.get('InResponseTo')
            if in_response_to and in_response_to in self.pending_requests:
                request_data = self.pending_requests[in_response_to]
                
                # Check if request has expired
                expires_at = datetime.fromisoformat(request_data["expires_at"])
                if datetime.now() > expires_at:
                    return False, None, "SAML request has expired"
                
                # Clean up the pending request
                del self.pending_requests[in_response_to]
            else:
                # If InResponseTo is missing or doesn't match, it might be a replay attack
                return False, None, "Invalid SAML response: No matching request found"
            
            # Extract assertion
            assertion = root.find('.//saml:Assertion', ns)
            if assertion is None:
                return False, None, "No assertion found in SAML response"
            
            # Verify signature if required
            if self.want_assertions_signed:
                signature = assertion.find('.//ds:Signature', ns)
                if signature is None:
                    return False, None, "Assertion is not signed"
                
                # In a real implementation, you would verify the signature here
                # This is a simplified version that just checks for presence
            
            # Extract subject (NameID)
            subject = assertion.find('.//saml:Subject', ns)
            if subject is None:
                return False, None, "No subject found in assertion"
            
            name_id = subject.find('.//saml:NameID', ns)
            if name_id is None:
                return False, None, "No NameID found in subject"
            
            user_identifier = name_id.text
            name_id_format = name_id.get('Format')
            
            # Extract attributes
            attributes = {}
            attribute_statements = assertion.findall('.//saml:AttributeStatement', ns)
            for statement in attribute_statements:
                for attribute in statement.findall('.//saml:Attribute', ns):
                    attr_name = attribute.get('Name')
                    attr_values = []
                    for value in attribute.findall('.//saml:AttributeValue', ns):
                        attr_values.append(value.text)
                    
                    if len(attr_values) == 1:
                        attributes[attr_name] = attr_values[0]
                    else:
                        attributes[attr_name] = attr_values
            
            # Build user info
            user_info = {
                "provider_id": self.provider_id,
                "provider_type": "saml",
                "user_id": user_identifier,
                "name_id_format": name_id_format,
                "attributes": attributes,
                "authenticated_at": datetime.now().isoformat()
            }
            
            # Extract common attributes if available
            if 'email' in attributes:
                user_info['email'] = attributes['email']
            elif 'mail' in attributes:
                user_info['email'] = attributes['mail']
            elif 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress' in attributes:
                user_info['email'] = attributes['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress']
            
            if 'givenName' in attributes:
                user_info['first_name'] = attributes['givenName']
            elif 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname' in attributes:
                user_info['first_name'] = attributes['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname']
            
            if 'surname' in attributes:
                user_info['last_name'] = attributes['surname']
            elif 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname' in attributes:
                user_info['last_name'] = attributes['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname']
            
            return True, user_info, None
            
        except Exception as e:
            logger.error(f"Error processing SAML response: {e}")
            return False, None, f"Failed to process SAML response: {e}"
    
    def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Authenticate a user with the SAML provider.
        
        Args:
            credentials: Authentication credentials
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        # SAML authentication is initiated by redirecting to the IdP
        # This method is typically not used directly
        return False, None, "SAML authentication requires redirect to IdP"
    
    def get_user_info(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Get user information from the SAML provider.
        
        Args:
            token: Authentication token
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        # SAML doesn't use tokens for user info retrieval
        # User info is extracted from the SAML response during authentication
        return False, None, "SAML doesn't support token-based user info retrieval"


class DirectoryServiceProvider(IdentityProvider):
    """
    Identity provider for directory services (LDAP, Active Directory).
    """
    def __init__(
        self,
        provider_id: str,
        name: str,
        config: Dict[str, Any],
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        super().__init__(
            provider_id=provider_id,
            name=name,
            provider_type="directory",
            config=config,
            is_active=is_active,
            metadata=metadata
        )
        
        # Validate required configuration
        required_fields = [
            "server_url", 
            "bind_dn",
            "bind_password",
            "base_dn",
            "user_search_filter"
        ]
        for field in required_fields:
            if field not in self.config:
                raise ConfigurationError(f"Missing required configuration field: {field}")
        
        # Initialize directory-specific properties
        self.server_url = self.config["server_url"]
        self.bind_dn = self.config["bind_dn"]
        self.bind_password = self.config["bind_password"]
        self.base_dn = self.config["base_dn"]
        self.user_search_filter = self.config["user_search_filter"]
        
        # Optional configuration
        self.use_ssl = self.config.get("use_ssl", True)
        self.use_tls = self.config.get("use_tls", False)
        self.timeout = self.config.get("timeout", 30)
        self.attribute_mapping = self.config.get("attribute_mapping", {
            "user_id": "uid",
            "email": "mail",
            "first_name": "givenName",
            "last_name": "sn",
            "display_name": "displayName",
            "groups": "memberOf"
        })
        
        # Initialize LDAP connection
        self._ldap_connection = None
    
    def _get_ldap_connection(self):
        """
        Get an LDAP connection.
        
        Returns:
            LDAP connection object
            
        Raises:
            ConfigurationError: If connection cannot be established
        """
        # This is a placeholder for actual LDAP connection logic
        # In a real implementation, you would use a library like python-ldap
        
        # Simulate connection
        if self._ldap_connection is None:
            try:
                # In a real implementation:
                # import ldap
                # ldap_connection = ldap.initialize(self.server_url)
                # ldap_connection.simple_bind_s(self.bind_dn, self.bind_password)
                
                # For this example, we'll just create a mock connection
                self._ldap_connection = {
                    "connected": True,
                    "server_url": self.server_url,
                    "bind_dn": self.bind_dn
                }
                
            except Exception as e:
                logger.error(f"Error connecting to LDAP server: {e}")
                raise ConfigurationError(f"Failed to connect to LDAP server: {e}")
        
        return self._ldap_connection
    
    def _search_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Search for a user in the directory.
        
        Args:
            username: Username to search for
            
        Returns:
            User attributes or None if not found
            
        Raises:
            AuthenticationError: If search fails
        """
        # This is a placeholder for actual LDAP search logic
        # In a real implementation, you would perform an LDAP search
        
        # Simulate search
        try:
            # Get connection
            connection = self._get_ldap_connection()
            
            # Prepare search filter
            search_filter = self.user_search_filter.replace("{username}", username)
            
            # In a real implementation:
            # result = connection.search_s(
            #     self.base_dn,
            #     ldap.SCOPE_SUBTREE,
            #     search_filter,
            #     list(self.attribute_mapping.values())
            # )
            
            # For this example, we'll simulate a result for a test user
            if username == "testuser":
                # Simulate found user
                return {
                    "uid": ["testuser"],
                    "mail": ["testuser@example.com"],
                    "givenName": ["Test"],
                    "sn": ["User"],
                    "displayName": ["Test User"],
                    "memberOf": [
                        "cn=users,ou=groups,dc=example,dc=com",
                        "cn=developers,ou=groups,dc=example,dc=com"
                    ]
                }
            
            # User not found
            return None
            
        except Exception as e:
            logger.error(f"Error searching for user: {e}")
            raise AuthenticationError(f"Failed to search for user: {e}")
    
    def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Authenticate a user with the directory service.
        
        Args:
            credentials: Authentication credentials
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        # Extract credentials
        username = credentials.get("username")
        password = credentials.get("password")
        
        if not username or not password:
            return False, None, "Username and password are required"
        
        try:
            # Search for user
            user_attributes = self._search_user(username)
            if not user_attributes:
                return False, None, "User not found"
            
            # In a real implementation, you would bind with the user's DN and password
            # to verify credentials
            # user_dn = result[0][0]  # DN from search result
            # connection.simple_bind_s(user_dn, password)
            
            # For this example, we'll simulate authentication
            if username == "testuser" and password == "password":
                # Map attributes to user info
                user_info = {
                    "provider_id": self.provider_id,
                    "provider_type": "directory"
                }
                
                for user_attr, ldap_attr in self.attribute_mapping.items():
                    if ldap_attr in user_attributes:
                        attr_values = user_attributes[ldap_attr]
                        if len(attr_values) == 1 and user_attr != "groups":
                            user_info[user_attr] = attr_values[0]
                        else:
                            user_info[user_attr] = attr_values
                
                return True, user_info, None
            
            return False, None, "Invalid credentials"
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return False, None, f"Authentication failed: {e}"
    
    def get_user_info(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Get user information from the directory service.
        
        Args:
            token: Authentication token
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        # Directory services don't use tokens for user info retrieval
        # User info is extracted during authentication
        return False, None, "Directory services don't support token-based user info retrieval"
    
    def get_user_groups(self, username: str) -> List[str]:
        """
        Get groups for a user.
        
        Args:
            username: Username to get groups for
            
        Returns:
            List of group names
            
        Raises:
            AuthenticationError: If group retrieval fails
        """
        try:
            # Search for user
            user_attributes = self._search_user(username)
            if not user_attributes:
                return []
            
            # Extract groups
            groups_attr = self.attribute_mapping.get("groups", "memberOf")
            if groups_attr in user_attributes:
                # In a real implementation, you would parse the DNs to extract group names
                # For this example, we'll simulate group extraction
                group_dns = user_attributes[groups_attr]
                group_names = []
                
                for dn in group_dns:
                    # Extract CN from DN
                    if dn.startswith("cn="):
                        cn = dn.split(",")[0].split("=")[1]
                        group_names.append(cn)
                
                return group_names
            
            return []
            
        except Exception as e:
            logger.error(f"Error retrieving user groups: {e}")
            raise AuthenticationError(f"Failed to retrieve user groups: {e}")
