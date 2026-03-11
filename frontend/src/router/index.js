import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresRole: 'inventory_manager' },
    children: [
      {
        path: '',
        redirect: '/admin/categories'
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('../views/admin/Categories.vue'),
        meta: { title: '商品分类管理' }
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('../views/admin/Products.vue'),
        meta: { title: '商品管理' }
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('../views/admin/Inventory.vue'),
        meta: { title: '库存管理' }
      },
      {
        path: 'promotions',
        name: 'Promotions',
        component: () => import('../views/admin/Promotions.vue'),
        meta: { title: '促销活动管理' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresRole && userStore.userInfo?.role !== to.meta.requiresRole) {
    next('/home')
  } else if ((to.path === '/login' || to.path === '/register') && userStore.isAuthenticated) {
    if (userStore.userInfo?.role === 'inventory_manager') {
      next('/admin/categories')
    } else {
      next('/home')
    }
  } else if (to.path === '/home' && userStore.userInfo?.role === 'inventory_manager') {
    next('/admin/categories')
  } else {
    next()
  }
})

export default router
