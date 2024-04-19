<template>
  <div>
    <!-- 搜索 -->
    <div style="margin-bottom: 20px;">
      <el-select v-model="params.selectedModel" placeholder="请选择模型">
        <el-option v-for="item in model" :key="item" :label="item" :value="item"></el-option>
      </el-select>
      <el-button style="margin-left: 10px;" type="primary" @click="getList"><i class="el-icon-search"></i>搜索</el-button>
      <el-button style="margin-left: 10px;" type="danger" @click="reload"><i class="el-icon-refresh"></i>重置</el-button>
      <el-button style="margin-left: 10px;" type="success" @click="openFileSelection"><i class="el-icon-upload2"></i>导出</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="tableData" stripe>
      <el-table-column prop="id" label="ID"></el-table-column>
      <el-table-column prop="model" label="模型名"></el-table-column>
      <el-table-column prop="image" label="输入图片" show-overflow-tooltip></el-table-column>
      <el-table-column prop="wrong_result" label="错误结果" show-overflow-tooltip></el-table-column>
      <el-table-column prop="right_result" label="正确结果" show-overflow-tooltip></el-table-column>
      <el-table-column prop="time" label="时间"></el-table-column>
    </el-table>

    <!-- 分页 -->
    <div style="margin-top: 20px;">
      <el-pagination
        background
        :page-size="params.pageSize"
        :current-page="params.pageNum"
        layout="prev, pager, next"
        @current-change="handleCurrentChange"
        :total="total">
      </el-pagination>
    </div>

    <!-- 导出文件类型选择 -->
    <el-dialog
      title="导出文件类型"
      :visible.sync="FileTypeDialogVisible"
      width="15%">
      <span>
        <div style="text-align: center;">        
          <el-button type="primary" plain @click="getCSV">CSV</el-button>
          <el-button type="primary" plain @click="getTXT">TXT</el-button>
        </div>
      </span>
      <span slot="footer">
        <el-button @click=" FileTypeDialogVisible= false" type="danger">关闭</el-button>
      </span>
    </el-dialog>
    
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'WrongView',
  data() {
    return {
      tableData: [],
      total: 0,
      model: [],
      FileTypeDialogVisible: false,
      params: {
        pageNum: 1,
        pageSize: 10,
        selectedModel: ''
      }
    }
  },

  created() {
    this.load()
  },

  methods: {
    load() {
      request.get('/modelnames').then(res => {
        if (res.code === 200) {
          this.model = res.data
        }
      });
      this.getList()
    },

    // 打开文件选择对话框
    openFileSelection() {
      this.FileTypeDialogVisible = true
    },

    // 分页搜索
    getList() {
      request.get('/wrong/page', {
        params: this.params
      }).then(res => {
        if (res.code === 200) {
          this.tableData = res.data.list
          this.total = res.data.total
          this.$notify.success({
            title: '成功',
            message: `数据加载成功，耗时：${res.elapsed}s`,
          })
        }
      })
    },

    // 清空
    reload() {
      this.params.selectedModel = ''
      this.params.pageNum = 1
      this.params.pageSize = 10
      this.load()
    },

    // 导出CSV
    getCSV() {
      this.FileTypeDialogVisible = false
      window.open('http://localhost:5000/wrong/export?fileType=csv&selectedModel=' + this.params.selectedModel)
    },

    // 导出TXT
    getTXT() {
      this.FileTypeDialogVisible = false
      window.open('http://localhost:5000/wrong/export?fileType=txt&selectedModel=' + this.params.selectedModel)
    },



    //点击翻页
    handleCurrentChange(pageNum) {
      this.params.pageNum = pageNum
      this.getList()
    }
  }
}
</script>
