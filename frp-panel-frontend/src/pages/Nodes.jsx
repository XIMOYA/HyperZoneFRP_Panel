import React, { useState, useEffect } from 'react';
import {
  Table, Button, Space, Tag, Modal, Form, Input, message,
  Card, Row, Col, Statistic, Popconfirm, Tooltip, Badge
} from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined,
  CheckCircleOutlined, CloseCircleOutlined, ExclamationCircleOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { nodesAPI } from '../utils/api';
import { isAdmin } from '../utils/auth';

const Nodes = () => {
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingNode, setEditingNode] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchNodes();
  }, []);

  const fetchNodes = async () => {
    setLoading(true);
    try {
      const response = await nodesAPI.getNodes();
      setNodes(response.nodes || []);
    } catch (error) {
      console.error('获取节点列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingNode(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingNode(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      await nodesAPI.deleteNode(id);
      message.success('删除成功');
      fetchNodes();
    } catch (error) {
      console.error('删除节点失败:', error);
    }
  };

  const handleSubmit = async (values) => {
    try {
      if (editingNode) {
        await nodesAPI.updateNode(editingNode.id, values);
        message.success('更新成功');
      } else {
        await nodesAPI.createNode(values);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchNodes();
    } catch (error) {
      console.error('保存节点失败:', error);
    }
  };

  const handleViewStatus = async (record) => {
    try {
      const response = await nodesAPI.getNodeStatus(record.id);
      Modal.info({
        title: `节点状态 - ${record.name}`,
        width: 600,
        content: (
          <div>
            <p><strong>状态:</strong> {response.status}</p>
            {response.server_info && (
              <div>
                <p><strong>服务器信息:</strong></p>
                <pre style={{ background: '#f5f5f5', padding: 10, borderRadius: 4 }}>
                  {JSON.stringify(response.server_info, null, 2)}
                </pre>
              </div>
            )}
            {response.proxies && response.proxies.length > 0 && (
              <div>
                <p><strong>代理列表:</strong></p>
                <pre style={{ background: '#f5f5f5', padding: 10, borderRadius: 4 }}>
                  {JSON.stringify(response.proxies, null, 2)}
                </pre>
              </div>
            )}
            {response.error && (
              <p style={{ color: 'red' }}><strong>错误:</strong> {response.error}</p>
            )}
          </div>
        ),
      });
    } catch (error) {
      console.error('获取节点状态失败:', error);
    }
  };

  const getStatusTag = (status) => {
    const statusMap = {
      online: { color: 'success', icon: <CheckCircleOutlined />, text: '在线' },
      offline: { color: 'default', icon: <CloseCircleOutlined />, text: '离线' },
      error: { color: 'error', icon: <ExclamationCircleOutlined />, text: '错误' },
    };
    const config = statusMap[status] || statusMap.offline;
    return <Tag color={config.color} icon={config.icon}>{config.text}</Tag>;
  };

  const columns = [
    {
      title: '节点名称',
      dataIndex: 'name',
      key: 'name',
      render: (name, record) => (
        <Space>
          <Badge status={record.status === 'online' ? 'success' : 'default'} />
          {name}
        </Space>
      ),
    },
    {
      title: '服务器地址',
      key: 'address',
      render: (_, record) => `${record.host}:${record.port}`,
    },
    {
      title: 'Dashboard端口',
      dataIndex: 'dashboard_port',
      key: 'dashboard_port',
      render: (port) => port || '-',
    },
    {
      title: '区域',
      dataIndex: 'region',
      key: 'region',
      render: (region) => region || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: getStatusTag,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time) => time ? new Date(time).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title="查看状态">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => handleViewStatus(record)}
            />
          </Tooltip>
          {isAdmin() && (
            <>
              <Tooltip title="编辑">
                <Button
                  type="text"
                  icon={<EditOutlined />}
                  onClick={() => handleEdit(record)}
                />
              </Tooltip>
              <Popconfirm
                title="确定要删除这个节点吗？"
                onConfirm={() => handleDelete(record.id)}
                okText="确定"
                cancelText="取消"
              >
                <Tooltip title="删除">
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                  />
                </Tooltip>
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ];

  // 统计数据
  const stats = {
    total: nodes.length,
    online: nodes.filter(node => node.status === 'online').length,
    offline: nodes.filter(node => node.status === 'offline').length,
    error: nodes.filter(node => node.status === 'error').length,
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1>节点管理</h1>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchNodes}>
            刷新
          </Button>
          {isAdmin() && (
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
              添加节点
            </Button>
          )}
        </Space>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic title="总节点数" value={stats.total} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="在线节点"
              value={stats.online}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="离线节点"
              value={stats.offline}
              valueStyle={{ color: '#999' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="错误节点"
              value={stats.error}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <Table
          dataSource={nodes}
          columns={columns}
          loading={loading}
          rowKey="id"
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      {/* 添加/编辑节点模态框 */}
      <Modal
        title={editingNode ? '编辑节点' : '添加节点'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="name"
            label="节点名称"
            rules={[{ required: true, message: '请输入节点名称' }]}
          >
            <Input placeholder="请输入节点名称" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={16}>
              <Form.Item
                name="host"
                label="服务器地址"
                rules={[{ required: true, message: '请输入服务器地址' }]}
              >
                <Input placeholder="请输入服务器IP或域名" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="port"
                label="服务端口"
                rules={[{ required: true, message: '请输入端口' }]}
              >
                <Input placeholder="7000" type="number" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="dashboard_port"
                label="Dashboard端口"
              >
                <Input placeholder="7500" type="number" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="dashboard_user"
                label="Dashboard用户名"
              >
                <Input placeholder="admin" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="dashboard_password"
                label="Dashboard密码"
              >
                <Input.Password placeholder="请输入密码" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="token"
                label="认证Token"
              >
                <Input placeholder="请输入认证Token" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="region"
                label="区域"
              >
                <Input placeholder="如：华东、华北等" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea rows={3} placeholder="请输入节点描述" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingNode ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Nodes;

