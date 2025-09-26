import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { AlertTriangle, Check, X, Filter, Bell, BellOff } from 'lucide-react';
import { format } from 'date-fns';
import { api } from '../services/api';
import toast from 'react-hot-toast';

const Alerts = () => {
  const [filter, setFilter] = useState('all'); // all, active, acknowledged
  const queryClient = useQueryClient();

  // Fetch alerts
  const { data: alerts, isLoading } = useQuery(
    ['alerts', filter],
    () => {
      const params = new URLSearchParams();
      if (filter === 'active') params.append('is_active', 'true');
      if (filter === 'acknowledged') {
        params.append('is_active', 'true');
        params.append('is_acknowledged', 'true');
      }
      return api.get(`/api/alerts/?${params.toString()}`).then(res => res.data);
    }
  );

  // Fetch alert stats
  const { data: alertStats } = useQuery(
    'alert-stats',
    () => api.get('/api/alerts/stats/active').then(res => res.data)
  );

  // Acknowledge alert mutation
  const acknowledgeMutation = useMutation(
    (alertId) => api.put(`/api/alerts/${alertId}/acknowledge`, {
      acknowledged_by: 'user'
    }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('alerts');
        queryClient.invalidateQueries('alert-stats');
        toast.success('Alert acknowledged');
      },
      onError: () => {
        toast.error('Failed to acknowledge alert');
      },
    }
  );

  // Dismiss alert mutation
  const dismissMutation = useMutation(
    (alertId) => api.put(`/api/alerts/${alertId}/dismiss`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('alerts');
        queryClient.invalidateQueries('alert-stats');
        toast.success('Alert dismissed');
      },
      onError: () => {
        toast.error('Failed to dismiss alert');
      },
    }
  );

  const handleAcknowledge = (alertId) => {
    acknowledgeMutation.mutate(alertId);
  };

  const handleDismiss = (alertId) => {
    dismissMutation.mutate(alertId);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'border-red-500 bg-red-50 text-red-800';
      case 'medium':
        return 'border-yellow-500 bg-yellow-50 text-yellow-800';
      case 'low':
        return 'border-blue-500 bg-blue-50 text-blue-800';
      default:
        return 'border-gray-500 bg-gray-50 text-gray-800';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high':
        return 'text-red-500';
      case 'medium':
        return 'text-yellow-500';
      case 'low':
        return 'text-blue-500';
      default:
        return 'text-gray-500';
    }
  };

  if (isLoading) {
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
        <h1 className="text-2xl font-bold text-gray-900">Alerts</h1>
        <p className="mt-1 text-sm text-gray-500">
          Monitor feeder status and system alerts
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="stat-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Total Active</dt>
                <dd className="text-lg font-medium text-gray-900">{alertStats?.total_active || 0}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Bell className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">High Priority</dt>
                <dd className="text-lg font-medium text-gray-900">
                  {alertStats?.by_severity?.high || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Check className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Acknowledged</dt>
                <dd className="text-lg font-medium text-gray-900">
                  {alerts?.filter(a => a.is_acknowledged).length || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BellOff className="h-8 w-8 text-gray-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Dismissed</dt>
                <dd className="text-lg font-medium text-gray-900">
                  {alerts?.filter(a => !a.is_active).length || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filter Alerts
            </label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
            >
              <option value="all">All Alerts</option>
              <option value="active">Active Only</option>
              <option value="acknowledged">Acknowledged</option>
            </select>
          </div>
          <div className="flex items-end">
            <button className="btn-secondary flex items-center">
              <Filter className="h-4 w-4 mr-2" />
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {alerts?.map((alert) => (
          <div
            key={alert.id}
            className={`card border-l-4 ${getSeverityColor(alert.severity)}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <AlertTriangle className={`h-6 w-6 ${getSeverityIcon(alert.severity)}`} />
                </div>
                <div className="ml-4">
                  <div className="flex items-center">
                    <h3 className="text-lg font-medium text-gray-900">{alert.title}</h3>
                    <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                      {alert.severity.toUpperCase()}
                    </span>
                    {alert.is_acknowledged && (
                      <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        ACKNOWLEDGED
                      </span>
                    )}
                  </div>
                  <p className="mt-1 text-sm text-gray-600">{alert.message}</p>
                  <div className="mt-2 text-xs text-gray-500">
                    <span>Feeder: {alert.feeder_id}</span>
                    <span className="mx-2">•</span>
                    <span>Created: {format(new Date(alert.created_at), 'MMM dd, yyyy HH:mm')}</span>
                    {alert.acknowledged_at && (
                      <>
                        <span className="mx-2">•</span>
                        <span>Acknowledged: {format(new Date(alert.acknowledged_at), 'MMM dd, yyyy HH:mm')}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex space-x-2">
                {!alert.is_acknowledged && (
                  <button
                    onClick={() => handleAcknowledge(alert.id)}
                    className="text-green-600 hover:text-green-800 flex items-center text-sm"
                  >
                    <Check className="h-4 w-4 mr-1" />
                    Acknowledge
                  </button>
                )}
                <button
                  onClick={() => handleDismiss(alert.id)}
                  className="text-gray-600 hover:text-gray-800 flex items-center text-sm"
                >
                  <X className="h-4 w-4 mr-1" />
                  Dismiss
                </button>
              </div>
            </div>

            {alert.trigger_data && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <details className="text-sm">
                  <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
                    View Trigger Data
                  </summary>
                  <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                    {JSON.stringify(JSON.parse(alert.trigger_data), null, 2)}
                  </pre>
                </details>
              </div>
            )}
          </div>
        ))}
      </div>

      {alerts?.length === 0 && (
        <div className="text-center py-12">
          <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No alerts found</h3>
          <p className="text-gray-500">
            {filter === 'all' ? 'No alerts have been generated yet.' : 'No alerts match your current filter.'}
          </p>
        </div>
      )}
    </div>
  );
};

export default Alerts;
