from utils.data_pipeline import DataPipeline
from sklearn.ensemble import RandomForestRegressor
import importlib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import pandas as pd

def main():
    import numpy as np
    import os
    data_dir = 'data'
    # 自动选择 data 目录下最新/最大 csv 文件
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    if not csv_files:
        raise FileNotFoundError('data 目录下未找到任何 csv 文件！')
    # 选择最大（行数最多）或最新（按修改时间）的 csv 文件
    csv_files_fullpath = [os.path.join(data_dir, f) for f in csv_files]
    # 优先按文件大小排序，若相同则按修改时间
    csv_files_fullpath.sort(key=lambda x: (os.path.getsize(x), os.path.getmtime(x)), reverse=True)
    csv_path = csv_files_fullpath[0]
    print(f"自动选择数据文件: {csv_path}")

    target_col = '后区1'  # 自动切换为 processed_lottery_data.csv 的后区1
    # 支持的模型类型: 'rf', 'xgboost', 'lstm', 'transformer'
    model_types = ['rf', 'xgboost', 'lstm', 'transformer']
    pipeline = DataPipeline(csv_path, target_col=target_col)
    df = pipeline.load_data()
    print("初始特征列：", df.columns.tolist())
    pipeline.preprocess()
    print("预处理后特征列：", pipeline.df.columns.tolist())
    pipeline.feature_engineering()
    print("特征工程后特征列：", pipeline.df.columns.tolist())
    X, y = pipeline.split_X_y()
    print("split_X_y 后特征列：", X.columns.tolist())
    # 数据有效性检查
    if y is None or y.shape[0] == 0 or X.shape[1] == 0:
        print("数据文件无有效目标列或特征列，请检查数据文件格式和内容！")
        print(f"当前特征列: {list(X.columns)}，目标列: {target_col if y is not None else '无'}")
        return
    # 强制将所有特征列转换为数值型（非数值会变为NaN）
    # 排除目标列名作为特征
    X = X.drop(columns=[target_col], errors='ignore')
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors='coerce')
    X = X.select_dtypes(include=[float, int])
    # 先用均值填充所有数值型特征的缺失值
    X = X.fillna(X.mean())
    # 生成交互特征（两两乘积）和历史统计特征，提升性能
    from itertools import combinations
    inter_feats = {f'{f1}_x_{f2}': X[f1] * X[f2] for f1, f2 in combinations(X.columns, 2)}
    window = 3
    roll_feats = {}
    for col in X.columns:
        roll_feats[f'{col}_rollmean'] = X[col].rolling(window, min_periods=1).mean()
        roll_feats[f'{col}_rollstd'] = X[col].rolling(window, min_periods=1).std().fillna(0)
        roll_feats[f'{col}_rollmin'] = X[col].rolling(window, min_periods=1).min()
        roll_feats[f'{col}_rollmax'] = X[col].rolling(window, min_periods=1).max()
    # 一次性合并所有新特征，避免碎片化
    X = pd.concat([X] + [pd.DataFrame(inter_feats), pd.DataFrame(roll_feats)], axis=1)
    # 再剔除所有包含 NaN 的列和行，尤其是 Date 列
    if 'Date' in X.columns:
        X = X.drop(columns=['Date'], errors='ignore')
    X = X.dropna(axis=1, how='any')  # 删除包含NaN的列
    X = X.dropna(axis=0, how='any')  # 删除包含NaN的行
    print("特征工程后特征列（含交互与统计特征）:", X.columns.tolist())
    # 自动特征选择：用随机森林评估特征重要性，筛选top 20特征
    from sklearn.ensemble import RandomForestRegressor
    rf_fs = None
    if X.shape[1] > 20:
        rf_fs = RandomForestRegressor(n_estimators=50, random_state=42)
        rf_fs.fit(X, y)
        importances = rf_fs.feature_importances_
        top_idx = importances.argsort()[::-1][:20]
        top_features = X.columns[top_idx]
        X = X[top_features]
        print("自动筛选Top20特征:", list(top_features))

    # 第3步：数据标准化和归一化
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    print("归一化前X统计:")
    print(X.describe())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    print("标准化后X均值:", X_scaled.mean(axis=0))
    print("标准化后X方差:", X_scaled.std(axis=0))
    minmax = MinMaxScaler()
    X_norm = minmax.fit_transform(X)
    print("归一化后X最小值:", X_norm.min(axis=0))
    print("归一化后X最大值:", X_norm.max(axis=0))
    # 默认后续流程用标准化数据
    X = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
    if X.shape[1] == 0:
        print("没有可用的数值型特征用于训练，请检查数据！")
        print("建议：请将目标列设置为数据中除日期外的某一数值列，如 'Bonus1' 或 'Bonus2'，或检查数据管道是否误删特征。")
        return
    pipeline.X = X  # 保证后续标准化和编码用的也是数值型特征
    pipeline.scale_features()
    print("标准化后特征列：", pipeline.X.columns.tolist())
    pipeline.encode_categorical()
    print("编码后特征列：", pipeline.X.columns.tolist())
    print(f"数据加载与处理完成，特征维度: {X.shape if X is not None else '无'}")

    # 训练/测试集划分
    if y is not None:
        # 确保 y 只包含数值，去除非数字内容
        y = pd.to_numeric(y, errors='coerce')
        valid_idx = y.notna()
        X_valid = X.loc[valid_idx]
        y_valid = y.loc[valid_idx]
        print(f"y_train/y内容预览: {y_valid.values}")
        X_train, X_test, y_train, y_test = train_test_split(X_valid, y_valid, test_size=0.2, random_state=42)

        preds = {}
        from sklearn.model_selection import GridSearchCV
        model_objs = {}
        for model_type in model_types:
            print(f"\n===== 测试模型: {model_type} =====")
            # 输出训练数据统计信息
            print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
            print(f"X_train describe:\n{X_train.describe()}")
            print(f"y_train describe:\n{pd.Series(y_train).describe()}")
            if np.any(np.isnan(X_train)) or np.any(np.isnan(y_train)):
                print("警告：训练数据中存在 NaN，模型训练可能失败！")
            if np.all(X_train == 0) or np.all(y_train == 0):
                print("警告：训练数据全为0，模型无法学习有效信息！")

            if model_type == 'rf':
                # 随机森林参数自动调优
                param_grid = {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [2, 4, 6, None],
                    'min_samples_split': [2, 4, 8]
                }
                grid = GridSearchCV(RandomForestRegressor(random_state=42), param_grid, cv=2, n_jobs=-1)
                grid.fit(X_train, y_train)
                print(f"RF最优参数: {grid.best_params_}")
                model = grid.best_estimator_
                y_pred = model.predict(X_test)
                preds['rf'] = y_pred
                model_objs['rf'] = model
                print("MSE:", mean_squared_error(y_test, y_pred))
                print("R2:", r2_score(y_test, y_pred))

            elif model_type == 'xgboost':
                try:
                    from models import xgboost_model as xgb_mod
                    import xgboost as xgb
                    param_grid = {
                        'n_estimators': [50, 100, 200],
                        'max_depth': [2, 4, 6],
                        'learning_rate': [0.01, 0.1, 0.2]
                    }
                    grid = GridSearchCV(xgb.XGBRegressor(objective='reg:squarederror', eval_metric='rmse'), param_grid, cv=2, n_jobs=-1)
                    grid.fit(X_train, y_train)
                    print(f"XGBoost最优参数: {grid.best_params_}")
                    model = grid.best_estimator_
                    y_pred = model.predict(X_test)
                    preds['xgboost'] = y_pred
                    model_objs['xgboost'] = model
                    print("XGBoost预测结果:", y_pred)
                except Exception as e:
                    print("XGBoost模型训练失败（请确保已安装 xgboost 包且 models 目录有 __init__.py）:", e)

            elif model_type == 'lstm':
                try:
                    from models import lstm_model as lstm_mod
                    X_train_lstm = X_train.values.reshape((X_train.shape[0], 1, X_train.shape[1]))
                    X_test_lstm = X_test.values.reshape((X_test.shape[0], 1, X_test.shape[1]))
                    best_score = float('inf')
                    best_params = None
                    best_pred = None
                    # 参数网格
                    for units in [32, 64, 128]:
                        for batch_size in [8, 16, 32]:
                            for epochs in [10, 20]:
                                print(f"LSTM参数: units={units}, batch_size={batch_size}, epochs={epochs}")
                                # 动态构建模型
                                def build_custom_lstm(input_shape):
                                    import tensorflow as tf
                                    model = tf.keras.Sequential([
                                        tf.keras.layers.LSTM(units, input_shape=input_shape, return_sequences=True),
                                        tf.keras.layers.LSTM(units//2),
                                        tf.keras.layers.Dense(32, activation='relu'),
                                        tf.keras.layers.Dense(1, activation='linear')
                                    ])
                                    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
                                    return model
                                model = build_custom_lstm((1, X_train.shape[1]))
                                model.fit(X_train_lstm, y_train.values, epochs=epochs, batch_size=batch_size, verbose=0)
                                y_pred = model.predict(X_test_lstm).flatten()
                                mse = np.mean((y_pred - y_test.values)**2)
                                print(f"LSTM参数组合MSE: {mse}")
                                if mse < best_score:
                                    best_score = mse
                                    best_params = {'units': units, 'batch_size': batch_size, 'epochs': epochs}
                                    best_pred = y_pred
                    preds['lstm'] = best_pred
                    model_objs['lstm'] = model  # 仅保存最后一次模型
                    print(f"LSTM最优参数: {best_params}, 最优MSE: {best_score}")
                    print("LSTM预测结果:", best_pred)
                except Exception as e:
                    print("LSTM模型训练失败（请确保已安装 tensorflow 包且 models 目录有 __init__.py）:", e)

            elif model_type == 'transformer':
                try:
                    from models import transformer_model as transformer_mod
                    X_train_tf = X_train.values.reshape((X_train.shape[0], 1, X_train.shape[1]))
                    X_test_tf = X_test.values.reshape((X_test.shape[0], 1, X_test.shape[1]))
                    best_score = float('inf')
                    best_params = None
                    best_pred = None
                    for units in [32, 64, 128]:
                        for batch_size in [8, 16, 32]:
                            for epochs in [10, 20]:
                                print(f"Transformer参数: units={units}, batch_size={batch_size}, epochs={epochs}")
                                def build_custom_transformer(input_shape):
                                    import tensorflow as tf
                                    inputs = tf.keras.Input(shape=input_shape)
                                    x = tf.keras.layers.MultiHeadAttention(num_heads=4, key_dim=units//4)(inputs, inputs)
                                    x = tf.keras.layers.LayerNormalization()(x)
                                    x = tf.keras.layers.Dense(units, activation='relu')(x)
                                    outputs = tf.keras.layers.Dense(1, activation='linear')(x)
                                    outputs = tf.keras.layers.Flatten()(outputs)
                                    model = tf.keras.Model(inputs, outputs)
                                    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
                                    return model
                                model = build_custom_transformer((1, X_train.shape[1]))
                                model.fit(X_train_tf, y_train.values, epochs=epochs, batch_size=batch_size, verbose=0)
                                y_pred = model.predict(X_test_tf).flatten()
                                mse = np.mean((y_pred - y_test.values)**2)
                                print(f"Transformer参数组合MSE: {mse}")
                                if mse < best_score:
                                    best_score = mse
                                    best_params = {'units': units, 'batch_size': batch_size, 'epochs': epochs}
                                    best_pred = y_pred
                    preds['transformer'] = best_pred
                    model_objs['transformer'] = model  # 仅保存最后一次模型
                    print(f"Transformer最优参数: {best_params}, 最优MSE: {best_score}")
                    print("Transformer预测结果:", best_pred)
                except Exception as e:
                    print("Transformer模型训练失败（请确保已安装 tensorflow 包且 models 目录有 __init__.py）:", e)

            else:
                print(f"未知模型类型: {model_type}")

        # 集成方式优化
        if preds:
            import numpy as np
            import matplotlib.pyplot as plt
            min_len = min(len(p) for p in preds.values())
            # 1. 简单平均
            ensemble_pred = np.mean([p[:min_len] for p in preds.values()], axis=0)
            print(f"\n===== 集成模型平均预测结果 =====\n{ensemble_pred}")

            # 2. 加权平均（按模型MSE倒数加权）
            mses = {}
            for name, pred in preds.items():
                mses[name] = np.mean((pred[:min_len] - y_test.values[:min_len])**2)
            weights = np.array([1/mses[n] if mses[n]>0 else 0 for n in preds.keys()])
            weights = weights / weights.sum() if weights.sum()>0 else np.ones_like(weights)/len(weights)
            weighted_pred = np.sum([w*p[:min_len] for w,p in zip(weights, preds.values())], axis=0)
            print(f"===== 加权平均集成结果（MSE倒数加权） =====\n{weighted_pred}")

            # 3. 简单Stacking（用线性回归融合）
            from sklearn.linear_model import LinearRegression
            stack_X = np.vstack([p[:min_len] for p in preds.values()]).T
            stack_y = y_test.values[:min_len]
            stack_model = LinearRegression().fit(stack_X, stack_y)
            stack_pred = stack_model.predict(stack_X)
            print(f"===== 简单Stacking集成结果（线性回归融合） =====\n{stack_pred}")

            # 结果可视化
            plt.figure(figsize=(10, 6))
            for name, pred in preds.items():
                plt.plot(pred[:min_len], label=f'{name}预测')
            plt.plot(y_test.values[:min_len], label='真实值', linestyle='--', color='black')
            plt.plot(ensemble_pred, label='平均集成', linestyle=':')
            plt.plot(weighted_pred, label='加权集成', linestyle='-.')
            plt.plot(stack_pred, label='Stacking集成', linestyle='--')
            plt.title('各模型与集成预测对比')
            plt.legend()
            plt.xlabel('样本')
            plt.ylabel('目标值')
            plt.tight_layout()
            plt.savefig('ensemble_vs_true.png')
            print('已保存集成预测对比图：ensemble_vs_true.png')

            # 特征重要性条形图（以rf为例）
            if 'rf' in model_objs:
                try:
                    importances = model_objs['rf'].feature_importances_
                    feat_names = X.columns
                    plt.figure(figsize=(10, 6))
                    plt.barh(feat_names, importances)
                    plt.title('随机森林特征重要性')
                    plt.tight_layout()
                    plt.savefig('rf_feature_importance.png')
                    print('已保存特征重要性图：rf_feature_importance.png')
                except Exception as e:
                    print('特征重要性可视化失败:', e)
        else:
            print("无可用模型预测结果，无法集成。")
    else:
        print("未指定目标列，无法训练模型。")

if __name__ == '__main__':
    main()
