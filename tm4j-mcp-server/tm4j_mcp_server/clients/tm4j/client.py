"""
TM4J API Client
"""

import requests
from typing import Optional, Dict, Any, List
from tm4j_mcp_server.clients.tm4j.models import (
    TM4JTestRun,
    TM4JTestCase,
    TM4JTestResult,
    TM4JTestExecution,
    TM4JFolder
)


class TM4JClient:
    """Клиент для TM4J API v2"""
    
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
        url = f'{self.base_url}{endpoint}'
        try:
            response = self.session.request(method, url, headers=self._get_headers(), **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"TM4J API error: {e}")
            return None
    
    def get_test_run(self, test_run_key: str) -> Optional[Dict[str, Any]]:
        """
        Получить данные TestCycle по ключу
        
        Endpoint: GET /testrun/{testRunKey}
        """
        endpoint = f'/testrun/{test_run_key}'
        data = self._request('GET', endpoint)
        return data
    
    def get_test_case(self, test_case_key: str) -> Optional[Dict[str, Any]]:
        """
        Получить данные TestCase по ключу
        
        Endpoint: GET /testcase/{testCaseKey}
        """
        endpoint = f'/testcase/{test_case_key}'
        data = self._request('GET', endpoint)
        return data
    
    def get_test_case_results(self, test_case_key: str) -> Optional[List[Dict[str, Any]]]:
        """
        Получить все результаты тест-кейса
        
        Endpoint: GET /testcase/{testCaseKey}/testresult
        """
        endpoint = f'/testcase/{test_case_key}/testresult'
        data = self._request('GET', endpoint)
        return data
    
    def get_latest_test_result(self, test_case_key: str) -> Optional[Dict[str, Any]]:
        """
        Получить последний результат тест-кейса
        
        Endpoint: GET /testcase/{testCaseKey}/testresult/latest
        """
        endpoint = f'/testcase/{test_case_key}/testresult/latest'
        data = self._request('GET', endpoint)
        return data
    
    def update_test_result(self, test_result_key: str, status: str, 
                          start_time: Optional[str] = None,
                          end_time: Optional[str] = None,
                          steps: Optional[List[Dict[str, Any]]] = None,
                          attachments: Optional[List[Dict[str, Any]]] = None,
                          error_message: Optional[str] = None,
                          stack_trace: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Обновить результат тест-кейса
        
        Endpoint: PUT /testresult/{testResultKey}
        """
        endpoint = f'/testresult/{test_result_key}'
        payload = {
            'status': status,
            'startTime': start_time,
            'endTime': end_time,
            'steps': steps,
            'attachments': attachments,
            'errorMessage': error_message,
            'stackTrace': stack_trace
        }
        # Удалить None значения
        payload = {k: v for k, v in payload.items() if v is not None}
        
        data = self._request('PUT', endpoint, json=payload)
        return data
    
    def get_test_runs(self, folder_key: Optional[str] = None, 
                     status: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Получить список TestCycles
        
        Endpoint: GET /testrun
        """
        endpoint = '/testrun'
        params = {}
        if folder_key:
            params['folderKey'] = folder_key
        if status:
            params['status'] = status
        
        data = self._request('GET', endpoint, params=params)
        return data
    
    def get_test_cases_in_folder(self, folder_key: str) -> Optional[List[Dict[str, Any]]]:
        """
        Получить тест-кейсы в папке
        
        Endpoint: GET /folder/{folderKey}/testcase
        """
        endpoint = f'/folder/{folder_key}/testcase'
        data = self._request('GET', endpoint)
        return data
    
    def get_folders(self) -> Optional[List[Dict[str, Any]]]:
        """
        Получить список папок
        
        Endpoint: GET /folder
        """
        endpoint = '/folder'
        data = self._request('GET', endpoint)
        return data
    
    def get_test_executions(self, test_run_key: str) -> Optional[List[Dict[str, Any]]]:
        """
        Получить список выполнений тестов
        
        Endpoint: GET /testrun/{testRunKey}/testexecution
        """
        endpoint = f'/testrun/{test_run_key}/testexecution'
        data = self._request('GET', endpoint)
        return data
    
    def create_test_execution(self, test_run_key: str, test_case_key: str,
                             status: str = 'PENDING') -> Optional[Dict[str, Any]]:
        """
        Создать выполнение теста
        
        Endpoint: POST /testrun/{testRunKey}/testexecution
        """
        endpoint = f'/testrun/{test_run_key}/testexecution'
        payload = {
            'testCaseKey': test_case_key,
            'status': status
        }
        data = self._request('POST', endpoint, json=payload)
        return data
    
    def update_test_execution(self, test_execution_key: str, status: str,
                             start_time: Optional[str] = None,
                             end_time: Optional[str] = None,
                             steps: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
        """
        Обновить выполнение теста
        
        Endpoint: PUT /testexecution/{testExecutionKey}
        """
        endpoint = f'/testexecution/{test_execution_key}'
        payload = {
            'status': status,
            'startTime': start_time,
            'endTime': end_time,
            'steps': steps
        }
        # Удалить None значения
        payload = {k: v for k, v in payload.items() if v is not None}
        
        data = self._request('PUT', endpoint, json=payload)
        return data
    
    def upload_attachment(self, test_execution_key: str, file_path: str,
                         file_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Загрузить файл-приложение к выполнению теста
        
        Endpoint: POST /testexecution/{testExecutionKey}/attachment
        """
        endpoint = f'/testexecution/{test_execution_key}/attachment'
        
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
    
    def delete_attachment(self, test_execution_key: str, attachment_key: str) -> bool:
        """
        Удалить файл-приложение
        
        Endpoint: DELETE /testexecution/{testExecutionKey}/attachment/{attachmentKey}
        """
        endpoint = f'/testexecution/{test_execution_key}/attachment/{attachment_key}'
        data = self._request('DELETE', endpoint)
        return data is not None