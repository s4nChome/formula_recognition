from app import app
from flask import request
import time
from recognize import *
from models import *
from helpers import *
from threading import Thread
from queue import Queue, Empty
import csv
from flask import send_file

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 获取模型名字
@app.route("/modelnames", methods=["GET"])
def getmodelnames():
    start_time = time.time()
    model_names = ModelName.query.with_entities(ModelName.name).all()
    data = [name[0] for name in model_names]
    end_time = time.time()
    elapse = "{:.5f}".format(end_time - start_time)
    return api_response(data=data, elapsed=elapse)

# 获取模型信息
@app.route("/modelinfo", methods=["GET"])
def getmodelinfo():
    start_time = time.time()
    model_name = request.args.get('model_name')
    model = ModelName.query.filter_by(name=model_name).first()
    if model is None:
        return api_response(data=None, elapsed=None, message='Model not found', code=404)
    data = {
        "model_name": model.name,
        "model_description": model.description,
        "model_url": model.url
    }
    end_time = time.time()
    elapse = "{:.5f}".format(end_time - start_time)
    return api_response(data=data, elapsed=elapse)

# 识别图片
@app.route('/recognize', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return api_response(data=None, elapsed=None, message='No file part', code=400)

    file = request.files['file']

    if file.filename == '':
        return api_response(data=None, elapsed=None, message='No selected file', code=400)

    # 保存图片到本地
    filepath = save_file(file, app.config['UPLOAD_FOLDER'], ALLOWED_EXTENSIONS)

    # 获取模型名称参数
    model_name = request.form.get('model_name')

    # 创建一个队列用于从线程中获取结果
    queue = Queue()

    # 定义一个函数以在线程中运行
    def process_file():
        try:
            if model_name == 'RapidLatexOCR':
                res,elapse = RapidLatexOCR_recognize(filepath)
            elif model_name == 'Pix2Text':
                res,elapse = Pix2Text_recognize(filepath)
            elif model_name == 'pix2tex_e35_step4941':
                res,elapse = Pix2Tex_recognize(filepath)
            elif model_name == 'InternVL':
                res,elapse = internVL_recognize(filepath)
            else:
                queue.put(('Error', 'No such model', 0))
                return
            queue.put((res, 'Success', elapse))
        except Exception as e:
            queue.put(('Error', str(e), 0))

    # 创建并启动线程
    thread = Thread(target=process_file)
    thread.start()

    # 等待线程完成，最多20秒
    try:
        result, message, elapse = queue.get(timeout=200)
    except Empty:
        # 保存识别超时的日志
        recognition_fail(filepath, 'Processing Timeout', model_name)
        return api_response(data=None, elapsed=None, message="Processing Timeout", code=408,filepath=filepath)

    if message != 'Success':
        # 保存识别失败的日志
        recognition_fail(filepath, message, model_name)
        return api_response(data=None, elapsed=None, message=message, code=400,filepath=filepath)

    # 保存识别成功的日志
    recognition_success(filepath, result, model_name)
    return api_response(data=result, elapsed=elapse,filepath=filepath)


# 上传改正后的Latex代码
@app.route('/wrong/upload', methods=['POST'])
def upload_correction():
    try:
        # 从请求中提取数据
        model = request.json['model']
        image_path = request.json['filepath']
        wrong_result = request.json['wrong_result']
        right_result = request.json['right_result']

        # 调用保存函数
        correction_result(image_path, wrong_result, right_result, model)
        return api_response()

    except Exception as e:
        # 捕获其他异常
        return api_response(message=str(e),code = 400)

# 分页查询识别成功列表
@app.route("/success/page", methods=["GET"])
def get_success_list_page():
    start_time = time.time()
    pageNum = request.args.get('pageNum', 1, type=int)
    pageSize = request.args.get('pageSize', 10, type=int)
    modelName = request.args.get('selectedModel', type=str)
    if modelName:
        success_query = Success.query.filter_by(model=modelName)
    else:
        success_query = Success.query

    total = success_query.count()
    total_pages = (total - 1) // pageSize + 1

    if pageNum > total_pages:
        pageNum = total_pages

    success_list = success_query.paginate(page=pageNum, per_page=pageSize, error_out=False)

    data = {
        "total": total,
        "list": [
            {
                "id": success.id,
                "time": success.time.strftime("%Y-%m-%d %H:%M:%S"),
                "model": success.model,
                "image": success.image,
                "result": success.result
            }
            for success in success_list.items
        ]
    }
    end_time = time.time()
    elapse = "{:.5f}".format(end_time - start_time)
    return api_response(data=data, elapsed=elapse)


# 分页查询识别失败列表
@app.route("/error/page", methods=["GET"])
def get_fail_list_page():
    start_time = time.time()
    pageNum = request.args.get('pageNum', 1, type=int)
    pageSize = request.args.get('pageSize', 10, type=int)
    modelName = request.args.get('selectedModel', type=str)
    if modelName:
        fail_query = Error.query.filter_by(model=modelName)
    else:
        fail_query = Error.query

    total = fail_query.count()
    total_pages = (total - 1) // pageSize + 1

    if pageNum > total_pages:
        pageNum = total_pages

    fail_list = fail_query.paginate(page=pageNum, per_page=pageSize, error_out=False)

    data = {
        "total": total,
        "list": [
            {
                "id": fail.id,
                "time": fail.time.strftime("%Y-%m-%d %H:%M:%S"),
                "model": fail.model,
                "image": fail.image,
                "reason": fail.reason
            }
            for fail in fail_list.items
        ]
    }
    end_time = time.time()
    elapse = "{:.5f}".format(end_time - start_time)
    return api_response(data=data, elapsed=elapse)

# 分页查询识别错误列表
@app.route("/wrong/page", methods=["GET"])
def get_wrong_list_page():
    start_time = time.time()
    pageNum = request.args.get('pageNum', 1, type=int)
    pageSize = request.args.get('pageSize', 10, type=int)
    modelName = request.args.get('selectedModel', type=str)
    if modelName:
        correction_query = Correction.query.filter_by(model=modelName)
    else:
        correction_query = Correction.query

    total = correction_query.count()
    total_pages = (total - 1) // pageSize + 1

    if pageNum > total_pages:
        pageNum = total_pages

    wrong_list = correction_query.paginate(page=pageNum, per_page=pageSize, error_out=False)

    data = {
        "total": total,
        "list": [
            {
                "id": wrong.id,
                "time": wrong.time.strftime("%Y-%m-%d %H:%M:%S"),
                "model": wrong.model,
                "image": wrong.image,
                "wrong_result": wrong.wrong_result,
                "right_result": wrong.right_result
            }
            for wrong in wrong_list.items
        ]
    }
    end_time = time.time()
    elapse = "{:.5f}".format(end_time - start_time)
    return api_response(data=data, elapsed=elapse)

# 导出识别成功列表
@app.route("/success/export", methods=["GET"])
def export_success_list():
    fileType = request.args.get('fileType', type=str)
    modelName = request.args.get('selectedModel', type=str)
    if modelName:
        Export_list = Success.query.filter_by(model=modelName).all()
    else:
        Export_list = Success.query.all()

    # 设置文件路径
    app.config['EXPORT_FOLDER'] = os.path.join(app.root_path, 'exports')

    # 如果不存在则创建文件夹
    if not os.path.exists(app.config['EXPORT_FOLDER']):
        os.makedirs(app.config['EXPORT_FOLDER'])

    txt_file_path = os.path.join(app.config['EXPORT_FOLDER'], 'success_export.txt')
    csv_file_path = os.path.join(app.config['EXPORT_FOLDER'], 'success_export.csv')

    #写入txt文件
    if fileType == 'txt':
        with open(txt_file_path, 'w') as txtfile:
            for success in Export_list:
                txtfile.write('id: ' + str(success.id) + '\n')
                txtfile.write('time: ' + success.time.strftime("%Y-%m-%d %H:%M:%S") + '\n')
                txtfile.write('model: ' + success.model + '\n')
                txtfile.write('image: ' + success.image + '\n')
                txtfile.write('result: ' + success.result + '\n\n')

        return send_file(txt_file_path, as_attachment=True, download_name='success_export.txt')
    
    #写入csv文件
    elif fileType == 'csv':
        # 定义CSV文件的表头
        fieldnames = ['id', 'time', 'model', 'image', 'result']
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for success in Export_list:
                writer.writerow({
                    'id': success.id,
                    'time': success.time.strftime("%Y-%m-%d %H:%M:%S"),
                    'model': success.model,
                    'image': success.image,
                    'result': success.result
                })
        return send_file(csv_file_path, as_attachment=True, download_name='success_export.csv')
    
    # 返回错误信息
    else:
        return api_response(message='Invalid file type', code=400)
    

# 导出识别失败列表
@app.route("/error/export", methods=["GET"])
def export_error_list():
    fileType = request.args.get('fileType', type=str)
    modelName = request.args.get('selectedModel', type=str)
    if modelName:
        Export_list = Error.query.filter_by(model=modelName).all()
    else:
        Export_list = Error.query.all()
    
    # 设置文件路径
    app.config['EXPORT_FOLDER'] = os.path.join(app.root_path, 'exports')

    # 如果不存在则创建文件夹
    if not os.path.exists(app.config['EXPORT_FOLDER']):
        os.makedirs(app.config['EXPORT_FOLDER'])

    txt_file_path = os.path.join(app.config['EXPORT_FOLDER'], 'error_export.txt')
    csv_file_path = os.path.join(app.config['EXPORT_FOLDER'], 'error_export.csv')

    # 写入txt文件
    if fileType == 'txt':
        with open(txt_file_path, 'w') as txtfile:
            for error in Export_list:
                txtfile.write('id: ' + str(error.id) + '\n')
                txtfile.write('time: ' + error.time.strftime("%Y-%m-%d %H:%M:%S") + '\n')
                txtfile.write('model: ' + error.model + '\n')
                txtfile.write('image: ' + error.image + '\n')
                txtfile.write('reason: ' + error.reason + '\n\n')

        return send_file(txt_file_path, as_attachment=True, download_name='error_export.txt')
    
    # 写入csv文件
    elif fileType == 'csv':
        # 定义CSV文件的表头
        fieldnames = ['id', 'time', 'model', 'image', 'reason']
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for error in Export_list:
                writer.writerow({
                    'id': error.id,
                    'time': error.time.strftime("%Y-%m-%d %H:%M:%S"),
                    'model': error.model,
                    'image': error.image,
                    'reason': error.reason
                })
        return send_file(csv_file_path, as_attachment=True, download_name='error_export.csv')
    
    # 返回错误信息
    else:
        return api_response(message='Invalid file type', code=400)


# 导出识别错误列表
@app.route("/wrong/export", methods=["GET"])
def export_fail_list():
    fileType = request.args.get('fileType', type=str)
    modelName = request.args.get('selectedModel', type=str)
    if modelName:
        Export_list = Correction.query.filter_by(model=modelName).all()
    else:
        Export_list = Correction.query.all()

    # 设置文件路径
    app.config['EXPORT_FOLDER'] = os.path.join(app.root_path, 'exports')

    # 如果不存在则创建文件夹
    if not os.path.exists(app.config['EXPORT_FOLDER']):
        os.makedirs(app.config['EXPORT_FOLDER'])
    
    txt_file_path = os.path.join(app.config['EXPORT_FOLDER'], 'correction_export.txt')
    csv_file_path = os.path.join(app.config['EXPORT_FOLDER'], 'correction_export.csv')

    # 写入txt文件
    if fileType == 'txt':
        with open(txt_file_path, 'w') as txtfile:
            for correction in Export_list:
                txtfile.write('id: ' + str(correction.id) + '\n')
                txtfile.write('time: ' + correction.time.strftime("%Y-%m-%d %H:%M:%S") + '\n')
                txtfile.write('model: ' + correction.model + '\n')
                txtfile.write('image: ' + correction.image + '\n')
                txtfile.write('wrong_result: ' + correction.wrong_result + '\n')
                txtfile.write('right_result: ' + correction.right_result + '\n\n')

        return send_file(txt_file_path, as_attachment=True, download_name='correction_export.txt')
    
    # 写入csv文件
    elif fileType == 'csv':
        # 定义CSV文件的表头
        fieldnames = ['id', 'time', 'model', 'image', 'wrong_result', 'right_result']
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for correction in Export_list:
                writer.writerow({
                    'id': correction.id,
                    'time': correction.time.strftime("%Y-%m-%d %H:%M:%S"),
                    'model': correction.model,
                    'image': correction.image,
                    'wrong_result': correction.wrong_result,
                    'right_result': correction.right_result
                })
        return send_file(csv_file_path, as_attachment=True, download_name='correction_export.csv')
    
    # 返回错误信息
    else:
        return api_response(message='Invalid file type', code=400)

# 获取绘图信息
@app.route("/statistics", methods=["GET"])
def get_statistics():
    start_time = time.time()
    error_count = Error.query.count()
    correction_count = Correction.query.count()
    success_count = Success.query.count() - correction_count
    total = success_count + error_count + correction_count

    data = {
        "success_count": success_count,
        "error_count":error_count,
        "correction_count":correction_count,
        "total":total,
    }
    end_time = time.time();
    elapse = "{:.5f}".format(end_time - start_time)
    return api_response(data=data,elapsed=elapse)

    