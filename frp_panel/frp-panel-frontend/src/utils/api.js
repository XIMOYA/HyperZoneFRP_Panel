import axios from 'axios';
import { message } from 'antd';

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加token到请求头
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const { response } = error;
    
    if (response) {
      const { status, data } = response;
      
      // 处理不同的错误状态码
      switch (status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          window.location.href = '/login';
          message.error('登录已过期，请重新登录');
          break;
        case 403:
          message.error('权限不足');
          break;
        case 404:
          message.error('请求的资源不存在');
          break;
        case 500:
          message.error('服务器内部错误');
          break;
        default:
          message.error(data?.error || '请求失败');
      }
    } else {
      message.error('网络错误，请检查网络连接');
    }
    
    return Promise.reject(error);
  }
);

// API方法
export const authAPI = {
  // 发送验证码
  sendVerificationCode: (email, purpose = 'register') => 
    api.post('/auth/send-verification-code', { email, purpose }),
  
  // 用户注册
  register: (data) => api.post('/auth/register', data),
  
  // 用户登录
  login: (data) => api.post('/auth/login', data),
  
  // 获取用户信息
  getProfile: () => api.get('/auth/profile'),
  
  // 更新用户信息
  updateProfile: (data) => api.put('/auth/profile', data),
};

export const nodesAPI = {
  // 获取节点列表
  getNodes: () => api.get('/nodes'),
  
  // 获取单个节点
  getNode: (id) => api.get(`/nodes/${id}`),
  
  // 创建节点
  createNode: (data) => api.post('/nodes', data),
  
  // 更新节点
  updateNode: (id, data) => api.put(`/nodes/${id}`, data),
  
  // 删除节点
  deleteNode: (id) => api.delete(`/nodes/${id}`),
  
  // 获取节点状态
  getNodeStatus: (id) => api.get(`/nodes/${id}/status`),
};

export const tunnelsAPI = {
  // 获取隧道列表
  getTunnels: (params) => api.get('/tunnels', { params }),
  
  // 获取单个隧道
  getTunnel: (id) => api.get(`/tunnels/${id}`),
  
  // 创建隧道
  createTunnel: (data) => api.post('/tunnels', data),
  
  // 更新隧道
  updateTunnel: (id, data) => api.put(`/tunnels/${id}`, data),
  
  // 删除隧道
  deleteTunnel: (id) => api.delete(`/tunnels/${id}`),
  
  // 启动隧道
  startTunnel: (id) => api.post(`/tunnels/${id}/start`),
  
  // 停止隧道
  stopTunnel: (id) => api.post(`/tunnels/${id}/stop`),
  
  // 批量操作
  batchOperation: (data) => api.post('/tunnels/batch', data),
};

export default api;


// 套餐API
export const packagesAPI = {
  // 获取套餐列表
  getPackages: () => api.get('/packages'),
  
  // 获取单个套餐详情
  getPackage: (id) => api.get(`/packages/${id}`),
  
  // 获取用户的套餐
  getUserPackages: () => api.get('/user/packages'),
  
  // 购买套餐
  purchasePackage: (id, data) => api.post(`/packages/${id}/purchase`, data),
};

// 用户组API
export const userGroupsAPI = {
  // 获取用户组列表
  getUserGroups: () => api.get('/user-groups'),
  
  // 获取单个用户组详情
  getUserGroup: (id) => api.get(`/user-groups/${id}`),
  
  // 创建用户组
  createUserGroup: (data) => api.post('/user-groups', data),
  
  // 更新用户组
  updateUserGroup: (id, data) => api.put(`/user-groups/${id}`, data),
  
  // 删除用户组
  deleteUserGroup: (id) => api.delete(`/user-groups/${id}`),
  
  // 获取用户组中的用户
  getUsersInGroup: (id) => api.get(`/user-groups/${id}/users`),
  
  // 将用户分配到用户组
  assignUserToGroup: (userId, groupId) => api.put(`/users/${userId}/group`, { group_id: groupId }),
};

// 流量统计API
export const trafficAPI = {
  // 获取实时流量数据
  getRealtimeTraffic: (tunnelId) => api.get('/traffic/realtime', { params: { tunnel_id: tunnelId } }),
  
  // 获取每日流量统计
  getDailyTraffic: (tunnelId, days) => api.get('/traffic/daily', { params: { tunnel_id: tunnelId, days } }),
  
  // 获取流量汇总统计
  getTrafficSummary: () => api.get('/traffic/summary'),
};

