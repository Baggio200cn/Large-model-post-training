// ==============================================
// AI彩票分析实验室 - 主JavaScript文件
// 版本: 2.0 - 完整生产版
// 更新日期: 2025-10-30
// 功能: 完整的API集成 + 错误处理 + 动态时间
// ==============================================

// 全局变量
let currentUpdateTime = '';
let debugMode = true; // 开启调试模式

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
    loadPrediction();
    loadHistory();
});

// ==============================================
// 1. 加载AI预测结果
// ==============================================
async function loadPrediction() {
    log('info', '开始加载预测数据...');
    
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
        // 调用预测API
        log('debug', '正在请求 /api/predict.py...');
        const response = await fetch('/api/predict.py');
        
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
        
        // 显示预测结果
        displayPrediction(data);
        
        // 获取并更新时间戳
        await fetchAndUpdateTimestamp();
        
    } catch (error) {
        log('error', '加载预测失败', error);
        showError('预测加载失败: ' + error.message);
    } finally {
        loadingEl.style.display = 'none';
        predictionsEl.style.display = 'block';
    }
}

// ==============================================
// 2. 获取并更新时间戳
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
// 3. 更新页面上的时间显示
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
// 4. 显示预测结果
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
// 5. 显示号码球（通用函数）
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
// 6. 显示模型信息
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
// 7. 加载历史开奖记录
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
// 8. 显示历史数据
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
// 9. 格式化号码显示
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
// 10. 显示关于页面
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
// 11. 隐藏关于页面
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
// 12. 错误显示
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
            <button onclick="loadPrediction()" class="btn btn-primary" style="
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
window.loadHistory = loadHistory;
window.showAbout = showAbout;
window.hideAbout = hideAbout;

// 初始化完成
log('success', 'main.js 加载完成！版本: 2.0');
