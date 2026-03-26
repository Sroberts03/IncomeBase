 import apiClient from './apiClient';

export interface CreateBorrowerRequest {
  full_name: string;
  email: string;
  zip_code: string;
}

export interface GenerateLinkRequest {
  borrower_id: string;
}

export interface VerifyZipRequest {
  link_token: string;
  zip_code: string;
}

const lenderFacade = {
  createBorrower: async (data: CreateBorrowerRequest) => {
    const response = await apiClient.post('/lender/create-borrower', data);
    return response.data;
  },

  generateLink: async (data: GenerateLinkRequest) => {
    const response = await apiClient.post('/lender/generate-link', data);
    return response.data;
  },

  verifyZip: async (data: VerifyZipRequest) => {
    const response = await apiClient.post('/lender/verify-zip', data);
    return response.data;
  },

  getDashboardStats: async () => {
    const response = await apiClient.get('/lender/dashboard-stats');
    return response.data;
  },

  getBorrowers: async () => {
    const response = await apiClient.get('/lender/borrowers');
    return response.data;
  },
};

export default lenderFacade;
