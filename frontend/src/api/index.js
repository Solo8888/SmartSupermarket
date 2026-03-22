import axios from 'axios'

const getBaseURL = () => {
  const envBaseURL = import.meta.env.VITE_API_BASE_URL
  
  if (envBaseURL) {
    return envBaseURL
  }
  
  const protocol = window.location.protocol
  const hostname = window.location.hostname
  const port = window.location.port
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:5000'
  }
  
  if (port) {
    return `${protocol}//${hostname}:${port.replace('3000', '5000')}`
  }
  
  return `${protocol}//${hostname}`
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
    // 设置Content-Type为UTF-8
    config.headers['Content-Type'] = 'application/json; charset=utf-8'
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
