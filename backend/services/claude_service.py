from google import genai
from google.genai import types
import json
import re
import os
import random

_api_key = os.environ.get("GEMINI_API_KEY", "")
DEMO_MODE = not _api_key or not _api_key.startswith("AIza")

if not DEMO_MODE:
    client = genai.Client(api_key=_api_key)
else:
    client = None
    print("[AI Newsroom] DEMO MODE active — using smart mock responses (no API key needed)")

MODEL = "gemini-2.0-flash"

SYSTEM = (
    "You are an expert AI Newsroom Assistant specializing in: "
    "1. Journalistic translation preserving formal news tone. "
    "2. Cultural adaptation for regional audiences. "
    "3. Sensitivity analysis for broadcast content. "
    "4. Real-time content localization. "
    "Always respond with valid JSON as specified. Never deviate from the output format."
)

# ── Demo translations for major languages ──────────────────────────────────
DEMO_TRANSLATIONS = {
    "hi": {
        "title": "विशाखापत्तनम में 6.8 तीव्रता का भूकंप, राज्य सरकार ने रेड अलर्ट जारी किया",
        "content": "विशाखापत्तनम: आज तड़के 3 बजकर 42 मिनट पर विशाखापत्तनम के तटीय क्षेत्र में 6.8 तीव्रता का भूकंप आया। राष्ट्रीय आपदा प्रतिक्रिया बल ने प्रभावित क्षेत्रों में 12 टीमें तैनात की हैं। प्राथमिक रिपोर्टों के अनुसार पुराने शहर में 200 से अधिक इमारतों को नुकसान पहुंचा है। राज्य सरकार ने रेड अलर्ट जारी करते हुए केंद्र से सहायता मांगी है। भूकंप के केंद्र से 50 किलोमीटर के दायरे में सुनामी की चेतावनी जारी की गई है।",
        "adaptations": ["मील को किलोमीटर में परिवर्तित किया गया", "स्थानीय प्रशासनिक संदर्भ जोड़े गए", "औपचारिक हिंदी पत्रकारिता शैली अपनाई गई"]
    },
    "ta": {
        "title": "விசாகபட்டினத்தில் 6.8 ரிக்டர் அதிர்வு, மாநில அரசு சிவப்பு எச்சரிக்கை பிறப்பித்தது",
        "content": "விசாகபட்டினம்: இன்று அதிகாலை 3 மணி 42 நிமிடத்திற்கு 6.8 ரிக்டர் அளவிலான நிலநடுக்கம் ஏற்பட்டது. தேசிய பேரிடர் மேலாண்மை படை 12 குழுக்களை பாதிக்கப்பட்ட பகுதிகளுக்கு அனுப்பியுள்ளது. 200-க்கும் மேற்பட்ட கட்டிடங்கள் சேதமடைந்துள்ளன. மாநில அரசு சிவப்பு எச்சரிக்கை விதித்து மத்திய உதவி கோரியுள்ளது.",
        "adaptations": ["தமிழ் செய்தி ஊடக நடை பின்பற்றப்பட்டது", "அலகுகள் மெட்ரிக் முறைக்கு மாற்றப்பட்டன"]
    },
    "te": {
        "title": "విశాఖపట్నంలో 6.8 తీవ్రత భూకంపం, రాష్ట్ర ప్రభుత్వం రెడ్ అలర్ట్ జారీ చేసింది",
        "content": "విశాఖపట్నం: ఈరోజు తెల్లవారుజామున 3:42 గంటలకు తీవ్రమైన భూకంపం సంభవించింది. జాతీయ విపత్తు స్పందన బలగం 12 బృందాలను అందుబాటులో ఉంచింది. 200కు పైగా భవనాలకు నష్టం వాటిల్లింది. రాష్ట్ర ప్రభుత్వం రెడ్ అలర్ట్ ప్రకటించింది.",
        "adaptations": ["తెలుగు పత్రికా విధానం అనుసరించబడింది", "స్థానిక సందర్భం జోడించబడింది"]
    },
    "bn": {
        "title": "বিশাখাপত্তনমে ৬.৮ মাত্রার ভূমিকম্প, রাজ্য সরকার লাল সতর্কতা জারি করেছে",
        "content": "বিশাখাপত্তনম: আজ ভোর ৩টা ৪২ মিনিটে ৬.৮ মাত্রার শক্তিশালী ভূমিকম্প আঘাত হেনেছে। জাতীয় দুর্যোগ মোকাবেলা বাহিনী ১২টি দল মোতায়েন করেছে। ২০০টিরও বেশি ভবন ক্ষতিগ্রস্ত হয়েছে। রাজ্য সরকার লাল সতর্কতা জারি করে কেন্দ্রীয় সহায়তা চেয়েছে।",
        "adaptations": ["বাংলা সাংবাদিকতার রীতি অনুসরণ করা হয়েছে", "এককগুলি মেট্রিক পদ্ধতিতে রূপান্তরিত করা হয়েছে"]
    },
    "mr": {
        "title": "विशाखापट्टणममध्ये 6.8 तीव्रतेचा भूकंप, राज्य सरकारने रेड अलर्ट जाहीर केला",
        "content": "विशाखापट्टणम: आज पहाटे 3 वाजून 42 मिनिटांनी 6.8 तीव्रतेचा भूकंप झाला. राष्ट्रीय आपत्ती प्रतिसाद दलाने 12 पथके तैनात केली आहेत. 200 पेक्षा जास्त इमारतींचे नुकसान झाले आहे. राज्य सरकारने रेड अलर्ट जाहीर करून केंद्राकडे मदत मागितली आहे.",
        "adaptations": ["मराठी पत्रकारिता शैली वापरली", "स्थानिक संदर्भ जोडले"]
    },
    "es": {
        "title": "Terremoto de magnitud 6.8 sacude Visakhapatnam; gobierno declara alerta roja",
        "content": "Visakhapatnam — Un poderoso terremoto de magnitud 6.8 sacudió la ciudad costera de Visakhapatnam a las 3:42 de la madrugada, hora local. La Fuerza Nacional de Respuesta a Desastres ha desplegado 12 equipos en las zonas afectadas. Informes preliminares indican daños estructurales en más de 200 edificios del distrito antiguo. El gobierno estatal ha declarado alerta roja y solicitado asistencia federal.",
        "adaptations": ["Unidades convertidas al sistema métrico", "Tono periodístico formal en español adoptado", "Contexto latinoamericano añadido donde corresponde"]
    },
    "fr": {
        "title": "Un séisme de magnitude 6,8 frappe Visakhapatnam ; le gouvernement déclare l'alerte rouge",
        "content": "Visakhapatnam — Un puissant séisme de magnitude 6,8 a frappé la ville côtière de Visakhapatnam à 3h42 du matin, heure locale. La Force nationale de réponse aux catastrophes a déployé 12 équipes dans les zones sinistrées. Les premiers rapports font état de dommages structurels dans plus de 200 bâtiments du vieux quartier. Le gouvernement de l'État a déclaré l'alerte rouge et demandé l'aide du gouvernement central.",
        "adaptations": ["Unités converties au système métrique", "Ton journalistique formel français adopté"]
    },
    "ar": {
        "title": "زلزال بقوة 6.8 درجة يضرب فيزاخاباتنام والحكومة تُعلن حالة التأهب القصوى",
        "content": "فيزاخاباتنام — ضرب زلزال عنيف بقوة 6.8 درجة على مقياس ريختر مدينة فيزاخاباتنام الساحلية في تمام الساعة 3:42 فجرًا بالتوقيت المحلي. وقد نشرت قوة الاستجابة الوطنية للكوارث 12 فرقة في المناطق المتضررة. وتشير التقارير الأولية إلى أضرار هيكلية في أكثر من 200 مبنى.",
        "adaptations": ["اتجاه النص من اليمين إلى اليسار", "الأسلوب الصحفي العربي الرسمي", "تحويل الوحدات إلى النظام المتري"]
    },
    "zh": {
        "title": "维萨卡帕特南发生6.8级地震，州政府发布红色预警",
        "content": "维萨卡帕特南——当地时间今日凌晨3时42分，沿海城市维萨卡帕特南发生6.8级强烈地震。国家灾难响应部队已向受灾地区派遣12支救援队。初步报告显示，老城区超过200栋建筑遭受结构性损坏。州政府已宣布红色预警并请求中央援助。",
        "adaptations": ["使用正式汉语新闻播报风格", "单位换算为公制系统", "添加了中国读者熟悉的地理背景"]
    },
    "ja": {
        "title": "ビシャーカパトナムでM6.8の地震発生、州政府が最高警戒態勢を宣言",
        "content": "ビシャーカパトナム — 本日午前3時42分、沿岸部のビシャーカパトナムでマグニチュード6.8の強い地震が発生しました。国家災害対応隊は被災地域に12チームを派遣しています。速報によると、旧市街で200棟以上の建物に構造的損傷が確認されています。州政府は最高警戒態勢を宣言し、中央政府に支援を要請しました。",
        "adaptations": ["NHKニューススタイルに合わせた表現", "単位はメートル法に変換", "日本の読者向けの地理的背景を追加"]
    },
    "gu": {
        "title": "વિશાખાપટ્ટણમમાં 6.8 તીવ્રતાનો ભૂકંપ, રાજ્ય સરકારે રેડ એલર્ટ જાહેર કર્યો",
        "content": "વિશાખાપટ્ટણમ: આજે વહેલી સવારે 3:42 વાગ્યે 6.8 તીવ્રતાનો ભૂકંપ આવ્યો. NDRF ની 12 ટીમો પ્રભાવિત વિસ્તારોમાં તૈનાત કરવામાં આવી છે. 200 થી વધુ ઇમારતોને નુકસાન થયું છે.",
        "adaptations": ["ગુજરાતી પત્રકારત્વ શૈલી", "સ્થાનિક સંદર્ભ ઉમેર્યો"]
    },
    "kn": {
        "title": "ವಿಶಾಖಪಟ್ಟಣದಲ್ಲಿ 6.8 ತೀವ್ರತೆಯ ಭೂಕಂಪ, ರಾಜ್ಯ ಸರ್ಕಾರ ರೆಡ್ ಅಲರ್ಟ್ ಘೋಷಿಸಿದೆ",
        "content": "ವಿಶಾಖಪಟ್ಟಣ: ಇಂದು ಮುಂಜಾನೆ 3:42 ಕ್ಕೆ 6.8 ತೀವ್ರತೆಯ ಭೂಕಂಪ ಸಂಭವಿಸಿದೆ. ರಾಷ್ಟ್ರೀಯ ವಿಪತ್ತು ಪ್ರತಿಕ್ರಿಯಾ ದಳ 12 ತಂಡಗಳನ್ನು ನಿಯೋಜಿಸಿದೆ. 200ಕ್ಕೂ ಹೆಚ್ಚು ಕಟ್ಟಡಗಳಿಗೆ ಹಾನಿಯಾಗಿದೆ.",
        "adaptations": ["ಕನ್ನಡ ಪತ್ರಿಕೋದ್ಯಮ ಶೈಲಿ", "ಸ್ಥಳೀಯ ಸಂದರ್ಭ ಸೇರಿಸಲಾಗಿದೆ"]
    },
    "ml": {
        "title": "വിശാഖപട്ടണത്ത് 6.8 തീവ്രതയിൽ ഭൂകമ്പം; സംസ്ഥാന സർക്കാർ റെഡ് അലേർട്ട് പ്രഖ്യാപിച്ചു",
        "content": "വിശാഖപട്ടണം: ഇന്ന് പുലർച്ചെ 3:42ന് 6.8 തീവ്രതയിൽ ശക്തമായ ഭൂകമ്പം ഉണ്ടായി. ദേശീയ ദുരന്ത നിവാരണ സേന 12 സംഘങ്ങളെ വിന്യസിച്ചിട്ടുണ്ട്. 200-ലധികം കെട്ടിടങ്ങൾക്ക് കേടുപാടുകൾ സംഭവിച്ചിട്ടുണ്ട്.",
        "adaptations": ["മലയാളം മാധ്യമ ശൈലി", "പ്രാദേശിക സന്ദർഭം ചേർത്തു"]
    },
    "pa": {
        "title": "ਵਿਸ਼ਾਖਾਪਟਨਮ ਵਿੱਚ 6.8 ਤੀਬਰਤਾ ਦਾ ਭੂਚਾਲ, ਰਾਜ ਸਰਕਾਰ ਨੇ ਰੈੱਡ ਅਲਰਟ ਜਾਰੀ ਕੀਤਾ",
        "content": "ਵਿਸ਼ਾਖਾਪਟਨਮ: ਅੱਜ ਤੜਕੇ 3:42 ਵਜੇ 6.8 ਤੀਬਰਤਾ ਦਾ ਭੂਚਾਲ ਆਇਆ। NDRF ਦੀਆਂ 12 ਟੀਮਾਂ ਤਾਇਨਾਤ ਕੀਤੀਆਂ ਗਈਆਂ ਹਨ। 200 ਤੋਂ ਵੱਧ ਇਮਾਰਤਾਂ ਨੂੰ ਨੁਕਸਾਨ ਹੋਇਆ ਹੈ।",
        "adaptations": ["ਪੰਜਾਬੀ ਪੱਤਰਕਾਰੀ ਸ਼ੈਲੀ", "ਸਥਾਨਕ ਸੰਦਰਭ ਜੋੜਿਆ"]
    },
}

LANG_NAMES = {
    "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "bn": "Bengali",
    "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada", "ml": "Malayalam",
    "pa": "Punjabi", "es": "Spanish", "fr": "French", "ar": "Arabic",
    "zh": "Mandarin", "ja": "Japanese"
}


def _call(prompt: str) -> str:
    if DEMO_MODE:
        raise RuntimeError("DEMO_MODE")
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM)
    )
    return response.text


def _parse(text: str, fallback: dict) -> dict:
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return fallback


# ── Helper to extract a meaningful title from content ─────────────────────
def _extract_title(text: str) -> str:
    first = text.strip().split('.')[0]
    return first[:90] if len(first) > 90 else first


def transcribe_and_clean(raw_text: str) -> dict:
    if not DEMO_MODE:
        prompt = f"""You are processing a raw broadcast transcript. Clean, structure, and prepare it for publication.

RAW TRANSCRIPT:
{raw_text}

Return JSON with this exact structure:
{{
  "title": "Generated news headline",
  "content": "Cleaned, structured news article text",
  "key_facts": ["fact 1", "fact 2", "fact 3"],
  "estimated_category": "Politics/Business/Sports/Entertainment/Health/Technology/International",
  "confidence": 0.95
}}"""
        return _parse(_call(prompt), {
            "title": "Untitled", "content": raw_text,
            "key_facts": [], "estimated_category": "General", "confidence": 0.5
        })

    # Demo mode — smart extraction from actual text
    words = raw_text.strip().split()
    sentences = [s.strip() for s in raw_text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    title = sentences[0][:85] if sentences else raw_text[:85]

    category = "General"
    text_lower = raw_text.lower()
    if any(w in text_lower for w in ["earthquake", "flood", "cyclone", "disaster", "storm"]):
        category = "Breaking News"
    elif any(w in text_lower for w in ["election", "minister", "parliament", "government", "policy"]):
        category = "Politics"
    elif any(w in text_lower for w in ["market", "economy", "gdp", "inflation", "stock", "trade"]):
        category = "Business"
    elif any(w in text_lower for w in ["cricket", "football", "tournament", "match", "player", "sports"]):
        category = "Sports"
    elif any(w in text_lower for w in ["health", "hospital", "vaccine", "disease", "medicine"]):
        category = "Health"
    elif any(w in text_lower for w in ["technology", "ai", "software", "cyber", "digital"]):
        category = "Technology"

    key_facts = []
    for s in sentences[1:4]:
        if len(s) > 15:
            key_facts.append(s.strip())

    return {
        "title": title,
        "content": raw_text.strip(),
        "key_facts": key_facts or ["Breaking news content", "Details emerging", "More updates to follow"],
        "estimated_category": category,
        "confidence": 0.91
    }


def translate_and_adapt(title: str, content: str, target_language: str, language_name: str) -> dict:
    if not DEMO_MODE:
        prompt = f"""Translate the following news article to {language_name} ({target_language}) with cultural adaptation.

TITLE: {title}
CONTENT: {content}

Requirements:
1. Preserve formal journalistic tone appropriate for {language_name} news broadcasting
2. Adapt cultural references, idioms, and measurements for {language_name}-speaking audiences
3. Use standard {language_name} journalistic conventions
4. Note any significant cultural adaptations made

Return JSON with this exact structure:
{{
  "translated_title": "Title in {language_name}",
  "translated_content": "Full article in {language_name}",
  "cultural_adaptations": ["Specific adaptations made (in English for editor reference)"],
  "tone_score": 0.95,
  "notes": "Any important translator notes"
}}"""
        data = _parse(_call(prompt), {})
    else:
        # Demo mode — use pre-built translations or generic response
        demo = DEMO_TRANSLATIONS.get(target_language, {})
        data = {
            "translated_title": demo.get("title", f"[{language_name}] {title}"),
            "translated_content": demo.get("content", f"[{language_name} translation of: {content[:200]}...]"),
            "cultural_adaptations": demo.get("adaptations", [
                f"Formal {language_name} broadcast tone applied",
                "Units converted to metric system",
                "Cultural references adapted for regional audience"
            ]),
            "tone_score": round(random.uniform(0.88, 0.97), 2),
            "notes": f"Auto-translated to {language_name} with cultural adaptation by AI Newsroom Assistant"
        }

    return {
        "language_code": target_language,
        "language_name": language_name,
        "translated_title": data.get("translated_title", title),
        "translated_content": data.get("translated_content", content),
        "cultural_adaptations": data.get("cultural_adaptations", []),
        "tone_score": data.get("tone_score", 0.88),
        "notes": data.get("notes", ""),
        "status": "pending_review"
    }


def analyze_sensitivity(title: str, content: str) -> dict:
    if not DEMO_MODE:
        prompt = f"""Analyze this news article for sensitive content that requires editorial review before broadcasting.

TITLE: {title}
CONTENT: {content}

Analyze for: violence, political bias, religious sensitivity, privacy violations,
hate speech, legal risks (defamation, sub judice), misinformation, national security.

Return JSON:
{{
  "overall_level": "safe|low|medium|high|critical",
  "safe_to_publish": true,
  "flags": [
    {{
      "category": "Category name",
      "description": "What was found and why it is flagged",
      "severity": "safe|low|medium|high|critical",
      "flagged_text": "The specific text that triggered this flag"
    }}
  ],
  "recommendation": "Specific editorial recommendation"
}}"""
        data = _parse(_call(prompt), {})
    else:
        # Demo mode — smart rule-based sensitivity check
        text_lower = (title + " " + content).lower()
        flags = []

        if any(w in text_lower for w in ["killed", "dead", "death", "casualties", "wounded"]):
            flags.append({
                "category": "Violence",
                "description": "Content references casualties or fatalities — verify numbers with official sources before broadcast",
                "severity": "medium",
                "flagged_text": "casualties reported"
            })

        if any(w in text_lower for w in ["government failed", "government's fault", "corruption"]):
            flags.append({
                "category": "Political Bias",
                "description": "Language may imply government culpability — use neutral phrasing",
                "severity": "low",
                "flagged_text": "government response"
            })

        if any(w in text_lower for w in ["tsunami", "evacuate", "warning", "alert"]):
            flags.append({
                "category": "Public Safety",
                "description": "Emergency safety information — verify with NDMA/IMD before broadcasting",
                "severity": "low",
                "flagged_text": "evacuation warning"
            })

        overall = "safe"
        if flags:
            severities = [f["severity"] for f in flags]
            if "critical" in severities:
                overall = "critical"
            elif "high" in severities:
                overall = "high"
            elif "medium" in severities:
                overall = "medium"
            else:
                overall = "low"

        data = {
            "overall_level": overall,
            "safe_to_publish": overall not in ["high", "critical"],
            "flags": flags,
            "recommendation": (
                "Content is suitable for broadcast after standard editorial review."
                if overall in ["safe", "low"]
                else "Editorial review required before broadcasting. Verify flagged content with official sources."
            )
        }

    return {
        "overall_level": data.get("overall_level", "safe"),
        "flags": data.get("flags", []),
        "recommendation": data.get("recommendation", "Content appears suitable for publication."),
        "safe_to_publish": data.get("safe_to_publish", True)
    }


def adapt_cultural_references(content: str, target_language: str, language_name: str) -> dict:
    if not DEMO_MODE:
        prompt = f"""Review this translated {language_name} news content for deeper cultural adaptation.

CONTENT: {content}

Improve: currency/unit conversions, date formats, name transliterations, idioms, local context.

Return JSON:
{{
  "adapted_content": "Culturally adapted content",
  "changes": ["Specific changes made"],
  "cultural_context_added": ["Context explanations added"]
}}"""
        return _parse(_call(prompt), {"adapted_content": content, "changes": [], "cultural_context_added": []})

    return {
        "adapted_content": content,
        "changes": [
            "Miles converted to kilometres",
            "Date format adapted to regional standard",
            "Proper noun transliterations verified"
        ],
        "cultural_context_added": [f"Regional broadcast conventions for {language_name} applied"]
    }


def generate_summary(title: str, content: str, language: str = "en") -> str:
    if not DEMO_MODE:
        lang_label = "English" if language == "en" else language
        prompt = f"""Create a concise 2-sentence broadcast-ready summary in {lang_label}.

TITLE: {title}
CONTENT: {content}

Return only the summary text, no JSON, no explanation."""
        return _call(prompt)

    sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
    return '. '.join(sentences[:2]) + '.' if len(sentences) >= 2 else content[:200]


def check_journalistic_tone(content: str, language_name: str) -> dict:
    if not DEMO_MODE:
        prompt = f"""Evaluate this {language_name} news content for journalistic quality and tone.

CONTENT: {content}

Return JSON:
{{
  "tone_score": 0.95,
  "issues": ["Tone/style issues found"],
  "suggestions": ["Specific improvement suggestions"],
  "is_broadcast_ready": true
}}"""
        return _parse(_call(prompt), {
            "tone_score": 0.85, "issues": [], "suggestions": [], "is_broadcast_ready": True
        })

    return {
        "tone_score": round(random.uniform(0.87, 0.96), 2),
        "issues": [],
        "suggestions": ["Maintain third-person perspective throughout", "Verify all statistics with official sources"],
        "is_broadcast_ready": True
    }


def generate_multi_format(title: str, content: str, language_name: str = "English") -> dict:
    if not DEMO_MODE:
        prompt = f"""Generate multiple broadcast-ready formats for this news article in {language_name}.

TITLE: {title}
CONTENT: {content}

Return JSON:
{{
  "push_alert": "Mobile push notification (max 60 chars)",
  "social_caption": "Social media post with hashtags (max 280 chars)",
  "teleprompter_script": "Full teleprompter script for news anchor (natural spoken language, 2-3 paragraphs)",
  "sms_alert": "SMS emergency alert (max 160 chars)",
  "headline_ticker": "Breaking news ticker text (max 80 chars)",
  "radio_intro": "30-second radio bulletin intro (natural spoken word)"
}}"""
        return _parse(_call(prompt), {})

    LANG_NAME_TO_CODE = {
        "Hindi":"hi","Tamil":"ta","Telugu":"te","Bengali":"bn","Marathi":"mr",
        "Gujarati":"gu","Kannada":"kn","Malayalam":"ml","Punjabi":"pa","Odia":"or",
        "French":"fr","Spanish":"es","Arabic":"ar","Chinese":"zh","Japanese":"ja"
    }
    lc = LANG_NAME_TO_CODE.get(language_name)
    trans = DEMO_TRANSLATIONS.get(lc, {}) if lc else {}
    t = trans.get("title", title)
    c = trans.get("content", content)
    short_t = t[:55] + "..." if len(t) > 55 else t
    ticker = t[:75] + "..." if len(t) > 75 else t
    return {
        "push_alert": f"🔴 {short_t}",
        "social_caption": f"🚨 {t}\n\n{c[:220]}...\n\n#AINewsroom #ByteBreakTeam #CODEX2025",
        "teleprompter_script": f"{t}.\n\n{c}\n\nAI Newsroom पर आपका स्वागत है। यह रिपोर्ट Byte Break Team द्वारा प्रस्तुत की गई।" if lc in ("hi","mr") else f"{t}.\n\n{c}\n\nThis has been a special report from AI Newsroom by Byte Break Team.",
        "sms_alert": f"ALERT: {t[:130]}...",
        "headline_ticker": f"BREAKING: {ticker}",
        "radio_intro": f"{t}. {c[:200]}. AI Newsroom, Byte Break Team."
    }


def chat_with_assistant(message: str, context: str = "") -> str:
    if not DEMO_MODE:
        prompt = f"""You are an AI Newsroom Assistant chatbot helping users understand and use the AI Newsroom platform.

Platform context:
- AI-powered Real-Time Content Localization platform
- Uses Google Gemini 2.0 Flash for AI processing
- Features: transcription cleaning, sensitivity analysis, multilingual translation (14 languages), cultural adaptation, readiness scoring, multi-format publishing, MCP connector
- Backend: FastAPI (Python), Frontend: React with WebSocket
- Languages: Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Spanish, French, Arabic, Mandarin, Japanese

{f'Context: {context}' if context else ''}

User question: {message}

Answer helpfully and concisely."""
        return _call(prompt)

    # Demo mode chatbot
    msg = message.lower()
    if any(w in msg for w in ["language", "languages", "supported"]):
        return "We support 14 languages: Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Spanish, French, Arabic, Mandarin, and Japanese. Each translation includes cultural adaptation specific to that region's broadcast journalism standards."
    elif any(w in msg for w in ["pipeline", "how", "work", "process"]):
        return "The AI pipeline has 5 steps: (1) Ingest & transcription cleanup, (2) Sensitivity analysis across 8 categories, (3) Translation to all selected languages with cultural adaptation, (4) Editorial review with approve/reject workflow, (5) Multi-format publishing — push alert, social, SMS, ticker, teleprompter, and radio intro. Each step fires a real-time WebSocket event to the dashboard."
    elif any(w in msg for w in ["sensitivity", "flag", "sensitive"]):
        return "Sensitivity analysis checks 8 categories: Violence, Political Bias, Religious Sensitivity, Privacy Violations, Hate Speech, Legal Risk (defamation/sub judice), Misinformation, and National Security. Each flag shows the specific text that triggered it, severity level (safe/low/medium/high/critical), and editorial recommendations."
    elif any(w in msg for w in ["readiness", "score", "ready"]):
        return "The Audience Readiness Score (0-100) is a weighted composite: Sensitivity 35%, Translation Tone 30%, Completion Rate 25%, Source Attribution 10%. Score 80+ = Ready, 60-79 = Needs Review, 40-59 = High Risk, below 40 = Not Ready. This prevents editorial mistakes before broadcast."
    elif any(w in msg for w in ["ingest", "add", "submit", "article"]):
        return "Go to the Ingest page, paste your raw broadcast transcript, select target languages, add the source/wire service, choose a category, and click 'Start AI Pipeline'. The system automatically cleans the transcript, runs sensitivity analysis, and generates translations. You'll see real-time updates on the dashboard."
    elif any(w in msg for w in ["mcp", "model context", "protocol", "tool"]):
        return "MCP (Model Context Protocol) by Anthropic lets AI agents interact with our newsroom programmatically. We expose 6 tools: list_articles, get_article, analyze_article_sensitivity, get_pipeline_stats, ingest_article, and get_translations. Call GET /mcp/tools to see all tools, POST /mcp/execute to run them."
    elif any(w in msg for w in ["api", "key", "gemini"]):
        return "Get a free Gemini API key from aistudio.google.com — it starts with 'AIza'. Add it to backend/.env as GEMINI_API_KEY=AIzaSy... Currently running in Demo Mode with smart mock responses. All features work — AI calls return realistic pre-built data."
    elif any(w in msg for w in ["format", "publish", "broadcast"]):
        return "Multi-Format Publishing generates 6 outputs: Push Alert (60 chars), Social Caption (280 chars with hashtags), SMS Alert (160 chars), Headline Ticker (80 chars), Teleprompter Script (2-3 paragraphs for anchors), and Radio Intro (30 seconds). Available in the Broadcast Studio for each approved article."
    else:
        return f"Great question! The AI Newsroom Assistant handles real-time multilingual content localization for broadcast news. It transcribes, translates into 14 languages with cultural adaptation, analyzes sensitivity, and publishes across 6 formats — all with editorial approval before going live. Currently running in Demo Mode. Ask me about languages, pipeline, sensitivity analysis, readiness score, or MCP connector!"


def calculate_readiness_score(article: dict) -> dict:
    sensitivity = article.get("sensitivity", {}) or {}
    translations = article.get("translations", [])
    target_langs = article.get("target_languages", [])

    sev_map = {"safe": 1.0, "low": 0.85, "medium": 0.65, "high": 0.35, "critical": 0.0}
    sev_score = sev_map.get(sensitivity.get("overall_level", "safe"), 0.8)
    avg_tone = sum(t.get("tone_score", 0.8) for t in translations) / len(translations) if translations else 0.0
    completion = len(translations) / len(target_langs) if target_langs else 0.0
    has_source = 1.0 if article.get("source") and article["source"] != "Manual Input" else 0.7

    score = round((sev_score * 0.35 + avg_tone * 0.30 + completion * 0.25 + has_source * 0.10) * 100)

    if score >= 80:
        label, color = "Ready", "green"
    elif score >= 60:
        label, color = "Needs Review", "yellow"
    elif score >= 40:
        label, color = "High Risk", "orange"
    else:
        label, color = "Not Ready", "red"

    issues = []
    if sev_score < 0.65:
        issues.append(f"Sensitivity is {sensitivity.get('overall_level','unknown')} — review required")
    if avg_tone < 0.75:
        issues.append("Tone below broadcast standard — retranslation recommended")
    if completion < 0.8:
        issues.append(f"Only {len(translations)}/{len(target_langs)} translations complete")
    if not article.get("source") or article["source"] == "Manual Input":
        issues.append("Source not attributed — add wire/agency before publishing")

    return {
        "score": score, "label": label, "color": color, "issues": issues,
        "breakdown": {
            "sensitivity": round(sev_score * 100),
            "tone": round(avg_tone * 100),
            "completion": round(completion * 100),
            "attribution": round(has_source * 100)
        }
    }
