# 第一章 什么让AI系统成为“智能体”？

## 一、能力目标
本章旨在帮助职业院校AI初学者老师理解“智能体”AI系统的基本概念、发展阶段及其在现实中的应用。通过本章学习，您将能够：
1. 说出什么是AI智能体（Agent）及其与传统AI模型的区别。
2. 理解智能体的能力分级及其核心特征。
3. 了解智能体未来发展的主要趋势。

## 二、主要知识点
1. 智能体的定义与五步循环工作机制
2. 智能体能力分级（Level 0-3）
3. 多智能体协作系统的基本思想
4. 智能体未来发展五大假设

## 三、专业名词解释（通俗易懂）
- **智能体（Agent）**：能感知环境、制定计划并采取行动以达成目标的AI系统。
- **LLM（大语言模型）**：像ChatGPT这样的AI模型，能理解和生成自然语言，但本身不是智能体。
- **RAG（检索增强生成）**：让AI能查找外部信息，提升回答的准确性。
- **多智能体系统**：多个智能体协作完成复杂任务，就像公司里不同部门分工合作。
- **上下文工程（Context Engineering）**：为AI挑选、整理最关键的信息，帮助其更高效地完成任务。

## 四、关键案例与代码（含详细中文解释）

### 案例1：智能体五步循环
```python
# 伪代码：一个简单的日程管理AI智能体
def agentic_ai(goal):
    # 1. 获取任务目标
    mission = goal
    # 2. 感知环境（如读取邮件、日历）
    info = get_environment_info()
    # 3. 制定计划
    plan = make_plan(mission, info)
    # 4. 执行计划
    result = execute_plan(plan)
    # 5. 学习与改进
    learn_from_result(result)
    return result
```
**说明：**
1. `get_environment_info()` 代表智能体主动收集所需信息。
2. `make_plan()` 让智能体根据目标和信息制定行动方案。
3. `execute_plan()` 让智能体实际去做，比如发邮件、更新日历。
4. `learn_from_result()` 让智能体根据结果不断优化自己。

### 案例2：多智能体协作
```python
# 伪代码：多个智能体协作完成产品发布
def launch_product():
    manager = ProjectManagerAgent()
    market = MarketResearchAgent()
    design = ProductDesignAgent()
    marketing = MarketingAgent()
    # 各智能体分工合作
    market_data = market.collect_data()
    product = design.create_concept(market_data)
    plan = manager.make_plan(product)
    marketing.promote(plan)
```
**说明：**
1. 每个智能体负责不同环节，像公司里的不同部门。
2. 通过信息共享和协作，提升整体效率和效果。

### 案例3：智能体主动发现用户需求
```python
def proactive_agent(user_behavior):
    if detect_interest(user_behavior, '新能源'):
        recommend('新能源课程')
    else:
        ask_user_for_interest()
```
**说明：**
智能体能主动分析用户行为，发现潜在需求并给出个性化推荐。

### 案例4：具身智能体与物理世界互动
```python
def fix_leaky_tap():
    agent = HomeRobotAgent()
    problem = agent.detect_problem()
    plan = agent.formulate_plan(problem)
    agent.execute(plan)
```
**说明：**
具身智能体（如家用机器人）能感知物理世界、制定维修计划并实际操作。

## 五、小结与思考题
1. 智能体与传统AI模型的核心区别是什么？
2. 多智能体协作在现实中的应用有哪些？
3. 你认为未来哪些行业最需要智能体？为什么？
4. 你如何看待具身智能体的未来应用？
