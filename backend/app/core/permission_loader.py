"""
Configurable permission loader for VitaChain RBAC
Loads permissions from configuration files instead of hardcoded values
"""

import yaml
from typing import Dict, List, Set, Any
from pathlib import Path
import structlog

from .permissions import UserRole, Permission, RBACManager

logger = structlog.get_logger("permission_loader")


class PermissionLoader:
    """Loads and manages RBAC permissions from configuration"""
    
    def __init__(self, config_path: str = "config/permissions.yaml"):
        self.config_path = Path(config_path)
        self._config_cache = {}
        self._permission_cache = {}
    
    def load_config(self) -> Dict[str, Any]:
        """Load permission configuration from YAML file"""
        try:
            if not self.config_path.exists():
                logger.warning(
                    "config_file_not_found",
                    config_path=str(self.config_path)
                )
                return {}
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            logger.info(
                "config_loaded",
                config_path=str(self.config_path),
                roles_count=len(config.get('roles', {}))
            )
            
            return config
            
        except Exception as e:
            logger.error(
                "config_load_error",
                config_path=str(self.config_path),
                error=str(e)
            )
            return {}
    
    def get_role_permissions(self, role: UserRole) -> Set[Permission]:
        """Get permissions for a specific role from config"""
        if not self._permission_cache:
            config = self.load_config()
            roles_config = config.get('roles', {})
            
            # Parse permissions from config
            role_config = roles_config.get(role.value, {})
            permissions_config = role_config.get('permissions', [])
            
            # Convert string permissions to Permission enum
            permissions = set()
            for perm_str in permissions_config:
                try:
                    permission = Permission(perm_str)
                    permissions.add(permission)
                except ValueError:
                    logger.warning(
                        "invalid_permission_in_config",
                        role=role.value,
                        permission=perm_str
                    )
                    continue
            
            self._permission_cache[role] = permissions
            
        return self._permission_cache.get(role, set())
    
    def get_role_hierarchy(self, role: UserRole) -> List[UserRole]:
        """Get role hierarchy from config"""
        if not self._config_cache:
            config = self.load_config()
            roles_config = config.get('roles', {})
            hierarchy_config = config.get('hierarchy', {})
            
            # Parse hierarchy from config
            role_hierarchy = []
            role_config = roles_config.get(role.value, {})
            inherits_from = role_config.get('inherits_from', [])
            
            for role_str in inherits_from:
                try:
                    inherited_role = UserRole(role_str)
                    role_hierarchy.append(inherited_role)
                except ValueError:
                    logger.warning(
                        "invalid_role_in_hierarchy",
                        role=role.value,
                        inherited_role=role_str
                    )
                    continue
            
            self._config_cache[role] = role_hierarchy
            
        return self._config_cache.get(role, [])
    
    def get_security_settings(self) -> Dict[str, Any]:
        """Get security settings from config"""
        if not self._config_cache:
            config = self.load_config()
            security_config = config.get('security', {})
            self._config_cache['security'] = security_config
            return security_config
        
        return self._config_cache.get('security', {})
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags from config"""
        if not self._config_cache:
            config = self.load_config()
            features_config = config.get('features', {})
            self._config_cache['features'] = features_config
            return features_config
        
        return self._config_cache.get('features', {})
    
    def reload_config(self) -> bool:
        """Reload configuration from file"""
        try:
            self._config_cache.clear()
            self._permission_cache.clear()
            config = self.load_config()
            return True
            
        except Exception as e:
            logger.error(
                "config_reload_error",
                error=str(e)
            )
            return False


class ConfigurableRBACManager(RBACManager):
    """RBAC Manager with configurable permissions"""
    
    def __init__(self, config_path: str = "config/permissions.yaml"):
        super().__init__()
        self.permission_loader = PermissionLoader(config_path)
        
        # Load permissions from config
        self._load_permissions_from_config()
    
    def _load_permissions_from_config(self):
        """Load role permissions from configuration file"""
        config = self.permission_loader.load_config()
        roles_config = config.get('roles', {})
        
        # Update role permissions from config
        for role_str, role_config in roles_config.items():
            try:
                role = UserRole(role_str)
                permissions = self.permission_loader.get_role_permissions(role)
                
                if permissions:
                    self._role_permissions[role] = permissions
                    
                    logger.info(
                        "role_permissions_loaded",
                        role=role.value,
                        permission_count=len(permissions)
                    )
                
            except ValueError as e:
                logger.error(
                    "invalid_role_in_config",
                    role=role_str,
                    error=str(e)
                )
        
        # Load role hierarchy from config
        hierarchy_config = config.get('hierarchy', {})
        for role_str, hierarchy_config in hierarchy_config.items():
            try:
                role = UserRole(role_str)
                role_hierarchy = self.permission_loader.get_role_hierarchy(role)
                
                if role_hierarchy:
                    self._role_hierarchy[role] = role_hierarchy
                    
                    logger.info(
                        "role_hierarchy_loaded",
                        role=role.value,
                        inherits_from=role_hierarchy
                    )
                
            except ValueError as e:
                logger.error(
                    "invalid_role_hierarchy_in_config",
                    role=role_str,
                    error=str(e)
                )
    
    def has_permission(self, user_role: UserRole, permission: Permission) -> bool:
        """Check permission using configurable permissions"""
        # Check if role exists in config
        if user_role not in self._role_permissions:
            logger.warning(
                "role_not_found_in_config",
                role=user_role.value
            )
            return False
        
        role_permissions = self._role_permissions.get(user_role, set())
        return permission in role_permissions
    
    def get_user_permissions(self, user_role: UserRole) -> Set[Permission]:
        """Get all permissions for a user role"""
        if user_role not in self._role_permissions:
            logger.warning(
                "role_not_found_in_config",
                role=user_role.value
            )
            return set()
        
        return self._role_permissions.get(user_role, set()).copy()
    
    def can_access_role(self, user_role: UserRole, target_role: UserRole) -> bool:
        """Check if user can access target role based on hierarchy"""
        if user_role == UserRole.ADMIN:
            return True  # Admin can access all roles
        
        if user_role not in self._role_hierarchy or target_role not in self._role_hierarchy:
            return False
        
        return target_role in self._role_hierarchy[user_role]


# Factory function to get appropriate RBAC manager
def get_rbac_manager(config_path: str = "config/permissions.yaml") -> RBACManager:
    """Get RBAC manager instance based on configuration"""
    try:
        # Check if config file exists
        if not Path(config_path).exists():
            logger.info(
                "config_file_not_found",
                config_path=config_path,
                using_default="true"
            )
            # Fall back to default RBAC manager
            return RBACManager()
        
        # Load configuration
        config = PermissionLoader(config_path).load_config()
        features = PermissionLoader(config_path).get_feature_flags()
        
        if features.get('configurable_permissions', False):
            logger.info(
                "using_default_rbac",
                reason="configurable_permissions_disabled"
            )
            return RBACManager()
        
        logger.info(
            "using_configurable_rbac",
            config_path=config_path
        )
        
        return ConfigurableRBACManager(config_path)


# Utility functions for backward compatibility
def create_default_config_file(config_path: str = "config/permissions.yaml") -> bool:
    """Create default configuration file if it doesn't exist"""
    if not Path(config_path).exists():
        try:
            # Import default permissions from hardcoded RBAC manager
            from .permissions import rbac_manager
            
            default_config = {
                'categories': {
                    'telemetry': {
                        'name': 'Télémétrie (KATARA)',
                        'description': 'Accès aux données des capteurs IoT',
                        'permissions': ['read:own_telemetry', 'write:own_devices']
                    },
                    'marketplace': {
                        'name': 'Marketplace (FARMARKET)',
                        'description': 'Accès au marché des produits agricoles',
                        'permissions': ['read:own_listings', 'write:own_listings', 'read:marketplace']
                    }
                },
                'roles': {
                    'FARMER': {
                        'name': 'Agriculteur',
                        'description': 'Producteur agricole utilisant KATARA et FARMARKET',
                        'inherits_from': [],
                        'permissions': [
                            'read:own_telemetry',
                            'write:own_devices',
                            'read:own_alerts',
                            'write:own_alerts',
                            'read:own_listings',
                            'write:own_listings',
                            'read:marketplace',
                            'write:own_orders',
                            'read:own_orders',
                            'read:profiles',
                            'write:profiles'
                        ]
                    }
                },
                'hierarchy': {
                    'ADMIN': {
                        'can_manage': ['SUPPORT', 'FARMER', 'RESTAURANT', 'CITIZEN'],
                        'can_impersonate': True
                    },
                    'SUPPORT': {
                        'can_manage': ['FARMER', 'RESTAURANT', 'CITIZEN'],
                        'can_impersonate': False
                    }
                },
                'security': {
                    'rate_limiting': {
                        'permission_checks': 100,
                        'data_access': 1000
                    },
                    'session_management': {
                        'max_sessions_per_user': 5,
                        'session_timeout': 3600
                    },
                    'audit_retention': {
                        'days': 90
                    }
                },
                'features': {
                    'configurable_permissions': True,
                    'audit_logging': True,
                    'rate_limiting': True,
                    'role_hierarchy': True,
                    'data_ownership': True
                }
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(
                "default_config_created",
                config_path=config_path
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "default_config_creation_error",
                config_path=config_path,
                error=str(e)
            )
            return False
