import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import { Loader2, ArrowLeft, Award, FileText } from "lucide-react";
import ReactMarkdown from "react-markdown";

const API_URL = import.meta.env.VITE_API_URL;

export default function Summary() {
  const { sessionId } = useParams();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await axios.get(
          `${API_URL}/sessions/${sessionId}/summary`
        );
        setData(res.data);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    };

    fetchSummary();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center text-gray-500">
          <Loader2 className="h-8 w-8 animate-spin mb-4 text-black" />
          <p>AI is evaluating your interview performance...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-8 text-center text-red-500">
        Failed to load summary.
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Interview Results
            </h1>

            <p className="text-gray-500 mt-1">
              Candidate:{" "}
              <span className="font-medium text-gray-900">
                {data.candidate_name}
              </span>{" "}
              | Role:{" "}
              <span className="font-medium text-gray-900">
                {data.role}
              </span>
            </p>
          </div>

          <Link
            to="/"
            className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-black transition-colors"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Home
          </Link>
        </div>

        <div className="bg-white rounded-3xl p-8 shadow-sm border border-gray-200">
          <div className="flex items-center space-x-3 mb-6 border-b border-gray-100 pb-4">
            <div className="p-2 bg-blue-50 text-blue-600 rounded-xl">
              <Award size={24} />
            </div>

            <h2 className="text-xl font-semibold text-gray-900">
              AI Evaluation
            </h2>
          </div>

          <div className="prose prose-blue max-w-none text-gray-700">
            <ReactMarkdown>{data.analysis}</ReactMarkdown>
          </div>
        </div>

        <div className="bg-white rounded-3xl p-8 shadow-sm border border-gray-200">
          <div className="flex items-center space-x-3 mb-6 border-b border-gray-100 pb-4">
            <div className="p-2 bg-gray-50 text-gray-600 rounded-xl">
              <FileText size={24} />
            </div>

            <h2 className="text-xl font-semibold text-gray-900">
              Session Transcript
            </h2>
          </div>

          <div className="space-y-8">
            {data.qa_pairs.map((qa: any, index: number) => (
              <div key={index} className="space-y-3">

                <div className="flex space-x-3">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-black text-white flex items-center justify-center text-sm font-bold">
                    Q{index + 1}
                  </span>

                  <div className="pt-1 text-gray-900 font-medium">
                    {qa.question}
                  </div>
                </div>

                <div className="flex space-x-3">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 text-gray-500 flex items-center justify-center text-sm font-bold">
                    A
                  </span>

                  <div className="pt-1 text-gray-600 bg-gray-50 p-4 rounded-2xl rounded-tl-none border border-gray-100 w-full">
                    {qa.answer}
                  </div>
                </div>

              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}