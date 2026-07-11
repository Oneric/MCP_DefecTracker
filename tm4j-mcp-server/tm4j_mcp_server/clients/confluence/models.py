"""
Confluence Server API Models
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class ConfluenceSpace:
    """Модель пространства Confluence"""
    key: str
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    permalink: Optional[str] = None


@dataclass
class ConfluencePage:
    """Модель страницы Confluence"""
    id: str
    title: str
    space_key: str
    status: Optional[str] = None
    version: int = 1
    creator: Optional[str] = None
    created: Optional[str] = None
    last_updated: Optional[str] = None
    permalink: Optional[str] = None


@dataclass
class ConfluenceComment:
    """Модель комментария Confluence"""
    id: str
    author: Optional[str] = None
    body: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None


@dataclass
class ConfluenceAttachment:
    """Модель приложения к странице Confluence"""
    key: str
    filename: str
    size: int
    mimetype: str
    created: Optional[str] = None
    author: Optional[str] = None
    thumbnail: Optional[str] = None