import re
        
class RiskAnalyzer:
    def __init__(self):
        self.patterns = {
            'data_resale': {
                'patterns': [
                    # Direct selling
                    r'\b(sell|sold|selling|monetize|monetization)\s+.{0,30}\b(data|information|personal)\b',
                    
                    # Ad-based monetization (NEW!)
                    r'\b(personali[sz]e|target|select|show|serve).*\bads?\b',
                    r'\badvert(is|iz)ers?.*\b(receive|get|access).*\b(information|data|reports?|insights?)\b',
                    r'\bprovide.*\b(partners?|advertisers?).*\b(analytics|insights?|reports?|information|data)\b',
                    r'\bshare.*\b(advertisers?|partners?).*\b(personali[sz]|target|measure)',
                    
                    # Business purposes sharing (NEW!)
                    r'\bshare.*\b(third[\s-]?part(y|ies)|partners?|affiliates?).*\b(business\s+purposes?|commercial|marketing)',
                ],
                'weight': 25
            },
            
            'vague_language': {
                'patterns': [
                    # Original patterns
                    r'\bat\s+our\s+discretion\b',
                    r'\bas\s+we\s+deem\s+(appropriate|necessary|fit)\b',
                    
                    # New patterns for sophisticated vagueness
                    r'\blegitimate\s+(business\s+)?interests?\b',
                    r'\b(necessary|appropriate|reasonable)\s+purposes?\b',
                    r'\bas\s+permitted\s+by\s+(applicable\s+)?law\b',
                    r'\bfor\s+the\s+purposes?\s+(described|outlined|set\s+out)\s+(below|in\s+this)',
                    r'\bimprove.*\bservices?\b(?!.*\bspecifically\b)',  # Vague unless specific
                    r'\brelated\s+services?\b',
                    r'\bother\s+purposes?\b',
                ],
                'weight': 20
            },
            
            # Keep biometric and retention as-is
            'biometric': {
                'patterns': [
                    r'\b(biometric|fingerprint|face\s+recognition|facial\s+recognition|voiceprint|faceprint)\b'
                ],
                'weight': 30
            },
            
            'indefinite_retention': {
                'patterns': [
                    r'\b(indefinitely|permanently|as\s+long\s+as\s+necessary|for\s+as\s+long\s+as)\b'
                ],
                'weight': 20
            }
        }
    
    def analyze(self, policy_text):
        clauses = [c.strip() for c in policy_text.split('\n\n') if len(c.strip()) > 50]
        
        results = {}
        
        for category, config in self.patterns.items():
            matches = []
            
            for i, clause in enumerate(clauses):
                # Check ALL patterns for this category
                for pattern in config['patterns']:
                    if re.search(pattern, clause, re.IGNORECASE):
                        match_obj = re.search(pattern, clause, re.IGNORECASE)
                        matched_text = match_obj.group(0) if match_obj else ''
                        
                        matches.append({
                            'clause_id': i,
                            'text': clause[:400],
                            'matched_keyword': matched_text,
                            'position': i,
                            'pattern': pattern  # Track which pattern matched
                        })
                        break  # Don't match same clause multiple times
            
            # Calculate score
            if len(matches) == 0:
                score = 0
            elif len(matches) == 1:
                score = config['weight']
            elif len(matches) == 2:
                score = min(config['weight'] * 2, 70)
            else:
                score = min(config['weight'] * len(matches), 100)
            
            results[category] = {
                'score': score,
                'risk_level': self._get_risk_level(score),
                'matches': matches[:5],
                'total_matches': len(matches)
            }
        
        # Calculate overall score
        total_weight = sum(config['weight'] for config in self.patterns.values())
        weighted_sum = sum(
            results[cat]['score'] * self.patterns[cat]['weight'] 
            for cat in self.patterns.keys()
        )
        overall_score = weighted_sum / total_weight
        
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