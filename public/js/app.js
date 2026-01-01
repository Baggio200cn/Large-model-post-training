// 大乐透预测系统前端脚本
console.log('系统初始化...');

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成');
    checkSystemHealth();
});

// 系统健康检查
async function checkSystemHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        console.log('系统状态:', data);
        
        const statusEl = document.getElementById('api-status');
        if (statusEl) {
            if (data.status === 'healthy') {
                statusEl.innerHTML = '<span class=\"status-indicator status-healthy\"></span>系统运行正常';
            } else {
                statusEl.innerHTML = '<span class=\"status-indicator status-error\"></span>系统异常';
            }
        }
    } catch (error) {
        console.error('健康检查失败:', error);
        const statusEl = document.getElementById('api-status');
        if (statusEl) {
            statusEl.innerHTML = '<span class=\"status-indicator status-error\"></span>无法连接到API服务';
        }
    }
}

// 数据分析函数
async function analyzeData() {
    console.log('开始数据分析...');
    const resultEl = document.getElementById('analysis-result');
    if (resultEl) {
        resultEl.innerHTML = '<p>正在分析数据...</p>';
        
        try {
            const response = await fetch('/api/data-analysis');
            const data = await response.json();
            
            if (data.status === 'success') {
                const analysis = data.analysis;
                let content = '<h3>数据分析结果</h3>';
                content += '<p><strong>分析期数:</strong> ' + (analysis.data_overview.total_draws || 'N/A') + '</p>';
                content += '<p><strong>更新时间:</strong> ' + (analysis.data_overview.last_update || 'N/A') + '</p>';
                content += '<h4>前区热门号码</h4>';
                content += '<p>' + (analysis.front_zone_analysis.hot_numbers || []).join(', ') + '</p>';
                content += '<h4>后区热门号码</h4>';
                content += '<p>' + (analysis.back_zone_analysis.hot_numbers || []).join(', ') + '</p>';
                
                resultEl.innerHTML = content;
            } else {
                resultEl.innerHTML = '<p>分析失败: ' + data.message + '</p>';
            }
        } catch (error) {
            resultEl.innerHTML = '<p>请求失败: ' + error.message + '</p>';
        }
    }
}

// AI预测函数
async function predict() {
    console.log('开始AI预测...');
    const resultEl = document.getElementById('prediction-result');
    if (resultEl) {
        resultEl.innerHTML = '<p>AI正在思考...</p>';
        
        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ prediction_type: 'all' })
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                const pred = data.prediction.ensemble_prediction;
                let content = '<h3>AI预测结果</h3>';
                content += '<p><strong>前区:</strong> ' + pred.front_zone.join(', ') + '</p>';
                content += '<p><strong>后区:</strong> ' + pred.back_zone.join(', ') + '</p>';
                content += '<p><strong>置信度:</strong> ' + (pred.confidence * 100).toFixed(1) + '%</p>';
                
                resultEl.innerHTML = content;
            } else {
                resultEl.innerHTML = '<p>预测失败: ' + data.message + '</p>';
            }
        } catch (error) {
            resultEl.innerHTML = '<p>请求失败: ' + error.message + '</p>';
        }
    }
}

// 灵修扰动函数
async function getSpiritualPerturbation() {
    console.log('获取灵修扰动...');
    const resultEl = document.getElementById('spiritual-result');
    if (resultEl) {
        resultEl.innerHTML = '<p>感应宇宙能量...</p>';
        
        try {
            const response = await fetch('/api/spiritual');
            const data = await response.json();
            
            if (data.status === 'success') {
                const spiritual = data.spiritual_perturbation;
                let content = '<h3>灵修扰动因子</h3>';
                content += '<p><strong>能量等级:</strong> ' + spiritual.perturbation_factors.energy_level + '</p>';
                content += '<p><strong>扰动强度:</strong> ' + spiritual.overall_intensity + '</p>';
                content += '<p><strong>宇宙共振:</strong> ' + spiritual.perturbation_factors.cosmic_alignment + '</p>';
                content += '<p><strong>冥想建议:</strong> ' + spiritual.spiritual_guidance.recommended_mantra + '</p>';
                
                resultEl.innerHTML = content;
            } else {
                resultEl.innerHTML = '<p>获取失败: ' + data.message + '</p>';
            }
        } catch (error) {
            resultEl.innerHTML = '<p>请求失败: ' + error.message + '</p>';
        }
    }
}

// 系统健康检查详情
function getSystemHealth() {
    console.log('系统健康检查...');
    checkSystemHealth();
    const resultEl = document.getElementById('monitor-result');
    if (resultEl) {
        resultEl.innerHTML = '<h3>系统检查完成</h3><p>请查看页面顶部的状态指示器</p>';
    }
}
