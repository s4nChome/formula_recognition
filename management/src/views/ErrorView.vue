<template>
  <div>
    <!-- 搜索 -->
    <div style="margin-bottom: 20px;">
      <el-select v-model="params.selectedModel" placeholder="请选择模型">
        <el-option v-for="item in model" :key="item" :label="item" :value="item"></el-option>
      </el-select>
      <el-button style="margin-left: 10px;" type="primary" @click="getList"><i class="el-icon-search"></i>搜索</el-button>
      <el-button style="margin-left: 10px;" type="danger" @click="reload"><i class="el-icon-refresh"></i>重置</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="tableData" stripe>
      <el-table-column prop="id" label="ID"></el-table-column>
      <el-table-column prop="model" label="模型名"></el-table-column>
      <el-table-column prop="image" label="输入图片" show-overflow-tooltip></el-table-column>
      <el-table-column prop="reason" label="错误信息" show-overflow-tooltip></el-table-column>
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
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'ErrorView',
  data() {
    return {
      tableData: [],
      total: 0,
      model: [],
      params:{
        pageNum: 1,
        pageSize: 10,
        selectedModel: ''
      }
    }
  },

  created(){
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

    // 分页搜索
    getList(){
      request.get('/error/page',{
      params: this.params}).then(res => {
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
    reload(){
      this.params.selectedModel = ''
      this.params.pageNum = 1
      this.params.pageSize = 10
      this.load()
    },

    //点击翻页
    handleCurrentChange(pageNum) {
      this.params.pageNum = pageNum
      this.getList()
    }
  }
}
</script>