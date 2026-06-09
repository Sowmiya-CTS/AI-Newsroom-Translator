import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional


# In-memory store for hackathon demo (replace with PostgreSQL in production)
_articles: Dict[str, dict] = {}


def generate_id() -> str:
    return str(uuid.uuid4())[:8].upper()


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def create_article(data: dict) -> dict:
    article_id = generate_id()
    article = {
        "id": article_id,
        "title": data["title"],
        "content": data["content"],
        "source": data.get("source", "Manual Input"),
        "category": data.get("category", "General"),
        "priority": data.get("priority", "normal"),
        "target_languages": data.get("target_languages", ["hi", "ta", "te", "bn"]),
        "status": "pending",
        "sensitivity": None,
        "translations": [],
        "editor_notes": [],
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    _articles[article_id] = article
    return article


def get_article(article_id: str) -> Optional[dict]:
    return _articles.get(article_id)


def get_all_articles() -> List[dict]:
    return sorted(_articles.values(), key=lambda x: x["created_at"], reverse=True)


def update_article(article_id: str, updates: dict) -> Optional[dict]:
    if article_id not in _articles:
        return None
    _articles[article_id].update(updates)
    _articles[article_id]["updated_at"] = now_iso()
    return _articles[article_id]


def add_translation(article_id: str, translation: dict) -> bool:
    if article_id not in _articles:
        return False
    translations = _articles[article_id].get("translations", [])
    existing = next((t for t in translations if t["language_code"] == translation["language_code"]), None)
    if existing:
        translations.remove(existing)
    translations.append(translation)
    _articles[article_id]["translations"] = translations
    _articles[article_id]["updated_at"] = now_iso()
    return True


def get_stats() -> dict:
    articles = list(_articles.values())
    return {
        "total": len(articles),
        "pending": sum(1 for a in articles if a["status"] == "pending"),
        "processing": sum(1 for a in articles if a["status"] == "processing"),
        "review": sum(1 for a in articles if a["status"] == "review"),
        "approved": sum(1 for a in articles if a["status"] == "approved"),
        "published": sum(1 for a in articles if a["status"] == "published"),
        "rejected": sum(1 for a in articles if a["status"] == "rejected"),
        "total_translations": sum(len(a.get("translations", [])) for a in articles),
        "critical_flags": sum(
            1 for a in articles
            if a.get("sensitivity") and a["sensitivity"].get("overall_level") in ["high", "critical"]
        ),
    }


def _seed_sample_data():
    from datetime import timedelta
    b = datetime.utcnow()
    def ts(h): return (b - timedelta(hours=h)).isoformat() + "Z"

    DATA = [
        {
            "id": "ART001",
            "title": "Major Earthquake Strikes Off Japan Coast — Tsunami Warning Issued",
            "content": "A powerful earthquake measuring 7.2 on the Richter scale struck off the northeastern coast of Japan at 5:48 AM local time. The Japan Meteorological Agency immediately issued a tsunami warning for coastal prefectures including Iwate, Miyagi, and Fukushima. Residents within one kilometer of the coast have been ordered to evacuate to higher ground. The epicenter was located approximately 80 kilometers east of Sendai at a depth of 35 kilometers. Emergency response teams have been deployed to affected areas. At least 12 injuries have been reported in Sendai city. The government has convened an emergency response committee. International agencies including the Pacific Tsunami Warning Center have extended warnings to neighboring countries.",
            "source": "AP Wire / NHK", "category": "International", "priority": "breaking",
            "target_languages": ["hi","ta","te","bn","mr","es"],
            "status": "published",
            "sensitivity": {
                "overall_level": "medium",
                "flags": [{"category": "Public Safety", "description": "Active tsunami warning with mandatory evacuation orders", "severity": "medium", "flagged_text": "tsunami warning"}],
                "recommendation": "Verify current tsunami warning status before broadcast. Ensure evacuation guidance is updated.",
                "safe_to_publish": True
            },
            "translations": [
                {"language_code":"hi","language_name":"Hindi","translated_title":"जापान तट के पास 7.2 तीव्रता का भूकंप, सुनामी चेतावनी जारी","translated_content":"जापान के उत्तरपूर्वी तट पर आज सुबह 5:48 बजे 7.2 तीव्रता का शक्तिशाली भूकंप आया। जापान मौसम विज्ञान एजेंसी ने इवाते, मियागी और फुकुशिमा प्रांतों के लिए सुनामी चेतावनी जारी की है। तटीय क्षेत्रों के नागरिकों को ऊंचे स्थानों पर जाने का आदेश दिया गया है। सेंदाई शहर में 12 से अधिक लोग घायल हुए हैं।","cultural_adaptations":["किलोमीटर में दूरी","हिंदी पत्रकारिता शैली","NDRF प्रतिक्रिया संदर्भ"],"tone_score":0.88,"status":"approved"},
                {"language_code":"ta","language_name":"Tamil","translated_title":"ஜப்பான் கடற்கரையில் 7.2 ரிக்டர் அதிர்வு — சுனாமி எச்சரிக்கை","translated_content":"ஜப்பானின் வடகிழக்கு கடற்கரைப் பகுதியில் இன்று அதிகாலை 5:48 மணிக்கு 7.2 ரிக்டர் அளவிலான நிலநடுக்கம் ஏற்பட்டது. ஜப்பான் வானிலை முன்னறிவிப்பு நிறுவனம் இவாட்டே, மியாகி மற்றும் புகுஷிமா மாகாணங்களுக்கு சுனாமி எச்சரிக்கை விடுத்துள்ளது.","cultural_adaptations":["தமிழ் செய்தி ஊடக நடை","அலகுகள் மாற்றம்"],"tone_score":0.86,"status":"approved"},
                {"language_code":"te","language_name":"Telugu","translated_title":"జపాన్ తీరంలో 7.2 తీవ్రత భూకంపం — సునామీ హెచ్చరిక జారీ","translated_content":"జపాన్ వాయువ్య తీరం వద్ద ఈరోజు తెల్లవారుజామున 5:48కి 7.2 తీవ్రత భూకంపం సంభవించింది. జపాన్ వాతావరణ సంస్థ సునామీ హెచ్చరిక జారీ చేసింది. సెందాయ్‌లో 12 మంది గాయపడ్డారు.","cultural_adaptations":["తెలుగు పత్రికా విధానం"],"tone_score":0.85,"status":"approved"},
                {"language_code":"bn","language_name":"Bengali","translated_title":"জাপান উপকূলে ৭.২ মাত্রার ভূমিকম্প — সুনামি সতর্কতা জারি","translated_content":"জাপানের উত্তর-পূর্ব উপকূলে ভোর ৫:৪৮টায় ৭.২ মাত্রার শক্তিশালী ভূমিকম্প আঘাত হেনেছে। জাপানের আবহাওয়া সংস্থা সুনামি সতর্কতা জারি করেছে।","cultural_adaptations":["বাংলা পত্রিকার ভাষারীতি"],"tone_score":0.87,"status":"approved"},
                {"language_code":"mr","language_name":"Marathi","translated_title":"जपानच्या किनारपट्टीजवळ ७.२ तीव्रतेचा भूकंप — त्सुनामी इशारा जारी","translated_content":"जपानच्या ईशान्य किनारपट्टीवर आज पहाटे ५:४८ वाजता ७.२ तीव्रतेचा भूकंप झाला. त्सुनामीचा इशारा जारी करण्यात आला आहे. सेंदाई शहरात १२ जण जखमी झाले आहेत.","cultural_adaptations":["मराठी पत्रकारिता शैली"],"tone_score":0.84,"status":"approved"},
                {"language_code":"es","language_name":"Spanish","translated_title":"Terremoto de magnitud 7.2 sacude la costa de Japón — Alerta de tsunami emitida","translated_content":"Un potente terremoto de magnitud 7.2 sacudió la costa nororiental de Japón a las 5:48 de la mañana. La Agencia Meteorológica de Japón emitió una alerta de tsunami para las prefecturas de Iwate, Miyagi y Fukushima. Al menos 12 heridos en Sendai.","cultural_adaptations":["Estilo periodístico formal","Sistema métrico"],"tone_score":0.89,"status":"approved"}
            ],
            "editor_notes": [{"note": "Verified with JMA official release", "action": "approve"}],
            "created_at": ts(7), "updated_at": ts(2)
        },
        {
            "id": "ART002",
            "title": "PM Announces $50 Billion Green Economy Package to Create 2 Million Jobs",
            "content": "The Prime Minister today unveiled a landmark $50 billion Green Economy Package aimed at revitalizing domestic manufacturing and creating 2 million jobs over five years. The package includes tax incentives for clean energy businesses, $20 billion in green infrastructure investment, and subsidies for electric vehicle adoption. The Finance Minister stated the initiative will position the country as a global leader in sustainable development. Opposition parties have called for independent scrutiny of the promised job creation figures.",
            "source": "Reuters / PTI", "category": "Politics", "priority": "high",
            "target_languages": ["hi","ta","bn","mr"],
            "status": "published",
            "sensitivity": {
                "overall_level": "low",
                "flags": [{"category": "Political Balance", "description": "Opposition criticism mentioned — ensure equal coverage", "severity": "low", "flagged_text": "Opposition parties"}],
                "recommendation": "Balanced coverage achieved. Verify job creation methodology with Finance Ministry.",
                "safe_to_publish": True
            },
            "translations": [
                {"language_code":"hi","language_name":"Hindi","translated_title":"प्रधानमंत्री ने 50 अरब डॉलर का हरित अर्थव्यवस्था पैकेज घोषित किया","translated_content":"प्रधानमंत्री ने आज 50 अरब डॉलर के हरित अर्थव्यवस्था पैकेज की घोषणा की। इससे पांच साल में 20 लाख रोजगार सृजित होंगे। स्वच्छ ऊर्जा व्यवसायों को कर में छूट और 20 अरब डॉलर की हरित बुनियादी ढांचे में निवेश शामिल है।","cultural_adaptations":["अरब/बिलियन रूपांतरण","हिंदी आर्थिक पत्रकारिता शैली"],"tone_score":0.91,"status":"approved"},
                {"language_code":"ta","language_name":"Tamil","translated_title":"பிரதமர் 50 பில்லியன் டாலர் பசுமை பொருளாதார திட்டத்தை அறிவித்தனர்","translated_content":"பிரதமர் இன்று 50 பில்லியன் டாலர் மதிப்பிலான பசுமை பொருளாதார திட்டத்தை அறிவித்தனர். இந்த திட்டம் ஐந்து ஆண்டுகளில் 20 லட்சம் வேலைவாய்ப்புகளை உருவாக்கும்.","cultural_adaptations":["தமிழ் பொருளாதார செய்தி நடை"],"tone_score":0.88,"status":"approved"},
                {"language_code":"bn","language_name":"Bengali","translated_title":"প্রধানমন্ত্রী ৫০ বিলিয়ন ডলারের সবুজ অর্থনীতি প্যাকেজ ঘোষণা করলেন","translated_content":"প্রধানমন্ত্রী আজ ৫০ বিলিয়ন ডলারের সবুজ অর্থনীতি প্যাকেজ ঘোষণা করেছেন। এই প্যাকেজে পাঁচ বছরে ২০ লাখ কর্মসংস্থান সৃষ্টির পরিকল্পনা রয়েছে।","cultural_adaptations":["বাংলা অর্থনৈতিক সংবাদ শৈলী"],"tone_score":0.87,"status":"approved"},
                {"language_code":"mr","language_name":"Marathi","translated_title":"पंतप्रधानांनी ५० अब्ज डॉलरचे हरित अर्थव्यवस्था पॅकेज जाहीर केले","translated_content":"पंतप्रधानांनी आज ५० अब्ज डॉलरच्या हरित अर्थव्यवस्था पॅकेजची घोषणा केली. पाच वर्षांत २० लाख रोजगार निर्मिती होणार असल्याचे सांगण्यात आले.","cultural_adaptations":["मराठी आर्थिक पत्रकारिता भाषा"],"tone_score":0.86,"status":"approved"}
            ],
            "editor_notes": [{"note": "Cross-checked with Finance Ministry press release", "action": "approve"}],
            "created_at": ts(5), "updated_at": ts(3)
        },
        {
            "id": "ART003",
            "title": "India Clinches ICC Cricket World Cup in Historic Final — Nation Celebrates",
            "content": "In one of the most dramatic finals in cricket history, India defeated Australia by 4 wickets in the ICC Cricket World Cup final held at Lord's Cricket Ground, London. Captain Rohit Sharma's explosive 89 off 64 balls set up the chase, while Virat Kohli's composed 47 sealed the victory with 3 overs to spare. This is India's third World Cup title. Millions of fans celebrated across the country as fireworks lit up major cities. The Prime Minister congratulated the team and declared a national holiday tomorrow.",
            "source": "ESPN / BCCI", "category": "Sports", "priority": "breaking",
            "target_languages": ["hi","ta","te","bn","mr"],
            "status": "published",
            "sensitivity": {"overall_level": "safe", "flags": [], "recommendation": "Content is safe for broadcast. Positive sporting achievement.", "safe_to_publish": True},
            "translations": [
                {"language_code":"hi","language_name":"Hindi","translated_title":"भारत ने ऐतिहासिक ICC क्रिकेट विश्व कप जीता, ऑस्ट्रेलिया को 4 विकेट से हराया","translated_content":"क्रिकेट इतिहास के सबसे रोमांचक फाइनल में भारत ने ऑस्ट्रेलिया को 4 विकेट से हराकर ICC विश्व कप जीत लिया। कप्तान रोहित शर्मा ने 64 गेंदों पर 89 रन बनाए। विराट कोहली के 47 रनों से जीत पक्की हुई। देशभर में जश्न का माहौल है।","cultural_adaptations":["क्रिकेट शब्दावली हिंदी में","खिलाड़ियों के पूरे नाम"],"tone_score":0.93,"status":"approved"},
                {"language_code":"ta","language_name":"Tamil","translated_title":"இந்தியா ICC உலகக்கோப்பையை வென்றது — வரலாற்றுச் சாதனை","translated_content":"கிரிக்கெட் வரலாற்றின் மிகவும் நாடகமான இறுதிப்போட்டியில் இந்தியா ஆஸ்திரேலியாவை 4 விக்கெட் வித்தியாசத்தில் வென்றது. அணித் தலைவர் ரோஹித் சர்மா 64 பந்தில் 89 ரன்கள் எடுத்தார்.","cultural_adaptations":["தமிழ் விளையாட்டு சொல்லாட்சி"],"tone_score":0.91,"status":"approved"},
                {"language_code":"te","language_name":"Telugu","translated_title":"భారత్ ICC క్రికెట్ వరల్డ్ కప్ గెలిచింది — చారిత్రాత్మక విజయం","translated_content":"క్రికెట్ చరిత్రలో అత్యంత రసవత్తరమైన ఫైనల్‌లో భారత్ ఆస్ట్రేలియాను 4 వికెట్లతో ఓడించింది. కెప్టెన్ రోహిత్ శర్మ 64 బంతుల్లో 89 పరుగులు చేశారు.","cultural_adaptations":["తెలుగు క్రీడా పత్రికా శైలి"],"tone_score":0.90,"status":"approved"},
                {"language_code":"bn","language_name":"Bengali","translated_title":"ভারত ICC ক্রিকেট বিশ্বকাপ জিতল — ঐতিহাসিক মুহূর্ত","translated_content":"ক্রিকেট ইতিহাসের সবচেয়ে নাটকীয় ফাইনালে ভারত অস্ট্রেলিয়াকে ৪ উইকেটে হারিয়ে ICC বিশ্বকাপ জিতেছে। অধিনায়ক রোহিত শর্মা ৬৪ বলে ৮৯ রান করেছেন।","cultural_adaptations":["বাংলা ক্রিকেট সংবাদ শৈলী"],"tone_score":0.92,"status":"approved"},
                {"language_code":"mr","language_name":"Marathi","translated_title":"भारताने ICC क्रिकेट विश्वचषक जिंकला — ऐतिहासिक विजय","translated_content":"क्रिकेट इतिहासातील सर्वात रोमहर्षक फायनलमध्ये भारताने ऑस्ट्रेलियाला ४ विकेटने पराभूत केले. कर्णधार रोहित शर्माने ६४ चेंडूत ८९ धावा केल्या.","cultural_adaptations":["मराठी क्रीडा पत्रकारिता शैली"],"tone_score":0.91,"status":"approved"}
            ],
            "editor_notes": [{"note": "High public interest — fast-tracked for broadcast", "action": "approve"}],
            "created_at": ts(3), "updated_at": ts(1)
        },
        {
            "id": "ART004",
            "title": "Climate Summit: 150 Nations Sign Historic Net-Zero Carbon Accord in Geneva",
            "content": "In a landmark achievement for global climate diplomacy, representatives from 150 nations signed the Geneva Carbon Accord at the conclusion of the 48-hour emergency climate summit. The agreement mandates net-zero emissions by 2045, phasing out coal-fired power plants by 2035, and establishing a $200 billion climate adaptation fund for developing nations. Environmental groups called it a turning point for humanity. Critics from oil-producing nations warned of economic disruption and demanded longer transition timelines. The accord will require ratification by member state parliaments.",
            "source": "Reuters / AFP", "category": "International", "priority": "high",
            "target_languages": ["hi","es","fr","ar"],
            "status": "review",
            "sensitivity": {
                "overall_level": "low",
                "flags": [{"category": "Political Balance", "description": "Dissenting views from oil-producing nations included", "severity": "low", "flagged_text": "Critics from oil-producing nations"}],
                "recommendation": "Balanced coverage achieved. Verify carbon accord details with UN official sources before broadcast.",
                "safe_to_publish": True
            },
            "translations": [
                {"language_code":"hi","language_name":"Hindi","translated_title":"जलवायु शिखर सम्मेलन: 150 देशों ने ऐतिहासिक कार्बन समझौते पर हस्ताक्षर किए","translated_content":"150 देशों के प्रतिनिधियों ने जिनेवा कार्बन समझौते पर हस्ताक्षर किए। समझौते के तहत 2045 तक नेट जीरो उत्सर्जन और 2035 तक कोयला बिजली संयंत्रों को बंद करना अनिवार्य होगा।","cultural_adaptations":["हिंदी जलवायु नीति शब्दावली"],"tone_score":0.87,"status":"pending_review"},
                {"language_code":"es","language_name":"Spanish","translated_title":"Cumbre climática: 150 naciones firman histórico acuerdo de carbono en Ginebra","translated_content":"Representantes de 150 naciones firmaron el Acuerdo de Carbono de Ginebra. El acuerdo exige emisiones netas cero para 2045 y la eliminación gradual de las centrales eléctricas de carbón para 2035.","cultural_adaptations":["Terminología climática en español formal"],"tone_score":0.89,"status":"pending_review"},
                {"language_code":"fr","language_name":"French","translated_title":"Sommet climatique : 150 nations signent un accord historique sur le carbone à Genève","translated_content":"Des représentants de 150 nations ont signé l'Accord de Carbone de Genève. L'accord exige des émissions nettes nulles d'ici 2045 et l'élimination progressive des centrales au charbon d'ici 2035.","cultural_adaptations":["Style journalistique français formel"],"tone_score":0.88,"status":"pending_review"},
                {"language_code":"ar","language_name":"Arabic","translated_title":"قمة المناخ: 150 دولة توقع اتفاقية الكربون التاريخية في جنيف","translated_content":"وقّع ممثلو 150 دولة على اتفاقية الكربون الجنيفية. وتلزم الاتفاقية بتحقيق صافي انبعاثات صفري بحلول عام 2045 والتخلص التدريجي من محطات الطاقة التي تعمل بالفحم بحلول 2035.","cultural_adaptations":["الأسلوب الصحفي العربي الرسمي","اتجاه النص من اليمين إلى اليسار"],"tone_score":0.86,"status":"pending_review"}
            ],
            "editor_notes": [],
            "created_at": ts(2), "updated_at": ts(1)
        },
        {
            "id": "ART005",
            "title": "Leading Tech Firm Unveils Next-Gen AI Model — Claims Human-Level Reasoning",
            "content": "A leading technology company unveiled its next-generation artificial intelligence model, claiming it achieves human-level reasoning across mathematics, coding, and creative writing tasks. The model reportedly outperforms existing benchmarks by 40%. Industry analysts note this could accelerate AI adoption across healthcare, education, and journalism. The company plans to integrate the model into consumer products by Q3. Regulatory bodies in the EU and US have announced reviews of the claims.",
            "source": "TechCrunch / Bloomberg", "category": "Technology", "priority": "high",
            "target_languages": ["hi","ta","te","bn","es"],
            "status": "approved",
            "sensitivity": {"overall_level": "safe", "flags": [], "recommendation": "Content is safe for broadcast. Technology news with broad public interest.", "safe_to_publish": True},
            "translations": [
                {"language_code":"hi","language_name":"Hindi","translated_title":"टेक कंपनी ने नया AI मॉडल लॉन्च किया — मानव-स्तरीय तर्कशक्ति का दावा","translated_content":"एक प्रमुख टेक कंपनी ने अपना नया आर्टिफिशियल इंटेलिजेंस मॉडल लॉन्च किया। कंपनी का दावा है कि यह गणित, कोडिंग और रचनात्मक लेखन में मानव-स्तरीय तर्कशक्ति रखता है।","cultural_adaptations":["हिंदी तकनीकी शब्दावली","भारतीय संदर्भ"],"tone_score":0.90,"status":"approved"},
                {"language_code":"ta","language_name":"Tamil","translated_title":"தொழில்நுட்ப நிறுவனம் புதிய AI மாதிரியை அறிவித்தது — மனித மட்ட சிந்தனை திறன்","translated_content":"ஒரு முன்னணி தொழில்நுட்ப நிறுவனம் அதன் அடுத்த தலைமுறை செயற்கை நுண்ணறிவு மாதிரியை அறிவித்தது. கணிதம், குறியீட்டு எழுத்து மற்றும் படைப்பு எழுத்தில் மனித மட்ட சிந்தனை திறன் அடைவதாக கூறப்படுகிறது.","cultural_adaptations":["தமிழ் தொழில்நுட்ப சொல்லாட்சி"],"tone_score":0.88,"status":"approved"},
                {"language_code":"te","language_name":"Telugu","translated_title":"టెక్ కంపెనీ కొత్త AI మోడల్ ప్రకటించింది — మానవ స్థాయి తర్కశక్తి వాదన","translated_content":"ఒక ప్రముఖ టెక్నాలజీ కంపెనీ తన తరువాతి తరం AI మోడల్‌ని ప్రకటించింది. గణితం, కోడింగ్ మరియు సృజనాత్మక రచనలో మానవ స్థాయి తర్కశక్తిని సాధించినట్లు వాదన.","cultural_adaptations":["తెలుగు సాంకేతిక పత్రికా శైలి"],"tone_score":0.87,"status":"approved"},
                {"language_code":"bn","language_name":"Bengali","translated_title":"প্রযুক্তি কোম্পানি নতুন AI মডেল উন্মোচন করল — মানব-স্তরের যুক্তির দাবি","translated_content":"একটি শীর্ষস্থানীয় প্রযুক্তি কোম্পানি তাদের পরবর্তী প্রজন্মের AI মডেল উন্মোচন করেছে। এটি গণিত, কোডিং এবং সৃজনশীল লেখায় মানব-স্তরের যুক্তি অর্জন করে বলে দাবি করা হয়েছে।","cultural_adaptations":["বাংলা প্রযুক্তি সংবাদ শৈলী"],"tone_score":0.89,"status":"approved"},
                {"language_code":"es","language_name":"Spanish","translated_title":"Empresa tecnológica presenta nueva IA con razonamiento a nivel humano","translated_content":"Una empresa tecnológica líder presentó su modelo de inteligencia artificial de próxima generación, afirmando que alcanza un razonamiento a nivel humano en matemáticas, programación y escritura creativa.","cultural_adaptations":["Terminología tecnológica en español"],"tone_score":0.91,"status":"approved"}
            ],
            "editor_notes": [{"note": "Pending broadcast slot allocation", "action": "approve"}],
            "created_at": ts(1), "updated_at": ts(0)
        },
        {
            "id": "ART006",
            "title": "Health Ministry Issues Alert on Surge in Respiratory Illness Across Three States",
            "content": "The Ministry of Health has issued a public health alert following a 300% surge in respiratory illness cases across three states over the past two weeks. The illness, characterized by high fever, severe cough, and breathing difficulties, has resulted in 847 hospitalizations. Health officials are urging citizens to wear masks in crowded places and seek immediate medical attention if symptoms develop. Three deaths have been reported among elderly patients with pre-existing conditions. Laboratories are working to identify whether this represents a new pathogen or a variant of a known virus. The WHO has been notified.",
            "source": "Health Ministry / WHO", "category": "Health", "priority": "high",
            "target_languages": ["hi","ta","bn"],
            "status": "review",
            "sensitivity": {
                "overall_level": "high",
                "flags": [
                    {"category": "Public Health Emergency", "description": "300% case surge — high public anxiety risk", "severity": "high", "flagged_text": "300% surge"},
                    {"category": "Fatality Reporting", "description": "Confirmed deaths — may cause public panic if uncontextualized", "severity": "high", "flagged_text": "Three deaths have been reported"},
                    {"category": "Medical Misinformation Risk", "description": "Unconfirmed pathogen — avoid speculation in broadcast", "severity": "medium", "flagged_text": "new pathogen or a variant"}
                ],
                "recommendation": "HOLD FOR CHIEF EDITOR REVIEW. Verify all statistics with official Ministry press release. Do not broadcast unconfirmed pathogen information.",
                "safe_to_publish": False
            },
            "translations": [
                {"language_code":"hi","language_name":"Hindi","translated_title":"स्वास्थ्य मंत्रालय ने तीन राज्यों में श्वसन रोग के बढ़ते मामलों पर अलर्ट जारी किया","translated_content":"स्वास्थ्य मंत्रालय ने तीन राज्यों में श्वसन रोग के मामलों में 300% वृद्धि के बाद सार्वजनिक स्वास्थ्य अलर्ट जारी किया है। 847 मरीज अस्पताल में भर्ती हैं। नागरिकों को भीड़-भाड़ वाली जगहों पर मास्क पहनने की सलाह दी गई है।","cultural_adaptations":["हिंदी जन स्वास्थ्य शब्दावली","AIIMS संदर्भ"],"tone_score":0.82,"status":"pending_review"},
                {"language_code":"ta","language_name":"Tamil","translated_title":"சுகாதார அமைச்சகம் மூன்று மாநிலங்களில் சுவாச நோய் அதிகரிப்பு குறித்து எச்சரிக்கை விடுத்தது","translated_content":"மூன்று மாநிலங்களில் சுவாச நோய் வழக்குகள் 300% அதிகரித்ததால் சுகாதார அமைச்சகம் பொது சுகாதார எச்சரிக்கை விடுத்துள்ளது. 847 பேர் மருத்துவமனையில் அனுமதிக்கப்பட்டுள்ளனர்.","cultural_adaptations":["தமிழ் மருத்துவ செய்தி நடை"],"tone_score":0.80,"status":"pending_review"},
                {"language_code":"bn","language_name":"Bengali","translated_title":"স্বাস্থ্য মন্ত্রণালয় তিন রাজ্যে শ্বাসযন্ত্রের রোগ বৃদ্ধি নিয়ে সতর্কতা জারি করেছে","translated_content":"তিনটি রাজ্যে শ্বাসযন্ত্রের রোগের ঘটনা ৩০০% বৃদ্ধির পর স্বাস্থ্য মন্ত্রণালয় জনস্বাস্থ্য সতর্কতা জারি করেছে। ৮৪৭ জন রোগী হাসপাতালে ভর্তি হয়েছেন।","cultural_adaptations":["বাংলা জনস্বাস্থ্য সংবাদ শৈলী"],"tone_score":0.81,"status":"pending_review"}
            ],
            "editor_notes": [],
            "created_at": ts(0), "updated_at": ts(0)
        }
    ]

    for item in DATA:
        _articles[item["id"]] = item


_seed_sample_data()
