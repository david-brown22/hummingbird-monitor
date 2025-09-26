import React, { useState } from 'react';
import { Settings as SettingsIcon, Save, RefreshCw, AlertTriangle, Database, Bell } from 'lucide-react';
import toast from 'react-hot-toast';

const Settings = () => {
  const [settings, setSettings] = useState({
    // Alert Settings
    visitThreshold: 50,
    nectarDepletionRate: 0.1,
    alertEmail: '',
    alertSms: '',
    
    // System Settings
    autoGenerateSummaries: true,
    summaryTime: '18:00',
    dataRetentionDays: 365,
    
    // AI Settings
    confidenceThreshold: 0.7,
    enableBirdIdentification: true,
    enableWeatherTracking: true,
    
    // Feeder Settings
    feederCount: 2,
    feederLocations: ['Front Yard', 'Back Yard'],
    
    // Camera Settings
    motionSensitivity: 'medium',
    recordingDuration: 30,
    imageQuality: 'high'
  });

  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Settings saved successfully');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset all settings to default values?')) {
      // Reset to default values
      setSettings({
        visitThreshold: 50,
        nectarDepletionRate: 0.1,
        alertEmail: '',
        alertSms: '',
        autoGenerateSummaries: true,
        summaryTime: '18:00',
        dataRetentionDays: 365,
        confidenceThreshold: 0.7,
        enableBirdIdentification: true,
        enableWeatherTracking: true,
        feederCount: 2,
        feederLocations: ['Front Yard', 'Back Yard'],
        motionSensitivity: 'medium',
        recordingDuration: 30,
        imageQuality: 'high'
      });
      toast.success('Settings reset to defaults');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="mt-1 text-sm text-gray-500">
            Configure system preferences and alert thresholds
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleReset}
            className="btn-secondary flex items-center"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="btn-primary flex items-center"
          >
            {isSaving ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            Save Settings
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alert Settings */}
        <div className="card">
          <div className="flex items-center mb-4">
            <AlertTriangle className="h-5 w-5 text-red-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Alert Settings</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Visit Threshold for Refill Alert
              </label>
              <input
                type="number"
                value={settings.visitThreshold}
                onChange={(e) => setSettings({...settings, visitThreshold: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">Number of visits per day to trigger refill alert</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nectar Depletion Rate
              </label>
              <input
                type="number"
                step="0.01"
                value={settings.nectarDepletionRate}
                onChange={(e) => setSettings({...settings, nectarDepletionRate: parseFloat(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">Estimated nectar depletion per visit (0.0 - 1.0)</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Alert Email
              </label>
              <input
                type="email"
                value={settings.alertEmail}
                onChange={(e) => setSettings({...settings, alertEmail: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
                placeholder="your-email@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Alert SMS
              </label>
              <input
                type="tel"
                value={settings.alertSms}
                onChange={(e) => setSettings({...settings, alertSms: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
                placeholder="+1234567890"
              />
            </div>
          </div>
        </div>

        {/* System Settings */}
        <div className="card">
          <div className="flex items-center mb-4">
            <SettingsIcon className="h-5 w-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">System Settings</h3>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Auto-generate Daily Summaries</label>
                <p className="text-xs text-gray-500">Automatically generate summaries at specified time</p>
              </div>
              <input
                type="checkbox"
                checked={settings.autoGenerateSummaries}
                onChange={(e) => setSettings({...settings, autoGenerateSummaries: e.target.checked})}
                className="h-4 w-4 text-hummingbird-600 focus:ring-hummingbird-500 border-gray-300 rounded"
              />
            </div>

            {settings.autoGenerateSummaries && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Summary Generation Time
                </label>
                <input
                  type="time"
                  value={settings.summaryTime}
                  onChange={(e) => setSettings({...settings, summaryTime: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Data Retention (Days)
              </label>
              <input
                type="number"
                value={settings.dataRetentionDays}
                onChange={(e) => setSettings({...settings, dataRetentionDays: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">How long to keep visit data (0 = forever)</p>
            </div>
          </div>
        </div>

        {/* AI Settings */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Database className="h-5 w-5 text-purple-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">AI Settings</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confidence Threshold
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={settings.confidenceThreshold}
                onChange={(e) => setSettings({...settings, confidenceThreshold: parseFloat(e.target.value)})}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>0%</span>
                <span>{Math.round(settings.confidenceThreshold * 100)}%</span>
                <span>100%</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">Minimum confidence for bird identification</p>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Enable Bird Identification</label>
                <p className="text-xs text-gray-500">Use AI to identify individual birds</p>
              </div>
              <input
                type="checkbox"
                checked={settings.enableBirdIdentification}
                onChange={(e) => setSettings({...settings, enableBirdIdentification: e.target.checked})}
                className="h-4 w-4 text-hummingbird-600 focus:ring-hummingbird-500 border-gray-300 rounded"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Enable Weather Tracking</label>
                <p className="text-xs text-gray-500">Track weather conditions during visits</p>
              </div>
              <input
                type="checkbox"
                checked={settings.enableWeatherTracking}
                onChange={(e) => setSettings({...settings, enableWeatherTracking: e.target.checked})}
                className="h-4 w-4 text-hummingbird-600 focus:ring-hummingbird-500 border-gray-300 rounded"
              />
            </div>
          </div>
        </div>

        {/* Feeder Settings */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Bell className="h-5 w-5 text-green-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Feeder Settings</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Number of Feeders
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={settings.feederCount}
                onChange={(e) => setSettings({...settings, feederCount: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Feeder Locations
              </label>
              <div className="space-y-2">
                {Array.from({length: settings.feederCount}, (_, i) => (
                  <input
                    key={i}
                    type="text"
                    value={settings.feederLocations[i] || ''}
                    onChange={(e) => {
                      const newLocations = [...settings.feederLocations];
                      newLocations[i] = e.target.value;
                      setSettings({...settings, feederLocations: newLocations});
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hummingbird-500 focus:border-transparent"
                    placeholder={`Feeder ${i + 1} location`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
