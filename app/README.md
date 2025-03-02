单元测试：

    ```
    python -m unittest tests.test_verification
    ```
创建虚拟环境（windows）

```
python -m venv env
```

进入虚拟环境

```
env\Scripts\activate
```

更新pip

```
 python.exe -m pip install --upgrade pip
```

添加依赖

```
echo 'fastapi[all]==0.115.6' > requirements.txt
```

运行

```
uvicorn main:app
```

