<template>
  <div class="home">
    <div>
      <el-card>
        <div id="chart" style="width: 100%; height: 500px;"></div>
      </el-card>
    </div>
  </div>
</template>

<script>
import request from '@/utils/request';
import * as echarts from 'echarts';

export default {
  name: 'HomeView',
  data() {
    return {
      tableData: [],
      totalCount: 0,
      successCount: 0,
      errorCount: 0,
      correctionCount: 0
    }
  },
  mounted() {
    this.load();
    // 监听窗口大小变化
    window.addEventListener('resize', this.handleResize);
  },

  beforeDestroy() {
    // 组件销毁时移除事件监听
    window.removeEventListener('resize', this.handleResize);
  },

  methods: {
    load() {
      request.get('/statistics').then(res => {
        if (res.code === 200) {
          this.totalCount = res.data.total;
          this.successCount = res.data.success_count;
          this.errorCount = res.data.error_count;
          this.correctionCount = res.data.correction_count;
          this.$notify.success({
            title: '成功',
            message: `图表加载成功，耗时：${res.elapsed}s`,
          })
          // 调用 renderChart 方法渲染图表
          this.renderChart();
        } else {
          // 处理非成功响应
          this.$notify.error({
            title: '失败',
            message: res.message
          })
        }
      })
    },

    renderChart() {
      var chart = echarts.init(document.getElementById('chart'));
      var option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)' // 提示框显示百分比
        },
        legend: {
          top: 'bottom',
          left: 'center'
        },
        series: [
          {
            name: '识别统计',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: true, // 显示标签
              formatter: '{b}: {d}%', // 标签显示格式，{b}是数据项名称，{d}是百分比
              position: 'outside' // 标签显示在扇区外侧
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 40,
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: true, // 显示标签的引导线
              length: 30, // 引导线的长度
              length2: 10 // 引导线的二级长度
            },
            data: [
              { value: this.successCount, name: '识别正确' },
              { value: this.errorCount, name: '识别失败' },
              { value: this.correctionCount, name: '识别错误' }
            ]
          }
        ]
      };
      chart.setOption(option);
    }

  }
}
</script>
