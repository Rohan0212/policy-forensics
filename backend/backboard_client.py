import requests
import os

class BackboardClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://app.backboard.io/api"
        self.assistant_id = None
        self.headers = {"X-API-Key": self.api_key}
    
    def is_configured(self):
        is_valid = self.api_key is not None and len(self.api_key) > 20 and self.api_key != 'your_api_key_here'
        if is_valid:
            print(f"🔑 Backboard API Key configured")
        else:
            print(f"⚠️ API Key not properly configured")
        return is_valid
    
    def _get_or_create_assistant(self):
        """Get or create a PolicyX-Ray assistant"""
        if self.assistant_id:
            return self.assistant_id
        
        try:
            # Create assistant
            print("🤖 Creating Backboard assistant...")
            response = requests.post(
                f"{self.base_url}/assistants",
                json={
                    "name": "PolicyX-Ray Analyzer",
                    "system_prompt": "You are a privacy policy expert. Analyze clauses for privacy risks and GDPR compliance. Be concise and factual."
                },
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            self.assistant_id = response.json()["assistant_id"]
            print(f"✅ Assistant created: {self.assistant_id}")
            return self.assistant_id
        except Exception as e:
            print(f"❌ Failed to create assistant: {e}")
            return None
    
    def _call_api(self, prompt, use_search=False):
        """Call Backboard.io API using assistant/thread pattern"""
        if not self.is_configured():
            return None
        
        try:
            # Get or create assistant
            assistant_id = self._get_or_create_assistant()
            if not assistant_id:
                return None
            
            # Create thread
            print("📝 Creating thread...")
            thread_response = requests.post(
                f"{self.base_url}/assistants/{assistant_id}/threads",
                json={},
                headers=self.headers,
                timeout=10
            )
            thread_response.raise_for_status()
            thread_id = thread_response.json()["thread_id"]
            print(f"✅ Thread created: {thread_id}")
            
            # Send message
            print(f"📡 Sending message to Backboard...")
            message_response = requests.post(
                f"{self.base_url}/threads/{thread_id}/messages",
                headers=self.headers,
                data={"content": prompt, "stream": "false"},
                timeout=30
            )
            message_response.raise_for_status()
            
            result = message_response.json()
            content = result.get("content", "")
            print(f"✅ Response received ({len(content)} chars)")
            return content
            
        except Exception as e:
            print(f"❌ Backboard API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text[:200]}")
            return None
    
#     def enhance_analysis(self, results):
#         """Phase 2: Add AI validation and GDPR citations"""
        
#         print("🤖 Starting AI enhancement with Backboard.io...")
        
#         # Enhance data_resale category
#         if 'data_resale' in results and results['data_resale']['matches']:
#             enhanced_matches = []
            
#             # Only enhance top 3 matches to save API calls
#             for idx, match in enumerate(results['data_resale']['matches'][:3]):
#                 print(f"🔍 Analyzing clause {idx + 1}/3...")
                
#                 # AI Validation
#                 validation_prompt = f"""Analyze this privacy policy clause:

# "{match['text']}"

# Question: Does this clause allow the company to SELL or MONETIZE user data to third parties?

# Answer with: YES or NO, followed by a 1-sentence explanation.
# Keep your response under 100 words."""

#                 ai_response = self._call_api(validation_prompt)
                
#                 if ai_response:
#                     match['ai_validation'] = ai_response
#                     print(f"✅ AI validation complete")
                    
#                     # GDPR Citation (only if AI says YES)
#                     if 'YES' in ai_response.upper():
#                         gdpr_prompt = f"""Identify which GDPR article restricts companies from selling user data without explicit consent.

# Then explain in 1 sentence how this clause potentially conflicts with that article.

# Format:
# Article: [GDPR Article number]
# Conflict: [Brief explanation]

# Keep response under 100 words."""

#                         gdpr_response = self._call_api(gdpr_prompt)
#                         if gdpr_response:
#                             match['gdpr_citation'] = gdpr_response
#                             print(f"⚖️ GDPR citation added")
#                 else:
#                     print(f"⚠️ Skipping clause {idx + 1} - API call failed")
                
#                 enhanced_matches.append(match)
            
#             results['data_resale']['matches'] = enhanced_matches
#             print("✨ Enhancement complete!")
        
#         return results
    
    def enhance_analysis(self, results):
        """Phase 2: Add AI validation and GDPR citations"""
    
        print("🤖 Starting AI enhancement with Backboard.io...")
    
        # Define which categories to enhance and their prompts
        categories_to_enhance = {
            'data_resale': {
                'validation': 'Does this clause allow the company to SELL or MONETIZE user data to third parties?',
                'gdpr_article': 'which GDPR article restricts companies from selling user data without explicit consent'
            },
            'biometric': {
                'validation': 'Does this clause allow collection of BIOMETRIC data (fingerprints, facial recognition, etc.)?',
                'gdpr_article': 'which GDPR article governs the processing of biometric data for identification purposes'
            },
            'indefinite_retention': {
                'validation': 'Does this clause allow the company to retain data INDEFINITELY without clear time limits?',
                'gdpr_article': 'which GDPR article requires data to be kept only as long as necessary (storage limitation)'
            },
            'vague_language': {
                'validation': 'Does this clause use vague language that gives the company excessive discretion?',
                'gdpr_article': 'which GDPR article requires transparency and specific purposes for data processing'
            }   
        }
    
        for category, prompts in categories_to_enhance.items():
            if category in results and results[category]['matches']:
                print(f"\n🔍 Enhancing {category}...")
                enhanced_matches = []
            
                # Only enhance top 2 matches per category (to limit API calls)
                for idx, match in enumerate(results[category]['matches'][:2]):
                    print(f"  → Analyzing clause {idx + 1}/2...")
                
                    # AI Validation
                    validation_prompt = f"""Analyze this privacy policy clause:

"{match['text']}"

Question: {prompts['validation']}

Answer with: YES or NO, followed by a 1-sentence explanation.
Keep your response under 100 words."""

                ai_response = self._call_api(validation_prompt)
                
                if ai_response:
                    match['ai_validation'] = ai_response
                    print(f"  ✅ AI validation complete")
                    
                    # GDPR Citation (only if AI says YES)
                    if 'YES' in ai_response.upper():
                        gdpr_prompt = f"""Identify {prompts['gdpr_article']}.

Then explain in 1 sentence how this clause potentially conflicts with that article.

Format:
Article: [GDPR Article number]
Conflict: [Brief explanation]

Keep response under 100 words."""

                        gdpr_response = self._call_api(gdpr_prompt)
                        if gdpr_response:
                            match['gdpr_citation'] = gdpr_response
                            print(f"  ⚖️ GDPR citation added")
                else:
                    print(f"  ⚠️ Skipping clause - API call failed")
                
                enhanced_matches.append(match)
            
            # Add back any remaining unenhanced matches
            enhanced_matches.extend(results[category]['matches'][2:])
            results[category]['matches'] = enhanced_matches
    
        print("\n✨ Enhancement complete!")
        return results