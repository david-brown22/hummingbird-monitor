import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Bird, Plus, Search, Filter, Edit, Trash2, Eye } from 'lucide-react';
import { format } from 'date-fns';
import { api } from '../services/api';
import toast from 'react-hot-toast';

const Birds = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedBird, setSelectedBird] = useState(null);
  const queryClient = useQueryClient();

  // Fetch birds
  const { data: birds, isLoading } = useQuery(
    'birds',
    () => api.get('/api/birds/').then(res => res.data)
  );

  // Delete bird mutation
  const deleteBirdMutation = useMutation(
    (birdId) => api.delete(`/api/birds/${birdId}`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('birds');
        toast.success('Bird deleted successfully');
      },
      onError: () => {
        toast.error('Failed to delete bird');
      },
    }
  );

  const handleDeleteBird = (birdId) => {
    if (window.confirm('Are you sure you want to delete this bird?')) {
      deleteBirdMutation.mutate(birdId);
    }
  };

  const filteredBirds = birds?.filter(bird =>
    bird.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    bird.embedding_id?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

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
          <h1 className="text-2xl font-bold text-gray-900">Birds</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage and view individual hummingbird profiles
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Bird
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search birds by name or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
            />
          </div>
        </div>
        <button className="btn-secondary flex items-center">
          <Filter className="h-4 w-4 mr-2" />
          Filters
        </button>
      </div>

      {/* Birds Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredBirds.map((bird) => (
          <div key={bird.id} className="card hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-12 w-12 bg-hummingbird-100 rounded-full flex items-center justify-center">
                    <Bird className="h-6 w-6 text-hummingbird-600" />
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    {bird.name || `Bird ${bird.id}`}
                  </h3>
                  <p className="text-sm text-gray-500">ID: {bird.embedding_id}</p>
                </div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setSelectedBird(bird)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <Eye className="h-4 w-4" />
                </button>
                <button className="text-gray-400 hover:text-gray-600">
                  <Edit className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDeleteBird(bird.id)}
                  className="text-red-400 hover:text-red-600"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Total Visits:</span>
                <span className="font-medium">{bird.total_visits}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">First Seen:</span>
                <span className="font-medium">
                  {format(new Date(bird.first_seen), 'MMM dd, yyyy')}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Last Seen:</span>
                <span className="font-medium">
                  {format(new Date(bird.last_seen), 'MMM dd, yyyy')}
                </span>
              </div>
            </div>

            {bird.distinctive_features && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-xs text-gray-600">
                  <span className="font-medium">Features:</span> {bird.distinctive_features}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredBirds.length === 0 && (
        <div className="text-center py-12">
          <Bird className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No birds found</h3>
          <p className="text-gray-500">
            {searchTerm ? 'Try adjusting your search terms.' : 'Start by adding your first bird.'}
          </p>
        </div>
      )}

      {/* Add Bird Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Bird</h3>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Bird Name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
                  placeholder="Enter bird name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Distinctive Features
                </label>
                <textarea
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
                  placeholder="Describe distinctive features"
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Add Bird
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Birds;
