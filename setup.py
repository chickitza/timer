from distutils.core import setup
import py2exe

setup(
    name='Timer',
    version='0.1',
    py_modules=['main', 'records'],  # 明确指出要包含的模块
    # 其他配置...
)