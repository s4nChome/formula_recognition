const { defineConfig } = require('@vue/cli-service');
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    //allowedHosts: 'all',
    //host: '0.0.0.0',  // 允许外部访问
    port: 8080,        // 指定端口
    // 根据需要添加其他配置
    // https: {
    //   key: require('fs').readFileSync('./certs/key.pem'),
    //   cert: require('fs').readFileSync('./certs/cert.pem'),
    //   passphrase: '12345678'
    // }
  }
});
