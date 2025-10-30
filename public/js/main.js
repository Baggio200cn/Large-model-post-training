// ==============================================
// AI彩票分析实验室 - 主JavaScript文件
// 更新日期: 2025-10-30
// 功能: 动态时间显示 + API数据加载
// ==============================================

// 全局变量
let currentUpdateTime = '';

// ==============================================
// 页面加载时自动执行
// ==============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 页面加载完成，开始初始化...');
    
    // 自动加载预测和历史数据
    loadPrediction();
    loadHistory();
});

// ==============================================
// 1. 加载AI预测结果
// ==============================================
async function loadPrediction() {
    console.log('📊 开始加载预测数据...');
    
    const loadingEl = document.getElementById('loading');
    const predictionsEl = document.getElementById('predictions');
    
    // 显示加载状态
    loadingEl.style.display = 'block';
    predictionsEl.style.display = 'none';
    
    try {
        // 调用预测API
        const response = await fetch('/api/predict-realtime.py');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ 预测数据加载成功:', data);
        
        // 显示预测结果
        displayPrediction(data);
        
        // 获取并更新时间戳
        await fetchAndUpdateTimestamp();
        
    } catch (error) {
        console.error('❌ 加载预测失败:', error);
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
    try {
        const response = await fetch('/api/latest-results.py');
        const data = await response.json();
        
        if (data.status === 'success' && data.updated_at) {
            currentUpdateTime = data.updated_at;
            updateTimestampDisplay(currentUpdateTime);
            console.log('⏰ 时间戳更新:', currentUpdateTime);
        }
    } catch (error) {
        console.error('⚠️ 时间戳获取失败:', error);
        // 使用当前时间作为备用
        const now = new Date();
        currentUpdateTime = now.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        }).replace(/\//g, '-');
        updateTimestampDisplay(currentUpdateTime);
    }
}

// ==============================================
// 3. 更新页面上的时间显示
// ==============================================
function updateTimestampDisplay(timestamp) {
    // 查找模型信息区域
    const modelInfoEl = document.getElementById('model-info');
    
    if (modelInfoEl) {
        // 更新或添加时间信息
        let timeText = `训练时间: ${timestamp}`;
        
        // 如果已经有内容，追加时间；否则直接设置
        if (modelInfoEl.innerHTML.trim()) {
            // 替换现有时间
            modelInfoEl.innerHTML = modelInfoEl.innerHTML.replace(
                /训练时间:.*?(\<|\n|$)/,
                `训练时间: ${timestamp}$1`
            );
            
            // 如果没有找到训练时间，添加到末尾
            if (!modelInfoEl.innerHTML.includes('训练时间')) {
                modelInfoEl.innerHTML += `<p class="update-time">⏰ ${timeText}</p>`;
            }
        } else {
            modelInfoEl.innerHTML = `<p class="update-time">⏰ ${timeText}</p>`;
        }
    }
    
    console.log('✅ 时间显示已更新:', timestamp);
}

// ==============================================
// 4. 显示预测结果
// ==============================================
function displayPrediction(data) {
    console.log('🎨 开始渲染预测结果...');
    
    // 红球显示
    const redBallsEl = document.getElementById('red-balls');
    if (redBallsEl && data.red_balls) {
        redBallsEl.innerHTML = data.red_balls
            .map(num => `<div class="ball red-ball">${num.toString().padStart(2, '0')}</div>`)
            .join('');
    }
    
    // 蓝球显示
    const blueBallsEl = document.getElementById('blue-balls');
    if (blueBallsEl && data.blue_balls) {
        blueBallsEl.innerHTML = data.blue_balls
            .map(num => `<div class="ball blue-ball">${num.toString().padStart(2, '0')}</div>`)
            .join('');
    }
    
    // 模型信息显示
    const modelInfoEl = document.getElementById('model-info');
    if (modelInfoEl) {
        let infoHTML = '<div class="model-details">';
        
        if (data.confidence) {
            infoHTML += `<p>📊 <strong>置信度:</strong> ${(data.confidence * 100).toFixed(1)}%</p>`;
        }
        
        if (data.model) {
            infoHTML += `<p>🤖 <strong>模型:</strong> ${data.model}</p>`;
        }
        
        if (data.based_on_count) {
            infoHTML += `<p>📈 <strong>基于:</strong> ${data.based_on_count} 期历史数据</p>`;
        }
        
        // 添加时间戳（如果已经获取到）
        if (currentUpdateTime) {
            infoHTML += `<p class="update-time">⏰ <strong>训练时间:</strong> ${currentUpdateTime}</p>`;
        }
        
        infoHTML += '</div>';
        modelInfoEl.innerHTML = infoHTML;
    }
    
    console.log('✅ 预测结果渲染完成');
}

// ==============================================
// 5. 加载历史开奖记录
// ==============================================
async function loadHistory() {
    console.log('📜 开始加载历史数据...');
    
    const loadingEl = document.getElementById('history-loading');
    const contentEl = document.getElementById('history-content');
    const errorEl = document.getElementById('history-error');
    
    // 显示加载状态
    loadingEl.style.display = 'flex';
    contentEl.style.display = 'none';
    errorEl.style.display = 'none';
    
    try {
        const response = await fetch('/api/history-realtime.py');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ 历史数据加载成功:', data);
        
        displayHistory(data);
        
        loadingEl.style.display = 'none';
        contentEl.style.display = 'block';
        
    } catch (error) {
        console.error('❌ 历史数据加载失败:', error);
        loadingEl.style.display = 'none';
        errorEl.style.display = 'block';
    }
}

// ==============================================
// 6. 显示历史数据
// ==============================================
function displayHistory(data) {
    const tbody = document.getElementById('history-tbody');
    
    if (!tbody || !data.history || data.history.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3">暂无数据</td></tr>';
        return;
    }
    
    // 只显示最近10期
    const recentData = data.history.slice(0, 10);
    
    tbody.innerHTML = recentData.map(item => `
        <tr>
            <td class="period">${item.period || '---'}</td>
            <td class="date">${item.date || '---'}</td>
            <td class="numbers">
                <div class="number-display">
                    ${formatNumbers(item.red_balls, 'red')}
                    <span class="separator">+</span>
                    ${formatNumbers(item.blue_balls, 'blue')}
                </div>
            </td>
        </tr>
    `).join('');
    
    console.log('✅ 历史数据渲染完成');
}

// ==============================================
// 7. 格式化号码显示
// ==============================================
function formatNumbers(numbers, type) {
    if (!numbers || !Array.isArray(numbers)) {
        return '<span>--</span>';
    }
    
    const className = type === 'red' ? 'red-ball-small' : 'blue-ball-small';
    
    return numbers
        .map(num => `<span class="ball-small ${className}">${num.toString().padStart(2, '0')}</span>`)
        .join(' ');
}

// ==============================================
// 8. 显示关于页面
// ==============================================
function showAbout() {
    document.getElementById('predictions').style.display = 'none';
    document.getElementById('about').style.display = 'block';
    console.log('📖 显示关于页面');
}

// ==============================================
// 9. 隐藏关于页面
// ==============================================
function hideAbout() {
    document.getElementById('about').style.display = 'none';
    document.getElementById('predictions').style.display = 'block';
    console.log('🔙 返回主页面');
}

// ==============================================
// 10. 错误显示
// ==============================================
function showError(message) {
    const predictionsEl = document.getElementById('predictions');
    predictionsEl.innerHTML = `
        <div class="error-message">
            <span class="icon">❌</span>
            <p>${message}</p>
            <button onclick="loadPrediction()" class="btn btn-primary">重试</button>
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

console.log('✅ main.js 加载完成！');
