# 能力目标

- 理解 Model Context Protocol (MCP) 的核心作用及其在 AI/LLM 系统中的应用场景。
- 掌握 MCP 在数据库集成、生成式媒体编排、外部 API 交互、信息抽取、工具开发、标准化通信、复杂工作流编排、物联网控制、金融服务自动化等方面的实际应用。
- 能够基于 MCP 协议，使用 ADK 和 FastMCP 框架搭建和集成智能体与外部系统。
- 能够分析 MCP 的优势、适用场景及其与传统工具调用的区别。

---

# 主要知识点

## MCP 的实际应用与场景

- MCP 拓展了 AI/LLM 的能力，使其能与数据库、生成式媒体服务、外部 API、IoT 设备、金融服务等多种系统进行标准化交互。
- 通过 MCP，智能体可实现如数据库查询、报告生成、媒体内容创作、实时数据获取、设备控制等复杂任务。
- MCP 支持开发自定义工具，并通过 MCP 服务器暴露给智能体，无需直接修改 LLM。
- MCP 提供统一的通信层，简化了不同 LLM 与应用之间的集成，提升了系统的可扩展性和互操作性。
- 智能体可通过 MCP 协议编排多步复杂工作流，实现跨系统的数据整合与自动化操作。

## Hands-On：ADK 与 MCP 的集成

- 通过 ADK，智能体可配置 MCPToolset，实现本地文件系统操作（如列出、读取、写入文件）。
- MCPToolset 支持通过 StdioServerParameters 连接 MCP 服务器，需指定本地文件夹的绝对路径作为操作根目录。
- MCP 服务器可通过 npx 直接运行，无需全局安装 Node.js 包，便于社区 MCP 服务器的快速部署。
- Python 环境下可通过 uvx 工具临时隔离运行 MCP 相关包，提升安全性与灵活性。

## FastMCP 框架

- FastMCP 是高层 Python 框架，简化 MCP 服务器开发，支持工具、资源、提示的快速定义与自动化 schema 生成。
- 支持服务组合、代理等高级架构模式，便于构建模块化、可扩展的 AI 系统。
- 通过 Python 装饰器注册工具，自动生成接口规范，减少人工配置与错误。
- 支持高效分布式部署，适合大规模 AI 应用场景。

## 客户端智能体配置

- ADK 智能体可通过 HttpServerParameters 连接 FastMCP 服务器，按需过滤可用工具。
- 智能体可根据任务自动发现并调用 MCP 服务器暴露的工具，实现动态扩展能力。

## MCP 的标准化优势

- MCP 作为开放标准，解决了 LLM 与外部系统集成的碎片化、不可复用问题。
- 客户端-服务器架构，支持工具、数据资源、交互提示的标准化暴露与消费。
- 促进生态系统互操作与组件复用，简化复杂智能体工作流开发。

---

# 名词解释

- **Model Context Protocol (MCP)**：一种开放标准协议，定义 LLM 与外部应用、数据源、工具之间的标准化通信方式。
- **ADK (Agent Development Kit)**：智能体开发工具包，支持 MCP 协议的集成与工具暴露。
- **FastMCP**：用于快速开发 MCP 服务器的 Python 框架，支持自动化接口生成与高级架构模式。
- **MCPToolset**：ADK 中用于连接 MCP 服务器的工具集，可配置连接参数与工具过滤。
- **StdioServerParameters/HttpServerParameters**：ADK 中用于配置 MCP 服务器连接方式的参数类。
- **npx**：Node.js 包管理工具，支持临时运行 npm 包，无需全局安装。
- **uvx**：Python 命令行工具，支持在临时隔离环境中运行 Python 包。
- **工具过滤（tool_filter）**：智能体可指定只暴露 MCP 服务器中的部分工具，提升安全性与专用性。

---

# 案例与代码

## ADK 智能体连接本地文件系统 MCP 服务器

```python
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_managed_files")
os.makedirs(TARGET_FOLDER_PATH, exist_ok=True)

root_agent = LlmAgent(
   model='gemini-2.0-flash',
   name='filesystem_assistant_agent',
   instruction=(
       '帮助用户管理文件。你可以列出、读取和写入文件。'
       f'你当前操作的目录为：{TARGET_FOLDER_PATH}'
   ),
   tools=[
       MCPToolset(
           connection_params=StdioServerParameters(
               command='npx',
               args=[
                   "-y",
                   "@modelcontextprotocol/server-filesystem",
                   TARGET_FOLDER_PATH,
               ],
           ),
           # 可选：只允许部分工具
           # tool_filter=['list_directory', 'read_file']
       )
   ],
)
```

## FastMCP 服务器开发与集成

```python
# fastmcp_server.py
from fastmcp import FastMCP

mcp_server = FastMCP()

@mcp_server.tool
def greet(name: str) -> str:
    """生成个性化问候语"""
    return f"你好，{name}！很高兴见到你。"

if __name__ == "__main__":
    mcp_server.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )
```

## ADK 智能体连接 FastMCP 服务器

```python
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, HttpServerParameters

FASTMCP_SERVER_URL = "http://localhost:8000"

root_agent = LlmAgent(
   model='gemini-2.0-flash',
   name='fastmcp_greeter_agent',
   instruction='你是一个友好的助手，可以通过“greet”工具为用户问候。',
   tools=[
       MCPToolset(
           connection_params=HttpServerParameters(
               url=FASTMCP_SERVER_URL,
           ),
           tool_filter=['greet']
       )
   ],
)
```

---

# 小结与思考题

## 小结

- MCP 作为开放标准，极大提升了 LLM 智能体与外部系统的集成能力，支持多种实际应用场景。
- ADK 和 FastMCP 框架为 MCP 的开发与集成提供了高效工具，简化了智能体与工具、数据源的连接流程。
- MCP 的标准化通信机制促进了生态系统的互操作与组件复用，是构建复杂、可扩展智能体系统的关键。

## 思考题

1. MCP 协议与传统工具调用方式相比，有哪些优势？在哪些场景下更适合使用 MCP？
2. 如何通过 MCP 实现智能体对数据库、生成式媒体、IoT 设备等多种系统的统一管理？
3. FastMCP 框架在 MCP 服务器开发中有哪些自动化和架构优化功能？
4. MCP 的标准化机制如何促进 AI 生态系统的互操作与扩展？
5. 请结合实际案例，设计一个基于 MCP 的智能体工作流，实现跨系统的数据整合与自动化操作。

---

# 参考文献

1. Model Context Protocol (MCP) Documentation. (Latest). Model Context Protocol (MCP). https://google.github.io/adk-docs/mcp/
2. FastMCP Documentation. FastMCP. https://github.com/jlowin/fastmcp
3. MCP Tools for Genmedia Services. MCP Tools for Genmedia Services. https://google.github.io/adk-docs/mcp/#mcp-servers-for-google-cloud-genmedia
4. MCP Toolbox for Databases Documentation. (Latest). MCP Toolbox for Databases. https://google.github.io/adk-docs/mcp/databases/
