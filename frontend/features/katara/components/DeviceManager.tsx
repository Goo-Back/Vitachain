"use client";

import React, { useState } from 'react';
import { useKataraDevices, KataraDevice, DeviceCreateRequest, DeviceUpdateRequest } from '@/hooks/useKataraDevices';

interface DeviceManagerProps {
  onDeviceSelect?: (device: KataraDevice) => void;
}

export default function DeviceManager({ onDeviceSelect }: DeviceManagerProps) {
  const { devices, loading, error, fetchDevices, createDevice, updateDevice, deleteDevice } = useKataraDevices();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingDevice, setEditingDevice] = useState<KataraDevice | null>(null);
  const [formData, setFormData] = useState<DeviceCreateRequest>({
    name: '',
    location_lat: 0,
    location_lng: 0,
  });
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    try {
      if (editingDevice) {
        await updateDevice(editingDevice.id, formData);
        setEditingDevice(null);
      } else {
        await createDevice(formData);
        setShowCreateForm(false);
      }
      
      setFormData({ name: '', location_lat: 0, location_lng: 0 });
      fetchDevices();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Operation failed');
    }
  };

  const handleEdit = (device: KataraDevice) => {
    setEditingDevice(device);
    setFormData({
      name: device.name || '',
      location_lat: device.location_lat || 0,
      location_lng: device.location_lng || 0,
    });
    setShowCreateForm(true);
  };

  const handleDelete = async (deviceId: string) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cet appareil ?')) {
      try {
        await deleteDevice(deviceId);
        fetchDevices();
      } catch (err) {
        setFormError(err instanceof Error ? err.message : 'Delete failed');
      }
    }
  };

  const handleCancel = () => {
    setShowCreateForm(false);
    setEditingDevice(null);
    setFormData({ name: '', location_lat: 0, location_lng: 0 });
    setFormError(null);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-100 text-green-800';
      case 'offline':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'online':
        return 'Actif';
      case 'offline':
        return 'Inactif';
      default:
        return 'Inconnu';
    }
  };

  if (loading && devices.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Gestion des Appareils</h2>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="p-3 border rounded animate-pulse">
              <div className="h-5 bg-gray-200 rounded mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">Gestion des Appareils</h2>
        <button
          onClick={() => setShowCreateForm(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          + Ajouter un Appareil
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
          Erreur: {error}
        </div>
      )}

      {formError && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
          {formError}
        </div>
      )}

      {showCreateForm && (
        <div className="mb-6 p-4 border rounded-lg bg-gray-50">
          <h3 className="text-lg font-medium mb-4">
            {editingDevice ? 'Modifier l\'Appareil' : 'Ajouter un Nouvel Appareil'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom de l'appareil
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Latitude
                </label>
                <input
                  type="number"
                  step="any"
                  value={formData.location_lat}
                  onChange={(e) => setFormData({ ...formData, location_lat: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Longitude
                </label>
                <input
                  type="number"
                  step="any"
                  value={formData.location_lng}
                  onChange={(e) => setFormData({ ...formData, location_lng: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>
            <div className="flex space-x-3">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                {editingDevice ? 'Mettre à Jour' : 'Créer'}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Annuler
              </button>
            </div>
          </form>
        </div>
      )}

      {devices.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">📡</div>
          <p>Aucun appareil enregistré</p>
          <p className="text-sm mt-2">Ajoutez votre premier appareil ESP32 pour commencer</p>
        </div>
      ) : (
        <div className="space-y-3">
          {devices.map((device) => (
            <div
              key={device.id}
              className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <div className="font-medium text-gray-900">
                    {device.name || `Appareil ${device.device_id.slice(-8)}`}
                  </div>
                  <div className="text-sm text-gray-500">
                    ID: {device.device_id}
                  </div>
                  {device.location_lat && device.location_lng && (
                    <div className="text-xs text-gray-400 mt-1">
                      📍 {device.location_lat.toFixed(4)}, {device.location_lng.toFixed(4)}
                    </div>
                  )}
                  <div className="text-xs text-gray-400 mt-1">
                    Créé: {new Date(device.created_at).toLocaleDateString('fr-FR')}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(device.status)}`}>
                    {getStatusText(device.status)}
                  </span>
                </div>
              </div>
              
              <div className="flex space-x-2 mt-3">
                <button
                  onClick={() => onDeviceSelect?.(device)}
                  className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                >
                  Voir
                </button>
                <button
                  onClick={() => handleEdit(device)}
                  className="px-3 py-1 text-sm bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200 transition-colors"
                >
                  Modifier
                </button>
                <button
                  onClick={() => handleDelete(device.id)}
                  className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
                >
                  Supprimer
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
