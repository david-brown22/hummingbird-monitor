import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Activity, Calendar, Clock, Thermometer, Filter, Download } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { api } from '../services/api';

const Visits = () => {
  const [dateFilter, setDateFilter] = useState('');
  const [feederFilter, setFeederFilter] = useState('');
  const [birdFilter, setBirdFilter] = useState('');

  // Fetch visits
  const { data: visits, isLoading } = useQuery(
    ['visits', dateFilter, feederFilter, birdFilter],
    () => {
      const params = new URLSearchParams();
      if (dateFilter) params.append('date_from', dateFilter);
      if (feederFilter) params.append('feeder_id', feederFilter);
      if (birdFilter) params.append('bird_id', birdFilter);
      
      return api.get(`/api/visits/?${params.toString()}`).then(res => res.data);
    }
  );

  // Fetch daily stats
  const { data: dailyStats } = useQuery(
    'daily-stats',
    () => api.get('/api/visits/stats/daily').then(res => res.data)
  );

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
        <h1 className="text-2xl font-bold text-gray-900">Visits</h1>
        <p className="mt-1 text-sm text-gray-500">
          Track and analyze hummingbird visit patterns
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
                <dt className="text-sm font-medium text-gray-500 truncate">Total Visits</dt>
                <dd className="text-lg font-medium text-gray-900">{dailyStats?.total_visits || 0}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Calendar className="h-8 w-8 text-nature-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Unique Birds</dt>
                <dd className="text-lg font-medium text-gray-900">{dailyStats?.unique_birds || 0}</dd>
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
                <dt className="text-sm font-medium text-gray-500 truncate">Avg Duration</dt>
                <dd className="text-lg font-medium text-gray-900">
                  {dailyStats?.average_duration ? `${Math.round(dailyStats.average_duration)}s` : 'N/A'}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Thermometer className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Peak Hour</dt>
                <dd className="text-lg font-medium text-gray-900">{dailyStats?.peak_hour || 'N/A'}</dd>
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
              Date Filter
            </label>
            <input
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Feeder ID
            </label>
            <input
              type="text"
              value={feederFilter}
              onChange={(e) => setFeederFilter(e.target.value)}
              placeholder="Filter by feeder"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Bird ID
            </label>
            <input
              type="text"
              value={birdFilter}
              onChange={(e) => setBirdFilter(e.target.value)}
              placeholder="Filter by bird"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-end">
            <button className="btn-secondary flex items-center">
              <Filter className="h-4 w-4 mr-2" />
              Apply
            </button>
          </div>
        </div>
      </div>

      {/* Visits Table */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Recent Visits</h3>
          <button className="btn-secondary flex items-center">
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Bird
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Feeder
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Confidence
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Weather
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {visits?.map((visit) => (
                <tr key={visit.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-8 w-8 bg-hummingbird-100 rounded-full flex items-center justify-center mr-3">
                        <Activity className="h-4 w-4 text-hummingbird-600" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {visit.bird_name || 'Unidentified'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {visit.bird_id ? `ID: ${visit.bird_id}` : 'New bird'}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {format(parseISO(visit.visit_time), 'MMM dd, yyyy')}
                    </div>
                    <div className="text-sm text-gray-500">
                      {format(parseISO(visit.visit_time), 'HH:mm:ss')}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-hummingbird-100 text-hummingbird-800">
                      {visit.feeder_id}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {visit.duration_seconds ? `${Math.round(visit.duration_seconds)}s` : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-hummingbird-600 h-2 rounded-full"
                          style={{ width: `${(visit.confidence_score || 0) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-900">
                        {visit.confidence_score ? `${Math.round(visit.confidence_score * 100)}%` : 'N/A'}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {visit.weather_condition || 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {visits?.length === 0 && (
          <div className="text-center py-8">
            <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No visits found</h3>
            <p className="text-gray-500">Try adjusting your filters or check back later.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Visits;
