"use client";

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@supabase/supabase-js';

// Types
export interface AIAnalysisRequest {
  analysis_type: 'crop_health' | 'irrigation' | 'yield_prediction' | 'pest_risk';
  time_range_days?: number;
  include_weather?: boolean;
  include_ndvi?: boolean;
  custom_parameters?: Record<string, any>;
}

export interface AIAnalysisJob {
  analysis_id: string;
  analysis_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  estimated_completion?: string;
  created_at: string;
}

export interface AIRecommendation {
  id: string;
  device_id: string;
  analysis_type: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  action_items: string[];
  confidence_score: number;
  created_at: string;
  expires_at?: string;
  metadata?: Record<string, any>;
}

export interface AIAnalysisResult {
  analysis_id: string;
  device_id: string;
  analysis_type: string;
  status: 'completed' | 'failed';
  results: {
    summary: string;
    insights: string[];
    recommendations: AIRecommendation[];
    risk_factors: Array<{
      factor: string;
      severity: 'low' | 'medium' | 'high' | 'critical';
      description: string;
    }>;
    performance_metrics?: {
      crop_health_score?: number;
      irrigation_efficiency?: number;
      yield_potential?: number;
      pest_risk_level?: number;
    };
    charts?: Array<{
      type: string;
      title: string;
      data: any;
    }>;
  };
  created_at: string;
  completed_at?: string;
}

export function useKataraAI() {
  const [analysisJobs, setAnalysisJobs] = useState<AIAnalysisJob[]>([]);
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [analysisResults, setAnalysisResults] = useState<AIAnalysisResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize Supabase client
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  // Start AI analysis
  const startAnalysis = useCallback(async (deviceId: string, request: AIAnalysisRequest): Promise<AIAnalysisJob> => {
    try {
      setError(null);
      
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`/api/katara/analyze/${deviceId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.error?.message || 'Failed to start AI analysis');
      }

      const job = await response.json();
      setAnalysisJobs(prev => [...prev, job]);
      return job;
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('AI analysis start error:', err);
      throw new Error(errorMessage);
    }
  }, [supabase]);

  // Get AI recommendations for device
  const getRecommendations = useCallback(async (deviceId: string, startDate?: string, endDate?: string): Promise<AIRecommendation[]> => {
    try {
      setError(null);
      
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response = await fetch(`/api/katara/recommendations/${deviceId}?${params}`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.error?.message || 'Failed to fetch AI recommendations');
      }

      const data = await response.json();
      const recs = data.recommendations || [];
      setRecommendations(recs);
      return recs;
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('AI recommendations fetch error:', err);
      return [];
    }
  }, [supabase]);

  // Check analysis job status
  const checkJobStatus = useCallback(async (jobId: string): Promise<AIAnalysisJob | null> => {
    try {
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`/api/katara/analysis/${jobId}/status`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        return null;
      }

      const job = await response.json();
      
      // Update job in state
      setAnalysisJobs(prev => prev.map(j => j.analysis_id === jobId ? job : j));
      
      // If completed, fetch the results
      if (job.status === 'completed') {
        fetchAnalysisResults(job.analysis_id);
      }
      
      return job;
      
    } catch (err) {
      console.error('Job status check error:', err);
      return null;
    }
  }, [supabase]);

  // Fetch analysis results
  const fetchAnalysisResults = useCallback(async (analysisId: string): Promise<AIAnalysisResult | null> => {
    try {
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`/api/katara/analysis/${analysisId}/results`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        return null;
      }

      const result = await response.json();
      setAnalysisResults(prev => [...prev, result]);
      return result;
      
    } catch (err) {
      console.error('Analysis results fetch error:', err);
      return null;
    }
  }, [supabase]);

  // Get all analysis jobs for current user
  const getUserAnalysisJobs = useCallback(async (): Promise<AIAnalysisJob[]> => {
    try {
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const response = await fetch('/api/katara/analysis/jobs', {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        return [];
      }

      const data = await response.json();
      setAnalysisJobs(data.jobs || []);
      return data.jobs || [];
      
    } catch (err) {
      console.error('User analysis jobs fetch error:', err);
      return [];
    }
  }, [supabase]);

  // Cancel analysis job
  const cancelAnalysis = useCallback(async (jobId: string): Promise<void> => {
    try {
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`/api/katara/analysis/${jobId}/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.error?.message || 'Failed to cancel analysis');
      }

      // Update job status in state
      setAnalysisJobs(prev => prev.map(job => 
        job.analysis_id === jobId ? { ...job, status: 'failed' } : job
      ));
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Analysis cancel error:', err);
      throw new Error(errorMessage);
    }
  }, [supabase]);

  // Clear data
  const clearData = useCallback(() => {
    setAnalysisJobs([]);
    setRecommendations([]);
    setAnalysisResults([]);
    setError(null);
  }, []);

  return {
    analysisJobs,
    recommendations,
    analysisResults,
    loading,
    error,
    startAnalysis,
    getRecommendations,
    checkJobStatus,
    fetchAnalysisResults,
    getUserAnalysisJobs,
    cancelAnalysis,
    clearData,
  };
}
