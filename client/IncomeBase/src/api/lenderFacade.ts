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

export interface SendEmailRequest {
  borrowerId: string;
  token: string;
  subject: string;
  htmlContent: string;
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

  getBorrowerDetails: async (borrowerId: string) => {
    const response = await apiClient.get(`/lender/borrower/${borrowerId}`);
    return response.data;
  },

  getLenderInfo: async () => {
    const response = await apiClient.get('/lender/info');
    return response.data;
  },

  sendEmail: async (data: SendEmailRequest) => {
    // We map camelCase (htmlContent, borrowerId) to snake_case on the backend using the python pydantic alias generator
    // apiClient already sends JSON correctly
    const response = await apiClient.post('/lender/send-email', data);
    return response.data;
  }
};

export default lenderFacade;
