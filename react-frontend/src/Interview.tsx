import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { Send, User, Bot, Loader2, CheckCircle } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL;

export default function Interview() {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  const [currentQuestion, setCurrentQuestion] = useState<any>(null);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [questionCount, setQuestionCount] = useState(1);
  const [finished, setFinished] = useState(false);

  useEffect(() => {
    const fetchQuestion = async () => {
      try {
        const res = await axios.post(
          `${API_URL}/sessions/${sessionId}/next_question`
        );

        setCurrentQuestion(res.data);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setLoading(false);
      }
    };

    fetchQuestion();
  }, [sessionId]);

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) return;

    setSubmitting(true);

    try {
      await axios.post(
        `${API_URL}/qa/${currentQuestion.id}/answer`,
        { answer }
      );

      if (questionCount >= 5) {
        setFinished(true);

        setTimeout(() => {
          navigate(`/summary/${sessionId}`);
        }, 1500);

        return;
      }

      setAnswer("");

      const res = await axios.post(
        `${API_URL}/sessions/${sessionId}/next_question`
      );

      setCurrentQuestion(res.data);
      setQuestionCount((prev) => prev + 1);
    } catch (err) {
      console.error(err);
    }

    setSubmitting(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center text-gray-500">
          <Loader2 className="h-8 w-8 animate-spin mb-4 text-black" />
          <p>Analyzing technical requirements...</p>
        </div>
      </div>
    );
  }

  if (finished) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center text-gray-900">
          <CheckCircle className="h-12 w-12 text-green-500 mb-4" />
          <h2 className="text-2xl font-semibold">
            Interview Complete
          </h2>
          <p className="text-gray-500 mt-2">
            Generating your evaluation summary...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      <div className="w-full md:w-1/2 bg-gray-50 border-r border-gray-200 p-8 flex flex-col justify-center">
        <div className="max-w-lg mx-auto w-full space-y-6">
          <div className="flex items-center space-x-3 text-sm font-medium text-gray-500 uppercase tracking-wider">
            <Bot size={20} className="text-blue-600" />
            <span>Question {questionCount} of 5</span>
          </div>

          <h2 className="text-2xl md:text-3xl font-semibold leading-relaxed text-gray-900">
            {currentQuestion?.question_text || "Loading question..."}
          </h2>

          <div className="p-4 bg-blue-50 border border-blue-100 rounded-2xl text-sm text-blue-800 leading-relaxed">
            Take your time to formulate a structured answer. Focus on your
            technical reasoning and trade-offs.
          </div>
        </div>
      </div>

      <div className="w-full md:w-1/2 bg-white p-8 flex flex-col">
        <div className="max-w-lg mx-auto w-full flex-1 flex flex-col h-full">
          <div className="flex items-center space-x-3 text-sm font-medium text-gray-500 mb-4">
            <User size={20} className="text-gray-400" />
            <span>Your Response</span>
          </div>

          <textarea
            className="flex-1 w-full p-6 border border-gray-200 rounded-3xl focus:ring-2 focus:ring-black focus:border-transparent outline-none resize-none transition-all text-gray-800 text-lg leading-relaxed shadow-inner bg-gray-50"
            placeholder="Type your technical answer here..."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
          />

          <div className="mt-6 flex justify-end">
            <button
              onClick={handleSubmitAnswer}
              disabled={submitting || !answer.trim()}
              className="inline-flex items-center px-8 py-4 border border-transparent rounded-2xl shadow-sm text-base font-medium text-white bg-black hover:bg-gray-800 focus:outline-none transition-all disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <Loader2 className="animate-spin -ml-1 mr-2 h-5 w-5" />
                  Evaluating...
                </>
              ) : (
                <>
                  Submit Answer
                  <Send className="ml-2 h-5 w-5" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}