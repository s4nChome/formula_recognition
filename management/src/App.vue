
import router from './router';
<template>
  <div id="app">
    <el-container>
      <el-header>
        <span>Formula Recognition</span>
      </el-header>
      <el-container>
        <el-aside width="200px">
          <el-menu :default-active="$route.path" router>
            <el-menu-item index="/">
              <i class="el-icon-s-data"></i>
              <span>概览</span>
            </el-menu-item>
            <el-menu-item index="/success">
              <i class="el-icon-success"></i>
              <span>识别成功</span>
            </el-menu-item>
            <el-menu-item index="/error">
              <i class="el-icon-error"></i>
              <span>识别失败</span>
            </el-menu-item>
            <el-menu-item index="/wrong">
              <i class="el-icon-question"></i>
              <span>识别错误</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <router-view/>
        </el-main>
      </el-container>
    </el-container>


   
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script&display=swap');

.el-header{
  margin-bottom: 3px;
  background-color: white;
  color: #333;
  text-align: center;
  line-height: 60px;
}

.el-header span{
  font-family: 'Dancing Script', cursive;
  font-size: 30px;
}
  
.el-aside {
  overflow: hidden;
  background-color: white;
  color: #333;
  min-height: calc(100vh - 63px);
  margin-right: 3px;
  font-weight: bold;
}
  
  .el-main {
    background-color: white;
  }

</style>
