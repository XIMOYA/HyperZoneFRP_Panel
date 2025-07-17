import React, { useState } from 'react';
import { Form, Input, Button, Card, Tabs, message, Divider } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../utils/api';
import { setToken, setUser } from '../utils/auth';

const Login = () => {
  const [loading, setLoading] = useState(false);
  const [sendingCode, setSendingCode] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const navigate = useNavigate();

  // 登录处理
  const handleLogin = async (values) => {
    setLoading(true);
    try {
      const response = await authAPI.login({
        username: values.username,
        password: values.password,
      });
      
      setToken(response.access_token);
      setUser(response.user);
      message.success('登录成功');
      navigate('/dashboard');
    } catch (error) {
      console.error('登录失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 发送验证码
  const handleSendCode = async (email) => {
    if (!email) {
      message.error('请输入邮箱地址');
      return;
    }

    setSendingCode(true);
    try {
      await authAPI.sendVerificationCode(email, 'register');
      message.success('验证码已发送，请查收邮件');
      
      // 开始倒计时
      setCountdown(60);
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (error) {
      console.error('发送验证码失败:', error);
    } finally {
      setSendingCode(false);
    }
  };

  // 注册处理
  const handleRegister = async (values) => {
    setLoading(true);
    try {
      await authAPI.register({
        username: values.username,
        email: values.email,
        password: values.password,
        verification_code: values.verification_code,
      });
      
      message.success('注册成功，请登录');
      // 切换到登录标签页
      document.querySelector('[data-node-key="login"]').click();
    } catch (error) {
      console.error('注册失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 登录表单
  const LoginForm = () => (
    <Form
      name="login"
      onFinish={handleLogin}
      autoComplete="off"
      size="large"
    >
      <Form.Item
        name="username"
        rules={[{ required: true, message: '请输入用户名或邮箱' }]}
      >
        <Input
          prefix={<UserOutlined />}
          placeholder="用户名或邮箱"
        />
      </Form.Item>

      <Form.Item
        name="password"
        rules={[{ required: true, message: '请输入密码' }]}
      >
        <Input.Password
          prefix={<LockOutlined />}
          placeholder="密码"
        />
      </Form.Item>

      <Form.Item>
        <Button
          type="primary"
          htmlType="submit"
          loading={loading}
          block
        >
          登录
        </Button>
      </Form.Item>
    </Form>
  );

  // 注册表单
  const RegisterForm = () => {
    const [form] = Form.useForm();

    return (
      <Form
        form={form}
        name="register"
        onFinish={handleRegister}
        autoComplete="off"
        size="large"
      >
        <Form.Item
          name="username"
          rules={[
            { required: true, message: '请输入用户名' },
            { min: 3, message: '用户名至少3个字符' },
            { max: 20, message: '用户名最多20个字符' },
          ]}
        >
          <Input
            prefix={<UserOutlined />}
            placeholder="用户名"
          />
        </Form.Item>

        <Form.Item
          name="email"
          rules={[
            { required: true, message: '请输入邮箱' },
            { type: 'email', message: '请输入有效的邮箱地址' },
          ]}
        >
          <Input
            prefix={<MailOutlined />}
            placeholder="邮箱"
          />
        </Form.Item>

        <Form.Item
          name="verification_code"
          rules={[{ required: true, message: '请输入验证码' }]}
        >
          <Input
            placeholder="邮箱验证码"
            addonAfter={
              <Button
                type="link"
                size="small"
                loading={sendingCode}
                disabled={countdown > 0}
                onClick={() => {
                  const email = form.getFieldValue('email');
                  handleSendCode(email);
                }}
                style={{ padding: 0, height: 'auto' }}
              >
                {countdown > 0 ? `${countdown}s` : '发送验证码'}
              </Button>
            }
          />
        </Form.Item>

        <Form.Item
          name="password"
          rules={[
            { required: true, message: '请输入密码' },
            { min: 8, message: '密码至少8个字符' },
            {
              pattern: /^(?=.*[A-Za-z])(?=.*\d)/,
              message: '密码必须包含字母和数字',
            },
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="密码"
          />
        </Form.Item>

        <Form.Item
          name="confirmPassword"
          dependencies={['password']}
          rules={[
            { required: true, message: '请确认密码' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('password') === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('两次输入的密码不一致'));
              },
            }),
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="确认密码"
          />
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            block
          >
            注册
          </Button>
        </Form.Item>
      </Form>
    );
  };

  const tabItems = [
    {
      key: 'login',
      label: '登录',
      children: <LoginForm />,
    },
    {
      key: 'register',
      label: '注册',
      children: <RegisterForm />,
    },
  ];

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
    }}>
      <Card
        style={{
          width: '100%',
          maxWidth: 400,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
        }}
      >
        <div style={{
          textAlign: 'center',
          marginBottom: 24,
        }}>
          <h1 style={{
            fontSize: 24,
            fontWeight: 'bold',
            color: '#1890ff',
            margin: 0,
          }}>
            FRP管理面板
          </h1>
          <p style={{
            color: '#666',
            margin: '8px 0 0 0',
          }}>
            内网穿透服务管理平台
          </p>
        </div>

        <Tabs
          defaultActiveKey="login"
          items={tabItems}
          centered
        />
      </Card>
    </div>
  );
};

export default Login;

