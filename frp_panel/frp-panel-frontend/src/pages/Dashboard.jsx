import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Table, Tag, Progress, Alert } from 'antd';
import {
  CloudServerOutlined,
  ApiOutlined,
  UserOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { nodesAPI, tunnelsAPI } from '../utils/api';
import { isAdmin } from '../utils/auth';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalNodes: 0,
    onlineNodes: 0,
    totalTunnels: 0,
    runningTunnels: 0,
  });
  const [recentNodes, setRecentNodes] = useState([]);
  const [recentTunnels, setRecentTunnels] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // 获取节点数据
      const nodesResponse = await nodesAPI.getNodes();
      const nodes = nodesResponse.nodes || [];
      
      // 获取隧道数据
      const tunnelsResponse = await tunnelsAPI.getTunnels();
      const tunnels = tunnelsResponse.tunnels || [];

      // 计算统计数据
      const onlineNodes = nodes.filter(node => node.status === 'online').length;
      const runningTunnels = tunnels.filter(tunnel => tunnel.status === 'running').length;

      setStats({
        totalNodes: nodes.length,
        onlineNodes,
        totalTunnels: tunnels.length,
        runningTunnels,
      });

      // 设置最近的节点和隧道
      setRecentNodes(nodes.slice(0, 5));
      setRecentTunnels(tunnels.slice(0, 5));
    } catch (error) {
      console.error('获取仪表盘数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 节点状态标签
  const getNodeStatusTag = (status) => {
    const statusMap = {
      online: { color: 'success', icon: <CheckCircleOutlined />, text: '在线' },
      offline: { color: 'default', icon: <CloseCircleOutlined />, text: '离线' },
      error: { color: 'error', icon: <ExclamationCircleOutlined />, text: '错误' },
    };
    const config = statusMap[status] || statusMap.offline;
    return <Tag color={config.color} icon={config.icon}>{config.text}</Tag>;
  };

  // 隧道状态标签
  const getTunnelStatusTag = (status) => {
    const statusMap = {
      running: { color: 'success', icon: <CheckCircleOutlined />, text: '运行中' },
      stopped: { color: 'default', icon: <CloseCircleOutlined />, text: '已停止' },
      error: { color: 'error', icon: <ExclamationCircleOutlined />, text: '错误' },
    };
    const config = statusMap[status] || statusMap.stopped;
    return <Tag color={config.color} icon={config.icon}>{config.text}</Tag>;
  };

  // 节点表格列
  const nodeColumns = [
    {
      title: '节点名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '地址',
      dataIndex: 'host',
      key: 'host',
      render: (host, record) => `${host}:${record.port}`,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: getNodeStatusTag,
    },
    {
      title: '区域',
      dataIndex: 'region',
      key: 'region',
      render: (region) => region || '-',
    },
  ];

  // 隧道表格列
  const tunnelColumns = [
    {
      title: '隧道名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type) => <Tag>{type.toUpperCase()}</Tag>,
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
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: getTunnelStatusTag,
    },
  ];

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>仪表盘</h1>
      
      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="节点总数"
              value={stats.totalNodes}
              prefix={<CloudServerOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="在线节点"
              value={stats.onlineNodes}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <Progress
              percent={stats.totalNodes > 0 ? (stats.onlineNodes / stats.totalNodes) * 100 : 0}
              showInfo={false}
              strokeColor="#52c41a"
              size="small"
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="隧道总数"
              value={stats.totalTunnels}
              prefix={<ApiOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="运行中隧道"
              value={stats.runningTunnels}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <Progress
              percent={stats.totalTunnels > 0 ? (stats.runningTunnels / stats.totalTunnels) * 100 : 0}
              showInfo={false}
              strokeColor="#52c41a"
              size="small"
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
      </Row>

      {/* 系统状态提醒 */}
      {stats.totalNodes === 0 && (
        <Alert
          message="系统提醒"
          description={
            isAdmin() 
              ? "当前没有可用节点，请先添加FRP服务器节点。" 
              : "当前没有可用节点，请联系管理员添加FRP服务器节点。"
          }
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      <Row gutter={[16, 16]}>
        {/* 最近节点 */}
        <Col xs={24} lg={12}>
          <Card
            title="最近节点"
            extra={<a href="/nodes">查看全部</a>}
            loading={loading}
          >
            <Table
              dataSource={recentNodes}
              columns={nodeColumns}
              pagination={false}
              size="small"
              rowKey="id"
            />
          </Card>
        </Col>

        {/* 最近隧道 */}
        <Col xs={24} lg={12}>
          <Card
            title="最近隧道"
            extra={<a href="/tunnels">查看全部</a>}
            loading={loading}
          >
            <Table
              dataSource={recentTunnels}
              columns={tunnelColumns}
              pagination={false}
              size="small"
              rowKey="id"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;

