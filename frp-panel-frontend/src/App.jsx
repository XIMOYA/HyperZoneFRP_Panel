import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { isAuthenticated } from './utils/auth';
import MainLayout from './components/Layout/MainLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Nodes from './pages/Nodes';
import Tunnels from './pages/Tunnels';
import Packages from './pages/Packages';
import TrafficStats from './pages/TrafficStats';
import './App.css';

// 路由保护组件
const ProtectedRoute = ({ children }) => {
  return isAuthenticated() ? children : <Navigate to="/login" replace />;
};

// 登录页面路由保护
const LoginRoute = ({ children }) => {
  return isAuthenticated() ? <Navigate to="/dashboard" replace /> : children;
};

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Routes>
          <Route
            path="/login"
            element={
              <LoginRoute>
                <Login />
              </LoginRoute>
            }
          />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Routes>
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/nodes" element={<Nodes />} />
                    <Route path="/tunnels" element={<Tunnels />} />
                    <Route path="/packages" element={<Packages />} />
                    <Route path="/traffic" element={<TrafficStats />} />
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  </Routes>
                </MainLayout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </ConfigProvider>
  );
}

export default App;
