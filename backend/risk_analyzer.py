import re

class RiskAnalyzer:
    def __init__(self):
        self.patterns = {
            'data_resale': {
                'regex': r'\b(sell|monetize|share.*with.*affiliates|third[\s-]?party.*marketing|commercial.*purposes)\b',
                'weight': 25
            },
            'biometric': {
                'regex': r'\b(biometric|fingerprint|facial.*recognition|face.*scan|iris.*scan|voiceprint|retina)\b',
                'weight': 30
            },
            'indefinite_retention': {
                'regex': r'\b(as long as necessary|indefinitely|permanently|for.*duration.*of|until.*you.*delete)\b',
                'weight': 20
            },
            'vague_language': {
                'regex': r'\b(may|might|could|reasonably|appropriate.*discretion|necessary.*purposes)\b',
                'weight': 15
            }
        }
    
    def analyze(self, policy_text):
        # Split into clauses (paragraphs)
        clauses = [c.strip() for c in policy_text.split('\n\n') if len(c.strip()) > 50]
        
        results = {}
        
        for category, config in self.patterns.items():
            pattern = config['regex']
            weight = config['weight']
            matches = []
            
            for i, clause in enumerate(clauses):
                if re.search(pattern, clause, re.IGNORECASE):
                    # Find the specific matched text
                    match_obj = re.search(pattern, clause, re.IGNORECASE)
                    matched_text = match_obj.group(0) if match_obj else ''
                    
                    matches.append({
                        'clause_id': i,
                        'text': clause[:400],  # Limit to 400 chars
                        'matched_keyword': matched_text,
                        'position': i
                    })
            
            # Calculate score (0-100)
            score = min(len(matches) * weight, 100)
            
            results[category] = {
                'score': score,
                'risk_level': self._get_risk_level(score),
                'matches': matches[:5],  # Top 5 matches only
                'total_matches': len(matches)
            }
        
        # Calculate overall risk score
        overall_score = sum(r['score'] for r in results.values()) / len(results)
        results['overall'] = {
            'score': round(overall_score, 1),
            'risk_level': self._get_risk_level(overall_score)
        }
        
        return results
    
    def _get_risk_level(self, score):
        if score < 30:
            return 'low'
        elif score < 60:
            return 'medium'
        else:
            return 'high'