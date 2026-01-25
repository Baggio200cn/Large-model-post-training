# 第七章 多智能体协作模式

## 一、能力目标
本章旨在帮助职业院校AI初学者老师理解多智能体协作（Multi-Agent Collaboration）模式的基本原理、常见结构、应用场景及其在智能体系统中的作用。通过本章学习，您将能够：
1. 说出什么是多智能体协作及其核心思想。
2. 理解多智能体系统的常见结构和通信方式。
3. 掌握多智能体协作在实际AI任务中的典型应用方法。

## 二、主要知识点
1. 多智能体协作的定义与基本原理：将复杂任务分解，由多个专长智能体分工协作完成。
2. 多智能体系统的常见结构：顺序传递、并行处理、辩论共识、层级管理、专家团队、批判-复审等。
3. 多智能体通信与协调方式：单体、网络、主管、层级、自定义等模型。
4. 典型应用场景：科研分析、软件开发、内容创作、金融分析、客户支持、供应链优化等。
5. 相关工具与框架（如Crew AI、Google ADK等）。

## 三、专业名词解释（通俗易懂）
- **多智能体协作（Multi-Agent Collaboration）**：多个AI智能体像团队一样分工合作，协同完成复杂任务。
- **顺序传递**：一个智能体完成后把结果交给下一个，像流水线。
- **并行处理**：多个智能体同时处理不同部分，最后合并结果。
- **层级结构**：有“主管”智能体分配任务，下面有多个“员工”智能体。
- **批判-复审**：一组智能体先产出结果，另一组负责检查和优化。
- **Crew AI/Google ADK**：常用的多智能体协作开发框架。

## 四、关键案例与代码（含详细中文解释）

### 案例1：科研团队多智能体协作（伪代码）
```python
# 研究员负责查找资料，分析员负责数据分析，撰稿人负责写报告
researcher = ResearchAgent()
analyst = DataAnalysisAgent()
writer = SynthesisAgent()
info = researcher.search("AI发展趋势")
analysis = analyst.analyze(info)
report = writer.write(analysis)
```
**说明：**
每个智能体专注于自己的环节，分工明确，协作高效。

### 案例2：Crew AI框架多智能体协作
```python
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
researcher = Agent(role='研究员', goal='查找AI趋势', ...)
writer = Agent(role='撰稿人', goal='写博客', ...)
research_task = Task(description="调研AI趋势", agent=researcher)
writing_task = Task(description="写博客", agent=writer, context=[research_task])
crew = Crew(agents=[researcher, writer], tasks=[research_task, writing_task], process=Process.sequential, llm=llm)
result = crew.kickoff()
print(result)
```
**说明：**
用Crew AI可以很方便地定义多智能体协作流程。

### 案例3：Google ADK层级结构多智能体
```python
from google.adk.agents import LlmAgent, BaseAgent
class TaskExecutor(BaseAgent):
    ...
greeter = LlmAgent(name="Greeter", ...)
task_doer = TaskExecutor()
coordinator = LlmAgent(name="Coordinator", sub_agents=[greeter, task_doer], ...)
assert greeter.parent_agent == coordinator
assert task_doer.parent_agent == coordinator
```
**说明：**
主管智能体分配任务，员工智能体各司其职。

### 案例4：Google ADK并行与顺序协作
```python
from google.adk.agents import ParallelAgent, SequentialAgent, Agent
# 并行：天气和新闻同时获取
weather_fetcher = Agent(name="weather_fetcher", ...)
news_fetcher = Agent(name="news_fetcher", ...)
data_gatherer = ParallelAgent(name="data_gatherer", sub_agents=[weather_fetcher, news_fetcher])
# 顺序：先抓取数据再处理
step1 = Agent(name="Step1_Fetch", output_key="data")
step2 = Agent(name="Step2_Process", instruction="分析state['data']并总结")
pipeline = SequentialAgent(name="MyPipeline", sub_agents=[step1, step2])
```
**说明：**
并行适合独立任务，顺序适合有依赖关系的多步任务。

## 五、小结与思考题
1. 多智能体协作模式相比单一智能体有哪些优势？
2. 请举例说明多智能体协作在实际工作中的应用场景。
3. 你认为在什么情况下适合采用层级结构或并行结构？
4. 多智能体系统如何保证协作的高效与结果的可靠？
