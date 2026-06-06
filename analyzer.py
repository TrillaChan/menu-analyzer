import os
import base64
import asyncio
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-02-15-preview"
)

async def analyze_menu(image_path: str) -> dict:
    """Analyse une image de menu et retourne les plats + allergènes."""
    
    # Lire et encoder l'image en base64
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    # Détecter le format
    ext = image_path.split(".")[-1].lower()
    media_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"
    
    response = await client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": """Analyse ce menu de restaurant et retourne une réponse structurée avec :
1. La liste des plats détectés
2. Les ingrédients principaux de chaque plat
3. Les allergènes potentiels (gluten, lactose, fruits à coque, etc.)

Format de réponse souhaité :
- Nom du plat
  - Ingrédients : ...
  - Allergènes : ...
"""
                    }
                ]
            }
        ],
        max_tokens=1000
    )
    
    return {
        "analyse": response.choices[0].message.content,
        "tokens_utilisés": response.usage.total_tokens
    }


async def main():
    # Test avec une image
    image_path = "menu_test.jpg"  # tu mettras une vraie photo ici
    
    if not os.path.exists(image_path):
        print("⚠️  Pas d'image trouvée. Place une photo de menu nommée 'menu_test.jpg' dans le dossier.")
        return
    
    print("🔍 Analyse en cours...")
    resultat = await analyze_menu(image_path)
    print("\n✅ Résultat :\n")
    print(resultat["analyse"])
    print(f"\n📊 Tokens utilisés : {resultat['tokens_utilisés']}")


if __name__ == "__main__":
    asyncio.run(main())