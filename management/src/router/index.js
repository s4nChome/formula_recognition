import Vue from 'vue'
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/success',
    name: 'success',
    component: () => import('../views/SuccessView.vue')
  },
  {
    path:'/error',
    name:'error',
    component: () => import('../views/ErrorView.vue')
  },
  {
    path:'/wrong',
    name:'wrong',
    component: () => import('../views/WrongView.vue')
  }

]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
