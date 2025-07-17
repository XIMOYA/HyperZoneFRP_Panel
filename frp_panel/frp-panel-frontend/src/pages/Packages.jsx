import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Button, Tag, Statistic, Modal, Form, Input, message,
  Descriptions, Divider, Space, Typography, Badge, Tooltip, Empty, Radio
} from 'antd';
import {
  ShoppingCartOutlined, CheckCircleOutlined, InfoCircleOutlined,
  DollarOutlined, ClockCircleOutlined, ThunderboltOutlined
} from '@ant-design/icons';
import { packagesAPI } from '../utils/api';
import { formatBytes } from '../utils/format';

const { Title, Paragraph, Text } = Typography;

const Packages = () => {
  const [packages, setPackages] = useState([]);
  const [userPackages, setUserPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [paymentModalVisible, setPaymentModalVisible] = useState(false);
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('alipay');

  useEffect(() => {
    fetchPackages();
    fetchUserPackages();
  }, []);

  const fetchPackages = async () => {
    try {
      setLoading(true);
      const response = await packagesAPI.getPackages();
      setPackages(response.packages || []);
    } catch (error) {
      console.error('获取套餐列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserPackages = async () => {
    try {
      const response = await packagesAPI.getUserPackages();
      setUserPackages(response.user_packages || []);
    } catch (error) {
      console.error('获取用户套餐失败:', error);
    }
  };

  const handlePurchase = (pkg) => {
    setSelectedPackage(pkg);
    setPaymentModalVisible(true);
  };

  const handlePaymentSubmit = async () => {
    try {
      await packagesAPI.purchasePackage(selectedPackage.id, { payment_method: paymentMethod });
      message.success('套餐购买成功！');
      setPaymentModalVisible(false);
      fetchUserPackages();
    } catch (error) {
      console.error('购买套餐失败:', error);
    }
  };

  const renderPackageCard = (pkg) => {
    // 检查用户是否已购买该套餐
    const isPurchased = userPackages.some(up => 
      up.package_id === pkg.id && up.is_active && new Date(up.end_date) > new Date()
    );

    return (
      <Col xs={24} sm={12} md={8} key={pkg.id}>
        <Card
          hoverable
          style={{ height: '100%' }}
          actions={[
            <Button 
              type="primary" 
              icon={<ShoppingCartOutlined />}
              onClick={() => handlePurchase(pkg)}
              disabled={isPurchased}
            >
              {isPurchased ? '已购买' : '立即购买'}
            </Button>
          ]}
        >
          <div style={{ position: 'relative' }}>
            {isPurchased && (
              <Badge.Ribbon text="已购买" color="green" />
            )}
            <Title level={4}>{pkg.name}</Title>
            <Statistic
              value={pkg.price}
              prefix="¥"
              suffix="元"
              valueStyle={{ color: '#1890ff' }}
            />
            <Paragraph type="secondary">有效期: {pkg.duration} 天</Paragraph>
            <Divider />
            <Descriptions column={1} size="small">
              <Descriptions.Item label="最大隧道数">
                {pkg.max_tunnels} 个
              </Descriptions.Item>
              <Descriptions.Item label="流量限制">
                {formatBytes(pkg.max_traffic)}
              </Descriptions.Item>
              {pkg.upload_speed_limit && (
                <Descriptions.Item label="上传速率">
                  {pkg.upload_speed_limit} KB/s
                </Descriptions.Item>
              )}
              {pkg.download_speed_limit && (
                <Descriptions.Item label="下载速率">
                  {pkg.download_speed_limit} KB/s
                </Descriptions.Item>
              )}
            </Descriptions>
            {pkg.description && (
              <>
                <Divider />
                <Paragraph>{pkg.description}</Paragraph>
              </>
            )}
          </div>
        </Card>
      </Col>
    );
  };

  const renderUserPackages = () => {
    if (userPackages.length === 0) {
      return (
        <Card>
          <Empty description="您还没有购买任何套餐" />
        </Card>
      );
    }

    return (
      <div>
        <Title level={4}>我的套餐</Title>
        <Row gutter={[16, 16]}>
          {userPackages.map(userPackage => {
            const pkg = userPackage.package;
            const isActive = userPackage.is_active && new Date(userPackage.end_date) > new Date();
            
            return (
              <Col xs={24} sm={12} md={8} key={userPackage.id}>
                <Card>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Title level={5}>{pkg.name}</Title>
                      <Tag color={isActive ? 'success' : 'default'}>
                        {isActive ? '使用中' : '已过期'}
                      </Tag>
                    </div>
                    <Descriptions column={1} size="small">
                      <Descriptions.Item label="开始时间">
                        {new Date(userPackage.start_date).toLocaleString()}
                      </Descriptions.Item>
                      <Descriptions.Item label="结束时间">
                        {new Date(userPackage.end_date).toLocaleString()}
                      </Descriptions.Item>
                      <Descriptions.Item label="已用流量">
                        {formatBytes(userPackage.used_traffic)} / {formatBytes(pkg.max_traffic)}
                      </Descriptions.Item>
                    </Descriptions>
                  </Space>
                </Card>
              </Col>
            );
          })}
        </Row>
      </div>
    );
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3}>套餐购买</Title>
        <Paragraph>
          选择适合您需求的套餐，享受更多的隧道数量和流量配额。
        </Paragraph>
      </div>

      {userPackages.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          {renderUserPackages()}
        </div>
      )}

      <Title level={4}>可用套餐</Title>
      <Row gutter={[16, 16]}>
        {packages.map(renderPackageCard)}
      </Row>

      <Modal
        title="确认购买"
        open={paymentModalVisible}
        onCancel={() => setPaymentModalVisible(false)}
        footer={null}
      >
        {selectedPackage && (
          <div>
            <Descriptions title="套餐信息" column={1} bordered>
              <Descriptions.Item label="套餐名称">{selectedPackage.name}</Descriptions.Item>
              <Descriptions.Item label="价格">¥{selectedPackage.price}元</Descriptions.Item>
              <Descriptions.Item label="有效期">{selectedPackage.duration}天</Descriptions.Item>
              <Descriptions.Item label="最大隧道数">{selectedPackage.max_tunnels}个</Descriptions.Item>
              <Descriptions.Item label="流量限制">{formatBytes(selectedPackage.max_traffic)}</Descriptions.Item>
            </Descriptions>
            
            <Divider />
            
            <Form layout="vertical" onFinish={handlePaymentSubmit}>
              <Form.Item label="支付方式">
                <Radio.Group value={paymentMethod} onChange={e => setPaymentMethod(e.target.value)}>
                  <Radio.Button value="alipay">支付宝</Radio.Button>
                  <Radio.Button value="wechat">微信支付</Radio.Button>
                </Radio.Group>
              </Form.Item>
              
              <Form.Item style={{ textAlign: 'right', marginBottom: 0 }}>
                <Button type="default" onClick={() => setPaymentModalVisible(false)} style={{ marginRight: 8 }}>
                  取消
                </Button>
                <Button type="primary" htmlType="submit">
                  确认支付
                </Button>
              </Form.Item>
            </Form>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Packages;

