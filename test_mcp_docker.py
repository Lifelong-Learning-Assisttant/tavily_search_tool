#!/usr/bin/env python3
"""
Тестирование Tavily MCP сервера через Docker exec
"""
import asyncio
import json
import subprocess
import sys

class DockerMCPClient:
    def __init__(self, container_name="tavily_server"):
        self.container_name = container_name
        self.message_id = 1
        
    async def send_message(self, message):
        """Отправляем сообщение в Docker контейнер"""
        message_str = json.dumps(message)
        
        # Используем docker exec для отправки сообщения
        cmd = [
            "docker", "exec", "-i", self.container_name,
            "node", "build/index.js"
        ]
        
        print(f"📤 Отправка сообщения в контейнер {self.container_name}")
        print(f"Сообщение: {message_str}")
        
        try:
            # Запускаем процесс
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Отправляем сообщение
            stdout, stderr = process.communicate(input=message_str + "\n", timeout=10)
            
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            
            return stdout, stderr
            
        except subprocess.TimeoutExpired:
            print("❌ Таймаут при выполнении команды")
            process.kill()
            return None, "Timeout"
        except Exception as e:
            print(f"❌ Ошибка выполнения: {e}")
            return None, str(e)
            
    async def test_initialize(self):
        """Тестируем инициализацию"""
        message = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        self.message_id += 1
        
        stdout, stderr = await self.send_message(message)
        return stdout, stderr
        
    async def test_list_tools(self):
        """Тестируем получение списка инструментов"""
        message = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": "tools/list",
            "params": {}
        }
        self.message_id += 1
        
        stdout, stderr = await self.send_message(message)
        return stdout, stderr
        
    async def test_search(self):
        """Тестируем поиск"""
        message = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": "tools/call",
            "params": {
                "name": "tavily-search",
                "arguments": {
                    "query": "Что такое LangChain?",
                    "search_depth": "basic",
                    "topic": "general",
                    "max_results": 5
                }
            }
        }
        self.message_id += 1
        
        stdout, stderr = await self.send_message(message)
        return stdout, stderr

async def main():
    """Основная функция тестирования"""
    client = DockerMCPClient()
    
    print("=== Тестирование Tavily MCP сервера через Docker ===\n")
    
    # Проверяем, запущен ли контейнер
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={client.container_name}"],
            capture_output=True, text=True
        )
        if client.container_name not in result.stdout:
            print(f"❌ Контейнер {client.container_name} не запущен")
            print("Запустите: docker-compose up -d")
            return
        else:
            print(f"✅ Контейнер {client.container_name} запущен")
    except Exception as e:
        print(f"❌ Ошибка проверки контейнера: {e}")
        return
    
    print("\n" + "="*50)
    
    # Тестируем инициализацию
    print("\n1. Тест инициализации:")
    stdout, stderr = await client.test_initialize()
    if stdout:
        print(f"✅ Ответ: {stdout}")
    else:
        print(f"❌ Ошибка: {stderr}")
    
    print("\n" + "="*50)
    
    # Тестируем список инструментов
    print("\n2. Тест получения списка инструментов:")
    stdout, stderr = await client.test_list_tools()
    if stdout:
        print(f"✅ Ответ: {stdout}")
    else:
        print(f"❌ Ошибка: {stderr}")
    
    print("\n" + "="*50)
    
    # Тестируем поиск
    print("\n3. Тест поиска:")
    stdout, stderr = await client.test_search()
    if stdout:
        print(f"✅ Ответ: {stdout}")
    else:
        print(f"❌ Ошибка: {stderr}")

if __name__ == "__main__":
    asyncio.run(main())