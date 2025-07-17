// 认证相关工具函数

// 获取token
export const getToken = () => {
  return localStorage.getItem('token');
};

// 设置token
export const setToken = (token) => {
  localStorage.setItem('token', token);
};

// 移除token
export const removeToken = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

// 获取用户信息
export const getUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

// 设置用户信息
export const setUser = (user) => {
  localStorage.setItem('user', JSON.stringify(user));
};

// 检查是否已登录
export const isAuthenticated = () => {
  return !!getToken();
};

// 检查是否是管理员
export const isAdmin = () => {
  const user = getUser();
  return user && user.is_admin;
};

// 登出
export const logout = () => {
  removeToken();
  window.location.href = '/login';
};

