import { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, X, Bot, User as UserIcon, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import useAppStore from '../store/useAppStore';
import { chatWithAgent } from '../api/client';

export default function ChatAssistant() {
  const { analysisResult, updateReviewItem } = useAppStore();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', text: "Hi! I'm your AI career assistant. How can I help refine your resume?" }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Don't show chat until analysis is done
  if (!analysisResult) return null;

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isTyping) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setIsTyping(true);

    try {
      const resumeContext = analysisResult.sections ? 
        Object.values(analysisResult.sections).join('\n') : analysisResult.raw_text;
      
      const res = await chatWithAgent(
        userMsg, 
        resumeContext, 
        analysisResult.jd_data?.raw_text || ""
      );

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        text: res.response || "Something went wrong.",
        updatedSection: res.updated_section
      }]);

      // If the AI updated a section, apply it back to the review items
      if (res.updated_section && res.updated_content) {
        updateReviewItem(res.updated_section, { 
          edited_content: res.updated_content, 
          status: 'edited' 
        });
      }

    } catch {
      setMessages(prev => [...prev, { role: 'assistant', text: "Sorry, I encountered an error connecting to the backend." }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-tr from-indigo-600 to-cyan-500 rounded-full flex items-center justify-center text-white shadow-xl hover:shadow-cyan-500/30 transition-transform hover:scale-105 active:scale-95 z-40"
          >
            <MessageSquare className="w-6 h-6" />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-6 right-6 w-80 sm:w-96 h-[500px] max-h-[80vh] bg-slate-900 border border-slate-700/50 rounded-2xl shadow-2xl flex flex-col overflow-hidden z-50 glass-panel"
          >
            {/* Header */}
            <div className="bg-slate-800/80 p-4 border-b border-slate-700/50 flex justify-between items-center z-10">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-indigo-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-200">AI Assistant</h3>
                  <p className="text-xs text-slate-400">Online</p>
                </div>
              </div>
              <button 
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`flex gap-2 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                    <div className={`w-6 h-6 rounded-full flex-shrink-0 flex items-center justify-center mt-1 ${
                      msg.role === 'user' ? 'bg-cyan-500/20 text-cyan-400' : 'bg-indigo-500/20 text-indigo-400'
                    }`}>
                      {msg.role === 'user' ? <UserIcon className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                    </div>
                    <div className={`p-3 rounded-2xl text-sm whitespace-pre-wrap ${
                      msg.role === 'user' 
                        ? 'bg-cyan-600/90 text-white rounded-tr-none' 
                        : 'bg-slate-800 border border-slate-700 text-slate-200 rounded-tl-none'
                    }`}>
                      {msg.text}
                      {msg.updatedSection && (
                        <div className="mt-2 text-xs font-medium text-cyan-400 bg-cyan-400/10 inline-block px-2 py-1 rounded">
                          Updated: {msg.updatedSection}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div className="flex justify-start">
                  <div className="flex gap-2">
                    <div className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center mt-1">
                      <Bot className="w-3.5 h-3.5 text-indigo-400" />
                    </div>
                    <div className="p-3 rounded-2xl bg-slate-800 border border-slate-700 rounded-tl-none flex items-center gap-1.5">
                      <div className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce"></div>
                      <div className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                      <div className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <form onSubmit={handleSend} className="p-3 bg-slate-800/80 border-t border-slate-700/50 flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask to refine sections..."
                className="flex-1 bg-slate-900 border border-slate-600 rounded-xl px-3 py-2 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-500/50 focus:ring-1 ring-cyan-500/50"
              />
              <button
                type="submit"
                disabled={!input.trim() || isTyping}
                className="p-2 bg-gradient-to-tr from-indigo-500 to-cyan-500 text-white rounded-xl disabled:opacity-50 flex items-center justify-center transition-transform active:scale-95"
              >
                {isTyping ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
