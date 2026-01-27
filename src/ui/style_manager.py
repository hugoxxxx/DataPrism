#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Style Manager for DataPrism - High-End Studio Design System
DataPrism 样式管理器 - 高端影像工作站设计系统
"""

import json
import os
from typing import Dict, Any

class StyleManager:
    """
    Decoupled Style Manager supporting external JSON themes.
    解耦的样式管理器，支持从外部 JSON 加载主题。
    """
    
    _theme: Dict[str, Any] = {}
    
    @classmethod
    def load_theme(cls, theme_name: str = "studio_dark"):
        """Load theme from resources/themes/*.json"""
        try:
            # Look for theme file / 寻找主题文件
            # Assuming current file is in src/ui/
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            theme_path = os.path.join(base_path, "resources", "themes", f"{theme_name}.json")
            
            if os.path.exists(theme_path):
                with open(theme_path, 'r', encoding='utf-8') as f:
                    cls._theme = json.load(f)
                
                # Update static attributes for compatibility / 更新静态属性以保持兼容性
                colors = cls._theme.get("colors", {})
                typo = cls._theme.get("typography", {})
                
                cls.COLOR_BG_MAIN = colors.get("bg_main", cls.COLOR_BG_MAIN)
                cls.COLOR_BG_CARD = colors.get("bg_card", cls.COLOR_BG_CARD)
                cls.COLOR_BG_SIDEBAR = colors.get("bg_sidebar", cls.COLOR_BG_SIDEBAR)
                cls.COLOR_ACCENT = colors.get("accent", cls.COLOR_ACCENT)
                cls.COLOR_TEXT_PRIMARY = colors.get("text_primary", cls.COLOR_TEXT_PRIMARY)
                cls.COLOR_TEXT_SECONDARY = colors.get("text_secondary", cls.COLOR_TEXT_SECONDARY)
                cls.COLOR_BORDER = colors.get("border", cls.COLOR_BORDER)
                
                cls.FONT_FAMILY_MAIN = typo.get("family_main", cls.FONT_FAMILY_MAIN)
                cls.FONT_FAMILY_MONO = typo.get("family_mono", cls.FONT_FAMILY_MONO)
                cls.FONT_SIZE_BODY = typo.get("size_body", cls.FONT_SIZE_BODY)
                cls.FONT_SIZE_SMALL = typo.get("size_small", cls.FONT_SIZE_SMALL)
                cls.FONT_SIZE_TINY = typo.get("size_tiny", cls.FONT_SIZE_TINY)
                cls.FONT_SIZE_LCD = typo.get("size_lcd", cls.FONT_SIZE_LCD)
            else:
                # Minimal fallback if JSON is missing
                cls._theme = {
                    "colors": {"bg_main": "#101012", "text_primary": "#E0E0E0", "accent": "#D15400", "border": "#252528"},
                    "typography": {"family_main": "sans-serif", "size_body": "12px"}
                }
        except Exception as e:
            print(f"Failed to load theme: {e}")

    @classmethod
    def c(cls, key: str) -> str:
        """Helper to get a color value / 获取色彩值的助手函数"""
        if not cls._theme: cls.load_theme()
        return cls._theme.get("colors", {}).get(key, "#FF00FF") # Magenta for missing keys

    @classmethod
    def t(cls, key: str) -> str:
        """Helper to get a typography value / 获取字体值的助手函数"""
        if not cls._theme: cls.load_theme()
        return cls._theme.get("typography", {}).get(key, "12px")

    # --- Dynamic Tier Accessors for backward compatibility ---
    # These map the old static constants to the new theme JSON values
    
    @classmethod
    def _get_val(cls, cat: str, key: str, default: str) -> str:
        if not cls._theme: cls.load_theme()
        return cls._theme.get(cat, {}).get(key, default)

    # Colors
    @property
    def COLOR_BG_MAIN(cls): return cls._get_val("colors", "bg_main", "#101012")
    @property
    def COLOR_BG_CARD(cls): return cls._get_val("colors", "bg_card", "#1A1A1C")
    @property
    def COLOR_BG_SIDEBAR(cls): return cls._get_val("colors", "bg_sidebar", "#09090A")
    @property
    def COLOR_ACCENT(cls): return cls._get_val("colors", "accent", "#D15400")
    @property
    def COLOR_TEXT_PRIMARY(cls): return cls._get_val("colors", "text_primary", "#E0E0E0")
    @property
    def COLOR_TEXT_SECONDARY(cls): return cls._get_val("colors", "text_secondary", "#A8A8AB")
    @property
    def COLOR_BORDER(cls): return cls._get_val("colors", "border", "#252528")

    # Typography
    @property
    def FONT_FAMILY_MAIN(cls): return cls._get_val("typography", "family_main", '"Inter", sans-serif')
    @property
    def FONT_FAMILY_MONO(cls): return cls._get_val("typography", "family_mono", '"JetBrains Mono", monospace')
    @property
    def FONT_SIZE_BODY(cls): return cls._get_val("typography", "size_body", "13px")
    @property
    def FONT_SIZE_SMALL(cls): return cls._get_val("typography", "size_small", "12px")
    @property
    def FONT_SIZE_TINY(cls): return cls._get_val("typography", "size_tiny", "11px")
    @property
    def FONT_SIZE_LCD(cls): return cls._get_val("typography", "size_lcd", "24px")

    # Hack to make them work as class attributes (using meta-style or just defining them as class methods for now)
    # Since we can't easily use @property on a class without a metaclass in pure Python < 3.9, 
    # and to keep it simple, let's just use regular class attributes that we update in load_theme.
    
    # Static fallbacks for initialization
    COLOR_BG_MAIN = "#101012"
    COLOR_BG_CARD = "#1A1A1C"
    COLOR_BG_SIDEBAR = "#09090A"
    COLOR_ACCENT = "#D15400"
    COLOR_TEXT_PRIMARY = "#E0E0E0"
    COLOR_TEXT_SECONDARY = "#A8A8AB"
    COLOR_BORDER = "#252528"
    
    FONT_FAMILY_MAIN = '"Inter", sans-serif'
    FONT_FAMILY_MONO = '"JetBrains Mono", monospace'
    FONT_FAMILY_DISPLAY = '"Inter", sans-serif'
    FONT_SIZE_DISPLAY = "20px"
    FONT_SIZE_H1 = "16px"
    FONT_SIZE_H2 = "14px"
    FONT_SIZE_BODY = "13px"
    FONT_SIZE_SMALL = "12px"
    FONT_SIZE_TINY = "11px"
    FONT_SIZE_LCD = "24px"
    
    FONT_WEIGHT_LIGHT = "300"
    FONT_WEIGHT_REGULAR = "400"
    FONT_WEIGHT_MEDIUM = "500"
    FONT_WEIGHT_SEMIBOLD = "600"
    FONT_WEIGHT_BOLD = "700"

    @classmethod
    def get_main_style(cls):
        return f"""
            QMainWindow, QDialog {{
                background-color: {cls.c("bg_main")};
                color: {cls.c("text_primary")};
            }}
            QWidget {{
                color: {cls.c("text_primary")};
                font-family: {cls.t("family_main")};
                font-size: {cls.t("size_body")};
            }}
            QLabel {{
                color: {cls.c("text_primary")};
            }}
            /* Global Button Override for professional dialogs */
            QPushButton {{
                background-color: {cls.c("bg_card")};
                color: {cls.c("btn_secondary_text")};
                border: 1px solid {cls.c("border")};
                border-radius: 4px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: {cls.c("btn_secondary_hover")};
                border-color: {cls.c("accent")};
            }}
            /* Specific fix for QMessageBox buttons */
            QMessageBox QPushButton {{
                min-width: 80px;
                padding: 8px 20px;
                font-weight: 600;
            }}
            QSplitter::handle {{
                background-color: transparent;
            }}
            QSplitter::handle:horizontal {{
                border-left: 1px solid {cls.c("border")};
                width: 1px;
            }}
            
            /* Menu Styling */
            QMenu {{
                background-color: {cls.c("bg_card")};
                border: 1px solid {cls.c("border")};
                border-radius: 4px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 24px 6px 12px;
                background-color: transparent;
                color: {cls.c("text_primary")};
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {cls.c("btn_secondary_hover")};
                color: {cls.c("text_primary")};
            }}
            QMenu::separator {{
                height: 1px;
                background: {cls.c("border")};
                margin: 4px 0px;
            }}
            
            /* Tooltip Styling */
            QToolTip {{
                background-color: {cls.c("bg_card")};
                color: {cls.c("text_primary")};
                border: 1px solid {cls.c("border")};
                border-radius: 4px;
                padding: 4px;
            }}
        """

    @classmethod
    def get_button_style(cls, tier='secondary'):
        """3-Tier Hasselblad-style button system"""
        if tier == 'primary':
            bg = cls.c("btn_primary_bg")
            text = cls.c("btn_primary_text")
            border = "none"
            hover_bg = cls.c("btn_primary_hover")
        elif tier == 'ghost':
            bg = "transparent"
            text = cls.c("btn_ghost_text")
            border = "none"
            hover_bg = cls.c("btn_ghost_hover")
        else: # secondary
            bg = "transparent"
            text = cls.c("btn_secondary_text")
            border = f"1px solid {cls.c('btn_secondary_border')}"
            hover_bg = cls.c("btn_secondary_hover")

        return f"""
            QPushButton {{
                background-color: {bg};
                color: {text};
                border: {border};
                border-radius: 4px;
                padding: 10px 18px;
                font-weight: 500;
                font-size: {cls.t("size_small")};
                text-align: center;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                {"border-color: " + cls.c("accent") + ";" if tier == 'secondary' else ""}
                {"color: #FFFFFF;" if tier == 'ghost' else ""}
            }}
            QPushButton:pressed {{
                background-color: rgba(0,0,0,0.2);
            }}
        """

    @classmethod
    def get_sidebar_style(cls):
        return f"""
            QWidget#Sidebar {{
                background-color: {cls.c("bg_sidebar")};
                border-right: 1px solid {cls.c("border")};
            }}
            QLabel#SidebarTitle {{
                color: {cls.c("text_secondary")};
                font-weight: 600;
                font-size: {cls.t("size_tiny")};
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 15px;
                margin-bottom: 5px;
            }}
        """

    @classmethod
    def get_sidebar_item_style(cls):
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {cls.c("text_secondary")};
                border: none;
                border-radius: 4px;
                padding: 12px 14px;
                font-weight: 500;
                font-size: {cls.t("size_small")};
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {cls.c("btn_secondary_hover")};
                color: {cls.c("text_primary")};
            }}
            QPushButton:checked {{
                background-color: transparent;
                color: {cls.c("accent")};
                border-left: 2px solid {cls.c("accent")};
                font-weight: 600;
            }}
        """

    @classmethod
    def get_card_style(cls):
        return f"""
            QWidget#Card, QFrame#Card {{
                background-color: {cls.c("bg_card")};
                border: 1px solid {cls.c("border")};
                border-radius: 8px;
            }}
        """

    @classmethod
    def get_input_style(cls):
        return f"""
            QLineEdit, QComboBox, QSpinBox {{
                background-color: {cls.c("bg_card")};
                border: 1px solid {cls.c("border")};
                border-radius: 4px;
                padding: 8px 12px;
                color: {cls.c("text_primary")};
                selection-background-color: {cls.c("accent")};
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {cls.c("accent")};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
                subcontrol-origin: padding;
                subcontrol-position: top right;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
                image: none; /* Clear default arrow if problematic / 如果有问题则清除默认箭头 */
                border-left: 1px solid transparent; /* Placeholder / 占位符 */
                border-top: 1px solid {cls.c("text_secondary")};
                border-right: 1px solid transparent; 
                margin-top: 4px; 
            }}
            /* Attempt a pure CSS arrow trick or relies on default but colorized */
            QComboBox::down-arrow {{
                image: none;
                width: 0; 
                height: 0; 
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {cls.c("text_secondary")};
                margin-right: 6px;
                margin-top: 2px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {cls.c("bg_card")};
                border: 1px solid {cls.c("border")};
                selection-background-color: {cls.c("accent")};
                selection-color: #FFFFFF;
                color: {cls.c("text_primary")};
                outline: none;
                padding: 4px;
                min-width: 150px;
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 24px;
                padding: 4px 8px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {cls.c("btn_secondary_hover")};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {cls.c("accent")};
                color: #FFFFFF;
            }}
        """

    @classmethod
    def get_table_style(cls):
        # Unify for professional "Precision Sync" aesthetic
        # 统一字号以达成极简且严谨的“视觉协调”感
        font_size = cls.t("size_tiny") # 11px
        
        return f"""
            QTableView {{
                background-color: {cls.c("bg_main")};
                alternate-background-color: {cls.c("table_alternate")};
                selection-background-color: {cls.c("table_selection_bg")};
                selection-color: {cls.c("accent")};
                border: none;
                gridline-color: transparent;
                font-size: {font_size};
            }}
            QHeaderView::section {{
                background-color: {cls.c("bg_main")};
                color: {cls.c("text_secondary")};
                padding: 12px;
                border: none;
                border-bottom: 2px solid {cls.c("border")};
                letter-spacing: 1.5px;
                font-size: {font_size};
                font-weight: 600;
            }}
        """

    @classmethod
    def get_list_style(cls):
        return f"""
            QListWidget {{
                background-color: {cls.c("bg_main")};
                border: 1px solid {cls.c("border")};
                border-radius: 4px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px;
                color: {cls.c("text_secondary")};
            }}
            QListWidget::item:selected {{
                background-color: {cls.c("accent")};
                color: #FFFFFF;
                font-weight: bold;
            }}
        """
    
    @classmethod
    def get_lcd_style(cls):
        return f"""
            QWidget#LCDPanel {{
                background-color: #050506;
                border: 1px solid {cls.c("border")};
                border-radius: 4px;
            }}
            /* Specific ID list for better compatibility / 为了更好的兼容性使用具体 ID 列表 */
            QLabel#LCDValue_Ap, QLabel#LCDValue_Sh, QLabel#LCDValue_Iso {{
                color: {cls.c("accent")};
                font-family: {cls.t("family_mono")};
                font-size: {cls.t("size_lcd")};
                font-weight: 700;
            }}
            QLabel#LCDLabel_Ap, QLabel#LCDLabel_Sh, QLabel#LCDLabel_Iso {{
                color: {cls.c("text_secondary")};
                font-size: {cls.t("size_tiny")};
                text-transform: uppercase;
                font-weight: 600;
                margin-bottom: 4px;
            }}
        """
