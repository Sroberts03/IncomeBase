import type { BorrowerDetails } from "./BorrowerDetails";


export default function LinkEmail(borrowerDetails: BorrowerDetails, token: string, lenderName: string = 'Your Lender') {
    const baseUrl = import.meta.env.VITE_BASE_URL || '';
    const portalLink = token ? `${baseUrl}/upload/${token}` : 'Upload link not available';

    return [
        `Hi ${borrowerDetails.fullName || 'there'},`,
        "",
        "We are currently working on your loan application and are excited to get it across the finish line! To keep the process moving forward, we just need a few additional documents from you:",
        "",
        "\t- Recent pay stubs (covering the last 30 days)",
        "\t- Bank statements (all pages for the last 60 days)",
        "\t- A copy of your government-issued ID (Driver's License or Passport)",
        "",
        "The fastest and most secure way to provide these is by uploading them through your personal document portal:",
        "",
        portalLink,
        "",
        "This link will expire in 7 days, so please upload the documents at your earliest convenience.",
        "",
        "If you have any questions or need assistance with the upload process, feel free to reply to this email or contact our support team.",
        "",
        "Best regards,",
        "",
        lenderName,
        "[Your Position]",
        "[Company Name]"
    ].join('\n');
}