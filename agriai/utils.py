# agriai/utils.py
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.tavily import TavilyTools
from phi.tools.pubmed import PubmedTools

# Load environment variables
load_dotenv()

class PlantDiseasePredictor:
    def __init__(self):
        # Initialize models and tools
        self._configure_models()
        self._setup_research_tools()
        
    def _configure_models(self):
        """Configure the Gemini models with API keys"""
        try:
            self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
            if not self.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
                
            genai.configure(api_key=self.GOOGLE_API_KEY)
            self.image_model = genai.GenerativeModel('gemini-1.5-flash')
            self.research_model = Gemini(api_key=self.GOOGLE_API_KEY)
        except Exception as e:
            raise RuntimeError(f"Failed to configure models: {str(e)}")

    def _setup_research_tools(self):
        """Setup research tools with API keys"""
        try:
            self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
            if not self.TAVILY_API_KEY:
                raise ValueError("TAVILY_API_KEY not found in environment variables")
                
            self.tools = [TavilyTools(api_key=self.TAVILY_API_KEY), PubmedTools()]
            self.research_agent = Agent(tools=self.tools, model=self.research_model)
        except Exception as e:
            raise RuntimeError(f"Failed to setup research tools: {str(e)}")

    def analyze_plant_image(self, img_path):
        """
        Analyze plant image and extract symptoms
        Args:
            img_path: Path to the image file
        Returns:
            dict: {'success': bool, 'analysis': str, 'error': str}
        """
        try:
            img = Image.open(img_path)
            
            prompt = """
            Analyze this plant image and provide ONLY the following details in a clear, bullet-point format:
            - **Plant Name** (if identifiable)
            - **Visible Symptoms/Issues** (e.g., curling, spots, discoloration)
            - **Possible Causes** (e.g., fungal, bacterial, nutrient deficiency)

            Do NOT include treatment recommendations or unrelated explanations.
            """
            
            response = self.image_model.generate_content([prompt, img])
            return {
                'success': True,
                'analysis': response.text
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': f"Could not find image at {img_path}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error analyzing image: {str(e)}"
            }

    def research_disease(self, symptoms):
        """
        Research disease information based on symptoms
        Args:
            symptoms: String describing plant symptoms
        Returns:
            dict: {'success': bool, 'research': str, 'error': str}
        """
        if not symptoms.strip():
            return {
                'success': False,
                'error': "No symptoms provided"
            }

        try:
            prompt = f"""
            You are a plant disease expert.

            The plant shows the following symptoms: "{symptoms}"

            🎯 Your task:
            1. Search trusted agricultural sites and scientific sources (PubMed, Tavily, etc.).
            2. Based on the symptoms, identify and return **3 most likely diseases**. Explore fungal, bacterial, viral, and physiological causes — not just common ones.

            Return only the following structured output:

            📌 **Most Likely Disease:**
            - <Disease 1>: (Why it's likely based on specific symptom pattern)
            - <Disease 2>: (Specific indication such as pathogen type or climate-related factor)
            - <Disease 3>: (Physiological or pest-induced if relevant)

            ✅ **Preventive Measures:**
            - <Step 1>: (Include specific tips like resistant varieties, planting depth, spacing, or crop rotation)
            - <Step 2>: (Soil amendment or nutrition advice with fertilizer name or ratio)
            - <Step 3>: (Watering, mulching, or environment control strategy)

            💊 **Treatment Actions:**
            - <Treatment 1>: (Name of fungicide/insecticide/antibiotic; application interval)
            - <Treatment 2>: (Organic or natural option — e.g., neem oil, baking soda, etc.)
            - <Treatment 3>: (Physical method — e.g., pruning, soil solarization, removing infected plants)
            """

            response = self.research_agent.run(prompt)
            if response:
                return {
                    'success': True,
                    'research': response.content
                }
            else:
                return {
                    'success': False,
                    'error': "No response from research model"
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error researching disease: {str(e)}"
            }

    def handle_uploaded_file(self, uploaded_file):
        """
        Handle uploaded file and return temporary path
        Args:
            uploaded_file: Django UploadedFile object
        Returns:
            dict: {'success': bool, 'file_path': str, 'error': str}
        """
        try:
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)
            return {
                'success': True,
                'file_path': file_path,
                'filename': filename
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error handling uploaded file: {str(e)}"
            }

    def cleanup_file(self, file_path):
        """
        Clean up temporary file
        Args:
            file_path: Path to file to be removed
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not remove file {file_path}: {str(e)}")

# Singleton instance for easy access
predictor = PlantDiseasePredictor()