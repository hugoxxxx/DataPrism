#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV Parser for metadata import
CSV 元数据导入解析器
"""

import csv
from typing import List, Dict, Tuple
from pathlib import Path


class CSVParser:
    """
    CSV/TXT file parser with automatic delimiter detection
    支持自动检测分隔符的 CSV/TXT 文件解析器
    """
    
    def __init__(self, file_path: str):
        """
        Initialize CSV parser
        初始化 CSV 解析器
        
        Args:
            file_path: Path to CSV/TXT file / CSV/TXT 文件路径
        """
        self.file_path = file_path
        self.delimiter = None
        self.headers = []
        self.rows = []
    
    def _detect_delimiter(self) -> str:
        """
        Automatically detect delimiter (comma, tab, semicolon)
        自动检测分隔符（逗号、制表符、分号）
        
        Returns:
            Detected delimiter / 检测到的分隔符
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            
            # Count occurrences of potential delimiters
            # 统计潜在分隔符的出现次数
            comma_count = first_line.count(',')
            tab_count = first_line.count('\t')
            semicolon_count = first_line.count(';')
            
            # Choose the most frequent one
            # 选择出现最多的
            if tab_count > 0:
                return '\t'
            elif semicolon_count > comma_count:
                return ';'
            else:
                return ','
    
    def parse(self) -> Tuple[List[str], List[Dict[str, str]]]:
        """
        Parse CSV file and return headers and rows
        解析 CSV 文件并返回列标题和数据行
        
        Returns:
            Tuple of (headers, rows)
            headers: List of column names / 列名列表
            rows: List of dictionaries / 字典列表
        """
        # Detect delimiter
        self.delimiter = self._detect_delimiter()
        
        # Parse file
        with open(self.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=self.delimiter)
            self.headers = reader.fieldnames
            
            # Clean headers (remove whitespace)
            # 清理列标题（移除空白字符）
            self.headers = [h.strip() if h else h for h in self.headers]
            
            # Read all rows
            self.rows = []
            for row in reader:
                # Clean values (remove whitespace)
                # 清理值（移除空白字符）
                cleaned_row = {k.strip() if k else k: v.strip() if v else v 
                              for k, v in row.items()}
                self.rows.append(cleaned_row)
        
        return self.headers, self.rows
    
    def get_preview(self, num_rows: int = 5) -> List[Dict[str, str]]:
        """
        Get preview of first N rows
        获取前 N 行的预览
        
        Args:
            num_rows: Number of rows to preview / 预览行数
        
        Returns:
            List of first N rows / 前 N 行数据
        """
        return self.rows[:num_rows]
