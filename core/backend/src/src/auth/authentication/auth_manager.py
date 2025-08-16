"""
Authentication module for ApexAgent.

This module provides the core authentication functionality for the ApexAgent platform,
including user management, password handling, and session management.
"""

import os
import time
import uuid
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any, Tuple

# Try to import argon2, but fall back to bcrypt if not available
try:
    import argon2
    HASH_ALGORITHM = "argon2"
except ImportError:
    import bcrypt
    HASH_ALGORITHM = "bcrypt"

from src.core.error_handling.errors import AuthenticationError, ConfigurationError
from src.core.event_system.event_manager import EventManager

logger = logging.getLogger(__name__)

class User:
    """
    Represents a user in the system with authentication details.
    """
    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        user_id: str = None,
        first_name: str = None,
        last_name: str = None,
        is_active: bool = True,
        is_verified: bool = False,
        created_at: datetime = None,
        last_login: datetime = None,
        mfa_enabled: bool = False,
        mfa_methods: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.user_id = user_id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = is_active
        self.is_verified = is_verified
        self.created_at = created_at or datetime.now()
        self.last_login = last_login
        self.mfa_enabled = mfa_enabled
        self.mfa_methods = mfa_methods or []
        self.metadata = metadata or {}
        
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Convert user object to dictionary representation.
        
        Args:
            include_sensitive: Whether to include sensitive information like password hash
            
        Returns:
            Dictionary representation of the user
        """
        user_dict = {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "mfa_enabled": self.mfa_enabled,
            "mfa_methods": self.mfa_methods,
            "metadata": self.metadata
        }
        
        if include_sensitive:
            user_dict["password_hash"] = self.password_hash
            
        return user_dict
    
    @classmethod
    def from_dict(cls, user_dict: Dict[str, Any]) -> 'User':
        """
        Create a user object from dictionary representation.
        
        Args:
            user_dict: Dictionary representation of the user
            
        Returns:
            User object
        """
        created_at = user_dict.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        last_login = user_dict.get("last_login")
        if last_login and isinstance(last_login, str):
            last_login = datetime.fromisoformat(last_login)
            
        return cls(
            username=user_dict["username"],
            email=user_dict["email"],
            password_hash=user_dict["password_hash"],
            user_id=user_dict.get("user_id"),
            first_name=user_dict.get("first_name"),
            last_name=user_dict.get("last_name"),
            is_active=user_dict.get("is_active", True),
            is_verified=user_dict.get("is_verified", False),
            created_at=created_at,
            last_login=last_login,
            mfa_enabled=user_dict.get("mfa_enabled", False),
            mfa_methods=user_dict.get("mfa_methods", []),
            metadata=user_dict.get("metadata", {})
        )
        
    def __str__(self) -> str:
        return f"User(id={self.user_id}, username={self.username}, email={self.email})"


class PasswordManager:
    """
    Handles secure password operations including hashing and verification.
    """
    def __init__(self):
        self.algorithm = HASH_ALGORITHM
        
    def hash_password(self, password: str) -> str:
        """
        Hash a password using the configured algorithm.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password
        """
        if self.algorithm == "argon2":
            ph = argon2.PasswordHasher(
                time_cost=3,  # Number of iterations
                memory_cost=65536,  # 64MB
                parallelism=4,  # Number of parallel threads
                hash_len=32,  # Length of the hash in bytes
                salt_len=16  # Length of the salt in bytes
            )
            return ph.hash(password)
        elif self.algorithm == "bcrypt":
            salt = bcrypt.gensalt(rounds=12)
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        else:
            raise ConfigurationError(f"Unsupported password hashing algorithm: {self.algorithm}")
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against a hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Hashed password to verify against
            
        Returns:
            True if password matches hash, False otherwise
        """
        try:
            if self.algorithm == "argon2":
                ph = argon2.PasswordHasher()
                ph.verify(password_hash, password)
                return True
            elif self.algorithm == "bcrypt":
                return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
            else:
                raise ConfigurationError(f"Unsupported password hashing algorithm: {self.algorithm}")
        except (argon2.exceptions.VerifyMismatchError, ValueError):
            return False
    
    def needs_rehash(self, password_hash: str) -> bool:
        """
        Check if a password hash needs to be updated due to algorithm changes.
        
        Args:
            password_hash: Hashed password to check
            
        Returns:
            True if password needs rehashing, False otherwise
        """
        if self.algorithm == "argon2":
            ph = argon2.PasswordHasher()
            try:
                return ph.check_needs_rehash(password_hash)
            except:
                # If we can't check, assume it needs rehashing
                return True
        elif self.algorithm == "bcrypt":
            # Simple check for bcrypt - if it starts with $2b$ and has rounds < 12
            if password_hash.startswith('$2b$'):
                rounds = int(password_hash.split('$')[2])
                return rounds < 12
            return True
        else:
            raise ConfigurationError(f"Unsupported password hashing algorithm: {self.algorithm}")


class Session:
    """
    Represents a user session with authentication details.
    """
    def __init__(
        self,
        user_id: str,
        session_id: str = None,
        created_at: datetime = None,
        expires_at: datetime = None,
        ip_address: str = None,
        user_agent: str = None,
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = user_id
        self.created_at = created_at or datetime.now()
        # Default session expiration is 24 hours
        self.expires_at = expires_at or (self.created_at + timedelta(hours=24))
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.is_active = is_active
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert session object to dictionary representation.
        
        Returns:
            Dictionary representation of the session
        """
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, session_dict: Dict[str, Any]) -> 'Session':
        """
        Create a session object from dictionary representation.
        
        Args:
            session_dict: Dictionary representation of the session
            
        Returns:
            Session object
        """
        created_at = session_dict.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        expires_at = session_dict.get("expires_at")
        if expires_at and isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
            
        return cls(
            user_id=session_dict["user_id"],
            session_id=session_dict.get("session_id"),
            created_at=created_at,
            expires_at=expires_at,
            ip_address=session_dict.get("ip_address"),
            user_agent=session_dict.get("user_agent"),
            is_active=session_dict.get("is_active", True),
            metadata=session_dict.get("metadata", {})
        )
    
    def is_expired(self) -> bool:
        """
        Check if the session is expired.
        
        Returns:
            True if session is expired, False otherwise
        """
        return datetime.now() > self.expires_at
    
    def __str__(self) -> str:
        return f"Session(id={self.session_id}, user_id={self.user_id}, expires={self.expires_at})"


class AuthenticationManager:
    """
    Manages user authentication, including registration, login, and session management.
    """
    def __init__(self, event_manager: EventManager = None):
        self.users: Dict[str, User] = {}  # user_id -> User
        self.username_index: Dict[str, str] = {}  # username -> user_id
        self.email_index: Dict[str, str] = {}  # email -> user_id
        self.sessions: Dict[str, Session] = {}  # session_id -> Session
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> [session_id]
        self.password_manager = PasswordManager()
        self.event_manager = event_manager or EventManager()
        
        # Rate limiting for login attempts
        self.login_attempts: Dict[str, List[float]] = {}  # username/ip -> [timestamp]
        self.max_login_attempts = 5  # Maximum number of failed login attempts
        self.login_lockout_time = 300  # Lockout time in seconds (5 minutes)
        
    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
        metadata: Dict[str, Any] = None
    ) -> User:
        """
        Register a new user.
        
        Args:
            username: Unique username
            email: User's email address
            password: Plain text password
            first_name: User's first name
            last_name: User's last name
            metadata: Additional user metadata
            
        Returns:
            Newly created User object
            
        Raises:
            AuthenticationError: If username or email already exists
        """
        # Check if username or email already exists
        if username.lower() in [u.lower() for u in self.username_index.keys()]:
            raise AuthenticationError(f"Username '{username}' already exists")
        
        if email.lower() in [e.lower() for e in self.email_index.keys()]:
            raise AuthenticationError(f"Email '{email}' already exists")
        
        # Hash the password
        password_hash = self.password_manager.hash_password(password)
        
        # Create the user
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            metadata=metadata
        )
        
        # Store the user
        self.users[user.user_id] = user
        self.username_index[username.lower()] = user.user_id
        self.email_index[email.lower()] = user.user_id
        
        # Emit user registration event
        self.event_manager.emit_event("user.registered", {
            "user_id": user.user_id,
            "username": username,
            "email": email,
            "timestamp": datetime.now().isoformat()
        })
        
        return user
    
    def authenticate_user(
        self,
        username_or_email: str,
        password: str,
        ip_address: str = None,
        user_agent: str = None
    ) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Authenticate a user with username/email and password.
        
        Args:
            username_or_email: Username or email to authenticate
            password: Plain text password
            ip_address: IP address of the client
            user_agent: User agent of the client
            
        Returns:
            Tuple of (success, user, error_message)
        """
        # Check rate limiting
        rate_limit_key = f"{username_or_email.lower()}:{ip_address or 'unknown'}"
        if self._is_rate_limited(rate_limit_key):
            return False, None, "Too many failed login attempts. Please try again later."
        
        # Find the user
        user = self._find_user_by_username_or_email(username_or_email)
        if not user:
            # Record failed attempt
            self._record_login_attempt(rate_limit_key, success=False)
            return False, None, "Invalid username or password"
        
        # Check if user is active
        if not user.is_active:
            return False, None, "Account is disabled"
        
        # Verify password
        if not self.password_manager.verify_password(password, user.password_hash):
            # Record failed attempt
            self._record_login_attempt(rate_limit_key, success=False)
            return False, None, "Invalid username or password"
        
        # Check if password needs rehashing
        if self.password_manager.needs_rehash(user.password_hash):
            # Update password hash with new algorithm/parameters
            user.password_hash = self.password_manager.hash_password(password)
        
        # Update last login time
        user.last_login = datetime.now()
        
        # Record successful login attempt
        self._record_login_attempt(rate_limit_key, success=True)
        
        # Emit user login event
        self.event_manager.emit_event("user.login", {
            "user_id": user.user_id,
            "username": user.username,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.now().isoformat()
        })
        
        return True, user, None
    
    def create_session(
        self,
        user: User,
        ip_address: str = None,
        user_agent: str = None,
        duration_hours: int = 24,
        metadata: Dict[str, Any] = None
    ) -> Session:
        """
        Create a new session for a user.
        
        Args:
            user: User to create session for
            ip_address: IP address of the client
            user_agent: User agent of the client
            duration_hours: Session duration in hours
            metadata: Additional session metadata
            
        Returns:
            Newly created Session object
        """
        # Create the session
        session = Session(
            user_id=user.user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.now() + timedelta(hours=duration_hours),
            metadata=metadata
        )
        
        # Store the session
        self.sessions[session.session_id] = session
        
        # Add to user sessions
        if user.user_id not in self.user_sessions:
            self.user_sessions[user.user_id] = []
        self.user_sessions[user.user_id].append(session.session_id)
        
        # Emit session created event
        self.event_manager.emit_event("session.created", {
            "session_id": session.session_id,
            "user_id": user.user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "expires_at": session.expires_at.isoformat(),
            "timestamp": datetime.now().isoformat()
        })
        
        return session
    
    def validate_session(self, session_id: str) -> Tuple[bool, Optional[User], Optional[Session]]:
        """
        Validate a session and return the associated user.
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            Tuple of (is_valid, user, session)
        """
        # Check if session exists
        if session_id not in self.sessions:
            return False, None, None
        
        session = self.sessions[session_id]
        
        # Check if session is active
        if not session.is_active:
            return False, None, session
        
        # Check if session is expired
        if session.is_expired():
            # Invalidate the session
            session.is_active = False
            return False, None, session
        
        # Get the user
        if session.user_id not in self.users:
            # Session references a non-existent user
            session.is_active = False
            return False, None, session
        
        user = self.users[session.user_id]
        
        # Check if user is active
        if not user.is_active:
            session.is_active = False
            return False, None, session
        
        return True, user, session
    
    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate a session.
        
        Args:
            session_id: Session ID to invalidate
            
        Returns:
            True if session was invalidated, False if session doesn't exist
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        session.is_active = False
        
        # Emit session invalidated event
        self.event_manager.emit_event("session.invalidated", {
            "session_id": session_id,
            "user_id": session.user_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def invalidate_all_user_sessions(self, user_id: str) -> int:
        """
        Invalidate all sessions for a user.
        
        Args:
            user_id: User ID to invalidate sessions for
            
        Returns:
            Number of sessions invalidated
        """
        if user_id not in self.user_sessions:
            return 0
        
        count = 0
        for session_id in self.user_sessions[user_id]:
            if self.invalidate_session(session_id):
                count += 1
        
        return count
    
    def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Change a user's password.
        
        Args:
            user_id: User ID to change password for
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            Tuple of (success, error_message)
        """
        # Check if user exists
        if user_id not in self.users:
            return False, "User not found"
        
        user = self.users[user_id]
        
        # Verify current password
        if not self.password_manager.verify_password(current_password, user.password_hash):
            return False, "Current password is incorrect"
        
        # Hash the new password
        user.password_hash = self.password_manager.hash_password(new_password)
        
        # Emit password changed event
        self.event_manager.emit_event("user.password_changed", {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True, None
    
    def reset_password(
        self,
        user_id: str,
        new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Reset a user's password (admin function).
        
        Args:
            user_id: User ID to reset password for
            new_password: New password to set
            
        Returns:
            Tuple of (success, error_message)
        """
        # Check if user exists
        if user_id not in self.users:
            return False, "User not found"
        
        user = self.users[user_id]
        
        # Hash the new password
        user.password_hash = self.password_manager.hash_password(new_password)
        
        # Invalidate all sessions for this user
        self.invalidate_all_user_sessions(user_id)
        
        # Emit password reset event
        self.event_manager.emit_event("user.password_reset", {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True, None
    
    def update_user(
        self,
        user_id: str,
        email: str = None,
        first_name: str = None,
        last_name: str = None,
        is_active: bool = None,
        is_verified: bool = None,
        metadata: Dict[str, Any] = None
    ) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Update a user's information.
        
        Args:
            user_id: User ID to update
            email: New email address
            first_name: New first name
            last_name: New last name
            is_active: New active status
            is_verified: New verified status
            metadata: New or updated metadata
            
        Returns:
            Tuple of (success, user, error_message)
        """
        # Check if user exists
        if user_id not in self.users:
            return False, None, "User not found"
        
        user = self.users[user_id]
        
        # Update email if provided and different
        if email and email.lower() != user.email.lower():
            # Check if email already exists
            if email.lower() in [e.lower() for e in self.email_index.keys()]:
                return False, user, f"Email '{email}' already exists"
            
            # Update email index
            del self.email_index[user.email.lower()]
            self.email_index[email.lower()] = user_id
            user.email = email
            user.is_verified = False  # Require re-verification
        
        # Update other fields if provided
        if first_name is not None:
            user.first_name = first_name
        
        if last_name is not None:
            user.last_name = last_name
        
        if is_active is not None:
            user.is_active = is_active
            
            # If user is deactivated, invalidate all sessions
            if not is_active:
                self.invalidate_all_user_sessions(user_id)
        
        if is_verified is not None:
            user.is_verified = is_verified
        
        if metadata is not None:
            # Update metadata (merge with existing)
            user.metadata.update(metadata)
        
        # Emit user updated event
        self.event_manager.emit_event("user.updated", {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True, user, None
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if user was deleted, False if user doesn't exist
        """
        # Check if user exists
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        
        # Invalidate all sessions
        self.invalidate_all_user_sessions(user_id)
        
        # Remove from indexes
        del self.username_index[user.username.lower()]
        del self.email_index[user.email.lower()]
        
        # Remove user
        del self.users[user_id]
        
        # Emit user deleted event
        self.event_manager.emit_event("user.deleted", {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID to get
            
        Returns:
            User object or None if not found
        """
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: Username to get
            
        Returns:
            User object or None if not found
        """
        user_id = self.username_index.get(username.lower())
        if user_id:
            return self.users.get(user_id)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: Email to get
            
        Returns:
            User object or None if not found
        """
        user_id = self.email_index.get(email.lower())
        if user_id:
            return self.users.get(user_id)
        return None
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session ID to get
            
        Returns:
            Session object or None if not found
        """
        return self.sessions.get(session_id)
    
    def get_user_sessions(self, user_id: str) -> List[Session]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: User ID to get sessions for
            
        Returns:
            List of Session objects
        """
        if user_id not in self.user_sessions:
            return []
        
        return [self.sessions[session_id] for session_id in self.user_sessions[user_id]
                if session_id in self.sessions]
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        count = 0
        current_time = datetime.now()
        
        for session_id, session in list(self.sessions.items()):
            if session.expires_at < current_time:
                session.is_active = False
                count += 1
        
        return count
    
    def _find_user_by_username_or_email(self, username_or_email: str) -> Optional[User]:
        """
        Find a user by username or email.
        
        Args:
            username_or_email: Username or email to find
            
        Returns:
            User object or None if not found
        """
        # Try username first
        user = self.get_user_by_username(username_or_email)
        if user:
            return user
        
        # Try email
        return self.get_user_by_email(username_or_email)
    
    def _is_rate_limited(self, key: str) -> bool:
        """
        Check if a key is rate limited.
        
        Args:
            key: Key to check
            
        Returns:
            True if rate limited, False otherwise
        """
        if key not in self.login_attempts:
            return False
        
        # Get attempts within the lockout window
        current_time = time.time()
        recent_attempts = [t for t in self.login_attempts[key]
                          if current_time - t < self.login_lockout_time]
        
        # Update attempts list
        self.login_attempts[key] = recent_attempts
        
        # Check if too many attempts
        return len(recent_attempts) >= self.max_login_attempts
    
    def _record_login_attempt(self, key: str, success: bool) -> None:
        """
        Record a login attempt.
        
        Args:
            key: Key to record attempt for
            success: Whether the attempt was successful
        """
        if success:
            # Clear attempts on success
            if key in self.login_attempts:
                del self.login_attempts[key]
            return
        
        # Record failed attempt
        if key not in self.login_attempts:
            self.login_attempts[key] = []
        
        self.login_attempts[key].append(time.time())
