export interface BorrowerDetails {
  borrowerId: string;
  fullName: string;
  email: string;
  zipCode: string;
  status: string;
  createdAt: string;
  updatedAt: string;
  analysis?: BorrowerAnalysis;
  documentLink?: string;
}

export type IncomeTrend =
  | "Increasing"
  | "Stable"
  | "Declining"
  | "Volatile";

export type DepositSource =
  | "stripe"
  | "plaid"
  | "shopify"
  | "paypal"
  | "amazon_seller"
  | "upwork/fiverr"
  | "bank"
  | "other";

export interface MonthlyPoint {
    year: number;
    month: string;
    income: number;
}

export interface BorrowerAnalysis {
    monthlyAverageIncome: number;
    incomeStabilityScore: number;
    recurringIncomePercentage: number;
    incomeTrend: IncomeTrend;
    largestDepositSource: DepositSource;
    expenseToIncomeRatio: number;
    netBurnRate: number;
    
    incomeYtd: MonthlyPoint[] 
    incomeLast6: MonthlyPoint[] 
    incomeLast12: MonthlyPoint[] 
    incomeLast24: MonthlyPoint[] 

    nsfCountTotal: number;
    riskFactors: string[];
    anomalousDeposits: string[]; 
    confidenceScore: number; 
    analysisSummary: string; 
}
