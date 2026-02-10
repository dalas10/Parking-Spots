import apiClient from './api';

export interface PaymentIntent {
  client_secret: string;
  payment_intent_id: string;
  amount: number;
  currency: string;
}

export interface PaymentRecord {
  id: string;
  booking_id: string;
  amount: number;
  currency: string;
  status: string;
  payment_method?: string;
  last_four?: string;
  card_brand?: string;
  created_at: string;
}

export interface PayoutSummary {
  total_earnings: number;
  pending_payouts: number;
  completed_payouts: number;
  this_month_earnings: number;
}

export const paymentService = {
  async createPaymentIntent(bookingId: string): Promise<PaymentIntent> {
    const response = await apiClient.post<PaymentIntent>('/payments/create-payment-intent', {
      booking_id: bookingId,
    });
    return response.data;
  },

  async confirmPayment(paymentIntentId: string): Promise<{ message: string; status: string }> {
    const response = await apiClient.post<{ message: string; status: string }>(
      '/payments/confirm-payment',
      null,
      { params: { payment_intent_id: paymentIntentId } }
    );
    return response.data;
  },

  async requestRefund(
    paymentId: string,
    amount?: number,
    reason?: string
  ): Promise<any> {
    const response = await apiClient.post('/payments/refund', {
      payment_id: paymentId,
      amount,
      reason,
    });
    return response.data;
  },

  async getMyPayments(): Promise<PaymentRecord[]> {
    const response = await apiClient.get<PaymentRecord[]>('/payments/my-payments');
    return response.data;
  },

  async getOwnerPayouts(): Promise<any[]> {
    const response = await apiClient.get<any[]>('/payments/owner/payouts');
    return response.data;
  },

  async getPayoutSummary(): Promise<PayoutSummary> {
    const response = await apiClient.get<PayoutSummary>('/payments/owner/summary');
    return response.data;
  },

  async createConnectAccount(country: string = 'US'): Promise<{ account_id: string; onboarding_url: string }> {
    const response = await apiClient.post<{ account_id: string; onboarding_url: string }>(
      '/payments/connect/create-account',
      { country, business_type: 'individual' }
    );
    return response.data;
  },
};
