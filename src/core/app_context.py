#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application context / service locator for dependency injection
应用程序上下文/服务定位器，用于依赖注入
"""

from typing import Dict, Any, Type, TypeVar
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class AppContext:
    """
    Centralized service management for loose coupling
    集中式服务管理，用于松耦合
    
    Implements singleton pattern with lazy initialization
    实现单例模式和延迟初始化
    """
    
    _instance = None
    _services: Dict[str, Any] = {}
    
    def __new__(cls):
        """Implement singleton pattern / 实现单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, service_name: str, service: Any) -> None:
        """
        Register a service
        注册服务
        
        Args:
            service_name: Name of service / 服务名称
            service: Service instance / 服务实例
        """
        cls._services[service_name] = service
        logger.debug(f"Registered service: {service_name}")
    
    @classmethod
    def get(cls, service_name: str) -> Any:
        """
        Get a registered service
        获取已注册的服务
        
        Args:
            service_name: Name of service / 服务名称
        
        Returns:
            Service instance / 服务实例
        
        Raises:
            KeyError: If service not found / 如果未找到服务
        """
        if service_name not in cls._services:
            raise KeyError(f"Service not found: {service_name}")
        return cls._services[service_name]
    
    @classmethod
    def has(cls, service_name: str) -> bool:
        """Check if service is registered / 检查服务是否已注册"""
        return service_name in cls._services
    
    @classmethod
    def clear(cls) -> None:
        """Clear all services (for testing) / 清空所有服务（用于测试）"""
        cls._services.clear()
