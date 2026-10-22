import React, { useState } from 'react';
import { Card, SectionHeader } from './ui';
import { Bot, Send, Sparkles, Loader2 } from 'lucide-react';
import { sendQnAMessage } from '../services/api';

interface Message {
  sender: 'user' | 'ai';
  text: string;
}

interface AIAssistantWidgetProps {
  analysisId?: string;
  initialSummary?: string | null;
}

const QUICK_QUESTIONS = [
  'Perché mi consigli questo veicolo?',
  'Com\'è l\'autonomia in autostrada d\'inverno?',
  'Cosa succede se ricarico più alle colonnine?',
  'In quanti anni raggiungo il break-even?',
];

export const AIAssistantWidget: React.FC<AIAssistantWidgetProps> = ({ analysisId, initialSummary }) => {
  const [messages, setMessages] = useState<Message[]>(() => {
    if (initialSummary) {
      return [{ sender: 'ai', text: initialSummary }];
    }
    return [
      {
        sender: 'ai',
        text: 'Ciao! Sono il tuo Assistente EV. Fammi qualsiasi domanda sul confronto, sull\'autonomia o sui costi operativi della tua analisi.',
      },
    ];
  });
  const [input, setInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleSend = async (qText?: string) => {
    const question = qText || input.trim();
    if (!question || loading) return;

    setMessages((prev) => [...prev, { sender: 'user', text: question }]);
    if (!qText) setInput('');
    setLoading(true);

    try {
      const activeId = analysisId || 'demo-analysis-001';
      const res = await sendQnAMessage(activeId, question);
      setMessages((prev) => [...prev, { sender: 'ai', text: res.answer }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: 'Scusa, non sono riuscito a elaborare la risposta in questo momento. Per favore riprova.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="p-5 overflow-hidden border-primary/30">
      <SectionHeader
        icon={<Bot className="h-4 w-4 text-primary" />}
        title="Assistente EV Conversazionale (Q&A)"
        subtitle="Poni domande dirette sull'analisi generata per chiarire dubbi su risparmio, autonomia o ricarica."
      />

      <div className="mt-4 flex flex-col gap-3">
        {/* Messages Stream */}
        <div className="flex flex-col gap-2.5 max-h-80 overflow-y-auto rounded-xl border border-border bg-muted/20 p-3 text-xs leading-relaxed">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex gap-2 max-w-[85%] ${
                m.sender === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
              }`}
            >
              <div
                className={`grid h-6 w-6 shrink-0 place-items-center rounded-full ${
                  m.sender === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-emerald-600 text-white'
                }`}
              >
                {m.sender === 'user' ? 'Tu' : <Bot className="h-3.5 w-3.5" />}
              </div>
              <div
                className={`rounded-xl p-3 ${
                  m.sender === 'user'
                    ? 'bg-primary text-primary-foreground font-medium'
                    : 'bg-card border border-border text-foreground shadow-xs'
                }`}
              >
                {m.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex items-center gap-2 text-muted-foreground p-2">
              <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
              <span>L'Assistente EV sta elaborando la risposta…</span>
            </div>
          )}
        </div>

        {/* Quick Suggestion Pills */}
        <div className="flex flex-wrap items-center gap-1.5 pt-1">
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-1">
            <Sparkles className="h-3 w-3 text-amber-500" /> Domande rapide:
          </span>
          {QUICK_QUESTIONS.map((q, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSend(q)}
              disabled={loading}
              className="rounded-full border border-border bg-card px-2.5 py-1 text-[11px] font-medium text-foreground transition hover:bg-muted hover:border-primary/50 disabled:opacity-50"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Question Input */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2 pt-1"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Fai una domanda sull'analisi (es. 'Qual è l'autonomia invernale?')..."
            disabled={loading}
            className="flex-1 rounded-xl border border-border bg-background px-3.5 py-2 text-xs focus:border-primary focus:outline-hidden"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="btn-primary h-9 px-3.5 text-xs font-semibold shrink-0"
          >
            {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Send className="h-3.5 w-3.5" />}
            <span className="hidden sm:inline">Chiedi</span>
          </button>
        </form>
      </div>
    </Card>
  );
};

export default AIAssistantWidget;
