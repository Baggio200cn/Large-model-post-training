/**
 * AI彩票分析实验室 - 主JavaScript文件
 */

// 全局状态
let currentPrediction = null;

/**
 * 加载预测数据
 */
async function loadPrediction() {
    console.log('开始加载预测数据...');
    
    // 显示加载状态
    showLoading();

    try {
        // 调用API
        const response = await fetch('/api/predict');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentPrediction = data.data;
            displayPrediction(data.data);
        } else {
            showError(data.error || '预测失败，请稍后重试');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('网络错误或服务暂时不可用，请稍后重试');
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
 * 显示预测结果
 */
function displayPrediction(data) {
    console.log('显示预测结果:', data);
    
    // 显示红球
    const redContainer = document.getElementById('red-balls');
    if (redContainer) {
        redContainer.innerHTML = '';
        data.red.slice(0, 5).forEach(ball => {
            const div = createBallElement(ball, 'red');
            redContainer.appendChild(div);
        });
    }

    // 显示蓝球
    const blueContainer = document.getElementById('blue-balls');
    if (blueContainer) {
        blueContainer.innerHTML = '';
        data.blue.slice(0, 2).forEach(ball => {
            const div = createBallElement(ball, 'blue');
            blueContainer.appendChild(div);
        });
    }

    // 显示模型信息
    const modelInfo = document.getElementById('model-info');
    if (modelInfo && data.model_info) {
        const trainedDate = new Date(data.model_info.trained_at).toLocaleString('zh-CN');
        modelInfo.innerHTML = `
            <strong>模型信息：</strong>
            训练时间：${trainedDate} | 
            分析窗口：最近${data.model_info.window_size}期 | 
            方法：频率统计分析
        `;
    }

    // 隐藏加载，显示结果
    document.getElementById('loading').style.display = 'none';
    document.getElementById('predictions').style.display = 'block';
    document.getElementById('predictions').classList.add('fade-in');
}

/**
 * 创建彩球元素
 */
function createBallElement(ball, type) {
    const div = document.createElement('div');
    div.className = `ball ${type}`;
    div.innerHTML = `
        <span class="number">${ball.number.toString().padStart(2, '0')}</span>
        <span class="reason">${ball.reason}</span>
        <span class="probability">${(ball.probability * 100).toFixed(2)}%</span>
    `;
    
    // 添加点击效果
    div.addEventListener('click', () => {
        showBallDetail(ball, type);
    });
    
    return div;
}

/**
 * 显示彩球详情（可选功能）
 */
function showBallDetail(ball, type) {
    const typeName = type === 'red' ? '红球' : '蓝球';
    const message = `
${typeName} ${ball.number.toString().padStart(2, '0')}

分类：${ball.reason}
出现概率：${(ball.probability * 100).toFixed(2)}%

这个概率基于最近100期的历史数据统计。
注意：历史频率不能预测未来结果。
    `.trim();
    
    alert(message);
}

/**
 * 显示错误信息
 */
function showError(message) {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.innerHTML = `
            <div style="color: #dc3545;">
                <h3>❌ 出错了</h3>
                <p>${message}</p>
                <button onclick="loadPrediction()" class="btn btn-primary" style="margin-top: 20px;">
                    重试
                </button>
            </div>
        `;
    }
}

/**
 * 显示关于页面
 */
function showAbout() {
    document.getElementById('predictions').style.display = 'none';
    document.getElementById('about').style.display = 'block';
    document.getElementById('about').classList.add('fade-in');
}

/**
 * 隐藏关于页面
 */
function hideAbout() {
    document.getElementById('about').style.display = 'none';
    document.getElementById('predictions').style.display = 'block';
}

/**
 * 页面加载完成后自动执行
 */
window.addEventListener('DOMContentLoaded', () => {
    console.log('AI彩票分析实验室已启动');
    
    // 自动加载预测
    loadPrediction();
    
    // 添加键盘快捷键
    document.addEventListener('keydown', (e) => {
        // 按R键重新加载
        if (e.key === 'r' || e.key === 'R') {
            loadPrediction();
        }
        // 按ESC键关闭关于页面
        if (e.key === 'Escape') {
            const about = document.getElementById('about');
            if (about && about.style.display !== 'none') {
                hideAbout();
            }
        }
    });
});

/**
 * 工具函数：格式化日期
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * 工具函数：下载预测结果（可选功能）
 */
function downloadPrediction() {
    if (!currentPrediction) {
        alert('暂无预测数据');
        return;
    }
    
    const text = generatePredictionText(currentPrediction);
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `prediction_${new Date().getTime()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * 生成预测文本（用于下载）
 */
function generatePredictionText(data) {
    const lines = [];
    lines.push('='.repeat(50));
    lines.push('AI彩票分析实验室 - 预测结果');
    lines.push('='.repeat(50));
    lines.push('');
    lines.push('红球推荐：');
    data.red.slice(0, 5).forEach((ball, i) => {
        lines.push(`  ${i + 1}. ${ball.number.toString().padStart(2, '0')} - ${ball.reason} (${(ball.probability * 100).toFixed(2)}%)`);
    });
    lines.push('');
    lines.push('蓝球推荐：');
    data.blue.slice(0, 2).forEach((ball, i) => {
        lines.push(`  ${i + 1}. ${ball.number.toString().padStart(2, '0')} - ${ball.reason} (${(ball.probability * 100).toFixed(2)}%)`);
    });
    lines.push('');
    lines.push('='.repeat(50));
    lines.push('⚠️  免责声明');
    lines.push('='.repeat(50));
    lines.push('本预测仅基于历史数据统计，不能提高中奖概率。');
    lines.push('彩票是随机事件，请理性购买。');
    lines.push('');
    
    return lines.join('\n');
}

// 导出函数供HTML使用
window.loadPrediction = loadPrediction;
window.showAbout = showAbout;
window.hideAbout = hideAbout;
window.downloadPrediction = downloadPrediction;
