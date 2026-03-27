 import apiClient from './apiClient';

export interface CreateBorrowerRequest {
  fullName: string;
  email: string;
  zipCode: string;
}

export interface GenerateLinkRequest {
  borrowerId: string;
}

export interface VerifyZipRequest {
  linkToken: string;
  zipCode: string;
}

const lenderFacade = {
  createBorrower: async (data: CreateBorrowerRequest) => {
    console.log(data);
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
