# 第八章 记忆管理模式

## 一、能力目标
本章帮助职业院校AI初学者老师深入理解智能体系统中的记忆管理（Memory Management）原理、类型、应用场景及代码实现。通过本章学习，您将能够：
1. 说出智能体记忆管理的基本类型和作用。
2. 理解短期记忆与长期记忆的区别及管理方法。
3. 掌握记忆管理在实际AI应用中的典型场景和代码实现。

## 二、引言与基本原理
高效的记忆管理对于智能体保留信息至关重要。智能体需要不同类型的记忆，就像人类一样，才能高效运作。记忆让智能体能做出更合理的决策、保持对话连贯、不断优化自身行为。

智能体的记忆通常分为两大类：
- 短期记忆（上下文记忆）：类似于人类的工作记忆，保存当前正在处理或最近访问的信息。对于使用大语言模型（LLM）的智能体来说，短期记忆主要体现在“上下文窗口”中。这个窗口包含最近的消息、智能体回复、工具使用结果和智能体的反思，这些内容共同影响LLM的后续响应和行为。上下文窗口容量有限，限制了智能体能直接访问的最近信息量。高效的短期记忆管理需要在有限空间内保留最相关的信息，常用方法包括对旧对话片段进行摘要或突出关键信息。“长上下文”模型的出现只是扩大了短期记忆的容量，使单次交互能容纳更多信息，但这些内容依然是临时的，会话结束后即丢失，而且每次处理大量内容会增加成本和效率问题。因此，智能体还需要其他类型的记忆来实现真正的持久性，能够回忆过去的交互并建立长期知识库。
- 长期记忆（持久记忆）：类似于长期知识库，保存智能体在多次交互、任务或较长时间内需要保留的信息。这些数据通常存储在智能体处理环境之外，比如数据库、知识图谱或向量数据库。在向量数据库中，信息会被转化为数值向量进行存储，使智能体能通过语义相似度而非关键词精确匹配来检索数据，这就是“语义检索”。当智能体需要长期记忆中的信息时，会查询外部存储，检索相关数据，并将其整合到短期记忆中参与当前任务，实现历史知识与当前交互的结合。

## 三、记忆管理的实际应用场景
- 聊天机器人与对话AI：聊天机器人要保持对话的连贯性，依赖短期记忆来记住用户的前几次输入，从而做出相关回应。长期记忆则让机器人能够记住用户的偏好、历史问题或之前的讨论，实现个性化和持续性的交互体验。
- 任务型智能体：管理多步骤任务的智能体需要短期记忆来跟踪每一步的进展和当前目标，这些信息通常存储在任务上下文或临时存储中。长期记忆则用于访问用户的特定数据，比如历史任务、偏好等。
- 个性化体验：提供定制化服务的智能体会利用长期记忆保存和检索用户的偏好、历史行为和个人信息，从而根据用户的历史调整响应和建议。
- 学习与优化：智能体可以通过记忆管理不断学习和优化自身表现。成功的策略、错误和新知识会被存入长期记忆，便于未来适应和改进。例如，强化学习智能体会将学到的策略或知识以记忆形式保存。
- 信息检索（RAG）：专门用于回答问题的智能体会访问知识库（长期记忆），通常通过“检索增强生成”（RAG）技术实现。智能体先检索相关文档或数据，再结合生成模型给出更准确的答案。
- 自主系统（如机器人、自动驾驶）：机器人或自动驾驶汽车需要记忆地图、路线、物体位置和已学行为。短期记忆用于处理当前环境信息，长期记忆则保存更广泛的环境知识和经验。

## 四、关键案例与代码

### 案例1：Google ADK会话与状态管理
```python
from google.adk.sessions import InMemorySessionService
session_service = InMemorySessionService()
session = session_service.create_session(app_name="test_app", user_id="user1", session_id="session1")
print(session.state)  # 查看初始状态
```
说明：InMemorySessionService适合本地开发和测试，数据不会跨重启保留。生产环境可用DatabaseSessionService或VertexAiSessionService实现持久化和云端扩展。

### 案例2：ADK状态自动更新与工具式管理
```python
from google.adk.agents import LlmAgent
from google.adk.runners import Runner

greeting_agent = LlmAgent(
    name="Greeter",
    model="gemini-2.0-flash",
    instruction="生成简短友好的问候语。",
    output_key="last_greeting"
)
runner = Runner(agent=greeting_agent, app_name="state_app", session_service=session_service)
session = session_service.create_session(app_name="state_app", user_id="user1", session_id="session1")
user_message = "Hello"
for event in runner.run(user_id="user1", session_id="session1", new_message=user_message):
    if event.is_final_response():
        print("Agent responded.")
updated_session = session_service.get_session("state_app", "user1", "session1")
print(updated_session.state)  # 查看状态更新结果
```

```python
def log_user_login(tool_context):
    state = tool_context.state
    login_count = state.get("user:login_count", 0) + 1
    state["user:login_count"] = login_count
    state["task_status"] = "active"
    state["user:last_login_ts"] = time.time()
    state["temp:validation_needed"] = True
    return {"status": "success", "message": f"User login tracked. Total logins: {login_count}."}
```
说明：推荐通过工具函数封装状态更新，保证数据一致性和可追溯性。

### 案例3：ADK长期记忆管理
```python
from google.adk.memory import InMemoryMemoryService
memory_service = InMemoryMemoryService()
memory_service.add_session_to_memory(session)  # 添加会话内容到长期记忆
results = memory_service.search_memory("用户偏好")  # 检索长期记忆
print(results)
```
说明：生产环境可用VertexAiRagMemoryService实现云端持久化和高效语义检索。

### 案例4：LangChain与LangGraph记忆管理
```python
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory()
memory.save_context({"input": "天气怎么样？"}, {"output": "今天晴朗。"})
print(memory.load_memory_variables({}))
```
说明：ConversationBufferMemory自动保存对话历史，便于多轮对话上下文管理。

```python
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()
store.put(("user1", "chitchat"), "a-memory", {"rules": ["用户喜欢简洁语言"]})
item = store.get(("user1", "chitchat"), "a-memory")
print(item)
```
说明：LangGraph支持长期记忆的分层管理和语义检索，适合复杂应用场景。

## 五、专业名词解释
- 短期记忆（Short-Term Memory / Contextual Memory）：智能体在当前会话或任务中保存的临时信息，类似于人类的工作记忆。通常体现在上下文窗口，容量有限，会话结束后即丢失。
- 长期记忆（Long-Term Memory / Persistent Memory）：智能体跨会话、跨任务保存的重要信息，如用户偏好、历史任务、知识库等。通常存储在数据库、知识图谱或向量数据库中，支持语义检索。
- 上下文窗口（Context Window）：LLM（大语言模型）处理时能“记住”的最近内容片段，决定了短期记忆的容量。
- 语义检索（Semantic Search）：通过内容相似度而非关键词精确匹配来查找信息，常用于向量数据库和知识库检索。
- RAG（检索增强生成，Retrieval Augmented Generation）：智能体结合知识库检索和生成模型，提升回答的准确性和专业性。
- Session / State / MemoryService：Google ADK中的核心组件：Session表示会话线程，State为临时数据，MemoryService管理长期知识库。
- Memory Bank（记忆库）：云端智能体的持久化记忆服务，自动提取、存储和检索用户信息，实现个性化和连续性对话。

## 六、小结与思考题
**小结：**
记忆管理是智能体系统实现高级智能行为的基础。短期记忆保证对话和任务的连贯性，长期记忆让智能体能学习、个性化和优化自身表现。现代智能体框架（如Google ADK、LangChain、LangGraph）都提供了丰富的记忆管理工具和机制，支持多种应用场景和复杂任务。

**思考题：**
1. 为什么智能体需要记忆管理？请结合实际场景说明。
2. 记忆管理有哪些常见实现方式？各自适合什么场景？
3. 如何让AI系统在多轮对话中保持上下文连贯？有哪些技术手段？
4. 你认为未来记忆管理在AI应用中会有哪些创新？请举例说明。

## 七、参考文献
1. ADK Memory, https://google.github.io/adk-docs/sessions/memory/
2. LangGraph Memory, https://langchain-ai.github.io/langgraph/concepts/memory/
3. Vertex AI Agent Engine Memory Bank, https://cloud.google.com/blog/products/ai-machine-learning/vertex-ai-memory-bank-in-public-preview
