# HDFS客户端模块
# 使用WebHDFS REST API访问HDFS

import os
import time
import requests
import json
from typing import Optional, Dict, Any, List


class WebHDFSClient:
    """WebHDFS客户端类"""
    
    def __init__(self, host: str = 'master', port: int = 9870, user: str = 'root'):
        """初始化WebHDFS客户端
        
        Args:
            host: HDFS NameNode主机名
            port: HDFS NameNode HTTP端口
            user: HDFS用户名
        """
        self.host = host
        self.port = port
        self.user = user
        self.base_url = f"http://{host}:{port}/webhdfs/v1"
    
    def _make_request(self, method: str, path: str, params: Dict[str, Any] = None, data: bytes = None) -> Optional[requests.Response]:
        """发送HTTP请求
        
        Args:
            method: HTTP方法
            path: HDFS路径
            params: 请求参数
            data: 请求数据
            
        Returns:
            HTTP响应
        """
        url = f"{self.base_url}{path}"
        params = params or {}
        params['user.name'] = self.user
        
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.request(method, url, params=params, data=data, timeout=30)
                return response
            except requests.exceptions.ConnectionError as e:
                print(f"Connection error to {url} (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    print("Retrying...")
                    time.sleep(2)
                else:
                    print("All retry attempts failed")
                    return None
            except requests.exceptions.Timeout as e:
                print(f"Timeout error to {url} (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    print("Retrying...")
                    time.sleep(2)
                else:
                    print("All retry attempts failed")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Request error to {url} (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    print("Retrying...")
                    time.sleep(2)
                else:
                    print("All retry attempts failed")
                    return None
            except Exception as e:
                print(f"Unexpected error making request to {url} (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    print("Retrying...")
                    time.sleep(2)
                else:
                    print("All retry attempts failed")
                    return None
    
    def exists(self, path: str) -> bool:
        """检查文件或目录是否存在
        
        Args:
            path: HDFS路径
            
        Returns:
            是否存在
        """
        response = self._make_request('GET', path, {'op': 'GETFILESTATUS'})
        if response is None:
            print(f"Failed to check existence of {path}: no response")
            return False
        elif response.status_code == 200:
            return True
        elif response.status_code == 404:
            # 文件或目录不存在
            return False
        elif response.status_code == 403:
            print(f"Permission denied when checking existence of {path}: {response.text}")
            return False
        elif response.status_code >= 500:
            print(f"HDFS server error when checking existence of {path}: {response.status_code}, {response.text}")
            return False
        else:
            print(f"Unexpected status code when checking existence of {path}: {response.status_code}")
            return False
    
    def create_dir(self, path: str) -> bool:
        """创建目录
        
        Args:
            path: HDFS路径
            
        Returns:
            是否成功
        """
        response = self._make_request('PUT', path, {'op': 'MKDIRS'})
        if response is None:
            print(f"Failed to create directory {path}: no response")
            return False
        elif response.status_code == 200:
            print(f"Directory created successfully: {path}")
            return True
        elif response.status_code == 403:
            print(f"Permission denied when creating directory {path}: {response.text}")
            return False
        elif response.status_code == 404:
            print(f"Parent path does not exist for {path}")
            return False
        elif response.status_code == 409:
            print(f"Directory already exists: {path}")
            return False
        elif response.status_code >= 500:
            print(f"HDFS server error when creating directory {path}: {response.status_code}, {response.text}")
            return False
        else:
            print(f"Failed to create directory {path}: status code {response.status_code}, content: {response.text}")
            return False
    
    def write_file(self, path: str, data: bytes) -> bool:
        """写入文件
        
        Args:
            path: HDFS路径
            data: 文件数据
            
        Returns:
            是否成功
        """
        print(f"Writing file: {path}")
        print(f"Data size: {len(data)}")
        print(f"Data sample: {data[:100]}...")
        
        # 直接使用PUT请求上传数据，使用OPEN操作
        url = f"{self.base_url}{path}"
        params = {'op': 'CREATE', 'overwrite': 'true', 'user.name': self.user}
        
        print(f"Upload URL: {url}")
        
        try:
            # 发送请求
            response = requests.put(url, data=data, params=params, timeout=30, allow_redirects=False)
            
            print(f"Upload response status code: {response.status_code}")
            print(f"Upload response text: {response.text}")
            
            # 处理重定向
            if response.status_code == 307:
                redirect_url = response.headers.get('Location')
                print(f"Redirecting to: {redirect_url}")
                
                # 处理Docker容器内部主机名的重定向
                if redirect_url:
                    # 在Docker容器内部，保持使用原始主机名
                    # 在外部，将主机名替换为localhost
                    if not os.path.exists('/app'):
                        # 在外部环境，将worker1、worker2、master替换为localhost
                        redirect_url = redirect_url.replace('worker1', 'localhost')
                        redirect_url = redirect_url.replace('worker2', 'localhost')
                        redirect_url = redirect_url.replace('master', 'localhost')
                        print(f"Modified redirect URL: {redirect_url}")
                    
                    # 再次发送请求到修改后的URL
                    response = requests.put(redirect_url, data=data, timeout=30)
                    print(f"Redirect response status code: {response.status_code}")
                    print(f"Redirect response text: {response.text}")
            
            if response.status_code == 201:
                print(f"File uploaded successfully: {path}")
                return True
            else:
                print(f"Failed to upload data: status code {response.status_code}")
                return False
        except Exception as e:
            print(f"Error uploading data to {path}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def read_file(self, path: str) -> Optional[str]:
        """读取文件
        
        Args:
            path: HDFS文件路径
            
        Returns:
            文件内容
        """
        print(f"Reading file: {path}")
        response = self._make_request('GET', path, {'op': 'OPEN'})
        if response is None:
            print(f"No response when reading file: {path}")
            return None
        
        print(f"Response status code: {response.status_code}")
        
        # 处理重定向
        if response.status_code == 307:
            redirect_url = response.headers.get('Location')
            print(f"Redirecting to: {redirect_url}")
            if redirect_url:
                try:
                    response = requests.get(redirect_url, timeout=30)
                    print(f"Redirect response status code: {response.status_code}")
                except Exception as e:
                    print(f"Error reading file from {redirect_url}: {e}")
                    return None
        
        if response.status_code == 200:
            content = response.text
            print(f"File content length: {len(content)}")
            print(f"File content: {content}")
            return content
        else:
            print(f"Failed to read file {path}: {response.status_code}")
            print(f"Response text: {response.text}")
            return None
    
    def delete(self, path: str, recursive: bool = False) -> bool:
        """删除文件或目录
        
        Args:
            path: HDFS路径
            recursive: 是否递归删除
            
        Returns:
            是否成功
        """
        params = {'op': 'DELETE'}
        if recursive:
            params['recursive'] = 'true'
        
        response = self._make_request('DELETE', path, params)
        if response is None:
            print(f"Failed to delete {path}: no response")
            return False
        elif response.status_code == 200:
            print(f"Deleted successfully: {path}")
            return True
        elif response.status_code == 403:
            print(f"Permission denied when deleting {path}: {response.text}")
            return False
        elif response.status_code == 404:
            print(f"Path does not exist: {path}")
            return False
        elif response.status_code == 409:
            print(f"Directory not empty and recursive is false: {path}")
            return False
        elif response.status_code >= 500:
            print(f"HDFS server error when deleting {path}: {response.status_code}, {response.text}")
            return False
        else:
            print(f"Failed to delete {path}: status code {response.status_code}, content: {response.text}")
            return False
    
    def list_dir(self, path: str) -> Optional[List[Dict[str, Any]]]:
        """列出目录内容
        
        Args:
            path: HDFS目录路径
            
        Returns:
            目录内容列表
        """
        response = self._make_request('GET', path, {'op': 'LISTSTATUS'})
        if response is None:
            print(f"Failed to list directory {path}: no response")
            return None
        elif response.status_code == 200:
            try:
                data = response.json()
                file_list = data.get('FileStatuses', {}).get('FileStatus', [])
                print(f"Directory listing for {path}: {len(file_list)} items")
                return file_list
            except Exception as e:
                print(f"Error parsing directory listing for {path}: {e}")
                return None
        elif response.status_code == 403:
            print(f"Permission denied when listing directory {path}: {response.text}")
            return None
        elif response.status_code == 404:
            print(f"Directory does not exist: {path}")
            return None
        elif response.status_code >= 500:
            print(f"HDFS server error when listing directory {path}: {response.status_code}, {response.text}")
            return None
        else:
            print(f"Failed to list directory {path}: status code {response.status_code}, content: {response.text}")
            return None


# 全局HDFS客户端实例
# 根据环境选择合适的HDFS主机名
# 在Docker容器内部使用'master'，外部使用'localhost'
hdfs_host = os.getenv('HDFS_HOST', 'master' if os.path.exists('/app') else 'localhost')
hdfs_client = WebHDFSClient(host=hdfs_host, user=os.getenv('HDFS_USER', 'jupyter'))

# 在实例化后添加连接测试
try:
    if not hdfs_client.exists('/'):
        print('Warning: HDFS connection may be unstable')
except Exception as e:
    print(f'HDFS connection error: {e}')