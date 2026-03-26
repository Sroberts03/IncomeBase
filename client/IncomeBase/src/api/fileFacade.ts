import apiClient from './apiClient';
import { supabase } from './supabaseClient';

export interface SubmitFilesRequest {
  link_token: string;
  zip_code: string;
}

export interface AnalyzeFilesRequest {
  borrower_id: string;
}

const fileFacade = {
  uploadFile: async (borrowerId: string, file: File) => {
    // Path structure: borrower_id/file_name
    const filePath = `${borrowerId}/${file.name}`;
    const { data, error } = await supabase.storage
      .from('borrower-files')
      .upload(filePath, file, {
        upsert: true,
      });

    if (error) throw error;
    
    // Create record in files table
    const { error: dbError } = await supabase.from('files').insert({
      borrower_id: borrowerId,
      file_path: data.path,
      file_name: file.name,
      needs_to_be_processed: true,
    });

    if (dbError) throw dbError;

    return data;
  },

  submitFiles: async (data: SubmitFilesRequest) => {
    const response = await apiClient.post('/file/submit_files', data);
    return response.data;
  },

  analyzeFiles: async (data: AnalyzeFilesRequest) => {
    const response = await apiClient.post('/file/analyze_files', data);
    return response.data;
  },
};

export default fileFacade;
