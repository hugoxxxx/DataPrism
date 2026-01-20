#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command pattern implementation for undo/redo operations
撤销/重做操作的命令模式实现
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from collections import deque


class Command(ABC):
    """
    Abstract base class for commands (Command Pattern)
    命令的抽象基类（命令模式）
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command / 执行命令"""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command / 撤销命令"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get human-readable description / 获取人类可读的描述"""
        pass


class ModifyMetadataCommand(Command):
    """
    Command to modify metadata for a file
    修改文件元数据的命令
    """
    
    def __init__(
        self,
        file_path: str,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
        model: Any  # PhotoDataModel
    ):
        """
        Initialize metadata modification command
        初始化元数据修改命令
        
        Args:
            file_path: Path to image file / 图像文件路径
            old_data: Previous EXIF data / 先前的 EXIF 数据
            new_data: New EXIF data / 新的 EXIF 数据
            model: Data model reference / 数据模型引用
        """
        self.file_path = file_path
        self.old_data = old_data.copy()
        self.new_data = new_data.copy()
        self.model = model
    
    def execute(self) -> None:
        """Apply the modification / 应用修改"""
        self.model.set_exif_data(self.file_path, self.new_data)
        self.model.mark_modified(self.file_path)
    
    def undo(self) -> None:
        """Revert to old data / 恢复到旧数据"""
        self.model.set_exif_data(self.file_path, self.old_data)
    
    def get_description(self) -> str:
        """Get command description / 获取命令描述"""
        return f"Modify metadata: {self.file_path}"


class CommandHistory:
    """
    Manager for undo/redo operations
    撤销/重做操作的管理器
    """
    
    def __init__(self, max_history: int = 50):
        """
        Initialize command history
        初始化命令历史
        
        Args:
            max_history: Maximum number of commands to keep / 保留的最大命令数
        """
        self.undo_stack: deque = deque(maxlen=max_history)
        self.redo_stack: deque = deque(maxlen=max_history)
    
    def execute(self, command: Command) -> None:
        """
        Execute command and add to history
        执行命令并添加到历史
        
        Args:
            command: Command to execute / 要执行的命令
        """
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()  # Clear redo stack when new command is executed
    
    def undo(self) -> bool:
        """
        Undo last command
        撤销最后一个命令
        
        Returns:
            True if undo was successful / 撤销是否成功
        """
        if not self.undo_stack:
            return False
        
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        return True
    
    def redo(self) -> bool:
        """
        Redo last undone command
        重做最后撤销的命令
        
        Returns:
            True if redo was successful / 重做是否成功
        """
        if not self.redo_stack:
            return False
        
        command = self.redo_stack.pop()
        command.execute()
        self.undo_stack.append(command)
        return True
    
    def can_undo(self) -> bool:
        """Check if undo is possible / 检查是否可以撤销"""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible / 检查是否可以重做"""
        return len(self.redo_stack) > 0
    
    def clear(self) -> None:
        """Clear all history / 清空所有历史"""
        self.undo_stack.clear()
        self.redo_stack.clear()
