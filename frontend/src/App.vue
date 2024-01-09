<template>
  <div id="app">
    <!-- 头部区域 -->
    <div style="height: 60px; line-height: 60px; background-color: #fff;text-align: center;">
      <span style="font-family: 'Dancing Script', cursive;font-size: 30px;">Formula Recognition</span>
    </div>

    <!-- 主体区域 -->
    <div class="main-content">
      <router-view/>
    </div>



  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script&display=swap');

.main-content {
  width: 80%;
  min-height: calc(100vh - 70px);
  margin: 0 auto;
  margin-top: 5px;
  padding: 20px; 
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); 
  background-color: #fff; 
  border-radius: 5px;
}

</style>
