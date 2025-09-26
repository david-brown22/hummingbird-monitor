import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { FileText, Calendar, Plus, Download, Eye, RefreshCw, X } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { api } from '../services/api';
import toast from 'react-hot-toast';

const Summaries = () => {
  const [dateFilter, setDateFilter] = useState('');
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [selectedSummary, setSelectedSummary] = useState(null);
  const queryClient = useQueryClient();

  // Fetch summaries
  const { data: summaries, isLoading } = useQuery(
    ['summaries', dateFilter],
    () => {
      const params = new URLSearchParams();
      if (dateFilter) {
        const date = new Date(dateFilter);
        params.append('date_from', date.toISOString().split('T')[0]);
        params.append('date_to', date.toISOString().split('T')[0]);
      }
      return api.get(`/api/summaries/?${params.toString()}`).then(res => res.data);
    }
  );

  // Generate summary mutation
  const generateMutation = useMutation(
    (date) => api.post(`/api/summaries/generate/${date}`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('summaries');
        setShowGenerateModal(false);
        toast.success('Summary generated successfully');
      },
      onError: () => {
        toast.error('Failed to generate summary');
      },
    }
  );

  const handleGenerateSummary = (date) => {
    generateMutation.mutate(date);
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Daily Summaries</h1>
          <p className="mt-1 text-sm text-gray-500">
            AI-generated daily activity summaries
          </p>
        </div>
        <button
          onClick={() => setShowGenerateModal(true)}
          className="btn-primary flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Generate Summary
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filter by Date
            </label>
            <input
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={() => setDateFilter('')}
              className="btn-secondary"
            >
              Clear Filter
            </button>
          </div>
        </div>
      </div>

      {/* Summaries List */}
      <div className="space-y-4">
        {summaries?.map((summary) => (
          <div key={summary.id} className="card hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <div className="h-12 w-12 bg-hummingbird-100 rounded-full flex items-center justify-center">
                    <FileText className="h-6 w-6 text-hummingbird-600" />
                  </div>
                </div>
                <div className="ml-4 flex-1">
                  <div className="flex items-center">
                    <h3 className="text-lg font-medium text-gray-900">{summary.title}</h3>
                    <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-hummingbird-100 text-hummingbird-800">
                      {format(parseISO(summary.date), 'MMM dd, yyyy')}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-gray-600 line-clamp-2">
                    {summary.content}
                  </p>
                  <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                    <span>Visits: {summary.total_visits}</span>
                    <span>Birds: {summary.unique_birds}</span>
                    {summary.peak_hour && <span>Peak: {summary.peak_hour}</span>}
                    {summary.weather_summary && <span>Weather: {summary.weather_summary}</span>}
                  </div>
                </div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setSelectedSummary(summary)}
                  className="text-gray-400 hover:text-gray-600"
                  title="View full summary"
                >
                  <Eye className="h-4 w-4" />
                </button>
                <button className="text-gray-400 hover:text-gray-600" title="Download">
                  <Download className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {summaries?.length === 0 && (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No summaries found</h3>
          <p className="text-gray-500">
            {dateFilter ? 'No summaries found for the selected date.' : 'Generate your first daily summary.'}
          </p>
        </div>
      )}

      {/* Generate Summary Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Generate Daily Summary</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Select Date
                </label>
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
                  defaultValue={new Date().toISOString().split('T')[0]}
                />
              </div>
              <p className="text-sm text-gray-600">
                This will generate an AI-powered summary of hummingbird activity for the selected date.
              </p>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowGenerateModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => handleGenerateSummary(new Date().toISOString().split('T')[0])}
                className="btn-primary flex items-center"
                disabled={generateMutation.isLoading}
              >
                {generateMutation.isLoading ? (
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Plus className="h-4 w-4 mr-2" />
                )}
                Generate
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Summary Detail Modal */}
      {selectedSummary && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-medium text-gray-900">{selectedSummary.title}</h3>
              <button
                onClick={() => setSelectedSummary(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Date:</span>
                  <span className="ml-2 text-gray-900">
                    {format(parseISO(selectedSummary.date), 'MMMM dd, yyyy')}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Total Visits:</span>
                  <span className="ml-2 text-gray-900">{selectedSummary.total_visits}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Unique Birds:</span>
                  <span className="ml-2 text-gray-900">{selectedSummary.unique_birds}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Peak Hour:</span>
                  <span className="ml-2 text-gray-900">{selectedSummary.peak_hour || 'N/A'}</span>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-700 mb-2">Summary</h4>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-900 whitespace-pre-wrap">{selectedSummary.content}</p>
                </div>
              </div>

              {selectedSummary.weather_summary && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Weather</h4>
                  <p className="text-gray-900">{selectedSummary.weather_summary}</p>
                </div>
              )}

              {selectedSummary.unusual_activity && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Unusual Activity</h4>
                  <p className="text-gray-900">{selectedSummary.unusual_activity}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Summaries;
