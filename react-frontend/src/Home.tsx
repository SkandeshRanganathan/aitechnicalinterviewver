import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Upload, Briefcase, User, ArrowRight, Loader2 } from "lucide-react";

export default function Home() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !name || !role) {
      setError("Please fill out all fields and upload a resume.");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("candidate_name", name);
    formData.append("target_role", role);
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/upload_resume", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      
      const sessionId = res.data.id;
      
      await axios.post(`http://localhost:8000/sessions/${sessionId}/next_question`);
      
      navigate(`/interview/${sessionId}`);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to start interview. Is the backend running?");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-black text-white mb-6 shadow-xl">
            <Briefcase size={32} />
          </div>
          <h1 className="text-3xl font-bold tracking-tight mb-2 text-gray-900">Technical Interview</h1>
          <p className="text-gray-500">AI-powered role-based candidate screening</p>
        </div>

        <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-200">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-3 bg-red-50 text-red-700 text-sm rounded-xl border border-red-100">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Candidate Name</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  className="block w-full pl-10 pr-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-black focus:border-transparent outline-none transition-all text-black"
                  placeholder="John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Target Role</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Briefcase className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  className="block w-full pl-10 pr-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-black focus:border-transparent outline-none transition-all text-black"
                  placeholder="e.g. Backend Engineer, AI/ML"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Upload Resume (PDF)</label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-200 border-dashed rounded-xl hover:border-gray-300 transition-colors bg-gray-50">
                <div className="space-y-1 text-center">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="flex text-sm text-gray-600 justify-center">
                    <label className="relative cursor-pointer bg-transparent rounded-md font-medium text-black hover:text-gray-700 focus-within:outline-none">
                      <span>{file ? file.name : "Upload a file"}</span>
                      <input 
                        type="file" 
                        className="sr-only" 
                        accept=".pdf"
                        onChange={(e) => setFile(e.target.files?.[0] || null)}
                        required
                      />
                    </label>
                  </div>
                  <p className="text-xs text-gray-500">PDF up to 10MB</p>
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800 focus:outline-none transition-all disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin -ml-1 mr-2 h-5 w-5" />
                  Processing...
                </>
              ) : (
                <>
                  Start Assessment
                  <ArrowRight className="ml-2 h-5 w-5" />
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
