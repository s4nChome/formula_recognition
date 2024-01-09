import time
import re

# 导入模型
from pix2text import Pix2Text, merge_line_texts
from rapid_latex_ocr import LatexOCR

# 初始化两个模型的实例
model_rapid_latex_ocr = LatexOCR()
model_pix2text = Pix2Text()

# RapidLatexOCR
def RapidLatexOCR_recognize(filepath):
  res, elapse = model_rapid_latex_ocr(filepath)
  elapse = "{:.5f}".format(elapse)
  return res,elapse

# Pix2Text
def Pix2Text_recognize(filepath):
  start_time = time.time()
  p2t = Pix2Text()
  print(filepath)
  res = p2t.recognize(filepath)
  # 如果只需要识别出的文字和Latex表示，可以使用下面行的代码合并所有结果
  res = merge_line_texts(res, auto_line_break=True)

   # 删除所有的 $ 和换行符
  res = res.replace('$', '').replace('\n', '').replace('\r', '')
  end_time = time.time()
  elapse = "{:.5f}".format(end_time - start_time)
  return res,elapse
