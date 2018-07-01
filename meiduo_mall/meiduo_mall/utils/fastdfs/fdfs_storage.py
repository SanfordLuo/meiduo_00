from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings


class FastDFSStorage(Storage):
    """自定义文件存储系统：实现文件被转存到fdfs"""

    def __init__(self, client_conf=None, base_url=None):
        """构造方法
        当在存储数据时，django会自动的调用构造方法，"但不会传参进来"
        """
        self.client_conf = client_conf or settings.FDFS_CLIENT_CONF
        self.base_url = base_url or settings.FDFS_BASE_URL


    def _open(self, name, mode='rb'):
        """打开文件时调用的
        因为此时只有文件的上传，没有文件要打开，但是了又必须实现，所以pass
        """
        pass

    def _save(self, name, content):
        """
        存储文件时调用的
        :param name: 要存储的文件的名字
        :param content: 要存储的文件的对象，File类型的对象，需要调用read()读取出要上传的文件的内容
        :return: file_id
        """

        # 创建fdfs客户端，跟tracker进行交互
        # 'meiduo_mall/utils/fastdfs/client.conf'
        client = Fdfs_client(self.client_conf)
        # 调用上传方法：根据文件的内容上传的
        ret = client.upload_by_buffer(content.read())
        # 判断上传是否成功
        if ret.get('Status') != 'Upload successed.':
            raise Exception('upload file failed')

        # 返回file_id: 模型类会自动的读取这个file_id，存储到模型类中的ImageField字段
        file_id = ret.get('Remote file_id')
        return file_id

    def exists(self, name):
        """
        判断文件是否已经在本地存储，
        返回True表示文件已经存储在本地，django不会再去存储该文件
        返回False时,告诉Django该文件是新的文件，请你存储。只有返回False，Django才会积极的存储文件到fdfs
        :param name: 要上传的文件的名字
        :return: False
        """
        return False

    def url(self, name):
        """
        返回文件的全路径
        该方法时提供给模型类中的ImageField字段对应的属性调用的（file_id被存储在ImageField字段中）
        :param name: 要返回全路径的文件的名字
        :return: http://192.168.204.129:8888/group1/M00/00/00/wKjMgVs3VtiABbuCAAEuFfD3cc0009.jpg
        """
        # 'http://192.168.204.129:8888/'
        return self.base_url + name

