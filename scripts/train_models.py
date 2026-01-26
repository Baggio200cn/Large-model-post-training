"""
训练4个机器学习模型并转换为Vercel兼容格式
1. Random Forest (.pkl)
2. XGBoost (.pkl)
3. LSTM (.onnx)
4. Transformer (.onnx)

运行前安装依赖:
pip install scikit-learn xgboost tensorflow tf2onnx onnxruntime
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
from sklearn.metrics import hamming_loss

# XGBoost
import xgboost as xgb

# 深度学习
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


def load_training_data(data_dir='data/training'):
    """加载训练数据"""
    try:
        with open(f'{data_dir}/training_data.pkl', 'rb') as f:
            data = pickle.load(f)
        return data
    except FileNotFoundError:
        print("⚠️  训练数据文件不存在，使用内置数据生成...")
        return generate_training_data()


def generate_training_data():
    """从lottery_data生成训练数据"""
    # 尝试加载本地数据
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

    try:
        from utils._lottery_data import lottery_data
        data = lottery_data
    except ImportError:
        print("❌ 无法加载lottery_data")
        sys.exit(1)

    print(f"📊 使用 {len(data)} 期数据生成训练集...")

    sequence_length = 10
    X = []
    y_front = []
    y_back = []

    for i in range(len(data) - sequence_length):
        # 特征：过去sequence_length期的号码
        features = []
        for j in range(sequence_length):
            record = data[i + j]
            front = record.get('front_zone', [])
            back = record.get('back_zone', [])
            features.extend(front[:5] if len(front) >= 5 else front + [0] * (5 - len(front)))
            features.extend(back[:2] if len(back) >= 2 else back + [0] * (2 - len(back)))

        # 标签：下一期的号码
        next_record = data[i + sequence_length]
        next_front = next_record.get('front_zone', [])
        next_back = next_record.get('back_zone', [])

        # 前区标签 (35维one-hot)
        front_label = np.zeros(35)
        for n in next_front[:5]:
            if 1 <= n <= 35:
                front_label[n - 1] = 1

        # 后区标签 (12维one-hot)
        back_label = np.zeros(12)
        for n in next_back[:2]:
            if 1 <= n <= 12:
                back_label[n - 1] = 1

        X.append(features)
        y_front.append(front_label)
        y_back.append(back_label)

    X = np.array(X, dtype=np.float32)
    y_front = np.array(y_front, dtype=np.float32)
    y_back = np.array(y_back, dtype=np.float32)

    # 划分训练集和测试集
    split = int(len(X) * 0.8)

    return {
        'X_train': X[:split],
        'X_test': X[split:],
        'y_front_train': y_front[:split],
        'y_front_test': y_front[split:],
        'y_back_train': y_back[:split],
        'y_back_test': y_back[split:]
    }


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
            tree_method='hist',
            use_label_encoder=False,
            eval_metric='logloss'
        )
        clf.fit(X_train, y_train[:, i])
        models.append(clf)

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


def create_lstm_model(sequence_length, feature_dim, output_dim):
    """创建LSTM模型"""
    model = keras.Sequential([
        layers.Input(shape=(sequence_length, feature_dim)),
        layers.LSTM(64, return_sequences=True),
        layers.Dropout(0.2),
        layers.LSTM(32),
        layers.Dropout(0.2),
        layers.Dense(64, activation='relu'),
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

    # 重塑数据为时间序列格式 (samples, timesteps, features)
    n_timesteps = 10
    feature_dim = X_train.shape[1] // n_timesteps

    X_train_seq = X_train[:, :n_timesteps * feature_dim].reshape(-1, n_timesteps, feature_dim)
    X_test_seq = X_test[:, :n_timesteps * feature_dim].reshape(-1, n_timesteps, feature_dim)

    model = create_lstm_model(n_timesteps, feature_dim, y_train.shape[1])

    print("🎯 开始训练...")
    history = model.fit(
        X_train_seq, y_train,
        validation_data=(X_test_seq, y_test),
        epochs=30,
        batch_size=32,
        verbose=1
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
        'input_shape': (n_timesteps, feature_dim)
    }


def create_transformer_model(input_dim, output_dim):
    """创建Transformer模型"""
    inputs = layers.Input(shape=(input_dim,))

    # 重塑为序列
    x = layers.Dense(128)(inputs)
    x = layers.Reshape((16, 8))(x)

    # Multi-head attention
    attention_output = layers.MultiHeadAttention(num_heads=4, key_dim=8)(x, x)
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
        epochs=30,
        batch_size=32,
        verbose=1
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
        'input_shape': (X_train.shape[1],)
    }


def convert_keras_to_onnx(model, model_name, input_shape, output_dir):
    """将Keras模型转换为ONNX格式"""
    import tf2onnx

    print(f"\n🔄 转换 {model_name} 到ONNX格式...")

    output_path = f'{output_dir}/{model_name}.onnx'

    # 定义输入签名
    spec = (tf.TensorSpec(input_shape, tf.float32, name="input"),)

    # 转换
    model_proto, _ = tf2onnx.convert.from_keras(
        model,
        input_signature=spec,
        output_path=output_path
    )

    print(f"✅ 已保存: {output_path}")
    return output_path


def save_models(models, output_dir='models'):
    """保存所有模型"""
    os.makedirs(output_dir, exist_ok=True)

    saved_info = {'models': {}}

    for model_name, (model, metadata) in models.items():
        if 'lstm' in model_name.lower():
            # LSTM模型转换为ONNX
            input_shape = metadata.get('input_shape', (10, 7))
            batch_input_shape = (None,) + input_shape
            model_path = convert_keras_to_onnx(model, model_name, batch_input_shape, output_dir)
            saved_info['models'][model_name] = {
                'type': 'onnx',
                'format': 'onnx',
                'path': model_path,
                'metadata': metadata
            }

        elif 'transformer' in model_name.lower():
            # Transformer模型转换为ONNX
            input_shape = metadata.get('input_shape', (70,))
            batch_input_shape = (None,) + input_shape
            model_path = convert_keras_to_onnx(model, model_name, batch_input_shape, output_dir)
            saved_info['models'][model_name] = {
                'type': 'onnx',
                'format': 'onnx',
                'path': model_path,
                'metadata': metadata
            }

        else:
            # sklearn和xgboost模型保存为.pkl
            model_path = f'{output_dir}/{model_name}.pkl'
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            saved_info['models'][model_name] = {
                'type': 'sklearn',
                'format': 'pkl',
                'path': model_path,
                'metadata': metadata
            }

        print(f"💾 已保存: {model_name}")

    # 保存模型信息
    saved_info['version'] = '2.0.0'
    saved_info['trained_at'] = datetime.now().isoformat()

    info_path = f'{output_dir}/models_info.json'
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(saved_info, f, ensure_ascii=False, indent=2)

    print(f"\n📋 模型信息已保存: {info_path}")
    return saved_info


def upload_to_cos(output_dir='models'):
    """上传模型到腾讯云COS"""
    # 检查COS配置
    cos_configured = all([
        os.getenv('TENCENT_SECRET_ID'),
        os.getenv('TENCENT_SECRET_KEY'),
        os.getenv('TENCENT_COS_BUCKET'),
        os.getenv('TENCENT_COS_REGION')
    ])

    if not cos_configured:
        print("\n⚠️  腾讯云COS未配置，跳过上传")
        print("   请设置以下环境变量:")
        print("   - TENCENT_SECRET_ID")
        print("   - TENCENT_SECRET_KEY")
        print("   - TENCENT_COS_BUCKET")
        print("   - TENCENT_COS_REGION")
        return

    print("\n📤 上传模型到腾讯云COS...")

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))
    from utils.tencent_cos import get_cos_client

    client = get_cos_client()

    # 上传所有模型文件
    for filename in os.listdir(output_dir):
        local_path = os.path.join(output_dir, filename)
        cos_path = f'models/{filename}'

        print(f"   上传: {filename} -> {cos_path}")
        client.upload_file(local_path, cos_path)

    print("✅ 所有模型已上传到COS")


def main():
    print("=" * 70)
    print("🤖 训练机器学习模型 (Vercel兼容版)")
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
    print(f"   特征维度: {X_train.shape[1]}")
    print(f"   前区输出: {y_front_train.shape[1]}")
    print(f"   后区输出: {y_back_train.shape[1]}")

    models = {}

    # 训练前区模型
    print("\n" + "=" * 70)
    print("训练前区模型")
    print("=" * 70)

    rf_front, rf_front_meta = train_random_forest(
        X_train, y_front_train, X_test, y_front_test, 'front'
    )
    models['random_forest_front'] = (rf_front, rf_front_meta)

    xgb_front, xgb_front_meta = train_xgboost(
        X_train, y_front_train, X_test, y_front_test, 'front'
    )
    models['xgboost_front'] = (xgb_front, xgb_front_meta)

    lstm_front, lstm_front_meta = train_lstm(
        X_train, y_front_train, X_test, y_front_test, 'front'
    )
    models['lstm_front'] = (lstm_front, lstm_front_meta)

    transformer_front, transformer_front_meta = train_transformer(
        X_train, y_front_train, X_test, y_front_test, 'front'
    )
    models['transformer_front'] = (transformer_front, transformer_front_meta)

    # 训练后区模型
    print("\n" + "=" * 70)
    print("训练后区模型")
    print("=" * 70)

    rf_back, rf_back_meta = train_random_forest(
        X_train, y_back_train, X_test, y_back_test, 'back'
    )
    models['random_forest_back'] = (rf_back, rf_back_meta)

    xgb_back, xgb_back_meta = train_xgboost(
        X_train, y_back_train, X_test, y_back_test, 'back'
    )
    models['xgboost_back'] = (xgb_back, xgb_back_meta)

    lstm_back, lstm_back_meta = train_lstm(
        X_train, y_back_train, X_test, y_back_test, 'back'
    )
    models['lstm_back'] = (lstm_back, lstm_back_meta)

    transformer_back, transformer_back_meta = train_transformer(
        X_train, y_back_train, X_test, y_back_test, 'back'
    )
    models['transformer_back'] = (transformer_back, transformer_back_meta)

    # 保存模型
    print(f"\n{'='*70}")
    print("💾 保存模型 (sklearn -> .pkl, keras -> .onnx)")
    print(f"{'='*70}")

    saved_info = save_models(models, output_dir='models')

    # 上传到COS
    upload_to_cos(output_dir='models')

    print(f"\n{'='*70}")
    print("✅ 所有模型训练完成！")
    print(f"{'='*70}")
    print(f"\n共训练了 {len(models)} 个模型：")
    for name, info in saved_info['models'].items():
        meta = info['metadata']
        print(f"  - {name} ({info['format']}): 测试Loss={meta['test_loss']:.4f}")

    print("\n📁 模型文件保存在: models/")
    print("   - *.pkl: sklearn/xgboost模型 (Vercel可直接加载)")
    print("   - *.onnx: LSTM/Transformer模型 (需要onnxruntime)")

    return models, saved_info


if __name__ == '__main__':
    main()
