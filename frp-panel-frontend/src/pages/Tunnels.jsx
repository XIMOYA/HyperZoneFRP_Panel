import React, { useState, useEffect } from 'react';
import {
  Table, Button, Space, Tag, Modal, Form, Input, Select, message,
  Card, Row, Col, Statistic, Popconfirm, Tooltip, Badge, Switch
} from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined,
  PlayCircleOutlined, PauseCircleOutlined, CheckCircleOutlined,
  CloseCircleOutlined, ExclamationCircleOutlined
} from '@ant-design/icons';
import { tunnelsAPI, nodesAPI } from '../utils/api';
import { isAdmin } from '../utils/auth';

const { Option } = Select;

const Tunnels = () => {
  const [tunnels, setTunnels] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTunnel, setEditingTunnel] = useState(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchTunnels();
    fetchNodes();
  }, []);

  const fetchTunnels = async () => {
    setLoading(true);
    try {
      const response = await tunnelsAPI.getTunnels();
      setTunnels(response.tunnels || []);
    } catch (error) {
      console.error('获取隧道列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchNodes = async () => {
    try {
      const response = await nodesAPI.getNodes();
      setNodes(response.nodes || []);
    } catch (error) {
      console.error('获取节点列表失败:', error);
    }
  };

  const handleCreate = () => {
    setEditingTunnel(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingTunnel(record);
    const formData = { ...record };
    if (formData.custom_domains) {
      try {
        formData.custom_domains = JSON.parse(formData.custom_domains);
      } catch (e) {
        formData.custom_domains = [];
      }
    }
    form.setFieldsValue(formData);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      await tunnelsAPI.deleteTunnel(id);
      message.success('删除成功');
      fetchTunnels();
    } catch (error) {
      console.error('删除隧道失败:', error);
    }
  };

  const handleStart = async (id) => {
    try {
      await tunnelsAPI.startTunnel(id);
      message.success('启动成功');
      fetchTunnels();
    } catch (error) {
      console.error('启动隧道失败:', error);
    }
  };

  const handleStop = async (id) => {
    try {
      await tunnelsAPI.stopTunnel(id);
      message.success('停止成功');
      fetchTunnels();
    } catch (error) {
      console.error('停止隧道失败:', error);
    }
  };

  const handleBatchOperation = async (operation) => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要操作的隧道');
      return;
    }

    try {
      await tunnelsAPI.batchOperation({
        tunnel_ids: selectedRowKeys,
        operation,
      });
      message.success(`批量${operation === 'start' ? '启动' : operation === 'stop' ? '停止' : '删除'}成功`);
      setSelectedRowKeys([]);
      fetchTunnels();
    } catch (error) {
      console.error('批量操作失败:', error);
    }
  };

  const handleSubmit = async (values) => {
    try {
      const submitData = { ...values };
      if (submitData.custom_domains && Array.isArray(submitData.custom_domains)) {
        submitData.custom_domains = JSON.stringify(submitData.custom_domains);
      }

      if (editingTunnel) {
        await tunnelsAPI.updateTunnel(editingTunnel.id, submitData);
        message.success('更新成功');
      } else {
        await tunnelsAPI.createTunnel(submitData);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchTunnels();
    } catch (error) {
      console.error('保存隧道失败:', error);
    }
  };

  const getStatusTag = (status) => {
    const statusMap = {
      running: { color: 'success', icon: <CheckCircleOutlined />, text: '运行中' },
      stopped: { color: 'default', icon: <CloseCircleOutlined />, text: '已停止' },
      error: { color: 'error', icon: <ExclamationCircleOutlined />, text: '错误' },
    };
    const config = statusMap[status] || statusMap.stopped;
    return <Tag color={config.color} icon={config.icon}>{config.text}</Tag>;
  };

  const getTypeTag = (type) => {
    const colorMap = {
      tcp: 'blue',
      udp: 'green',
      http: 'orange',
      https: 'red',
    };
    return <Tag color={colorMap[type]}>{type.toUpperCase()}</Tag>;
  };

  const columns = [
    {
      title: '隧道名称',
      dataIndex: 'name',
      key: 'name',
      render: (name, record) => (
        <Space>
          <Badge status={record.status === 'running' ? 'success' : 'default'} />
          {name}
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: getTypeTag,
    },
    {
      title: '本地地址',
      key: 'local',
      render: (_, record) => `${record.local_ip}:${record.local_port}`,
    },
    {
      title: '远程端口',
      dataIndex: 'remote_port',
      key: 'remote_port',
      render: (port) => port || '-',
    },
    {
      title: '自定义域名',
      dataIndex: 'custom_domains',
      key: 'custom_domains',
      render: (domains) => {
        if (!domains) return '-';
        try {
          const domainList = JSON.parse(domains);
          return domainList.length > 0 ? domainList.join(', ') : '-';
        } catch (e) {
          return domains;
        }
      },
    },
    {
      title: '节点',
      key: 'node',
      render: (_, record) => record.node?.name || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: getStatusTag,
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          {record.status === 'running' ? (
            <Tooltip title="停止">
              <Button
                type="text"
                icon={<PauseCircleOutlined />}
                onClick={() => handleStop(record.id)}
              />
            </Tooltip>
          ) : (
            <Tooltip title="启动">
              <Button
                type="text"
                icon={<PlayCircleOutlined />}
                onClick={() => handleStart(record.id)}
              />
            </Tooltip>
          )}
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个隧道吗？"
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
        </Space>
      ),
    },
  ];

  // 统计数据
  const stats = {
    total: tunnels.length,
    running: tunnels.filter(tunnel => tunnel.status === 'running').length,
    stopped: tunnels.filter(tunnel => tunnel.status === 'stopped').length,
    error: tunnels.filter(tunnel => tunnel.status === 'error').length,
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: setSelectedRowKeys,
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1>隧道管理</h1>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchTunnels}>
            刷新
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            创建隧道
          </Button>
        </Space>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic title="总隧道数" value={stats.total} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="运行中"
              value={stats.running}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已停止"
              value={stats.stopped}
              valueStyle={{ color: '#999' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="错误"
              value={stats.error}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 批量操作 */}
      {selectedRowKeys.length > 0 && (
        <Card style={{ marginBottom: 16 }}>
          <Space>
            <span>已选择 {selectedRowKeys.length} 项</span>
            <Button onClick={() => handleBatchOperation('start')}>
              批量启动
            </Button>
            <Button onClick={() => handleBatchOperation('stop')}>
              批量停止
            </Button>
            <Popconfirm
              title="确定要删除选中的隧道吗？"
              onConfirm={() => handleBatchOperation('delete')}
              okText="确定"
              cancelText="取消"
            >
              <Button danger>批量删除</Button>
            </Popconfirm>
          </Space>
        </Card>
      )}

      <Card>
        <Table
          dataSource={tunnels}
          columns={columns}
          loading={loading}
          rowKey="id"
          rowSelection={rowSelection}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      {/* 添加/编辑隧道模态框 */}
      <Modal
        title={editingTunnel ? '编辑隧道' : '创建隧道'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={700}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="name"
                label="隧道名称"
                rules={[{ required: true, message: '请输入隧道名称' }]}
              >
                <Input placeholder="请输入隧道名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="type"
                label="隧道类型"
                rules={[{ required: true, message: '请选择隧道类型' }]}
              >
                <Select placeholder="请选择隧道类型">
                  <Option value="tcp">TCP</Option>
                  <Option value="udp">UDP</Option>
                  <Option value="http">HTTP</Option>
                  <Option value="https">HTTPS</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={16}>
              <Form.Item
                name="local_ip"
                label="本地IP"
                initialValue="127.0.0.1"
              >
                <Input placeholder="127.0.0.1" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="local_port"
                label="本地端口"
                rules={[{ required: true, message: '请输入本地端口' }]}
              >
                <Input placeholder="8080" type="number" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="remote_port"
                label="远程端口"
              >
                <Input placeholder="留空则自动分配" type="number" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="node_id"
                label="选择节点"
                rules={[{ required: true, message: '请选择节点' }]}
              >
                <Select placeholder="请选择节点">
                  {nodes.map(node => (
                    <Option key={node.id} value={node.id}>
                      {node.name} ({node.host})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="subdomain"
            label="子域名"
          >
            <Input placeholder="仅HTTP/HTTPS类型可用" />
          </Form.Item>

          <Form.Item
            name="custom_domains"
            label="自定义域名"
          >
            <Select
              mode="tags"
              placeholder="输入域名后按回车添加"
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea rows={3} placeholder="请输入隧道描述" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingTunnel ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Tunnels;

