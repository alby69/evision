import { describe, it, expect, vi } from 'vitest';
import { fetchAIExplain, sendQnAMessage } from '../services/api';

describe('AI Assistant & Service Integration', () => {
  it('should fetch AI explain response correctly from API', async () => {
    const mockSummary = { ai_summary: 'Analisi eccellente con grande risparmio.' };
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockSummary,
      }),
    );

    const result = await fetchAIExplain('demo-analysis-001');
    expect(result.ai_summary).toBe('Analisi eccellente con grande risparmio.');
  });

  it('should send QnA message and receive answer', async () => {
    const mockAnswer = { answer: 'L\'autonomia autostradale d\'inverno è di 210 km.' };
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockAnswer,
      }),
    );

    const result = await sendQnAMessage('demo-analysis-001', 'Qual è l\'autonomia in autostrada?');
    expect(result.answer).toContain('210 km');
  });
});
