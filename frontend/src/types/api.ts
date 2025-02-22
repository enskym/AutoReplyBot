export interface MessageTemplate {
    id: number;
    trigger_text: string;
    response_text: string;
    is_active: boolean;
    created_at: string;
    updated_at?: string;
}

export interface MessageLog {
    id: number;
    user_id: string;
    incoming_message: string;
    response_message: string;
    template_id?: number;
    created_at: string;
}

export interface DashboardStats {
    total_messages: number;
    active_templates: number;
    response_rate: number;
    recent_messages: MessageLog[];
}

export interface ApiResponse<T> {
    data: T;
    success: boolean;
    message?: string;
} 