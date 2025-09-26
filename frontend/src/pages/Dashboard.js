import React from 'react';
import { useQuery } from 'react-query';
import { 
  Activity, 
  Bird, 
  AlertTriangle, 
  TrendingUp,
  Clock,
  Thermometer
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { format, subDays } from 'date-fns';
import { api } from '../services/api';

const Dashboard = () => {
  // Fetch dashboard data
  const { data: stats, isLoading: statsLoading } = useQuery(
    'dashboard-stats',
    () => api.get('/api/visits/stats/daily').then(res => res.data),
    { refetchInterval: 30000 } // Refresh every 30 seconds
  );

  const { data: alerts, isLoading: alertsLoading } = useQuery(
    'active-alerts',
    () => api.get('/api/alerts/?is_active=true&limit=5').then(res => res.data)
  );

  const { data: recentVisits, isLoading: visitsLoading } = useQuery(
    'recent-visits',
    () => api.get('/api/visits/?limit=10').then(res => res.data)
  );

  // Mock data for charts (in production, this would come from the API)
  const visitTrendData = [
    { date: '2024-01-01', visits: 12, birds: 3 },
    { date: '2024-01-02', visits: 18, birds: 4 },
    { date: '2024-01-03', visits: 15, birds: 3 },
    { date: '2024-01-04', visits: 22, birds: 5 },
    { date: '2024-01-05', visits: 28, birds: 6 },
    { date: '2024-01-06', visits: 25, birds: 5 },
    { date: '2024-01-07', visits: 31, birds: 7 },
  ];

  const hourlyData = [
    { hour: '6:00', visits: 2 },
    { hour: '7:00', visits: 8 },
    { hour: '8:00', visits: 15 },
    { hour: '9:00', visits: 12 },
    { hour: '10:00', visits: 18 },
    { hour: '11:00', visits: 22 },
    { hour: '12:00', visits: 16 },
    { hour: '13:00', visits: 14 },
    { hour: '14:00', visits: 19 },
    { hour: '15:00', visits: 17 },
    { hour: '16:00', visits: 13 },
    { hour: '17:00', visits: 9 },
    { hour: '18:00', visits: 5 },
    { hour: '19:00', visits: 2 },
  ];

  if (statsLoading || alertsLoading || visitsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-hummingbird-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Monitor your hummingbird activity and feeder status
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="stat-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Activity className="h-8 w-8 text-hummingbird-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Total Visits Today</dt>
                <dd className="text-lg font-medium text-gray-900">{stats?.total_visits || 0}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Bird className="h-8 w-8 text-nature-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Unique Birds</dt>
                <dd className="text-lg font-medium text-gray-900">{stats?.unique_birds || 0}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Clock className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Peak Hour</dt>
                <dd className="text-lg font-medium text-gray-900">{stats?.peak_hour || 'N/A'}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Active Alerts</dt>
                <dd className="text-lg font-medium text-gray-900">{alerts?.length || 0}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Visit Trend */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">7-Day Visit Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={visitTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="visits" stroke="#f2850a" strokeWidth={2} />
              <Line type="monotone" dataKey="birds" stroke="#22c55e" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Hourly Activity */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Hourly Activity Pattern</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="visits" fill="#f2850a" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity and Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Visits */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Visits</h3>
          <div className="space-y-3">
            {recentVisits?.slice(0, 5).map((visit) => (
              <div key={visit.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                <div className="flex items-center">
                  <Bird className="h-5 w-5 text-hummingbird-600 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {visit.bird_name || 'Unidentified Bird'}
                    </p>
                    <p className="text-xs text-gray-500">
                      Feeder {visit.feeder_id} • {format(new Date(visit.visit_time), 'HH:mm')}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-900">
                    {visit.duration_seconds ? `${visit.duration_seconds}s` : 'N/A'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {visit.confidence_score ? `${Math.round(visit.confidence_score * 100)}%` : 'N/A'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Active Alerts */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Active Alerts</h3>
          <div className="space-y-3">
            {alerts?.length > 0 ? (
              alerts.map((alert) => (
                <div key={alert.id} className={`p-3 rounded-lg border-l-4 ${
                  alert.severity === 'high' ? 'border-red-500 bg-red-50' :
                  alert.severity === 'medium' ? 'border-yellow-500 bg-yellow-50' :
                  'border-blue-500 bg-blue-50'
                }`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{alert.title}</p>
                      <p className="text-xs text-gray-600 mt-1">{alert.message}</p>
                    </div>
                    <AlertTriangle className={`h-5 w-5 ${
                      alert.severity === 'high' ? 'text-red-500' :
                      alert.severity === 'medium' ? 'text-yellow-500' :
                      'text-blue-500'
                    }`} />
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-4">
                <AlertTriangle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No active alerts</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
