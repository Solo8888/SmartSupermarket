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
        meta: { title: '商品分类管理', requiresRole: 'system_admin' }
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('../views/admin/Products.vue'),
        meta: { title: '商品管理', requiresRole: 'system_admin' }
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
      },
      {
        path: 'stores',
        name: 'Stores',
        component: () => import('../views/admin/Stores.vue'),
        meta: { title: '门店管理', requiresRole: 'system_admin' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/admin/Users.vue'),
        meta: { title: '用户管理', requiresRole: 'system_admin' }
      },
      {
        path: 'user-stores',
        name: 'UserStores',
        component: () => import('../views/admin/UserStores.vue'),
        meta: { title: '用户门店管理', requiresRole: 'system_admin' }
      },
      {
        path: 'customer-flow',
        name: 'CustomerFlow',
        component: () => import('../views/admin/CustomerFlow.vue'),
        meta: { title: '客流管理', requiresRole: 'operations_manager' }
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
        path: 'categories',
        name: 'CustomerCategories',
        component: () => import('../views/customer/Categories.vue'),
        meta: { title: '分类', requiresRole: 'customer' }
      },
      {
        path: 'cart',
        name: 'Cart',
        component: () => import('../views/customer/Cart.vue'),
        meta: { title: '购物车', requiresRole: 'customer' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/customer/Profile.vue'),
        meta: { title: '我的', requiresRole: 'customer' }
      },
      {
        path: 'address-book',
        name: 'AddressBook',
        component: () => import('../views/customer/AddressBook.vue'),
        meta: { title: '地址管理', requiresRole: 'customer' }
      },
      {
        path: 'checkout',
        name: 'OrderCheckout',
        component: () => import('../views/customer/OrderCheckout.vue'),
        meta: { title: '确认订单', requiresRole: 'customer' }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('../views/customer/Orders.vue'),
        meta: { title: '我的订单', requiresRole: 'customer' }
      },
      {
        path: 'order-review/:id',
        name: 'OrderReview',
        component: () => import('../views/customer/OrderReview.vue'),
        meta: { title: '订单评价', requiresRole: 'customer' }
      },
      {
        path: 'order-detail/:id',
        name: 'OrderDetail',
        component: () => import('../views/customer/OrderDetail.vue'),
        meta: { title: '订单详情', requiresRole: 'customer' }
      },
      {
        path: 'product-detail/:id',
        name: 'ProductDetail',
        component: () => import('../views/customer/ProductDetail.vue'),
        meta: { title: '商品详情', requiresRole: 'customer' }
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
  const userRole = userInfo?.role
  const isManager = userRole === 'inventory_manager' || userRole === 'operations_manager' || userRole === 'system_admin'
  const isCustomer = userRole === 'customer'
  const isSystemAdmin = userRole === 'system_admin'
  
  // 角色权限级别：system_admin > operations_manager = inventory_manager > customer
  const roleHierarchy = {
    'system_admin': 4,
    'operations_manager': 2,
    'inventory_manager': 2,
    'customer': 1
  }
  
  // 检查权限
  const hasPermission = (requiredRole) => {
    // 系统管理员不能访问客流管理
    if (isSystemAdmin && requiredRole === 'operations_manager' && to.path === '/admin/customer-flow') {
      return false
    }
    if (isSystemAdmin) return true // 系统管理员有其他所有权限
    if (!userRole) return false
    return userRole === requiredRole
  }
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresRole && !hasPermission(to.meta.requiresRole)) {
    next('/home')
  } else if (to.meta.requiresRoles && !to.meta.requiresRoles.includes(userRole)) {
    next('/home')
  } else if (to.path === '/admin' && userRole === 'operations_manager') {
    next('/admin/promotions')
  } else if (to.path === '/admin' && userRole === 'inventory_manager') {
    next('/admin/inventory')
  } else if (to.path === '/admin' && userRole === 'system_admin') {
    next('/admin/categories')
  } else if (to.path === '/admin' && userRole === 'customer') {
    next('/customer/home')
  } else if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    if (isManager) {
      if (userRole === 'operations_manager') {
        next('/admin/promotions')
      } else if (userRole === 'system_admin') {
        next('/admin/categories')
      } else {
        next('/admin/inventory')
      }
    } else if (isCustomer) {
      next('/customer/home')
    }
  } else if (to.path === '/home' && isAuthenticated) {
    if (isManager) {
      if (userRole === 'operations_manager') {
        next('/admin/promotions')
      } else if (userRole === 'system_admin') {
        next('/admin/categories')
      } else {
        next('/admin/inventory')
      }
    } else if (isCustomer) {
      next('/customer/home')
    }
  } else {
    next()
  }
})

export default router
