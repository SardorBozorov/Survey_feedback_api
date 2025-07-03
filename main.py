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
    "uz": """Siz sun’iy intellektsiz va quyidagi respondent javoblari asosida foydalanuvchiga qisqa, samimiy, motivatsion va foydali tavsiya yozasiz. Tavsiya 4–5 gapdan oshmasin. Rasmiystik, salomlashuv, va keraksiz so‘zlardan qoching. Tavsiya respondentning daraja va ehtiyojlariga mos bo‘lsin. IT sohasining zamonaviy dunyodagi ahamiyati va imkoniyatlari haqida qisqacha ijobiy fikr kiriting — masalan, IT bilimlari bilan yaxshi ish topish, masofadan ishlash yoki mustaqil daromad topish mumkinligini. Har doim quyidagi jumla bilan boshlang: 
"So‘rovda qatnashganingiz uchun rahmat, bu o‘z ustingizda ishlayotganingizni ko‘rsatadi." 
Oxirida quyidagini qo‘shing:
"Shuning bilan birgalikda hulosalar ohirida bilimlaringizni rivojlantirish va vaqtingizni tejash uchun Coursera kurslari sizning IT ko‘nikmalaringizga mos ravishda tavsiya etiladi."\n\n""",

    "ru": """Вы — ИИ, анализирующий ответы на IT-опрос. На основе ответов напишите короткую (4–5 предложений), дружелюбную, мотивирующую и полезную рекомендацию во 2-м лице ("вы"). Избегайте приветствий, формальностей и лишней воды. Сообщение должно соответствовать уровню и интересам респондента. Добавьте позитивную мысль о важности ИТ — например, что знания в этой области помогают найти хорошую работу, работать удалённо или зарабатывать самостоятельно. Всегда начинайте с фразы:
"Спасибо за участие в опросе — это говорит о вашем стремлении развиваться." 
В конце добавьте:
"В завершение, для улучшения ваших цифровых навыков рекомендуются курсы Coursera, подобранные под ваш уровень."\n\n""",

    "en": """You are an AI assistant analyzing IT survey responses. Based on the answers, write a short (4–5 sentence), friendly, motivating, and practical recommendation using "you". Avoid greetings, formality, or filler. Tailor your message to the respondent’s skill level and interests. Include a positive note on the importance of IT — such as how IT skills help people get better jobs, work remotely, or earn independently. Always begin with the sentence: 
"Thanks for taking part in the survey — it shows you're committed to learning." 
End with:
"To conclude, Coursera courses are recommended to match your digital skill level and help you grow efficiently."\n\n"""
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
