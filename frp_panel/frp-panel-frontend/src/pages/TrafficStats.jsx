import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Select, DatePicker, Statistic, Table, Tag, Spin,
  Divider, Typography, Space, Progress, Radio
} from 'antd';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { trafficAPI, tunnelsAPI } from '../utils/api';
import { formatBytes } from '../utils/format';

const { Title, Paragraph } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

const TrafficStats = () => {
  const [loading, setLoading] = useState(true);
  const [tunnels, setTunnels] = useState([]);
  const [selectedTunnel, setSelectedTunnel] = useState('all');
  const [timeRange, setTimeRange] = useState('7d');
  const [summaryData, setSummaryData] = useState(null);
  const [dailyData, setDailyData] = useState([]);
  const [realtimeData, setRealtimeData] = useState([]);
  const [chartType, setChartType] = useState('area');

  useEffect(() => {
    fetchTunnels();
    fetchSummaryData();
  }, []);

  useEffect(() => {
    fetchDailyData();
    fetchRealtimeData();
    
    // 设置实时数据轮询
    const interval = setInterval(() => {
      fetchRealtimeData();
    }, 30000); // 每30秒更新一次
    
    return () => clearInterval(interval);
  }, [selectedTunnel, timeRange]);

  const fetchTunnels = async () => {
    try {
      const response = await tunnelsAPI.getTunnels();
      setTunnels(response.tunnels || []);
    } catch (error) {
      console.error('获取隧道列表失败:', error);
    }
  };

  const fetchSummaryData = async () => {
    try {
      setLoading(true);
      const response = await trafficAPI.getTrafficSummary();
      setSummaryData(response);
    } catch (error) {
      console.error('获取流量汇总数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDailyData = async () => {
    try {
      setLoading(true);
      const days = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 7;
      const tunnelId = selectedTunnel === 'all' ? undefined : selectedTunnel;
      
      const response = await trafficAPI.getDailyTraffic(tunnelId, days);
      
      // 处理数据，确保每天都有数据点
      const processedData = processDailyData(response.traffic_summaries, days);
      setDailyData(processedData);
    } catch (error) {
      console.error('获取每日流量数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRealtimeData = async () => {
    try {
      const tunnelId = selectedTunnel === 'all' ? undefined : selectedTunnel;
      const response = await trafficAPI.getRealtimeTraffic(tunnelId);
      
      // 处理数据，只保留最近的数据点
      const logs = response.traffic_logs || [];
      const processedData = logs.map(log => ({
        timestamp: new Date(log.timestamp).toLocaleTimeString(),
        upload: log.upload,
        download: log.download,
        total: log.upload + log.download
      }));
      
      setRealtimeData(processedData);
    } catch (error) {
      console.error('获取实时流量数据失败:', error);
    }
  };

  // 处理每日数据，确保每天都有数据点
  const processDailyData = (data, days) => {
    const result = [];
    const now = new Date();
    
    // 创建日期到数据的映射
    const dataMap = {};
    data.forEach(item => {
      dataMap[item.date] = item;
    });
    
    // 生成过去n天的日期
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      
      if (dataMap[dateStr]) {
        result.push({
          date: dateStr,
          upload: dataMap[dateStr].upload,
          download: dataMap[dateStr].download,
          total: dataMap[dateStr].upload + dataMap[dateStr].download
        });
      } else {
        result.push({
          date: dateStr,
          upload: 0,
          download: 0,
          total: 0
        });
      }
    }
    
    return result;
  };

  // 格式化图表数据
  const formatChartData = (data) => {
    return data.map(item => ({
      ...item,
      uploadFormatted: formatBytes(item.upload),
      downloadFormatted: formatBytes(item.download),
      totalFormatted: formatBytes(item.total)
    }));
  };

  // 渲染流量汇总卡片
  const renderSummaryCards = () => {
    if (!summaryData) return null;
    
    return (
      <Row gutter={16}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="总上传流量"
              value={formatBytes(summaryData.total_upload)}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="总下载流量"
              value={formatBytes(summaryData.total_download)}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="总流量"
              value={formatBytes(summaryData.total)}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>
    );
  };

  // 渲染隧道流量表格
  const renderTunnelTable = () => {
    if (!summaryData || !summaryData.tunnel_stats) return null;
    
    const columns = [
      {
        title: '隧道名称',
        dataIndex: 'tunnel_name',
        key: 'tunnel_name',
      },
      {
        title: '上传流量',
        dataIndex: 'upload',
        key: 'upload',
        render: (upload) => formatBytes(upload),
        sorter: (a, b) => a.upload - b.upload,
      },
      {
        title: '下载流量',
        dataIndex: 'download',
        key: 'download',
        render: (download) => formatBytes(download),
        sorter: (a, b) => a.download - b.download,
      },
      {
        title: '总流量',
        dataIndex: 'total',
        key: 'total',
        render: (total) => formatBytes(total),
        sorter: (a, b) => a.total - b.total,
        defaultSortOrder: 'descend',
      },
      {
        title: '占比',
        dataIndex: 'total',
        key: 'percentage',
        render: (total) => {
          const percentage = summaryData.total > 0 
            ? Math.round((total / summaryData.total) * 100) 
            : 0;
          return (
            <Progress 
              percent={percentage} 
              size="small" 
              format={(percent) => `${percent}%`}
            />
          );
        },
      },
    ];
    
    return (
      <Card title="隧道流量统计" style={{ marginTop: 16 }}>
        <Table
          dataSource={summaryData.tunnel_stats}
          columns={columns}
          rowKey="tunnel_id"
          pagination={false}
        />
      </Card>
    );
  };

  // 渲染每日流量图表
  const renderDailyChart = () => {
    const data = formatChartData(dailyData);
    
    if (chartType === 'area') {
      return (
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis tickFormatter={(value) => formatBytes(value, 0)} />
            <Tooltip 
              formatter={(value) => formatBytes(value)}
              labelFormatter={(label) => `日期: ${label}`}
            />
            <Legend />
            <Area type="monotone" dataKey="upload" name="上传" stackId="1" stroke="#82ca9d" fill="#82ca9d" />
            <Area type="monotone" dataKey="download" name="下载" stackId="1" stroke="#8884d8" fill="#8884d8" />
          </AreaChart>
        </ResponsiveContainer>
      );
    } else if (chartType === 'line') {
      return (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis tickFormatter={(value) => formatBytes(value, 0)} />
            <Tooltip 
              formatter={(value) => formatBytes(value)}
              labelFormatter={(label) => `日期: ${label}`}
            />
            <Legend />
            <Line type="monotone" dataKey="upload" name="上传" stroke="#82ca9d" />
            <Line type="monotone" dataKey="download" name="下载" stroke="#8884d8" />
            <Line type="monotone" dataKey="total" name="总计" stroke="#ff7300" />
          </LineChart>
        </ResponsiveContainer>
      );
    } else if (chartType === 'bar') {
      return (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis tickFormatter={(value) => formatBytes(value, 0)} />
            <Tooltip 
              formatter={(value) => formatBytes(value)}
              labelFormatter={(label) => `日期: ${label}`}
            />
            <Legend />
            <Bar dataKey="upload" name="上传" fill="#82ca9d" />
            <Bar dataKey="download" name="下载" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      );
    }
    
    return null;
  };

  // 渲染实时流量图表
  const renderRealtimeChart = () => {
    if (realtimeData.length === 0) return null;
    
    const data = formatChartData(realtimeData);
    
    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" />
          <YAxis tickFormatter={(value) => formatBytes(value, 0)} />
          <Tooltip 
            formatter={(value) => formatBytes(value)}
            labelFormatter={(label) => `时间: ${label}`}
          />
          <Legend />
          <Line type="monotone" dataKey="upload" name="上传" stroke="#82ca9d" />
          <Line type="monotone" dataKey="download" name="下载" stroke="#8884d8" />
        </LineChart>
      </ResponsiveContainer>
    );
  };

  return (
    <div>
      <Title level={3}>流量统计</Title>
      
      {/* 流量汇总卡片 */}
      {renderSummaryCards()}
      
      {/* 图表控制器 */}
      <Card style={{ marginTop: 16 }}>
        <Space style={{ marginBottom: 16 }}>
          <Select
            value={selectedTunnel}
            onChange={setSelectedTunnel}
            style={{ width: 200 }}
          >
            <Option value="all">所有隧道</Option>
            {tunnels.map(tunnel => (
              <Option key={tunnel.id} value={tunnel.id}>{tunnel.name}</Option>
            ))}
          </Select>
          
          <Select
            value={timeRange}
            onChange={setTimeRange}
            style={{ width: 120 }}
          >
            <Option value="7d">最近7天</Option>
            <Option value="30d">最近30天</Option>
          </Select>
          
          <Radio.Group value={chartType} onChange={e => setChartType(e.target.value)}>
            <Radio.Button value="area">面积图</Radio.Button>
            <Radio.Button value="line">折线图</Radio.Button>
            <Radio.Button value="bar">柱状图</Radio.Button>
          </Radio.Group>
        </Space>
        
        <Divider />
        
        <Spin spinning={loading}>
          <Title level={4}>每日流量统计</Title>
          {renderDailyChart()}
          
          <Divider />
          
          <Title level={4}>实时流量监控</Title>
          {renderRealtimeChart()}
        </Spin>
      </Card>
      
      {/* 隧道流量表格 */}
      {renderTunnelTable()}
    </div>
  );
};

export default TrafficStats;

