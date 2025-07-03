from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# Setup Gemini
genai.configure(api_key="AIzaSyAnmeaCHexhdi_GE-70ZzXQiUZ_xMc5HlY")  # Replace with secure method in production
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Default fallback feedback
# DEFAULT_FEEDBACK = (
#     "Siz bizning so‘rovnomada qatnashdingiz — bu esa siz IT sohasiga befarq emassiz degani. "
#     "IT bugungi kunda eng tez rivojlanayotgan va hayotning deyarli barcha sohalarini qamrab olayotgan yo‘nalishlardan biridir. "
#     "Siz qanday darajada bo‘lishingizdan qat’i nazar, har bir inson o‘z sharoitiga mos ravishda bilim olishi mumkin. "
#     "Masofaviy o‘quv platformalari, bepul darslar va amaliy kurslar orqali siz ham o‘z imkoniyatlaringizni kengaytirishingiz mumkin. "
#     "Shuning bilan birgalikda hulosalar ohirida bilimlaringizni rivojlantirish va vaqtingizni tejash uchun IT Ta’lim Uyushmasi tomonidan taqdim etilayotgan "
#     "Coursera kurslari sizning IT ko‘nikmalaringizga mos ravishda tavsiya etiladi."
# )

# Questions in 3 languages

question_sets = {
    "uz": [
        "1. IT sohasida ko‘proq bilim olishga qiziqasizmi?", 
        "2. Sizningcha, IT-ko‘nikmalarni yaxshilash ishingiz/o‘qishingiz/hayotingiz sifatini oshirishi mumkinmi?",
        "3. Siz hozirda IT va raqamli ko'nikmalaringiz darajasini qanday baholaysiz?",
        "4. IT sohasini chuqurroq o‘rganishingizga nimalar to‘sqinlik qiladi?",
        "5. Yaqin-atrofda bepul kurslar taqdim etilsa, qatnasharmidingiz?"
    ],
    "ru": [
        "1. Интересуетесь ли вы изучением IT (например, программирование, цифровые навыки)?",
        "2. Считаете ли вы, что улучшение IT-навыков может повысить качество вашей жизни/работы/учёбы?",
        "3. Как вы оцениваете свои текущие IT и цифровые навыки?",
        "4. Что мешает вам углубленно изучать IT?",
        "5. Если поблизости предложат бесплатные курсы, вы будете участвовать?"
    ],
    "en": [
        "1. Are you interested in learning more about IT (e.g., programming, digital tools)?",
        "2. Do you think improving your IT skills can improve your job/study/life?",
        "3. How would you rate your current IT and digital skills?",
        "4. What prevents you from studying IT more deeply?",
        "5. If free IT courses were available nearby, would you attend?"
    ]
}

# Prompt templates per language
prompts = {
    "uz": """Siz respondentlarning so‘rov javoblari asosida foydalanuvchiga qisqa, motivatsion, samimiy va foydali tavsiya beradigan sun’iy intellektsiz. Quyidagi javoblarga qarab 2-3 gaplik xulosa yozing. Salomlashish yoki rasmiy gaplar bo‘lmasin. Yozgan tavsiyangiz respondentning darajasiga mos bo‘lsin. Oxirida buni qo‘shing: 
"Shuning bilan birgalikda hulosalar ohirida bilimlaringizni rivojlantirish va vaqtingizni tejash uchun  Coursera kurslari sizning IT ko‘nikmalaringizga mos ravishda tavsiya etiladi."\n\n""",

    "ru": """Вы — ИИ, анализирующий ответы на IT-опрос. Напишите короткую, полезную и мотивирующую рекомендацию во 2-м лице ("вы") на основе ответов. Избегайте приветствий и формальностей. В конце добавьте: 
"В завершение, для улучшения ваших цифровых навыков рекомендуются курсы Coursera."\n\n""",

    "en": """You are an AI assistant analyzing IT survey responses. Based on the answers, write a short, friendly, motivating message using "you". Avoid greetings or formal introductions. End with: 
"To conclude, Coursera courses  are recommended to match your digital skill level."\n\n"""
}

# Input schema
class FeedbackRequest(BaseModel):
    language: str  # 'uz', 'ru', or 'en'
    a1: str
    a2: str
    a3: str
    a4: str
    a5: str

@app.post("/generate_feedback/")
async def generate_feedback(input: FeedbackRequest):
    lang = input.language.lower()
    if lang not in question_sets:
        lang = "uz"  # fallback

    questions = question_sets[lang]
    prompt = prompts[lang]

    answers = [input.a1, input.a2, input.a3, input.a4, input.a5]
    for i in range(5):
        prompt += f"Q{i+1}: {questions[i]}\nA{i+1}: {answers[i]}\n\n"

    try:
        response = await model.generate_content_async(prompt)
        return {
            "language": lang,
            "feedback": response.text.strip()
        }
    except Exception:
        return {
             False
        }
