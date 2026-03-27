import type { FileRecord } from '../types/FileRecords';
import apiClient from './apiClient';
import { supabase } from './supabaseClient';

export interface SubmitFilesRequest {
  linkToken: string;
  zipCode: string;
}

export interface AnalyzeFilesRequest {
  borrowerId: string;
}

const fileFacade = {
  uploadFile: async (file: File, zipCode: string, fileUUID: string, linkToken: string) => {
    // Path structure: borrowerId/fileName
    const filePath = `${fileUUID}/${zipCode}/${file.name}`;
    const { data, error } = await supabase.storage
      .from('documents')
      .upload(filePath, file);

    if (error) throw error;
    
    // Create record in files table
    const { error: dbError } = await supabase.from('files').insert({
      file_path: data.path,
      needs_to_be_processed: true,
      link_token: linkToken
    });

    if (dbError) throw dbError;

    return data;
  },

  submitFiles: async (data: SubmitFilesRequest) => {
    const response = await apiClient.post('/file/submit-files', data);
    return response.data;
  },

  analyzeFiles: async (data: AnalyzeFilesRequest) => {
    const response = await apiClient.post('/file/analyze-files', data);
    return response.data;
  },

  getFilesForBorrower: async (borrowerId: string) => {
    const response = await apiClient.get(`/file/borrower/${borrowerId}/files`);
    return response.data.files;
  },

  getSignedUrlsForFiles: async (files: FileRecord[]) => {
    const filePaths = files.map(file => file.filePath);
    const { data, error } = await supabase.storage
      .from('documents')
      .createSignedUrls(filePaths, 600); 

    if (error) {
      console.error('Error generating signed URLs:', error);
      throw error;
    }

    return data.map(item => item.signedUrl);
  }
};

export default fileFacade;
