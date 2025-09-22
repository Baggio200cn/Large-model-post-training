// 修正的 API 调用函数

// 1. 测试 API 连接
async function testAPI() {
    try {
        const response = await fetch('/api/test');
        const data = await response.json();
        console.log('API Test Result:', data);
        return data;
    } catch (error) {
        console.error('API Test Failed:', error);
        return null;
    }
}

// 2. 数据分析功能 - 确保路径正确
async function performDataAnalysis() {
    const resultsDiv = document.getElementById('analysisResults');
    const loadingDiv = document.getElementById('analysisLoading');
    const contentDiv = document.getElementById('analysisContent');
    
    resultsDiv.style.display = 'block';
    loadingDiv.style.display = 'block';
    contentDiv.innerHTML = '';
    
    try {
        // 使用正确的文件名路径
        const response = await fetch('/api/data-analysis');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        loadingDiv.style.display = 'none';
        
        if (data.status === 'success') {
            const analysis = data.analysis;
            contentDiv.innerHTML = `
                <div class="success">数据分析完成</div>
                <div class="analysis-results">
                    <div class="analysis-item"><strong>分析期数:</strong> ${analysis.data_overview.total_draws}</div>
                    <div class="analysis-item"><strong>更新时间:</strong> ${analysis.data_overview.last_update}</div>
                    <div class="analysis-item"><strong>前区热号:</strong> ${analysis.front_zone_analysis.hot_numbers.join(', ')}</div>
                    <div class="analysis-item"><strong>后区热号:</strong> ${analysis.back_zone_analysis.hot_numbers.join(', ')}</div>
                </div>
            `;
        } else {
            throw new Error(data.message || '分析失败');
        }
    } catch (error) {
        loadingDiv.style.display = 'none';
        contentDiv.innerHTML = `<div class="error">数据分析失败: ${error.message}</div>`;
    }
}

// 3. 获取最新开奖结果
async function loadLatestResults() {
    try {
        const loadingElement = document.querySelector('#latestResults .loading');
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }
        
        const response = await fetch('/api/latest-results');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            displayLatestResults(data.latest_results);
        } else {
            throw new Error(data.message || '获取数据失败');
        }
    } catch (error) {
        const contentElement = document.getElementById('latestResultsContent');
        if (contentElement) {
            contentElement.innerHTML = `<div class="error">获取最新开奖结果失败: ${error.message}</div>`;
        }
    }
}

// 4. AI预测功能
async function generateAIPrediction() {
    const resultsDiv = document.getElementById('predictionResults');
    const loadingDiv = document.getElementById('predictionLoading');
    const contentDiv = document.getElementById('predictionContent');
    
    resultsDiv.style.display = 'block';
    loadingDiv.style.display = 'block';
    contentDiv.innerHTML = '';
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prediction_type: 'all'
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        loadingDiv.style.display = 'none';
        
        if (data.status === 'success') {
            const pred = data.prediction.ensemble_prediction;
            contentDiv.innerHTML = `
                <div class="success">AI预测完成</div>
                <div class="analysis-results">
                    <div class="analysis-item"><strong>前区预测:</strong> ${pred.front_zone.join(', ')}</div>
                    <div class="analysis-item"><strong>后区预测:</strong> ${pred.back_zone.join(', ')}</div>
                    <div class="analysis-item"><strong>置信度:</strong> ${(pred.confidence * 100).toFixed(1)}%</div>
                    <div class="analysis-item"><strong>预测时间:</strong> ${data.timestamp}</div>
                </div>
            `;
        } else {
            throw new Error(data.message || '预测失败');
        }
    } catch (error) {
        loadingDiv.style.display = 'none';
        contentDiv.innerHTML = `<div class="error">AI预测失败: ${error.message}</div>`;
    }
}

// 5. 健康检查
async function performHealthCheck() {
    const resultsDiv = document.getElementById('healthResults');
    const loadingDiv = document.getElementById('healthLoading');
    const contentDiv = document.getElementById('healthContent');
    
    resultsDiv.style.display = 'block';
    loadingDiv.style.display = 'block';
    contentDiv.innerHTML = '';
    
    try {
        const response = await fetch('/api/health');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        loadingDiv.style.display = 'none';
        
        if (data.status === 'healthy') {
            contentDiv.innerHTML = `
                <div class="success">系统检查完成</div>
                <div class="analysis-results">
                    <div class="analysis-item"><strong>系统状态:</strong> ${data.status}</div>
                    <div class="analysis-item"><strong>服务版本:</strong> ${data.version}</div>
                    <div class="analysis-item"><strong>检查时间:</strong> ${data.timestamp}</div>
                </div>
            `;
        } else {
            throw new Error('系统状态异常');
        }
    } catch (error) {
        loadingDiv.style.display = 'none';
        contentDiv.innerHTML = `<div class="error">健康检查失败: ${error.message}</div>`;
    }
}

// 页面加载时的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 先测试 API 连接
    testAPI().then(result => {
        if (result && result.status === 'success') {
            console.log('API 连接正常');
            // 然后加载最新结果
            loadLatestResults();
        } else {
            console.error('API 连接失败');
        }
    });
});
