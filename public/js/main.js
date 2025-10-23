/**
 * AI彩票分析实验室 - 主JavaScript文件（智能API切换版）
 */

// 全局状态
let currentPrediction = null;
let historyData = null;

/**
 * 页面加载时初始化
 */
window.addEventListener('DOMContentLoaded', () => {
    console.log('页面加载完成，开始初始化...');
    loadPrediction();
    loadHistory();
});

/**
 * 加载预测数据（智能切换）
 */
async function loadPrediction() {
    console.log('开始加载预测数据...');
    
    // 显示加载状态
    showLoading();

    try {
        // 优先尝试使用缓存的模型（快速）
        let response = await fetch('/api/predict');
        
        // 如果缓存API失败，自动切换到实时API
        if (!response.ok) {
            console.log('缓存API失败，切换到实时API...');
            response = await fetch('/api/predict-realtime');
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentPrediction = data.data;
            displayPrediction(data.data, data.realtime);
        } else {
            showError(data.error || '预测失败，请稍后重试');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('网络错误或服务暂时不可用，请稍后重试');
    }
}

/**
 * 加载历史数据（智能切换）
 */
async function loadHistory() {
    console.log('开始加载历史数据...');
    
    const loadingEl = document.getElementById('history-loading');
    const contentEl = document.getElementById('history-content');
    const errorEl = document.getElementById('history-error');
    
    // 显示加载状态
    if (loadingEl) loadingEl.style.display = 'flex';
    if (contentEl) contentEl.style.display = 'none';
    if (errorEl) errorEl.style.display = 'none';

    try {
        // 优先尝试使用缓存的历史数据（快速）
        let response = await fetch('/api/history?limit=10');
        
        // 如果缓存API失败，自动切换到实时API
        if (!response.ok) {
            console.log('缓存历史API失败，切换到实时API...');
            response = await fetch('/api/history-realtime?limit=10');
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            historyData = data.data;
            displayHistory(data.data, data.realtime);
            
            // 隐藏加载，显示内容
            if (loadingEl) loadingEl.style.display = 'none';
            if (contentEl) contentEl.style.display = 'block';
        } else {
            throw new Error(data.error || '加载失败');
        }
    } catch (error) {
        console.error('History Error:', error);
        
        // 显示错误
        if (loadingEl) loadingEl.style.display = 'none';
        if (errorEl) errorEl.style.display = 'block';
    }
}

/**
 * 显示历史数据
 */
function displayHistory(data, isRealtime) {
    const tbody = document.getElementById('history-tbody');
    if (!tbody) return;
    
    // 清空现有内容
    tbody.innerHTML = '';
    
    // 生成表格行
    data.forEach((item, index) => {
        const row = document.createElement('tr');
        
        // 期号
        const periodCell = document.createElement('td');
        periodCell.className = 'period-cell';
        periodCell.textContent = item.period;
        
        // 日期
        const dateCell = document.createElement('td');
        dateCell.className = 'date-cell';
        dateCell.textContent = item.date;
        
        // 开奖号码
        const numbersCell = document.createElement('td');
        numbersCell.className = 'numbers-cell';
        
        // 创建号码显示区域
        const numbersContainer = document.createElement('div');
        numbersContainer.className = 'history-balls-container';
        
        // 红球
        item.red_balls.forEach(num => {
            const ball = document.createElement('span');
            ball.className = 'history-ball red';
            ball.textContent = String(num).padStart(2, '0');
            numbersContainer.appendChild(ball);
        });
        
        // 分隔符
        const separator = document.createElement('span');
        separator.className = 'ball-separator';
        separator.textContent = '+';
        numbersContainer.appendChild(separator);
        
        // 蓝球
        item.blue_balls.forEach(num => {
            const ball = document.createElement('span');
            ball.className = 'history-ball blue';
            ball.textContent = String(num).padStart(2, '0');
            numbersContainer.appendChild(ball);
        });
        
        numbersCell.appendChild(numbersContainer);
        
        // 添加到行
        row.appendChild(periodCell);
        row.appendChild(dateCell);
        row.appendChild(numbersCell);
        
        // 添加到表格
        tbody.appendChild(row);
        
        // 添加动画延迟
        row.style.animationDelay = `${index * 0.05}s`;
    });
    
    // 如果是实时数据，显示标记
    if (isRealtime) {
        const title = document.querySelector('.history-card .section-title .subtitle-small');
        if (title) {
            title.innerHTML = '最近10期数据 <span style="color: #10b981;">● 实时</span>';
        }
    }
}

/**
 * 显示加载状态
 */
function showLoading() {
    const loading = document.getElementById('loading');
    const predictions = document.getElementById('predictions');
    
    if (loading) loading.style.display = 'block';
    if (predictions) predictions.style.display = 'none';
}

/**
 * 显示错误
 */
function showError(message) {
    const loading = document.getElementById('loading');
    
    if (loading) {
        loading.innerHTML = `
            <div class="error">
                <span class="icon">❌</span>
                <h3>出错了</h3>
                <p>${message}</p>
                <button onclick="loadPrediction()" class="btn btn-primary">重试</button>
            </div>
        `;
    }
}

/**
 * 显示预测结果
 */
function displayPrediction(data, isRealtime) {
    const loading = document.getElementById('loading');
    const predictions = document.getElementById('predictions');
    
    if (loading) loading.style.display = 'none';
    if (predictions) predictions.style.display = 'block';
    
    // 显示红球
    displayBalls('red-balls', data.red, 'red');
    
    // 显示蓝球
    displayBalls('blue-balls', data.blue, 'blue');
    
    // 显示模型信息
    displayModelInfo(data.model_info, isRealtime);
}

/**
 * 显示号码球
 */
function displayBalls(containerId, balls, type) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    
    balls.forEach((ball, index) => {
        const ballEl = document.createElement('div');
        ballEl.className = `ball ${type}`;
        ballEl.style.animationDelay = `${index * 0.1}s`;
        
        ballEl.innerHTML = `
            <div class="ball-number">${String(ball.number).padStart(2, '0')}</div>
            <div class="ball-info">
                <div class="ball-probability">${(ball.probability * 100).toFixed(2)}%</div>
                <div class="ball-reason">${ball.reason}</div>
            </div>
        `;
        
        container.appendChild(ballEl);
    });
}

/**
 * 显示模型信息
 */
function displayModelInfo(info, isRealtime) {
    const container = document.getElementById('model-info');
    if (!container) return;
    
    const trainingDate = info.trained_at === 'unknown' 
        ? '未知' 
        : new Date(info.trained_at).toLocaleString('zh-CN');
    
    const dataSource = isRealtime 
        ? '<span style="color: #10b981; font-weight: 600;">● 实时API</span>' 
        : '缓存模型';
    
    container.innerHTML = `
        <div class="info-item">
            <span class="label">模型信息：</span>
            <span class="value">训练时间: ${trainingDate} | 分析窗口: 最近${info.window_size}期 | 方法: 频率统计分析 | 数据源: ${dataSource}</span>
        </div>
    `;
}

/**
 * 显示关于页面
 */
function showAbout() {
    const mainCard = document.querySelector('.main-card');
    const historyCard = document.querySelector('.history-card');
    const aboutCard = document.getElementById('about');
    
    if (mainCard) mainCard.style.display = 'none';
    if (historyCard) historyCard.style.display = 'none';
    if (aboutCard) aboutCard.style.display = 'block';
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * 隐藏关于页面
 */
function hideAbout() {
    const mainCard = document.querySelector('.main-card');
    const historyCard = document.querySelector('.history-card');
    const aboutCard = document.getElementById('about');
    
    if (mainCard) mainCard.style.display = 'block';
    if (historyCard) historyCard.style.display = 'block';
    if (aboutCard) aboutCard.style.display = 'none';
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

console.log('main.js 加载完成（智能API切换版）');