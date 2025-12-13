# Dockerfile для tavily_search_tool с поддержкой mcp-remote
# Расширяем официальный образ mcp/tavily

FROM mcp/tavily:latest

# Устанавливаем mcp-remote глобально
RUN npm install -g mcp-remote

# Запускаем MCP в HTTP режиме (прослушивание порта 8000)
# Используем mcp-remote с флагом --transport http и --port 8000
CMD ["mcp-remote", "--transport", "http", "--port", "8000"]