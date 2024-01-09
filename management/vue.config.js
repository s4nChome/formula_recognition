const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true
})
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    //host: '0.0.0.0',  // 允许外部访问
    port: 9090,        // 指定端口
    // 根据需要添加其他配置
  }
});