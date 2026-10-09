import { describe, it, expect } from 'vitest';
import { RecommendationRating } from '../types/api';

describe('Frontend Data Models & Enum Integrity', () => {
  it('should validate recommendation enum values', () => {
    expect(RecommendationRating.STRONG_BUY).toBe('STRONG_BUY');
    expect(RecommendationRating.BUY).toBe('BUY');
    expect(RecommendationRating.MAYBE).toBe('MAYBE');
    expect(RecommendationRating.KEEP_CURRENT).toBe('KEEP_CURRENT');
    expect(RecommendationRating.AVOID).toBe('AVOID');
  });
});
