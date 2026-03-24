import axios from 'axios'

const getBaseURL = () => {
  const envBaseURL = import.meta.env.VITE_API_BASE_URL
  
  if (envBaseURL) {
    return envBaseURL
  }
  
  const hostname = window.location.hostname
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:5000'
  }
  
  // 非localhost时使用内网穿透地址
  return 'https://d07dd15.r18.vip.cpolar.cn'
}

const request = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000
})

request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // 只有在非文件上传时设置Content-Type为UTF-8
    if (!config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json; charset=utf-8'
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default request
