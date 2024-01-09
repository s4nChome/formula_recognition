from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid
from flask import jsonify
import signal
from models import *
from app import db
from PIL import Image

def api_response(data=None, message=None, code=200, elapsed=None, filepath=None):
    response = {
        "data": data,
        "message": message,
        "code": code,
        "elapsed": elapsed,
        "filepath":filepath
    }
    return jsonify(response)

# 超时处理函数
def handler(signum, frame):
    raise TimeoutError("Processing Time Exceeded 10 Seconds")

# 设置超时的函数
def set_timeout(time):
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(time)

# 保存识别成功的日志
def recognition_success(image_path, result,model):
    recognition_success = Success(
        time=datetime.now(),
        model=model,
        image=image_path,
        result=result
    )
    db.session.add(recognition_success)
    db.session.commit()

# 保存识别失败的日志
def recognition_fail(image_path, reason,model):
    recognition_fail = Error(
        time=datetime.now(),
        model=model,
        image=image_path,
        reason=reason
    )
    db.session.add(recognition_fail)
    db.session.commit()

# 保存纠错的结果    
def correction_result(image_path, wrong_result,right_result, model):
    correction_result = Correction(
        time=datetime.now(),
        model=model,
        image=image_path,
        wrong_result=wrong_result,
        right_result=right_result
    )
    db.session.add(correction_result)
    db.session.commit()

# 保存识别图片
def save_file(file, upload_folder, allowed_extensions):
    # 检查文件扩展名是否允许
    if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
        # 确保上传文件夹存在，如果不存在则创建它
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # 生成唯一的文件名
        unique_filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(upload_folder, unique_filename)
        
        try:
            # 打开图像并获取其大小
            img = Image.open(file)
            width, height = img.size
            
            # 将图像的大小放大一倍
            img = img.resize((width * 2, height * 2), Image.BICUBIC)
            
            # 保存图像
            img.save(filepath)
            
            return filepath
        except Exception as e:
            # 处理可能的异常情况
            print(f"Error processing image: {e}")
            return None
    else:
        return None
