export interface FileRecord {
    id: string;
    borrowerId: string;
    filePath: string;
    classification: FileClassification | null;
    source: FileSource | null;
    fileName: string;
    needsToBeProcessed: boolean;
    createdAt: string;
    linkToken: string;
}

export type FileClassification = 'w2' | '1099' | 'bank_statement' | 'Institution Report' | 'other';
export type FileSource = 'stripe' | 'plaid' | 'shopify' | 'paypal' | 'amazon_seller' | 'upwork/fiverr' | 'bank' | 'other';