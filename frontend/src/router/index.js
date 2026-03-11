import { createRouter, createWebHistory } from 'vue-router'

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
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/admin/categories'
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('../views/admin/Categories.vue'),
        meta: { title: '商品分类管理', requiresRole: 'inventory_manager' }
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('../views/admin/Products.vue'),
        meta: { title: '商品管理', requiresRole: 'inventory_manager' }
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('../views/admin/Inventory.vue'),
        meta: { title: '库存管理', requiresRole: 'inventory_manager' }
      },
      {
        path: 'promotions',
        name: 'Promotions',
        component: () => import('../views/admin/Promotions.vue'),
        meta: { title: '促销活动管理', requiresRole: 'operations_manager' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const accessToken = localStorage.getItem('access_token')
  const userInfoStr = localStorage.getItem('user_info')
  let userInfo = null
  try {
    userInfo = userInfoStr ? JSON.parse(userInfoStr) : null
  } catch (e) {
    userInfo = null
  }
  
  const isAuthenticated = !!accessToken
  const isManager = userInfo?.role === 'inventory_manager' || userInfo?.role === 'operations_manager'
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.path.startsWith('/admin') && !isManager) {
    next('/home')
  } else if (to.meta.requiresRole && userInfo?.role !== to.meta.requiresRole) {
    next('/home')
  } else if (to.path === '/admin' && userInfo?.role === 'operations_manager') {
    next('/admin/promotions')
  } else if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    if (isManager) {
      if (userInfo?.role === 'operations_manager') {
        next('/admin/promotions')
      } else {
        next('/admin/categories')
      }
    } else {
      next('/home')
    }
  } else if (to.path === '/home' && isManager) {
    if (userInfo?.role === 'operations_manager') {
      next('/admin/promotions')
    } else {
      next('/admin/categories')
    }
  } else {
    next()
  }
})

export default router
