import time
from PIL import Image
from playwright.sync_api import sync_playwright

# 导入模型
from pix2text import Pix2Text, merge_line_texts
from rapid_latex_ocr import LatexOCR
from pix2tex.cli import LatexOCR as pix2tex

# 初始化两个模型的实例
model_rapid_latex_ocr = LatexOCR()
model_pix2text = Pix2Text()
model_pix2tex = pix2tex()

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

# 基于pix2tex的模型
def Pix2Tex_recognize(filepath):
  start_time = time.time()
  res = model_pix2tex(Image.open(filepath))
  end_time = time.time()
  elapse = "{:.5f}".format(end_time - start_time)
  return res,elapse


# internVL
def internVL_recognize(filepath):
  start_time = time.time()
  with sync_playwright() as p:
    browser = p.firefox.launch()
    page = browser.new_page()
    page.goto('https://internvl.opengvlab.com/')

    input_element = page.locator('input[type="file"]')
    input_element.set_input_files(filepath)

    page.wait_for_selector("[data-testid='textbox']")
    textbox = page.query_selector("[data-testid='textbox']")
    textbox.fill("请将这张图片转换为latex代码")

    page.wait_for_selector(".lg.primary.svelte-1ipelgc")
    button = page.query_selector(".lg.primary.svelte-1ipelgc")
    button.click()

    latex_element = page.locator('span.token.equation.string')
    res = latex_element.inner_text()
    res = res.replace('$', '').replace('\n', '').replace('\r', '')
    browser.close()

    end_time = time.time()
    elapse = "{:.5f}".format(end_time - start_time)
    return res,elapse
