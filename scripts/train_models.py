"""
训练4个机器学习模型
1. Random Forest
2. XGBoost
3. LSTM
4. Transformer
"""
import sys
import os
import pickle
import json
import numpy as np
from datetime import datetime

# 传统机器学习模型
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import hamming_loss, accuracy_score

# XGBoost
import xgboost as xgb

# 深度学习
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


def load_training_data(data_dir='data/training'):
    """加载训练数据"""
    with open(f'{data_dir}/training_data.pkl', 'rb') as f:
        data = pickle.load(f)
    return data


def train_random_forest(X_train, y_train, X_test, y_test, zone='front'):
    """训练随机森林模型"""
    print(f"\n{'='*60}")
    print(f"训练随机森林模型 - {zone}区")
    print(f"{'='*60}")

    model = MultiOutputClassifier(
        RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
    )

    print("🎯 开始训练...")
    model.fit(X_train, y_train)

    # 评估
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)

    train_loss = hamming_loss(y_train, train_pred)
    test_loss = hamming_loss(y_test, test_pred)

    print(f"✅ 训练完成")
    print(f"   训练集 Hamming Loss: {train_loss:.4f}")
    print(f"   测试集 Hamming Loss: {test_loss:.4f}")

    return model, {
        'train_loss': float(train_loss),
        'test_loss': float(test_loss),
        'model_type': 'RandomForest',
        'zone': zone
    }


def train_xgboost(X_train, y_train, X_test, y_test, zone='front'):
    """训练XGBoost模型"""
    print(f"\n{'='*60}")
    print(f"训练XGBoost模型 - {zone}区")
    print(f"{'='*60}")

    # XGBoost支持多标签分类
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        tree_method='hist'
    )

    # 对每个输出维度训练一个模型
    models = []
    n_outputs = y_train.shape[1]

    print(f"🎯 开始训练 {n_outputs} 个输出...")

    for i in range(n_outputs):
        if (i + 1) % 10 == 0:
            print(f"   进度: {i+1}/{n_outputs}")

        clf = xgb.XGBClassifier(
            n_estimators=50,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            tree_method='hist'
        )
        clf.fit(X_train, y_train[:, i])
        models.append(clf)

    # 评估
    train_preds = np.array([m.predict(X_train) for m in models]).T
    test_preds = np.array([m.predict(X_test) for m in models]).T

    train_loss = hamming_loss(y_train, train_preds)
    test_loss = hamming_loss(y_test, test_preds)

    print(f"✅ 训练完成")
    print(f"   训练集 Hamming Loss: {train_loss:.4f}")
    print(f"   测试集 Hamming Loss: {test_loss:.4f}")

    return models, {
        'train_loss': float(train_loss),
        'test_loss': float(test_loss),
        'model_type': 'XGBoost',
        'zone': zone,
        'n_models': len(models)
    }


def create_lstm_model(input_dim, output_dim):
    """创建LSTM模型"""
    model = keras.Sequential([
        layers.Input(shape=(10, input_dim // 10)),  # 假设10个时间步
        layers.LSTM(128, return_sequences=True),
        layers.Dropout(0.3),
        layers.LSTM(64),
        layers.Dropout(0.3),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(output_dim, activation='sigmoid')
    ])

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    return model


def train_lstm(X_train, y_train, X_test, y_test, zone='front'):
    """训练LSTM模型"""
    print(f"\n{'='*60}")
    print(f"训练LSTM模型 - {zone}区")
    print(f"{'='*60}")

    # 重塑数据为时间序列格式
    n_timesteps = 10
    feature_dim = X_train.shape[1] // n_timesteps

    X_train_reshaped = X_train[:, :n_timesteps * feature_dim].reshape(
        -1, n_timesteps, feature_dim
    )
    X_test_reshaped = X_test[:, :n_timesteps * feature_dim].reshape(
        -1, n_timesteps, feature_dim
    )

    model = create_lstm_model(n_timesteps * feature_dim, y_train.shape[1])

    print("🎯 开始训练...")
    history = model.fit(
        X_train_reshaped, y_train,
        validation_data=(X_test_reshaped, y_test),
        epochs=20,
        batch_size=32,
        verbose=0
    )

    train_loss = history.history['loss'][-1]
    test_loss = history.history['val_loss'][-1]

    print(f"✅ 训练完成")
    print(f"   训练集 Loss: {train_loss:.4f}")
    print(f"   测试集 Loss: {test_loss:.4f}")

    return model, {
        'train_loss': float(train_loss),
        'test_loss': float(test_loss),
        'model_type': 'LSTM',
        'zone': zone,
        'epochs': 20
    }


def create_transformer_model(input_dim, output_dim):
    """创建Transformer模型"""
    inputs = layers.Input(shape=(input_dim,))

    # 简化的Transformer编码器
    x = layers.Dense(128)(inputs)
    x = layers.Reshape((16, 8))(x)  # 重塑为序列

    # Multi-head attention
    attention_output = layers.MultiHeadAttention(
        num_heads=4,
        key_dim=8
    )(x, x)

    x = layers.Add()([x, attention_output])
    x = layers.LayerNormalization()(x)

    # Feed forward
    ff = layers.Dense(64, activation='relu')(x)
    ff = layers.Dense(8)(ff)

    x = layers.Add()([x, ff])
    x = layers.LayerNormalization()(x)

    # 输出层
    x = layers.Flatten()(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(output_dim, activation='sigmoid')(x)

    model = keras.Model(inputs=inputs, outputs=outputs)

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    return model


def train_transformer(X_train, y_train, X_test, y_test, zone='front'):
    """训练Transformer模型"""
    print(f"\n{'='*60}")
    print(f"训练Transformer模型 - {zone}区")
    print(f"{'='*60}")

    model = create_transformer_model(X_train.shape[1], y_train.shape[1])

    print("🎯 开始训练...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=20,
        batch_size=32,
        verbose=0
    )

    train_loss = history.history['loss'][-1]
    test_loss = history.history['val_loss'][-1]

    print(f"✅ 训练完成")
    print(f"   训练集 Loss: {train_loss:.4f}")
    print(f"   测试集 Loss: {test_loss:.4f}")

    return model, {
        'train_loss': float(train_loss),
        'test_loss': float(test_loss),
        'model_type': 'Transformer',
        'zone': zone,
        'epochs': 20
    }


def save_models(models, output_dir='data/models'):
    """保存所有模型"""
    os.makedirs(output_dir, exist_ok=True)

    saved_info = {}

    for model_name, (model, metadata) in models.items():
        model_path = f'{output_dir}/{model_name}.pkl'

        if 'LSTM' in model_name or 'Transformer' in model_name:
            # Keras模型保存为.h5格式
            model_path = f'{output_dir}/{model_name}.h5'
            model.save(model_path)
        else:
            # sklearn和xgboost模型保存为.pkl
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)

        saved_info[model_name] = {
            'path': model_path,
            'metadata': metadata,
            'saved_at': datetime.now().isoformat()
        }

        print(f"💾 已保存: {model_name} -> {model_path}")

    # 保存模型信息
    with open(f'{output_dir}/models_info.json', 'w', encoding='utf-8') as f:
        json.dump(saved_info, f, ensure_ascii=False, indent=2)

    return saved_info


def main():
    print("=" * 70)
    print("🤖 训练机器学习模型")
    print("=" * 70)

    # 加载数据
    print("\n📚 加载训练数据...")
    data = load_training_data()

    X_train = data['X_train']
    X_test = data['X_test']
    y_front_train = data['y_front_train']
    y_front_test = data['y_front_test']
    y_back_train = data['y_back_train']
    y_back_test = data['y_back_test']

    print(f"   训练集: {X_train.shape[0]} 样本")
    print(f"   测试集: {X_test.shape[0]} 样本")

    models = {}

    # 1. Random Forest - 前区
    rf_front, rf_front_meta = train_random_forest(
        X_train, y_front_train, X_test, y_front_test, 'front'
    )
    models['random_forest_front'] = (rf_front, rf_front_meta)

    # 2. XGBoost - 前区
    xgb_front, xgb_front_meta = train_xgboost(
        X_train, y_front_train, X_test, y_front_test, 'front'
    )
    models['xgboost_front'] = (xgb_front, xgb_front_meta)

    # 3. LSTM - 前区
    lstm_front, lstm_front_meta = train_lstm(
        X_train, y_front_train, X_test, y_front_test, 'front'
    )
    models['lstm_front'] = (lstm_front, lstm_front_meta)

    # 4. Transformer - 前区
    transformer_front, transformer_front_meta = train_transformer(
        X_train, y_front_train, X_test, y_front_test, 'front'
    )
    models['transformer_front'] = (transformer_front, transformer_front_meta)

    # 保存模型
    print(f"\n{'='*70}")
    print("💾 保存模型...")
    print(f"{'='*70}")

    saved_info = save_models(models)

    print(f"\n{'='*70}")
    print("✅ 所有模型训练完成！")
    print(f"{'='*70}")
    print(f"\n共训练了 {len(models)} 个模型：")
    for name, info in saved_info.items():
        meta = info['metadata']
        print(f"  - {name}: 测试Loss={meta['test_loss']:.4f}")

    return models, saved_info


if __name__ == '__main__':
    main()
