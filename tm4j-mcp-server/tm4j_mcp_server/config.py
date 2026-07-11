"""
Configuration module for TM4J MCP Server
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class JiraConfig:
    """Jira Server configuration"""
    url: str = "http://jira:8080"
    username: str = ""
    password: str = ""
    api_token: Optional[str] = None  # Для Jira Server 8.5+ с OAuth


@dataclass
class TM4JConfig:
    """TM4J API configuration"""
    url: str = "http://tm4j:8080"
    username: str = ""
    password: str = ""
    api_token: Optional[str] = None


@dataclass
class ConfluenceConfig:
    """Confluence API configuration"""
    url: str = "http://confluence:8090"
    username: str = ""
    password: str = ""
    api_token: Optional[str] = None


@dataclass
class StorageConfig:
    """SQLite storage configuration"""
    db_path: str = "./data/storage.db"


@dataclass
class PlaywrightConfig:
    """Playwright Docker configuration"""
    image: str = "mcr.microsoft.com/playwright:v1.40.0-jammy"
    container_name: str = "playwright-test-runner"
    browser: str = "chromium"
    headless: bool = True
    timeout: int = 30000  # 30 секунд


@dataclass
class SchedulerConfig:
    """Scheduler configuration"""
    check_interval: int = 60  # Проверка каждые 60 секунд
    max_concurrent_sessions: int = 2
    max_tasks_per_session: int = 100


@dataclass
class Config:
    """Main configuration class"""
    jira: JiraConfig = field(default_factory=JiraConfig)
    tm4j: TM4JConfig = field(default_factory=TM4JConfig)
    confluence: ConfluenceConfig = field(default_factory=ConfluenceConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    playwright: PlaywrightConfig = field(default_factory=PlaywrightConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        config = cls()
        
        # Jira
        config.jira.url = os.getenv("JIRA_URL", config.jira.url)
        config.jira.username = os.getenv("JIRA_USERNAME", config.jira.username)
        config.jira.password = os.getenv("JIRA_PASSWORD", config.jira.password)
        config.jira.api_token = os.getenv("JIRA_API_TOKEN", config.jira.api_token)
        
        # TM4J
        config.tm4j.url = os.getenv("TM4J_URL", config.tm4j.url)
        config.tm4j.username = os.getenv("TM4J_USERNAME", config.tm4j.username)
        config.tm4j.password = os.getenv("TM4J_PASSWORD", config.tm4j.password)
        config.tm4j.api_token = os.getenv("TM4J_API_TOKEN", config.tm4j.api_token)
        
        # Confluence
        config.confluence.url = os.getenv("CONFLUENCE_URL", config.confluence.url)
        config.confluence.username = os.getenv("CONFLUENCE_USERNAME", config.confluence.username)
        config.confluence.password = os.getenv("CONFLUENCE_PASSWORD", config.confluence.password)
        config.confluence.api_token = os.getenv("CONFLUENCE_API_TOKEN", config.confluence.api_token)
        
        # Storage
        config.storage.db_path = os.getenv("STORAGE_DB_PATH", config.storage.db_path)
        
        # Playwright
        config.playwright.image = os.getenv("PLAYWRIGHT_IMAGE", config.playwright.image)
        config.playwright.container_name = os.getenv("PLAYWRIGHT_CONTAINER_NAME", config.playwright.container_name)
        config.playwright.browser = os.getenv("PLAYWRIGHT_BROWSER", config.playwright.browser)
        config.playwright.headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() != "false"
        config.playwright.timeout = int(os.getenv("PLAYWRIGHT_TIMEOUT", config.playwright.timeout))
        
        # Scheduler
        config.scheduler.check_interval = int(os.getenv("SCHEDULER_CHECK_INTERVAL", config.scheduler.check_interval))
        config.scheduler.max_concurrent_sessions = int(os.getenv("MAX_CONCURRENT_SESSIONS", config.scheduler.max_concurrent_sessions))
        config.scheduler.max_tasks_per_session = int(os.getenv("MAX_TASKS_PER_SESSION", config.scheduler.max_tasks_per_session))
        
        return config
    
    @classmethod
    def get_config(cls) -> "Config":
        """Get configuration instance"""
        return cls.from_env()