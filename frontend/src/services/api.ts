import axios from 'axios';
import { MessageTemplate, MessageLog, DashboardStats, ApiResponse } from '../types/api';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Message Templates
export const getTemplates = () => 
    api.get<ApiResponse<MessageTemplate[]>>('/templates');

export const getTemplate = (id: number) => 
    api.get<ApiResponse<MessageTemplate>>(`/templates/${id}`);

export const createTemplate = (template: Omit<MessageTemplate, 'id' | 'created_at' | 'updated_at'>) => 
    api.post<ApiResponse<MessageTemplate>>('/templates', template);

export const updateTemplate = (id: number, template: Partial<MessageTemplate>) => 
    api.put<ApiResponse<MessageTemplate>>(`/templates/${id}`, template);

export const deleteTemplate = (id: number) => 
    api.delete<ApiResponse<void>>(`/templates/${id}`);

// Message Logs
export const getMessageLogs = (page = 1, limit = 10) => 
    api.get<ApiResponse<MessageLog[]>>('/logs', { params: { page, limit } });

// Dashboard Stats
export const getDashboardStats = () => 
    api.get<ApiResponse<DashboardStats>>('/stats');

// Error Handler
api.interceptors.response.use(
    response => response,
    error => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
); 