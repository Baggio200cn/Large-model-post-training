// ==============================================
// AI彩票分析实验室 - 主JavaScript文件
// 版本: 3.0 - 包含重新分析功能
// 更新日期: 2025-10-31
// ==============================================

// ==============================================
// 全局变量
// ==============================================
let currentUpdateTime = '';
let debugMode = true;
let currentStrategy = 'balanced';
let predictionHistory = [];

// ==============================================
// 工具函数：日志输出
// ==============================================
function log(type, message, data = null) {
    if (!debugMode) return;
    
    const emoji = {
        'info': 'ℹ️',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'debug': '🔍'
    };
    
    const prefix = `${emoji[type] || '📝'} [${new Date().toLocaleTimeString()}]`;
    
    if (data) {
        console.log(`${prefix} ${message}`, data);
    } else {
        console.log(`${prefix} ${message}`);
    }
}

// ==============================================
// 页面加载时自动执行
// ==============================================
document.addEventListener('DOMContentLoaded', function() {
    log('info', '页面加载完成，开始初始化...');
    
    // 自动加载预测和历史数据
    loadPrediction(false);
    loadHistory();
});

// ==============================================
// 1. 加载AI预测结果（支持重新分析）
// ==============================================
async function loadPrediction(forceNew = false) {
    log('info', `加载预测数据... (重新生成: ${forceNew})`);
    
    const loadingEl = document.getElementById('loading');
    const predictionsEl = document.getElementById('predictions');
    
    if (!loadingEl || !predictionsEl) {
        log('error', '找不到必要的DOM元素');
        return;
    }
    
    // 显示加载状态
    loadingEl.style.display = 'block';
    predictionsEl.style.display = 'none';
    
    try {
        // 生成随机种子（确保每次都不同）
        const seed = Date.now() + Math.floor(Math.random() * 10000);
        
        // 构建API URL（带种子和策略参数）
        const apiUrl = `/api/predict.py?seed=${seed}&strategy=${currentStrategy}`;
        
        log('debug', `请求API: ${apiUrl}`);
        
        // 调用预测API
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        log('success', '预测数据加载成功', data);
        
        // 验证数据结构
        if (!data.red_balls || !data.blue_balls) {
            throw new Error('API返回数据结构不完整');
        }
        
        if (!Array.isArray(data.red_balls) || !Array.isArray(data.blue_balls)) {
            throw new Error('号码数据必须是数组格式');
        }
        
        // 如果是重新分析，添加到历史记录
        if (forceNew && predictionHistory.length < 10) {
            predictionHistory.push({
                timestamp: new Date().toLocaleString('zh-CN'),
                data: data
            });
        }
        
        // 显示预测结果
        displayPrediction(data);
        
        // 更新策略显示
        updateStrategyDisplay();
        
        // 获取并更新时间戳
        await fetchAndUpdateTimestamp();
        
        // 如果是重新分析，显示提示
        if (forceNew) {
            showReanalysisNotification();
        }
        
    } catch (error) {
        log('error', '加载预测失败', error);
        showError('预测加载失败: ' + error.message);
    } finally {
        loadingEl.style.display = 'none';
        predictionsEl.style.display = 'block';
    }
}

// ==============================================
// 2. 重新分析按钮处理
// ==============================================
function reanalyze() {
    log('info', '用户点击重新分析按钮');
    
    // 显示策略选择器
    showStrategySelector();
    
    // 执行新的预测
    loadPrediction(true);
}

// ==============================================
// 3. 策略选择器
// ==============================================
function showStrategySelector() {
    // 如果已经存在选择器，直接返回
    if (document.getElementById('strategy-selector')) {
        return;
    }
    
    const modelInfoEl = document.getElementById('model-info');
    if (!modelInfoEl) return;
    
    // 创建策略选择HTML
    const selectorHTML = `
        <div id="strategy-selector" class="strategy-selector">
            <h4>🎯 选择预测策略</h4>
            <div class="strategy-options">
                <button class="strategy-btn ${currentStrategy === 'conservative' ? 'active' : ''}" 
                        onclick="changeStrategy('conservative')">
                    🛡️ 保守型
                    <small>侧重高频号码</small>
                </button>
                <button class="strategy-btn ${currentStrategy === 'balanced' ? 'active' : ''}" 
                        onclick="changeStrategy('balanced')">
                    ⚖️ 平衡型
                    <small>高频+随机混合</small>
                </button>
                <button class="strategy-btn ${currentStrategy === 'aggressive' ? 'active' : ''}" 
                        onclick="changeStrategy('aggressive')">
                    🚀 激进型
                    <small>探索冷门号码</small>
                </button>
                <button class="strategy-btn ${currentStrategy === 'random' ? 'active' : ''}" 
                        onclick="changeStrategy('random')">
                    🎲 随机型
                    <small>完全随机探索</small>
                </button>
            </div>
        </div>
    `;
    
    // 插入到模型信息前面
    modelInfoEl.insertAdjacentHTML('beforebegin', selectorHTML);
}

// ==============================================
// 4. 切换预测策略
// ==============================================
function changeStrategy(strategy) {
    log('info', `切换策略: ${strategy}`);
    
    currentStrategy = strategy;
    
    // 更新按钮状态
    const buttons = document.querySelectorAll('.strategy-btn');
    buttons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeBtn = Array.from(buttons).find(btn => 
        btn.getAttribute('onclick').includes(strategy)
    );
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
    
    // 立即生成新预测
    loadPrediction(true);
}

// ==============================================
// 5. 更新策略显示
// ==============================================
function updateStrategyDisplay() {
    const modelInfoEl = document.getElementById('model-info');
    if (!modelInfoEl) return;
    
    // 查找或创建策略显示元素
    let strategyEl = modelInfoEl.querySelector('.current-strategy');
    if (!strategyEl) {
        strategyEl = document.createElement('p');
        strategyEl.className = 'current-strategy';
        modelInfoEl.insertBefore(strategyEl, modelInfoEl.firstChild);
    }
    
    const strategyNames = {
        'conservative': '🛡️ 保守型策略',
        'balanced': '⚖️ 平衡型策略',
        'aggressive': '🚀 激进型策略',
        'random': '🎲 随机型策略'
    };
    
    strategyEl.innerHTML = `<strong>当前策略:</strong> ${strategyNames[currentStrategy]}`;
}

// ==============================================
// 6. 显示重新分析提示
// ==============================================
function showReanalysisNotification() {
    // 创建提示元素
    const notification = document.createElement('div');
    notification.className = 'reanalysis-notification';
    notification.innerHTML = `
        <span class="icon">🔄</span>
        <span class="text">已生成新的预测结果</span>
    `;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 3秒后自动消失
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// ==============================================
// 7. 获取并更新时间戳
// ==============================================
async function fetchAndUpdateTimestamp() {
    log('info', '开始获取时间戳...');
    
    try {
        const response = await fetch('/api/latest-results.py');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        log('debug', '时间戳API响应', data);
        
        if (data.status === 'success' && data.updated_at) {
            currentUpdateTime = data.updated_at;
            updateTimestampDisplay(currentUpdateTime);
            log('success', '时间戳更新成功', currentUpdateTime);
        } else {
            throw new Error('时间戳数据格式不正确');
        }
        
    } catch (error) {
        log('warning', '时间戳获取失败，使用当前时间', error);
        
        // 使用当前时间作为备用
        const now = new Date();
        currentUpdateTime = now.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        }).replace(/\//g, '-');
        
        updateTimestampDisplay(currentUpdateTime);
    }
}

// ==============================================
// 8. 更新页面上的时间显示
// ==============================================
function updateTimestampDisplay(timestamp) {
    log('info', '更新时间显示', timestamp);
    
    const modelInfoEl = document.getElementById('model-info');
    
    if (!modelInfoEl) {
        log('warning', '找不到 model-info 元素');
        return;
    }
    
    // 查找现有的时间元素
    let timeElement = modelInfoEl.querySelector('.update-time');
    
    if (timeElement) {
        // 更新现有元素
        timeElement.innerHTML = `⏰ <strong>训练时间:</strong> ${timestamp}`;
    } else {
        // 添加新元素
        const newTimeElement = document.createElement('p');
        newTimeElement.className = 'update-time';
        newTimeElement.innerHTML = `⏰ <strong>训练时间:</strong> ${timestamp}`;
        modelInfoEl.appendChild(newTimeElement);
    }
    
    log('success', '时间显示已更新');
}

// ==============================================
// 9. 显示预测结果
// ==============================================
function displayPrediction(data) {
    log('info', '开始渲染预测结果', data);
    
    // 显示红球
    displayBalls('red-balls', data.red_balls, 'red-ball');
    
    // 显示蓝球
    displayBalls('blue-balls', data.blue_balls, 'blue-ball');
    
    // 显示模型信息
    displayModelInfo(data);
    
    log('success', '预测结果渲染完成');
}

// ==============================================
// 10. 显示号码球（通用函数）
// ==============================================
function displayBalls(containerId, balls, ballClass) {
    const container = document.getElementById(containerId);
    
    if (!container) {
        log('error', `找不到容器: ${containerId}`);
        return;
    }
    
    if (!balls || !Array.isArray(balls) || balls.length === 0) {
        log('warning', `${containerId} 数据无效`, balls);
        container.innerHTML = '<p style="color: #999;">暂无数据</p>';
        return;
    }
    
    log('debug', `渲染 ${containerId}`, balls);
    
    // 生成号码球HTML
    const ballsHTML = balls.map(num => {
        const displayNum = String(num).padStart(2, '0');
        return `<div class="ball ${ballClass}">${displayNum}</div>`;
    }).join('');
    
    container.innerHTML = ballsHTML;
    log('success', `${containerId} 渲染完成`);
}

// ==============================================
// 11. 显示模型信息
// ==============================================
function displayModelInfo(data) {
    const modelInfoEl = document.getElementById('model-info');
    
    if (!modelInfoEl) {
        log('warning', '找不到 model-info 元素');
        return;
    }
    
    let infoHTML = '<div class="model-details">';
    
    // 置信度
    if (data.confidence !== undefined) {
        const confidencePercent = (data.confidence * 100).toFixed(1);
        infoHTML += `<p>📊 <strong>置信度:</strong> ${confidencePercent}%</p>`;
    }
    
    // 模型名称
    if (data.model) {
        infoHTML += `<p>🤖 <strong>模型:</strong> ${data.model}</p>`;
    }
    
    // 数据基础
    if (data.based_on_count) {
        infoHTML += `<p>📈 <strong>基于:</strong> ${data.based_on_count} 期历史数据</p>`;
    }
    
    // 训练时间（如果已经获取到）
    if (currentUpdateTime) {
        infoHTML += `<p class="update-time">⏰ <strong>训练时间:</strong> ${currentUpdateTime}</p>`;
    }
    
    infoHTML += '</div>';
    modelInfoEl.innerHTML = infoHTML;
    
    log('success', '模型信息显示完成');
}

// ==============================================
// 12. 加载历史开奖记录
// ==============================================
async function loadHistory() {
    log('info', '开始加载历史数据...');
    
    const loadingEl = document.getElementById('history-loading');
    const contentEl = document.getElementById('history-content');
    const errorEl = document.getElementById('history-error');
    
    if (!loadingEl || !contentEl || !errorEl) {
        log('error', '找不到历史数据相关的DOM元素');
        return;
    }
    
    // 显示加载状态
    loadingEl.style.display = 'flex';
    contentEl.style.display = 'none';
    errorEl.style.display = 'none';
    
    try {
        log('debug', '正在请求 /api/history.py...');
        const response = await fetch('/api/history.py');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        log('success', '历史数据加载成功', data);
        
        // 验证数据结构
        if (!data.history || !Array.isArray(data.history)) {
            throw new Error('历史数据格式不正确');
        }
        
        displayHistory(data);
        
        loadingEl.style.display = 'none';
        contentEl.style.display = 'block';
        
    } catch (error) {
        log('error', '历史数据加载失败', error);
        loadingEl.style.display = 'none';
        errorEl.style.display = 'block';
        
        // 更新错误信息
        const errorText = errorEl.querySelector('p');
        if (errorText) {
            errorText.textContent = `加载失败: ${error.message}`;
        }
    }
}

// ==============================================
// 13. 显示历史数据
// ==============================================
function displayHistory(data) {
    log('info', '开始渲染历史数据', data);
    
    const tbody = document.getElementById('history-tbody');
    
    if (!tbody) {
        log('error', '找不到 history-tbody 元素');
        return;
    }
    
    if (!data.history || data.history.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: #999;">暂无数据</td></tr>';
        log('warning', '历史数据为空');
        return;
    }
    
    // 只显示最近10期
    const recentData = data.history.slice(0, 10);
    log('debug', `渲染 ${recentData.length} 条历史记录`);
    
    const rowsHTML = recentData.map(item => {
        const period = item.period || '---';
        const date = item.date || '---';
        const redBalls = formatNumbers(item.red_balls, 'red');
        const blueBalls = formatNumbers(item.blue_balls, 'blue');
        
        return `
            <tr>
                <td class="period">${period}</td>
                <td class="date">${date}</td>
                <td class="numbers">
                    <div class="number-display">
                        ${redBalls}
                        <span class="separator">+</span>
                        ${blueBalls}
                    </div>
                </td>
            </tr>
        `;
    }).join('');
    
    tbody.innerHTML = rowsHTML;
    log('success', '历史数据渲染完成');
}

// ==============================================
// 14. 格式化号码显示
// ==============================================
function formatNumbers(numbers, type) {
    if (!numbers || !Array.isArray(numbers) || numbers.length === 0) {
        return '<span style="color: #999;">--</span>';
    }
    
    const className = type === 'red' ? 'red-ball-small' : 'blue-ball-small';
    
    return numbers.map(num => {
        const displayNum = String(num).padStart(2, '0');
        return `<span class="ball-small ${className}">${displayNum}</span>`;
    }).join(' ');
}

// ==============================================
// 15. 预测历史功能
// ==============================================
function showPredictionHistory() {
    if (predictionHistory.length === 0) {
        alert('暂无预测历史记录');
        return;
    }
    
    const historyHTML = `
        <div class="modal-overlay" id="history-modal" onclick="closeHistoryModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h2>📊 预测历史记录</h2>
                    <button class="close-btn" onclick="closeHistoryModal()">×</button>
                </div>
                
                <div class="modal-body">
                    <div class="history-list">
                        ${predictionHistory.map((record, index) => `
                            <div class="history-item">
                                <div class="history-header">
                                    <span class="history-index">#${index + 1}</span>
                                    <span class="history-time">${record.timestamp}</span>
                                </div>
                                <div class="history-numbers">
                                    <div class="red-numbers">
                                        ${record.data.red_balls.map(n => 
                                            `<span class="ball-small red-ball-small">${String(n).padStart(2, '0')}</span>`
                                        ).join('')}
                                    </div>
                                    <span class="separator">+</span>
                                    <div class="blue-numbers">
                                        ${record.data.blue_balls.map(n => 
                                            `<span class="ball-small blue-ball-small">${String(n).padStart(2, '0')}</span>`
                                        ).join('')}
                                    </div>
                                </div>
                                <div class="history-meta">
                                    <span>策略: ${record.data.model}</span>
                                    <span>置信度: ${(record.data.confidence * 100).toFixed(1)}%</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="clearPredictionHistory()">清空历史</button>
                    <button class="btn btn-primary" onclick="closeHistoryModal()">关闭</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', historyHTML);
}

function closeHistoryModal() {
    const modal = document.getElementById('history-modal');
    if (modal) {
        modal.remove();
    }
}

function clearPredictionHistory() {
    if (confirm('确定要清空所有预测历史记录吗？')) {
        predictionHistory = [];
        closeHistoryModal();
        log('info', '预测历史已清空');
    }
}

// ==============================================
// 16. 显示关于页面
// ==============================================
function showAbout() {
    const predictionsEl = document.getElementById('predictions');
    const aboutEl = document.getElementById('about');
    
    if (predictionsEl && aboutEl) {
        predictionsEl.style.display = 'none';
        aboutEl.style.display = 'block';
        log('info', '显示关于页面');
    }
}

// ==============================================
// 17. 隐藏关于页面
// ==============================================
function hideAbout() {
    const predictionsEl = document.getElementById('predictions');
    const aboutEl = document.getElementById('about');
    
    if (predictionsEl && aboutEl) {
        aboutEl.style.display = 'none';
        predictionsEl.style.display = 'block';
        log('info', '返回主页面');
    }
}

// ==============================================
// 18. 错误显示
// ==============================================
function showError(message) {
    log('error', '显示错误信息', message);
    
    const predictionsEl = document.getElementById('predictions');
    
    if (!predictionsEl) return;
    
    predictionsEl.innerHTML = `
        <div class="error-message" style="
            text-align: center;
            padding: 40px 20px;
            background: #fff3cd;
            border-radius: 10px;
            margin: 20px 0;
        ">
            <span style="font-size: 48px;">❌</span>
            <h3 style="color: #856404; margin: 20px 0;">加载失败</h3>
            <p style="color: #856404; margin-bottom: 20px;">${message}</p>
            <button onclick="loadPrediction(false)" class="btn btn-primary" style="
                padding: 12px 30px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
            ">
                🔄 重试
            </button>
        </div>
    `;
}

// ==============================================
// 导出函数（供HTML调用）
// ==============================================
window.loadPrediction = loadPrediction;
window.reanalyze = reanalyze;
window.changeStrategy = changeStrategy;
window.loadHistory = loadHistory;
window.showAbout = showAbout;
window.hideAbout = hideAbout;
window.showPredictionHistory = showPredictionHistory;
window.closeHistoryModal = closeHistoryModal;
window.clearPredictionHistory = clearPredictionHistory;

// 初始化完成
log('success', 'main.js 加载完成！版本: 3.0 - 包含重新分析功能');
```

---

## 🚀 最简单的方法：完整替换

### Step 1: 打开 GitHub 编辑器

访问：
```
https://github.com/Baggio200cn/Large-model-post-training/blob/main/public/js/main.js
```

### Step 2: 点击编辑按钮

点击右上角的铅笔图标 ✏️

### Step 3: 全选删除

- 按 `Ctrl + A` (全选)
- 按 `Delete` (删除)

### Step 4: 粘贴新代码

- 复制上面完整的 main.js 代码
- 粘贴到编辑器中（`Ctrl + V`）

### Step 5: 提交更改

滚动到页面底部：
- **Commit message**: `feat: Add complete reanalysis functionality with strategy selection`
- 点击 **"Commit changes"** 按钮

---

## ✅ 验证步骤

### 提交后：

1. **Vercel 会自动部署**（等待 1-2 分钟）

2. **访问您的网站**

3. **按 F12** 打开控制台

4. **应该看到**：
```
   ✅ [时间] main.js 加载完成！版本: 3.0 - 包含重新分析功能
