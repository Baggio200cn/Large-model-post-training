"""
腾讯云对象存储（COS）工具模块
用于上传和下载数据、模型文件
"""
import os
import json
import pickle
import tempfile
from typing import Optional, Dict, Any
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


class TencentCOSClient:
    """腾讯云COS客户端"""

    def __init__(
        self,
        secret_id: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: Optional[str] = None,
        bucket: Optional[str] = None
    ):
        """
        初始化腾讯云COS客户端

        Args:
            secret_id: 腾讯云SecretId（可从环境变量获取）
            secret_key: 腾讯云SecretKey（可从环境变量获取）
            region: 存储桶区域（如：ap-guangzhou）
            bucket: 存储桶名称
        """
        self.secret_id = secret_id or os.getenv('TENCENT_SECRET_ID')
        self.secret_key = secret_key or os.getenv('TENCENT_SECRET_KEY')
        self.region = region or os.getenv('TENCENT_COS_REGION', 'ap-guangzhou')
        self.bucket = bucket or os.getenv('TENCENT_COS_BUCKET')

        if not all([self.secret_id, self.secret_key, self.bucket]):
            raise ValueError(
                "缺少腾讯云配置！请设置环境变量：\n"
                "TENCENT_SECRET_ID, TENCENT_SECRET_KEY, TENCENT_COS_BUCKET"
            )

        # 初始化配置
        self.config = CosConfig(
            Region=self.region,
            SecretId=self.secret_id,
            SecretKey=self.secret_key,
            Scheme='https'
        )

        # 创建客户端
        self.client = CosS3Client(self.config)

        print(f"✅ 腾讯云COS客户端初始化成功")
        print(f"   区域: {self.region}")
        print(f"   存储桶: {self.bucket}")

    def upload_file(self, local_path: str, cos_path: str) -> Dict[str, Any]:
        """
        上传文件到COS

        Args:
            local_path: 本地文件路径
            cos_path: COS上的路径（如：data/lottery_history.json）

        Returns:
            上传结果信息
        """
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"本地文件不存在: {local_path}")

        print(f"📤 上传文件: {local_path} -> cos://{self.bucket}/{cos_path}")

        try:
            response = self.client.upload_file(
                Bucket=self.bucket,
                LocalFilePath=local_path,
                Key=cos_path,
                PartSize=10,
                MAXThread=10
            )

            file_size = os.path.getsize(local_path) / 1024  # KB
            print(f"✅ 上传成功！文件大小: {file_size:.2f} KB")

            return {
                'success': True,
                'cos_path': cos_path,
                'local_path': local_path,
                'size_kb': file_size,
                'etag': response.get('ETag', '')
            }

        except Exception as e:
            print(f"❌ 上传失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def download_file(self, cos_path: str, local_path: str) -> Dict[str, Any]:
        """
        从COS下载文件

        Args:
            cos_path: COS上的路径
            local_path: 本地保存路径

        Returns:
            下载结果信息
        """
        # 确保本地目录存在
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        print(f"📥 下载文件: cos://{self.bucket}/{cos_path} -> {local_path}")

        try:
            response = self.client.download_file(
                Bucket=self.bucket,
                Key=cos_path,
                DestFilePath=local_path
            )

            file_size = os.path.getsize(local_path) / 1024  # KB
            print(f"✅ 下载成功！文件大小: {file_size:.2f} KB")

            return {
                'success': True,
                'cos_path': cos_path,
                'local_path': local_path,
                'size_kb': file_size
            }

        except Exception as e:
            print(f"❌ 下载失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def upload_json(self, data: Any, cos_path: str) -> Dict[str, Any]:
        """
        上传JSON数据到COS

        Args:
            data: 要上传的数据（将被序列化为JSON）
            cos_path: COS上的路径

        Returns:
            上传结果信息
        """
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', delete=False) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            temp_path = f.name

        try:
            result = self.upload_file(temp_path, cos_path)
            return result
        finally:
            os.unlink(temp_path)

    def download_json(self, cos_path: str) -> Any:
        """
        从COS下载JSON数据

        Args:
            cos_path: COS上的路径

        Returns:
            解析后的JSON数据
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            result = self.download_file(cos_path, temp_path)

            if result['success']:
                with open(temp_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data
            else:
                raise Exception(f"下载失败: {result.get('error')}")

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def upload_pickle(self, data: Any, cos_path: str) -> Dict[str, Any]:
        """
        上传pickle序列化的数据到COS

        Args:
            data: 要上传的数据（将被pickle序列化）
            cos_path: COS上的路径

        Returns:
            上传结果信息
        """
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pkl', delete=False) as f:
            pickle.dump(data, f)
            temp_path = f.name

        try:
            result = self.upload_file(temp_path, cos_path)
            return result
        finally:
            os.unlink(temp_path)

    def download_pickle(self, cos_path: str) -> Any:
        """
        从COS下载pickle数据

        Args:
            cos_path: COS上的路径

        Returns:
            反序列化后的数据
        """
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pkl', delete=False) as f:
            temp_path = f.name

        try:
            result = self.download_file(cos_path, temp_path)

            if result['success']:
                with open(temp_path, 'rb') as f:
                    data = pickle.load(f)
                return data
            else:
                raise Exception(f"下载失败: {result.get('error')}")

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def list_files(self, prefix: str = '', max_keys: int = 1000) -> list:
        """
        列出COS中的文件

        Args:
            prefix: 路径前缀（如：data/）
            max_keys: 最大返回数量

        Returns:
            文件列表
        """
        print(f"📋 列出文件: cos://{self.bucket}/{prefix}")

        try:
            response = self.client.list_objects(
                Bucket=self.bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )

            files = []
            if 'Contents' in response:
                for item in response['Contents']:
                    files.append({
                        'key': item['Key'],
                        'size': int(item['Size']),
                        'last_modified': item['LastModified']
                    })

            print(f"✅ 找到 {len(files)} 个文件")
            return files

        except Exception as e:
            print(f"❌ 列出文件失败: {str(e)}")
            return []

    def file_exists(self, cos_path: str) -> bool:
        """
        检查文件是否存在

        Args:
            cos_path: COS上的路径

        Returns:
            是否存在
        """
        try:
            self.client.head_object(
                Bucket=self.bucket,
                Key=cos_path
            )
            return True
        except:
            return False


# 创建全局客户端实例（可选）
_global_client: Optional[TencentCOSClient] = None


def get_cos_client() -> TencentCOSClient:
    """获取全局COS客户端实例"""
    global _global_client

    if _global_client is None:
        _global_client = TencentCOSClient()

    return _global_client


if __name__ == '__main__':
    # 测试代码
    print("=" * 60)
    print("腾讯云COS工具测试")
    print("=" * 60)

    try:
        client = TencentCOSClient()

        # 测试列出文件
        files = client.list_files(prefix='data/')

        if files:
            print("\n当前存储的文件：")
            for f in files:
                print(f"  - {f['key']} ({f['size']} bytes)")
        else:
            print("\n暂无文件")

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        print("\n请确保已设置环境变量：")
        print("  export TENCENT_SECRET_ID=your_secret_id")
        print("  export TENCENT_SECRET_KEY=your_secret_key")
        print("  export TENCENT_COS_BUCKET=your_bucket_name")
        print("  export TENCENT_COS_REGION=ap-guangzhou")
