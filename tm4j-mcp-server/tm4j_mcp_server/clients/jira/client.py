"""
Jira Server API Client
"""

import requests
from typing import Optional, Dict, Any, List
from tm4j_mcp_server.clients.jira.models import JiraProject, JiraIssue, JiraCustomField


class JiraClient:
    """Клиент для Jira Server API v2"""
    
    def __init__(self, base_url: str, username: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_key = api_key
        self.session = requests.Session()
        
    def _get_headers(self) -> Dict[str, str]:
        """Получить заголовки для запросов"""
        return {
            'Authorization': f'Basic {self.username}:{self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Отправить запрос к API"""
        url = f'{self.base_url}/rest/api/2{endpoint}'
        try:
            response = self.session.request(method, url, headers=self._get_headers(), **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Jira API error: {e}")
            return None
    
    def get_projects(self) -> Optional[List[Dict[str, Any]]]:
        """
        Получить список проектов
        
        Endpoint: GET /rest/api/2/project
        """
        endpoint = '/project'
        data = self._request('GET', endpoint)
        return data
    
    def get_project(self, project_key: str) -> Optional[Dict[str, Any]]:
        """
        Получить данные проекта по ключу
        
        Endpoint: GET /rest/api/2/project/{projectKey}
        """
        endpoint = f'/project/{project_key}'
        data = self._request('GET', endpoint)
        return data
    
    def get_custom_fields(self, project_key: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Получить список кастомных полей
        
        Endpoint: GET /rest/api/2/customFieldManagement/customFields
        """
        endpoint = '/customFieldManagement/customFields'
        params = {}
        if project_key:
            params['projectId'] = project_key
        
        data = self._request('GET', endpoint, params=params)
        return data
    
    def get_custom_field(self, custom_field_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить данные кастомного поля по ID
        
        Endpoint: GET /rest/api/2/customFieldManagement/customFields/{customFieldId}
        """
        endpoint = f'/customFieldManagement/customFields/{custom_field_id}'
        data = self._request('GET', endpoint)
        return data
    
    def get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        Получить данные задачи по ключу
        
        Endpoint: GET /rest/api/2/issue/{issueKey}
        """
        endpoint = f'/issue/{issue_key}'
        data = self._request('GET', endpoint)
        return data
    
    def get_issue_custom_fields(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        Получить кастомные поля задачи
        
        Endpoint: GET /rest/api/2/issue/{issueKey}/fields
        """
        endpoint = f'/issue/{issue_key}/fields'
        data = self._request('GET', endpoint)
        return data
    
    def update_issue(self, issue_key: str, fields: Optional[Dict[str, Any]] = None,
                    update_fields: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Обновить задачу
        
        Endpoint: PUT /rest/api/2/issue/{issueKey}
        """
        endpoint = f'/issue/{issue_key}'
        payload = {}
        if fields:
            payload['fields'] = fields
        if update_fields:
            payload['update'] = update_fields
        
        data = self._request('PUT', endpoint, json=payload)
        return data
    
    def get_custom_field_values(self, issue_key: str, custom_field_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить значения кастомного поля для задачи
        
        Endpoint: GET /rest/api/2/issue/{issueKey}/customfield_{customFieldId}
        """
        endpoint = f'/issue/{issue_key}/customfield_{custom_field_id}'
        data = self._request('GET', endpoint)
        return data
    
    def update_custom_field(self, issue_key: str, custom_field_id: str, value: Any) -> Optional[Dict[str, Any]]:
        """
        Обновить значение кастомного поля для задачи
        
        Endpoint: PUT /rest/api/2/issue/{issueKey}/customfield_{customFieldId}
        """
        endpoint = f'/issue/{issue_key}/customfield_{custom_field_id}'
        payload = {'value': value}
        data = self._request('PUT', endpoint, json=payload)
        return data
    
    def search_issues(self, jql: str, start: int = 0, max_results: int = 100) -> Optional[Dict[str, Any]]:
        """
        Поиск задач по JQL
        
        Endpoint: GET /rest/api/2/search
        """
        endpoint = '/search'
        params = {
            'jql': jql,
            'start': start,
            'maxResults': max_results
        }
        data = self._request('GET', endpoint, params=params)
        return data
    
    def get_field_configuration(self) -> Optional[Dict[str, Any]]:
        """
        Получить конфигурацию полей
        
        Endpoint: GET /rest/api/2/fieldconfiguration
        """
        endpoint = '/fieldconfiguration'
        data = self._request('GET', endpoint)
        return data
    
    def get_field_configuration_columns(self, field_configuration_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Получить колонки для конфигурации полей
        
        Endpoint: GET /rest/api/2/fieldconfiguration/{fieldConfigurationId}/columns
        """
        endpoint = f'/fieldconfiguration/{field_configuration_id}/columns'
        data = self._request('GET', endpoint)
        return data