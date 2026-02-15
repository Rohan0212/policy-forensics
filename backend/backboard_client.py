import requests
import os

class BackboardClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://app.backboard.io/api"
        self.headers = {"X-API-Key": self.api_key}
        self.assistant_id = None
        self.knowledge_base_id = None
    
    def is_configured(self):
        is_valid = self.api_key is not None and len(self.api_key) > 20 and self.api_key != 'your_api_key_here'
        if is_valid:
            print(f"🔑 Backboard API Key configured")
        else:
            print(f"⚠️ API Key not properly configured")
        return is_valid
    
    def _create_knowledge_base(self):
        """Create knowledge base with GDPR articles"""
        if self.knowledge_base_id:
            return self.knowledge_base_id
        
        try:
            print("📚 Creating GDPR knowledge base...")
            
            # Read GDPR articles
            gdpr_path = os.path.join(os.path.dirname(__file__), 'gdpr_articles.txt')
            with open(gdpr_path, 'r', encoding='utf-8') as f:
                gdpr_text = f.read()
            
            # Create knowledge base
            response = requests.post(
                f"{self.base_url}/knowledge-bases",
                json={
                    "name": "GDPR Regulation",
                    "description": "GDPR articles for privacy policy analysis"
                },
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            kb_id = response.json()["knowledge_base_id"]
            
            print(f"✅ Knowledge base created: {kb_id}")
            
            # Upload GDPR document to knowledge base
            print("📄 Uploading GDPR articles...")
            upload_response = requests.post(
                f"{self.base_url}/knowledge-bases/{kb_id}/documents",
                json={
                    "content": gdpr_text,
                    "metadata": {
                        "source": "GDPR Regulation (EU) 2016/679",
                        "type": "legal_text"
                    }
                },
                headers=self.headers,
                timeout=15
            )
            upload_response.raise_for_status()
            print("✅ GDPR articles uploaded to knowledge base")
            
            self.knowledge_base_id = kb_id
            return kb_id
            
        except Exception as e:
            print(f"❌ Failed to create knowledge base: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text[:300]}")
            return None
    
    def _get_or_create_assistant(self):
        """Get or create assistant with GDPR knowledge base"""
        if self.assistant_id:
            return self.assistant_id
        
        try:
            # First create knowledge base
            kb_id = self._create_knowledge_base()
            if not kb_id:
                print("⚠️ Proceeding without knowledge base")
            
            # Create assistant
            print("🤖 Creating Backboard assistant with RAG...")
            assistant_config = {
                "name": "PolicyX-Ray GDPR Analyzer",
                "system_prompt": """You are a GDPR compliance expert. Analyze privacy policy clauses against GDPR regulations.

When analyzing clauses:
1. Search the knowledge base for relevant GDPR articles
2. Compare the clause against the specific GDPR requirements
3. Identify conflicts or compliance issues
4. Cite the specific GDPR article number and provision
5. Be precise and factual

Always format GDPR citations as: "Article X(Y)(Z)" followed by the article name.""",
                "model": "gpt-4o"  # Using GPT-4o as it's cheaper and you already have it
            }
            
            # Add knowledge base if created successfully
            if kb_id:
                assistant_config["knowledge_base_ids"] = [kb_id]
                print("✅ Assistant will use GDPR knowledge base (RAG enabled)")
            
            response = requests.post(
                f"{self.base_url}/assistants",
                json=assistant_config,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            self.assistant_id = response.json()["assistant_id"]
            print(f"✅ Assistant created: {self.assistant_id}")
            return self.assistant_id
            
        except Exception as e:
            print(f"❌ Failed to create assistant: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text[:300]}")
            return None
    
    def _call_api(self, prompt):
        """Call Backboard.io API with RAG support"""
        if not self.is_configured():
            return None
        
        try:
            # Get or create assistant (with knowledge base)
            assistant_id = self._get_or_create_assistant()
            if not assistant_id:
                return None
            
            # Create thread
            thread_response = requests.post(
                f"{self.base_url}/assistants/{assistant_id}/threads",
                json={},
                headers=self.headers,
                timeout=10
            )
            thread_response.raise_for_status()
            thread_id = thread_response.json()["thread_id"]
            
            # Send message (RAG happens automatically if knowledge base is attached)
            message_response = requests.post(
                f"{self.base_url}/threads/{thread_id}/messages",
                headers=self.headers,
                data={"content": prompt, "stream": "false"},
                timeout=30
            )
            message_response.raise_for_status()
            
            result = message_response.json()
            content = result.get("content", "")
            return content
            
        except Exception as e:
            print(f"❌ Backboard API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text[:200]}")
            return None
    
    def enhance_analysis(self, results):
        """Phase 2: Add AI validation with RAG-based GDPR analysis"""
        
        print("🤖 Starting RAG-enhanced AI analysis...")
        
        # Map categories to GDPR focus areas
        category_gdpr_focus = {
            'data_resale': 'consent requirements and lawful basis for selling or monetizing user data',
            'biometric': 'special categories of personal data, specifically biometric data processing',
            'indefinite_retention': 'storage limitation and data retention requirements',
            'vague_language': 'transparency, purpose limitation, and specificity requirements'
        }
        
        for category, gdpr_focus in category_gdpr_focus.items():
            if category in results and results[category]['matches']:
                print(f"\n🔍 Enhancing {category} with RAG...")
                
                all_matches = results[category]['matches']
                
                # Enhance up to 3 clauses per category
                max_to_enhance = min(3, len(all_matches))
                
                for idx in range(max_to_enhance):
                    match = all_matches[idx]
                    print(f"  → Analyzing clause {idx + 1}/{max_to_enhance}...")
                    
                    # RAG-enhanced validation prompt
                    validation_prompt = f"""Analyze this privacy policy clause for GDPR compliance:

CLAUSE:
"{match['text']}"

FOCUS AREA: {gdpr_focus}

INSTRUCTIONS:
1. Search the GDPR knowledge base for relevant articles about {gdpr_focus}
2. Determine if this clause violates or conflicts with GDPR requirements
3. Answer YES or NO
4. Provide a 1-2 sentence explanation citing the specific GDPR article

FORMAT:
[YES/NO]. [Explanation with GDPR Article citation]"""

                    ai_response = self._call_api(validation_prompt)
                    
                    if ai_response:
                        match['ai_validation'] = ai_response
                        print(f"  ✅ RAG-enhanced validation complete")
                        
                        # If violation detected, get detailed GDPR citation
                        if 'YES' in ai_response.upper() or 'VIOLAT' in ai_response.upper() or 'CONFLICT' in ai_response.upper():
                            citation_prompt = f"""Based on the GDPR knowledge base, provide a detailed regulatory citation for this issue:

CLAUSE: "{match['text']}"

ISSUE: {gdpr_focus}

Provide:
1. The specific GDPR Article number and name
2. A 1-2 sentence explanation of how this clause conflicts with that article

FORMAT:
Article: [Article number and name]
Conflict: [Detailed explanation]"""

                            gdpr_response = self._call_api(citation_prompt)
                            if gdpr_response:
                                match['gdpr_citation'] = gdpr_response
                                print(f"  ⚖️ GDPR citation retrieved from knowledge base")
                    else:
                        print(f"  ⚠️ API call failed for clause {idx + 1}")
        
        print("\n✨ RAG-enhanced analysis complete!")
        return results