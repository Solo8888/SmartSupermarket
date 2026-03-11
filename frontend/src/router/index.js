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
  },
  {
    path: '/customer',
    component: () => import('../layouts/CustomerLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/customer/home'
      },
      {
        path: 'home',
        name: 'CustomerHome',
        component: () => import('../views/customer/CustomerHome.vue'),
        meta: { title: '首页', requiresRole: 'customer' }
      },
      {
        path: 'cart',
        name: 'Cart',
        component: () => import('../views/customer/Cart.vue'),
        meta: { title: '购物车', requiresRole: 'customer' }
      },
      {
        path: 'orders',
        name: 'CustomerOrders',
        component: () => import('../views/customer/Orders.vue'),
        meta: { title: '我的订单', requiresRole: 'customer' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/customer/Profile.vue'),
        meta: { title: '我的', requiresRole: 'customer' }
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
  const isCustomer = userInfo?.role === 'customer'
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresRole && userInfo?.role !== to.meta.requiresRole) {
    next('/home')
  } else if (to.meta.requiresRoles && !to.meta.requiresRoles.includes(userInfo?.role)) {
    next('/home')
  } else if (to.path === '/admin' && userInfo?.role === 'operations_manager') {
    next('/admin/promotions')
  } else if (to.path === '/admin' && userInfo?.role === 'inventory_manager') {
    next('/admin/categories')
  } else if (to.path === '/admin' && userInfo?.role === 'customer') {
    next('/customer/home')
  } else if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    if (isManager) {
      if (userInfo?.role === 'operations_manager') {
        next('/admin/promotions')
      } else {
        next('/admin/categories')
      }
    } else if (isCustomer) {
      next('/customer/home')
    }
  } else if (to.path === '/home' && isAuthenticated) {
    if (isManager) {
      if (userInfo?.role === 'operations_manager') {
        next('/admin/promotions')
      } else {
        next('/admin/categories')
      }
    } else if (isCustomer) {
      next('/customer/home')
    }
  } else {
    next()
  }
})

export default router
