"""
Confluence Server API Client
"""

import requests
from typing import Optional, Dict, Any, List
from tm4j_mcp_server.clients.confluence.models import ConfluenceSpace, ConfluencePage, ConfluenceComment


class ConfluenceClient:
    """Клиент для Confluence Server API v2"""
    
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
        url = f'{self.base_url}/rest/api/v3{endpoint}'
        try:
            response = self.session.request(method, url, headers=self._get_headers(), **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Confluence API error: {e}")
            return None
    
    def get_spaces(self, status: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Получить список пространств
        
        Endpoint: GET /rest/api/v3/space
        """
        endpoint = '/space'
        params = {}
        if status:
            params['status'] = status
        
        data = self._request('GET', endpoint, params=params)
        return data
    
    def get_space(self, space_key: str) -> Optional[Dict[str, Any]]:
        """
        Получить данные пространства по ключу
        
        Endpoint: GET /rest/api/v3/space/{spaceKey}
        """
        endpoint = f'/space/{space_key}'
        data = self._request('GET', endpoint)
        return data
    
    def get_pages(self, space_key: str, title: Optional[str] = None,
                 status: Optional[str] = None, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """
        Получить страницы в пространстве
        
        Endpoint: GET /rest/api/v3/page/list
        """
        endpoint = '/page/list'
        params = {
            'spaceKey': space_key,
            'limit': limit
        }
        if title:
            params['title'] = title
        if status:
            params['status'] = status
        
        data = self._request('GET', endpoint, params=params)
        return data
    
    def get_page(self, page_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить страницу по ID
        
        Endpoint: GET /rest/api/v3/page/{pageId}
        """
        endpoint = f'/page/{page_id}'
        data = self._request('GET', endpoint)
        return data
    
    def get_page_content(self, page_id: str, representation: str = 'storage') -> Optional[Dict[str, Any]]:
        """
        Получить контент страницы
        
        Endpoint: GET /rest/api/v3/content/{contentId}
        """
        endpoint = f'/content/{page_id}'
        params = {'representation': representation}
        data = self._request('GET', endpoint, params=params)
        return data
    
    def get_page_comments(self, page_id: str, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """
        Получить комментарии к странице
        
        Endpoint: GET /rest/api/v3/content/{contentId}/comment
        """
        endpoint = f'/content/{page_id}/comment'
        params = {'limit': limit}
        data = self._request('GET', endpoint, params=params)
        return data
    
    def create_page(self, space_key: str, title: str, body: str,
                   parent_page_id: Optional[str] = None,
                   status: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Создать страницу
        
        Endpoint: POST /rest/api/v3/page
        """
        endpoint = '/page'
        payload = {
            'space': {'key': space_key},
            'title': title,
            'body': body,
            'representation': 'storage'
        }
        if parent_page_id:
            payload['parent'] = {'type': 'page', 'id': parent_page_id}
        if status:
            payload['status'] = status
        
        data = self._request('POST', endpoint, json=payload)
        return data
    
    def update_page(self, page_id: str, title: Optional[str] = None,
                   body: Optional[str] = None, status: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Обновить страницу
        
        Endpoint: PUT /rest/api/v3/page/{pageId}
        """
        endpoint = f'/page/{page_id}'
        payload = {}
        if title:
            payload['title'] = title
        if body:
            payload['body'] = body
            payload['representation'] = 'storage'
        if status:
            payload['status'] = status
        
        data = self._request('PUT', endpoint, json=payload)
        return data
    
    def delete_page(self, page_id: str, recursive: bool = False) -> bool:
        """
        Удалить страницу
        
        Endpoint: DELETE /rest/api/v3/page/{pageId}
        """
        endpoint = f'/page/{page_id}'
        params = {'recursive': recursive}
        data = self._request('DELETE', endpoint, params=params)
        return data is not None
    
    def add_comment(self, page_id: str, body: str) -> Optional[Dict[str, Any]]:
        """
        Добавить комментарий к странице
        
        Endpoint: POST /rest/api/v3/content/{contentId}/comment
        """
        endpoint = f'/content/{page_id}/comment'
        payload = {'body': body, 'representation': 'storage'}
        data = self._request('POST', endpoint, json=payload)
        return data
    
    def get_attachment(self, page_id: str, attachment_key: str) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о приложении к странице
        
        Endpoint: GET /rest/api/v3/content/{contentId}/attachment/{attachmentKey}
        """
        endpoint = f'/content/{page_id}/attachment/{attachment_key}'
        data = self._request('GET', endpoint)
        return data
    
    def upload_attachment(self, page_id: str, file_path: str,
                         file_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Загрузить файл-приложение к странице
        
        Endpoint: POST /rest/api/v3/content/{contentId}/attachment
        """
        endpoint = f'/content/{page_id}/attachment'
        
        if file_name:
            files = {'file': open(file_path, 'rb')}
            data = self._request('POST', endpoint, files=files)
        else:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = self._request('POST', endpoint, files=files)
        
        if data:
            return data
        else:
            # Закрыть файл если ошибка
            if 'file' in locals():
                f.close()
            return None
    
    def delete_attachment(self, page_id: str, attachment_key: str) -> bool:
        """
        Удалить файл-приложение
        
        Endpoint: DELETE /rest/api/v3/content/{contentId}/attachment/{attachmentKey}
        """
        endpoint = f'/content/{page_id}/attachment/{attachment_key}'
        data = self._request('DELETE', endpoint)
        return data is not None