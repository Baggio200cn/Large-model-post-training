# utils/data_pipeline.py
"""
统一数据管道：数据加载、预处理、特征工程、标准化、编码等
供ML和统计模型共用
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split

class DataPipeline:
    def __init__(self, csv_path, target_col=None):
        self.csv_path = csv_path
        self.target_col = target_col
        self.df = None
        self.X = None
        self.y = None
        self.feature_names = None
        self.scaler = None
        self.encoder = None

    def load_data(self):
        self.df = pd.read_csv(self.csv_path)
        return self.df

    def preprocess(self, fillna_method='ffill', dropna=False):
        # 修正FutureWarning，推荐用ffill/bfill方法
        if fillna_method == 'ffill':
            self.df = self.df.ffill()
        elif fillna_method == 'bfill':
            self.df = self.df.bfill()
        elif fillna_method:
            self.df = self.df.fillna(method=fillna_method)
        if dropna:
            self.df = self.df.dropna()
        return self.df

    def feature_engineering(self):
        # 示例：添加奇偶比、和值、连号数等特征
        df = self.df.copy()
        if 'front1' in df.columns:
            front_cols = [c for c in df.columns if c.startswith('front')]
            df['front_sum'] = df[front_cols].sum(axis=1)
            df['front_even_count'] = df[front_cols].apply(lambda x: sum(n%2==0 for n in x), axis=1)
            df['front_consecutive'] = df[front_cols].apply(lambda x: sum(np.diff(sorted(x))==1), axis=1)
        self.df = df
        return self.df

    def split_X_y(self):
        if self.target_col:
                self.X = self.df.drop(columns=[self.target_col], errors='ignore')
                if self.target_col in self.df.columns:
                    self.y = self.df[self.target_col]
                else:
                    self.y = None
        else:
            self.X = self.df
            self.y = None
        self.feature_names = self.X.columns.tolist()
        return self.X, self.y

    def scale_features(self):
        # 只对数值型特征做标准化，防止字符串报错
        numeric_cols = self.X.select_dtypes(include=[np.number]).columns
        self.scaler = StandardScaler()
        X_scaled = self.X.copy()
        if not numeric_cols.empty:
            X_scaled[numeric_cols] = self.scaler.fit_transform(self.X[numeric_cols])
        self.X = X_scaled
        return self.X

    def encode_categorical(self):
        # 示例：对所有object类型做独热编码
        cat_cols = self.X.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            encoded = self.encoder.fit_transform(self.X[cat_cols])
            encoded_df = pd.DataFrame(encoded, columns=[str(c) for c in self.encoder.get_feature_names_out(cat_cols)])
            encoded_df.index = self.X.index  # 索引对齐，防止concat报错
            self.X = pd.concat([self.X.drop(columns=cat_cols), encoded_df], axis=1)
        return self.X

    def train_test_split(self, test_size=0.2, random_state=42):
        return train_test_split(self.X, self.y, test_size=test_size, random_state=random_state)
