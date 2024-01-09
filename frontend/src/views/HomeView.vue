<template>
  <div>
    <el-row :gutter="8" style="text-align: center">
      <el-col :xs="24" :sm="24" :md="12" :lg="10" :xl="7" style="margin-bottom: 0.2rem;float: left;">
        <el-card>
          <el-col :span="24">
            <span>请选择要使用的模型：</span>
            <el-select v-model="selectedModel" placeholder="请选择要使用的模型">
              <el-option v-for="item in modelnames" :key="item" :label="item" :value="item"></el-option>
            </el-select>
          </el-col>
          <el-col :span="24">
            <el-button type="primary" size="text" @click="openModelInfo">查看模型详细信息</el-button>
          </el-col>
          <el-col :span="24">
            <!-- 文件上传区域 -->
            <el-upload class="upload-demo" drag action="" :before-upload="handleFileChange">
              <i class="el-icon-upload"></i>
              <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            </el-upload>
          </el-col>
          <el-col :span="24">
            <span>已选择文件：</span>
            <span>{{ selectedFile ? selectedFile.name : '' }}</span>
          </el-col>
          <el-col :span="24" style="text-align: center;margin: 5px 0">
            <el-button type="danger" plain @click="clearInput">清空输入</el-button>
            <el-button type="primary" plain @click="importFromClipboard">从剪切板导入</el-button>
            <el-button type="success" plain @click="startRecognition">开始识别</el-button>
          </el-col>
          <!-- 图片预览区域 -->
          <el-col>
            <el-image @dblclick="showLargeImage"
              style="height: 150px;width: 100%;text-align: center;background-color: #dddddd" :src="src"></el-image>
          </el-col>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="14" :xl="17" style="float: left;">
        <!-- 识别结果展示区域 -->
        <el-card shadow="always" :body-style="{ padding: '20px' }">
          <el-col>
            <span style="font-size: large;">识别状态：{{ status }}</span>
            <el-button style="float: right; padding: 3px 0" type="text" @click="clearOutput">清空输出</el-button>
          </el-col>
          <el-col style="height: 300px; font-size: 20px;line-height: 300px; background-color: #f5f7fa; overflow-y: auto;">
            <div v-html="renderedLatex" style="text-align: center;"></div>
          </el-col>
          <el-col>
            <el-input v-model="latexString" type="textarea" :rows="5" readonly
              style="height: 120px; margin-top: 5px; overflow-y:auto;"></el-input>
          </el-col>
          <el-col style="text-align: center;margin: 5px 0">
            <el-button type="danger" plain size="default" @click="showCorrectDialog">识别有误</el-button>
            <el-button type="success" plain size="default" @click="copyToClipboard">复制代码</el-button>
          </el-col>

        </el-card>
      </el-col>
    </el-row>

    <!-- 大图模态对话框 -->
    <el-dialog :visible.sync="largeImageDialogVisible" width="80%">
      <el-image :src="src" style="width: 100%;"></el-image>
    </el-dialog>

    <!-- 模型信息概览区域 -->
    <el-dialog title="模型详细信息" :visible.sync="ModelInfoDialogVisible" width="40%">
      <div style="margin-top: 5px;">
        <el-descriptions style="margin-top: 2px;" :column="1" border>
          <el-descriptions-item label="模型名称">{{ modelName }}</el-descriptions-item>
          <el-descriptions-item label="模型描述">{{ modelDescription }}</el-descriptions-item>
          <el-descriptions-item label="GitHub地址">
            <el-link :href="modelUrl" target="_blank">{{ modelUrl }}</el-link>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <span slot="footer">
        <el-button type="primary" @click=closeModelInfoDialog>OK</el-button>
      </span>
    </el-dialog>

    <!-- 结果纠错区域 -->
    <el-dialog title="识别错误" :visible.sync="CorrectDialogVisible" width="60%">
      <div style="margin-top: 5px;">
        <el-col style="height: 300px; font-size: 20px;line-height: 300px; background-color: #f5f7fa; overflow-y: auto;">
          <div v-html="correctRenderedLatex" style="word-wrap: break-word; text-align: center;"></div>
        </el-col>
      </div>
      <div>
        <el-input v-model="correctLatexString" type="textarea" :rows="5"
          style="height: 120px; margin-top: 5px; overflow-y:auto;"></el-input>
      </div>
      <div style="margin-top: 5px;text-align: center;">
        <el-button type="danger" plain @click="cancelCorrectLatex">取消</el-button>
        <el-button type="primary" plain @click="tempSave">暂存</el-button>
        <el-button type="success" plain @click="updateCorrectLatex">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import request from "@/utils/request";
import { Result } from "element-ui";
import katex from 'katex';

export default {
  name: 'HomeView',

  data() {
    return {
      modelnames: [],
      selectedModel: '',
      modelName: '',
      modelUrl: '',
      modelDescription: '',
      ModelInfoDialogVisible: false,
      selectedFile: null,
      filepath: null,
      latexString: '',
      renderedLatex: '',
      status: '等待图片输入...',
      src: '',
      largeImageDialogVisible: false,
      CorrectDialogVisible: false,
      correctLatexString: '',
      correctRenderedLatex: '',
      tempLatexString: '',
      tempRenderedLatex: ''
    };
  },

  created() {
    this.load();
  },

  mounted() {
    document.addEventListener('paste', this.handlePaste);
  },

  beforeDestroy() {
    document.removeEventListener('paste', this.handlePaste);
  },


  watch: {
    // 监听识别结果变化，重新渲染 LaTeX 代码
    correctLatexString() {
      this.renderCorrectLatex();
    }
  },

  methods: {
    // 页面初始化时加载模型列表
    load() {
      request.get('/modelnames').then(res => {
        if (res.code === 200) {
          this.modelnames = res.data;
          this.$notify.success({
            title: '成功',
            message: `模型获取成功，耗时：${res.elapsed}s`,
          });
        }
      });
    },

    // 显示模型详细信息
    openModelInfo() {
      if (this.selectedModel === '') {
        this.$notify.error({
          title: '错误',
          message: '请先选择模型',
        });
        return;
      }
      this.ModelInfoDialogVisible = true;
      request.get('/modelinfo', {
        params: {
          model_name: this.selectedModel,
        },
      }).then(res => {
        if (res.code === 200) {
          this.modelName = res.data.model_name;
          this.modelUrl = res.data.model_url;
          this.modelDescription = res.data.model_description;
          this.$notify.success({
            title: '成功',
            message: `模型详细信息获取成功，耗时：${res.elapsed}s`,
          });
        }
      });
    },

    // 关闭模型详情对话框
    closeModelInfoDialog() {
      this.ModelInfoDialogVisible = false;
      this.modelName = '';
      this.modelUrl = '';
      this.modelDescription = '';
    },

    // 文件上传
    handleFileChange(file) {
      this.selectedFile = file;
      this.src = URL.createObjectURL(file);
      return false; // 阻止自动上传
    },
    // 清空输入
    clearInput() {
      this.selectedFile = null;
      this.src = '';
    },

    // 粘贴事件处理
    handlePaste(event) {
      if (event.clipboardData && event.clipboardData.items) {
        const items = event.clipboardData.items;
        let flag = false;
        for (const item of items) {
          if (item.type.indexOf('image') !== -1) {
            const file = item.getAsFile();
            this.src = URL.createObjectURL(file);
            this.selectedFile = file; // 保存文件对象以备后用
            flag = true;
            break;
          }
        }
        if (flag) {
          this.$notify.success({
            title: '成功',
            message: '图片粘贴成功',
          })
        }
      }
    },

    // 开始识别
    startRecognition() {
      if (this.selectedModel === '') {
        this.$notify.error({
          title: '错误',
          message: '请先选择模型',
        });
        return;
      }
      if (this.selectedFile === null) {
        this.$notify.error({
          title: '错误',
          message: '请先上传文件',
        });
        return;
      }
      this.clearAll();
      this.status = '正在识别...';

      // 准备表单数据
      let formData = new FormData();
      formData.append('file', this.selectedFile);
      formData.append('model_name', this.selectedModel);

      //发送识别请求
      request.post('/recognize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
        .then(res => {
          if (res.code === 200) {
            this.status = '识别成功';
            this.filepath = res.filepath;
            this.latexString = res.data; // 获取识别结果
            this.renderLatex(); // 渲染 LaTeX 代码
            this.$notify.success({
              title: '成功',
              message: `识别成功,耗时：${res.elapsed}s`,
            });
          } else {
            this.status = '识别失败';
            this.$notify.error({
              title: '失败',
              message: res.message || '识别失败',
            });
          }
        })
        .catch(error => {
          this.$notify.error({
            title: '错误',
            message: error.message,
          });
        });
    },

    // 渲染 LaTeX 代码
    renderLatex() {
      this.renderedLatex = katex.renderToString(this.latexString, {
        throwOnError: false,
        output: "mathml"
      });
      //console.log(this.renderedLatex);
    },

    // 渲染纠错 Latex 代码
    renderCorrectLatex() {
      this.correctRenderedLatex = katex.renderToString(this.correctLatexString, {
        throwOnError: false,
        output: "mathml"
      });
      //console.log(this.renderedLatex);
    },

    //清空所有
    clearAll() {
      this.latexString = '';
      this.renderedLatex = '';
      this.correctLatexString = '';
      this.correctRenderedLatex = '';
      this.tempLatexString = '';
      this.tempRenderedLatex = '';
    },

    // 清空输出
    clearOutput() {
      this.clearAll();
      this.status = '等待图片输入...';
    },

    // 从剪切板导入图片
    async importFromClipboard() {
      try {
        // 获取剪切板上的内容
        const clipboardItems = await navigator.clipboard.read();

        for (const clipboardItem of clipboardItems) {
          for (const type of clipboardItem.types) {
            if (type.startsWith('image/')) {
              // 获取图片数据
              const blob = await clipboardItem.getType(type);
              this.src = URL.createObjectURL(blob);
              // 更新 selectedFile
              this.selectedFile = new File([blob], "image.png", { type: blob.type });
              this.$notify.success({
                title: '成功',
                message: '图片粘贴成功',
              })
              break;
            }
          }
        }
      } catch (error) {
        this.$notify.error({
          title: '错误',
          message: error,
        })
      }
    },


    // 复制到剪切板
    async copyToClipboard() {
      if (!this.latexString) {
        this.$notify.error({
          title: '错误',
          message: '没有 LaTeX 代码可复制',
        });
        return;
      }
      try {
        // 使用 navigator.clipboard API 复制文本
        await navigator.clipboard.writeText(this.latexString);
        this.$notify.success({
          title: '成功',
          message: 'LaTeX 代码已复制到剪切板',
        });
      } catch (err) {
        console.error('复制到剪切板失败:', err);
        this.$notify.error({
          title: '错误',
          message: '复制到剪切板失败',
        });
      }
    },


    // 显示大图
    showLargeImage() {
      this.largeImageDialogVisible = true;
    },

    // 显示纠错对话框
    showCorrectDialog() {
      if (this.latexString === '') {
        this.$notify.error({
          title: '错误',
          message: '请先识别图片',
        })
      } else if (this.tempLatexString != '' && this.tempRenderedLatex != '') {
        this.correctLatexString = this.tempLatexString;
        this.correctRenderedLatex = this.tempRenderedLatex
      }
      else {
        this.correctLatexString = this.latexString;
        this.correctRenderedLatex = this.renderedLatex;
      }
      this.CorrectDialogVisible = true;
    },

    // 暂存修改结果
    tempSave() {
      this.tempLatexString = this.correctLatexString;
      this.tempRenderedLatex = this.correctRenderedLatex;
      this.CorrectDialogVisible = true;
    },

    // 取消修改Latex代码
    cancelCorrectLatex() {
      this.CorrectDialogVisible = false;
      this.tempLatexString = '';
      this.tempRenderedLatex = '';
      this.correctLatexString = this.latexString;
      this.correctRenderedLatex = this.renderedLatex;
    },

    // 上传修改后的Latex代码
    updateCorrectLatex() {
      const data = {
        filepath: this.filepath,
        model: this.selectedModel,
        wrong_result: this.latexString,
        right_result: this.correctLatexString,
      };
      request.post('/wrong/upload', data)
        .then(res => {
          if (res.code === 200) {
            this.$notify.success({
              title: '成功',
              message: '保存成功',
            });
          } else {
            this.$notify.error({
              title: '错误',
              message: res.message,
            })
          }
        })
      this.CorrectDialogVisible = false;
    }
  },
};
</script>

<style scoped>
.image-preview-container {
  width: 100%;
  /* 固定宽度 */
  max-width: 300px;
  /* 限制最大宽度 */
  height: 200px;
  /* 固定高度 */
  margin: 10px auto;
  /* 居中显示 */
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  /* 隐藏溢出的部分 */
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-image .el-image__inner {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
  /* 保持图片比例 */
  object-position: top;
}

.el-card {
  height: 550px
}
</style>