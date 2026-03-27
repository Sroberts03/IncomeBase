import { 
  Link, 
  ShieldCheck, 
  UploadCloud, 
  Bell, 
  BarChart3, 
  ChevronRight 
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans selection:bg-blue-100">
      {/* Hero Section */}
      <header className="max-w-7xl mx-auto px-6 pt-16 pb-24 text-center lg:text-left grid lg:grid-cols-2 gap-16 items-center">
        <div>
          <h1 className="text-5xl lg:text-7xl font-extrabold leading-[1.1] text-slate-900 mb-6">
            The 30-second <br />
            <span className="text-blue-600">Verification Hook.</span>
          </h1>
          <p className="text-xl text-slate-500 mb-10 max-w-lg mx-auto lg:mx-0 leading-relaxed">
            Send a secure link, verify identity via ZIP/SSN, and get instant income insights. The most seamless pipeline from Lender to Borrower.
          </p>
          <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 justify-center lg:justify-start">
            <button className="bg-blue-600 text-white px-8 py-4 rounded-2xl font-bold text-lg hover:bg-blue-700 transition-all transform hover:-translate-y-1 shadow-xl shadow-blue-600/20 flex items-center justify-center">
              Create First Borrower <ChevronRight className="ml-2 h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Workflow Visualizer */}
        <div className="relative bg-slate-50 rounded-[2.5rem] p-8 border border-slate-100 shadow-inner">
          <div className="space-y-4">
            <WorkflowStep 
              active 
              icon={<Link className="text-blue-600" />} 
              label="Lender creates secure upload link" 
            />
            <WorkflowStep 
              icon={<ShieldCheck className="text-slate-400" />} 
              label="Borrower verifies via ZIP or Last 4 SSN" 
            />
            <WorkflowStep 
              icon={<UploadCloud className="text-slate-400" />} 
              label="Instant document classification & feedback" 
            />
            <div className="h-4 border-l-2 border-dashed border-slate-200 ml-6 my-2"></div>
            <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="bg-green-100 p-2 rounded-lg"><BarChart3 className="text-green-600 h-5 w-5" /></div>
                <span className="font-bold text-sm">Underwriter Analysis Ready</span>
              </div>
              <span className="text-[10px] font-bold bg-green-50 text-green-700 px-2 py-1 rounded">READY</span>
            </div>
          </div>
        </div>
      </header>

      {/* The "Correct" 3-Step Process Section */}
      <section id="workflow" className="bg-slate-900 py-24 text-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="mb-16">
            <h2 className="text-3xl font-bold mb-4">A Unified Pipeline</h2>
            <p className="text-slate-400">From the first link to the final underwriter review.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-12">
            <Feature 
              number="01"
              title="Identity Gate"
              desc="Borrowers join your link and must verify their location (ZIP) or identity (SSN) before uploading a single file."
            />
            <Feature 
              number="02"
              title="Smart Feedback"
              desc="As borrowers upload, IncomeBase classifies documents in real-time. If they miss a page, they know instantly."
            />
            <Feature 
              number="03"
              title="Final Analysis"
              desc="Underwriters are notified the second a folder is complete. Review, click 'Analyze', and get instant income insights."
            />
          </div>
        </div>
      </section>

      {/* Trust/Notification Hook */}
      <section className="py-20 max-w-4xl mx-auto text-center px-6">
        <div className="bg-blue-50 p-10 rounded-[3rem] border border-blue-100">
          <Bell className="h-12 w-12 text-blue-600 mx-auto mb-6" />
          <h2 className="text-3xl font-extrabold text-slate-900 mb-4">Never chase a document again.</h2>
          <p className="text-slate-600 mb-8 max-w-md mx-auto">
            Get notified via email or dashboard the moment a borrower completes their upload. One-click analysis starts your review.
          </p>
          <button className="text-blue-600 font-bold hover:underline">Explore the Underwriter Dashboard &rarr;</button>
        </div>
      </section>
    </div>
  );
};

type WorkflowStepProps = {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
};

const WorkflowStep = ({ icon, label, active = false }: WorkflowStepProps) => (
  <div className={`flex items-center space-x-4 p-4 rounded-2xl transition ${active ? 'bg-white shadow-md border border-slate-100' : 'opacity-50'}`}>
    <div className={`p-2.5 rounded-xl ${active ? 'bg-blue-50' : 'bg-slate-200'}`}>
      {icon}
    </div>
    <span className={`text-sm font-semibold ${active ? 'text-slate-900' : 'text-slate-500'}`}>{label}</span>
  </div>
);

type FeatureProps = {
  number: string;
  title: string;
  desc: string;
};

const Feature = ({ number, title, desc }: FeatureProps) => (
  <div className="group">
    <div className="text-5xl font-black text-slate-800 group-hover:text-blue-500 transition-colors mb-4">{number}</div>
    <h3 className="text-xl font-bold mb-3">{title}</h3>
    <p className="text-slate-400 leading-relaxed text-sm">{desc}</p>
  </div>
);