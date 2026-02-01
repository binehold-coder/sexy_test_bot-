#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler
from config import BOT_TOKEN, ADMIN_ID

# Состояния беседы (используются для читаемости)
CHOOSING_LANGUAGE, ANSWERING_QUESTIONS, RESULTS = range(3)

LANGUAGES = {
    "ru": "Русский",
    "uk": "Українська",
    "fr": "Français",
}

# Тексты интерфейса по языкам
MESSAGES = {
    "choose_language": {
        "ru": "Выберите язык теста:",
        "uk": "Оберіть мову тесту:",
        "fr": "Choisissez la langue du test :",
    },
    "already_completed": {
        "ru": "Вы уже прошли тест. Повторное прохождение недоступно.",
        "uk": "Ви вже пройшли тест. Повторне проходження недоступне.",
        "fr": "Vous avez déjà passé le test. Un second passage n'est pas disponible.",
    },
    "welcome": {
        "ru": "🔐 Добро пожаловать в тест психосексуальной самооценки.\n\nЭтот тест предназначен для взрослых (18+) и разработан для анонимной самооценки.\n\nПожалуйста, отвечайте честно.\n\nНажмите /begin чтобы начать тест.",
        "uk": "🔐 Ласкаво просимо до тесту психосексуальної самооцінки.\n\nЦей тест призначений для дорослих (18+) та створений для анонімної самооцінки.\n\nБудь ласка, відповідайте чесно.\n\nНатисніть /begin, щоб розпочати тест.",
        "fr": "🔐 Bienvenue au test d'auto-évaluation psychosexuelle.\n\nCe test est destiné aux adultes (18+) et conçu pour une auto-évaluation anonyme.\n\nMerci de répondre honnêtement.\n\nAppuyez sur /begin pour démarrer le test.",
    },
    "begin_first": {
        "ru": "Пожалуйста, выберите язык через /start, затем нажмите /begin.",
        "uk": "Будь ласка, оберіть мову через /start, потім натисніть /begin.",
        "fr": "Veuillez d'abord choisir la langue via /start, puis appuyer sur /begin.",
    },
    "numeric_error": {
        "ru": "Пожалуйста, введите корректное число.",
        "uk": "Будь ласка, введіть коректне число.",
        "fr": "Veuillez entrer un nombre valide.",
    },
    "thank_you": {
        "ru": "Спасибо за участие!",
        "uk": "Дякуємо за участь!",
        "fr": "Merci pour votre participation !",
    },
    "cancelled": {
        "ru": "Тест отменен.",
        "uk": "Тест скасовано.",
        "fr": "Test annulé.",
    },
    "error_restart": {
        "ru": "Ошибка: начните заново с /start.",
        "uk": "Помилка: почніть заново з /start.",
        "fr": "Erreur : recommencez avec /start.",
    },
    "answer_error": {
        "ru": "Ошибка в обработке ответа.",
        "uk": "Помилка обробки відповіді.",
        "fr": "Erreur lors du traitement de la réponse.",
    },
    "question_prefix": {
        "ru": "Вопрос",
        "uk": "Питання",
        "fr": "Question",
    },
}


def tr(lang: str, key: str) -> str:
    """Простая функция для выборки перевода"""
    return MESSAGES.get(key, {}).get(lang, MESSAGES.get(key, {}).get("ru", ""))


# Унифицированные вопросы с переводами и ключами ответов
QUESTIONS = [
    {
        "id": 1,
        "type": "numeric",
        "text": {
            "ru": "В каком возрасте у тебя был первый секс?",
            "uk": "У якому віці у тебе був перший секс?",
            "fr": "À quel âge as-tu eu ton premier rapport sexuel ?",
        },
    },
    {
        "id": 2,
        "type": "numeric",
        "text": {
            "ru": "Сколько у тебя было половых партнеров за всю жизнь?",
            "uk": "Скільки в тебе було статевих партнерів за все життя?",
            "fr": "Combien de partenaires sexuels as-tu eus au total ?",
        },
    },
    {
        "id": 3,
        "type": "numeric",
        "text": {
            "ru": "Сколько у тебя половых партнеров сейчас?",
            "uk": "Скільки в тебе статевих партнерів зараз?",
            "fr": "Combien de partenaires sexuels as-tu actuellement ?",
        },
    },
    {
        "id": 4,
        "type": "choice",
        "text": {
            "ru": "Как часто ты занимаешься сексом?",
            "uk": "Як часто ти займаєшся сексом?",
            "fr": "À quelle fréquence as-tu des rapports sexuels ?",
        },
        "options": ["often", "sometimes", "rarely", "never"],
        "labels": {
            "ru": {"often": "Часто", "sometimes": "Иногда", "rarely": "Редко", "never": "Никогда"},
            "uk": {"often": "Часто", "sometimes": "Іноді", "rarely": "Рідко", "never": "Ніколи"},
            "fr": {"often": "Souvent", "sometimes": "Parfois", "rarely": "Rarement", "never": "Jamais"},
        },
    },
    {
        "id": 5,
        "type": "numeric",
        "text": {
            "ru": "Сколько оргазмов ты можешь испытать с партнером за ночь?",
            "uk": "Скільки оргазмів ти можеш пережити з партнером за ніч?",
            "fr": "Combien d'orgasmes peux-tu avoir avec un partenaire en une nuit ?",
        },
    },
    {
        "id": 6,
        "type": "numeric",
        "text": {
            "ru": "Какова для тебя оптимальная продолжительность полового акта?",
            "uk": "Яка для тебе оптимальна тривалість статевого акту?",
            "fr": "Quelle est pour toi la durée optimale d'un rapport sexuel ?",
        },
    },
    {
        "id": 7,
        "type": "choice",
        "text": {
            "ru": "У тебя есть постоянный партнер?",
            "uk": "У тебе є постійний партнер?",
            "fr": "As-tu un partenaire régulier ?",
        },
        "options": ["yes", "no"],
        "labels": {
            "ru": {"yes": "Да", "no": "Нет"},
            "uk": {"yes": "Так", "no": "Ні"},
            "fr": {"yes": "Oui", "no": "Non"},
        },
    },
    {
        "id": 8,
        "type": "choice",
        "text": {
            "ru": "Ты ему изменял/а?",
            "uk": "Ти йому/їй зраджував(ла)?",
            "fr": "L'as-tu trompé(e) ?",
        },
        "options": ["yes", "no"],
        "labels": {
            "ru": {"yes": "Да", "no": "Нет"},
            "uk": {"yes": "Так", "no": "Ні"},
            "fr": {"yes": "Oui", "no": "Non"},
        },
    },
    {
        "id": 9,
        "type": "choice",
        "text": {
            "ru": "Испытываешь ли ты сейчас сексуальную неудовлетворенность?",
            "uk": "Чи відчуваєш ти зараз сексуальну незадоволеність?",
            "fr": "Ressens-tu actuellement une insatisfaction sexuelle ?",
        },
        "options": ["yes", "no"],
        "labels": {
            "ru": {"yes": "Да", "no": "Нет"},
            "uk": {"yes": "Так", "no": "Ні"},
            "fr": {"yes": "Oui", "no": "Non"},
        },
    },
    {
        "id": 10,
        "type": "choice",
        "text": {
            "ru": "Как часто ты занимаешься онанизмом?",
            "uk": "Як часто ти займаєшся онанізмом?",
            "fr": "À quelle fréquence te masturbes-tu ?",
        },
        "options": ["often", "sometimes", "rarely", "never"],
        "labels": {
            "ru": {"often": "Часто", "sometimes": "Иногда", "rarely": "Редко", "never": "Никогда"},
            "uk": {"often": "Часто", "sometimes": "Іноді", "rarely": "Рідко", "never": "Ніколи"},
            "fr": {"often": "Souvent", "sometimes": "Parfois", "rarely": "Rarement", "never": "Jamais"},
        },
    },
    {
        "id": 11,
        "type": "choice",
        "text": {
            "ru": "Смотришь ли ты порнофильмы? Посещаешь порносайты?",
            "uk": "Чи дивишся ти порнофільми? Відвідуєш порносайти?",
            "fr": "Regardes-tu des films pornographiques ? Visites-tu des sites porno ?",
        },
        "options": ["yes", "no"],
        "labels": {
            "ru": {"yes": "Да", "no": "Нет"},
            "uk": {"yes": "Так", "no": "Ні"},
            "fr": {"yes": "Oui", "no": "Non"},
        },
    },
    {
        "id": 12,
        "type": "choice",
        "text": {
            "ru": "Какой тип порно тебе наиболее интересен (традиционный, анальный, оральный, групповой, садо-мазо, разные извращения)?",
            "uk": "Який тип порно тобі найбільше цікавий (традиційний, анальний, оральний, груповий, садо-мазо, різні збочення)?",
            "fr": "Quel type de porno t'intéresse le plus (traditionnel, anal, oral, en groupe, sado‑maso, diverses perversions) ?",
        },
        "options": ["traditional", "anal", "oral", "group", "sadomaso", "perversions"],
        "labels": {
            "ru": {
                "traditional": "Традиционный",
                "anal": "Анальный",
                "oral": "Оральный",
                "group": "Групповой",
                "sadomaso": "Садо-мазо",
                "perversions": "Разные извращения",
            },
            "uk": {
                "traditional": "Традиційний",
                "anal": "Анальний",
                "oral": "Оральний",
                "group": "Груповий",
                "sadomaso": "Садо-мазо",
                "perversions": "Різні збочення",
            },
            "fr": {
                "traditional": "Traditionnel",
                "anal": "Anal",
                "oral": "Oral",
                "group": "En groupe",
                "sadomaso": "Sado‑maso",
                "perversions": "Diverses perversions",
            },
        },
    },
    {
        "id": 13,
        "type": "choice",
        "text": {
            "ru": "Какой из вышеперечисленных видов секса тебе хочется испытать?",
            "uk": "Який із перелічених видів сексу тобі хочеться спробувати?",
            "fr": "Lequel des types de sexe ci‑dessus aimerais-tu essayer ?",
        },
        "options": ["traditional", "anal", "oral", "group", "sadomaso", "perversions"],
        "labels": {
            "ru": {
                "traditional": "Традиционный",
                "anal": "Анальный",
                "oral": "Оральный",
                "group": "Групповой",
                "sadomaso": "Садо-мазо",
                "perversions": "Разные извращения",
            },
            "uk": {
                "traditional": "Традиційний",
                "anal": "Анальний",
                "oral": "Оральний",
                "group": "Груповий",
                "sadomaso": "Садо-мазо",
                "perversions": "Різні збочення",
            },
            "fr": {
                "traditional": "Traditionnel",
                "anal": "Anal",
                "oral": "Oral",
                "group": "En groupe",
                "sadomaso": "Sado‑maso",
                "perversions": "Diverses perversions",
            },
        },
    },
    {
        "id": 14,
        "type": "choice",
        "text": {
            "ru": "Привлекают ли тебя сексуально люди твоего пола?",
            "uk": "Чи приваблюють тебе сексуально люди твоєї статі?",
            "fr": "Les personnes de ton sexe t'attirent‑elles sexuellement ?",
        },
        "options": ["yes", "no"],
        "labels": {
            "ru": {"yes": "Да", "no": "Нет"},
            "uk": {"yes": "Так", "no": "Ні"},
            "fr": {"yes": "Oui", "no": "Non"},
        },
    },
    {
        "id": 15,
        "type": "choice",
        "text": {
            "ru": "У тебя был секс с лицом своего пола?",
            "uk": "У тебе був секс з людиною своєї статі?",
            "fr": "As-tu déjà eu un rapport sexuel avec une personne de ton sexe ?",
        },
        "options": ["yes", "no"],
        "labels": {
            "ru": {"yes": "Да", "no": "Нет"},
            "uk": {"yes": "Так", "no": "Ні"},
            "fr": {"yes": "Oui", "no": "Non"},
        },
    },
    {
        "id": 16,
        "type": "choice",
        "text": {
            "ru": "Бывают ли у тебя фантазии о сексе с кем-то из знакомых/друзей?",
            "uk": "Чи бувають у тебе фантазії про секс з кимось із знайомих/друзів?",
            "fr": "As-tu des fantasmes sexuels avec quelqu'un de tes connaissances/amis ?",
        },
        "options": ["yes", "no"],
        "labels": {
            "ru": {"yes": "Да", "no": "Нет"},
            "uk": {"yes": "Так", "no": "Ні"},
            "fr": {"yes": "Oui", "no": "Non"},
        },
    },
    {
        "id": 17,
        "type": "choice",
        "text": {
            "ru": "Хочешь ли ты иметь с ним сексуальную связь?",
            "uk": "Чи хочеш ти мати з ним/нею сексуальний зв'язок?",
            "fr": "Souhaites-tu avoir une relation sexuelle avec lui/elle ?",
        },
        "options": ["yes", "no"],
        "labels": {
            "ru": {"yes": "Да", "no": "Нет"},
            "uk": {"yes": "Так", "no": "Ні"},
            "fr": {"yes": "Oui", "no": "Non"},
        },
    },
    {
        "id": 18,
        "type": "text",
        "text": {
            "ru": "Укажи свой размер груди/члена",
            "uk": "Вкажи свій розмір грудей/члена",
            "fr": "Indique ta taille de poitrine/de pénis",
        },
    },
]


# Профили с переводами
PROFILES = {
    "ru": {
        "bad_decision": {
            "name": "Ходячее плохое решение",
            "description": "Ты — тот самый человек, после которого друзья говорят «ну я же говорил». Тебя заводит не секс, а момент, когда всё начинает идти не по плану. Ты умеешь смотреть так, что у людей резко портятся моральные ориентиры. С тобой легко сделать глупость и сложно сделать выводы. Ты не давишь — ты создаёшь условия. Иногда ты сам не помнишь, как всё началось. Зато финал обычно неловко вспоминать. И да, ты этим гордишься.",
            "advice": "",
        },
        "passive_aggressive": {
            "name": "Пассивно-агрессивный соблазн",
            "description": "Ты ничего не предлагаешь напрямую — ты просто «шутил». Потом ещё раз «шутил». А потом все внезапно оказались без иллюзий. Ты мастер двусмысленных фраз и слишком долгих пауз. Люди рядом с тобой начинают сомневаться в своей силе воли. Ты делаешь вид, что ни при чём, и формально — так и есть. Но мы-то всё понимаем. Ангел с алиби.",
            "advice": "",
        },
        "emotional_wrecker": {
            "name": "Эмоциональный вредитель",
            "description": "Ты приходишь за близостью, а уходишь, оставив вопросы. Тебя тянет туда, где «не стоит», и это твой любимый маршрут. Ты можешь быть нежным, но только до первого внутреннего сигнала «мне скучно». После тебя часто остаётся фраза «что это вообще было?». Ты не обещаешь ничего — и всё равно разочаровываешь. Талант, надо признать. Зато честно.",
            "advice": "",
        },
        "logic_sabotage": {
            "name": "Флирт как форма насилия над логикой",
            "description": "С тобой люди делают то, что утром сами бы себе запретили. Ты отлично чувствуешь момент, когда разум сдаётся. Твоя сексуальность — это не страсть, это подрывная деятельность. Ты не повышаешь голос, ты понижаешь стандарты. Иногда кажется, что ты просто разговариваешь. А потом — бац, и репутация пошла трещинами. Ты называешь это «химией». Остальные — «ошибкой».",
            "advice": "",
        },
        "shame_repeat": {
            "name": "Стыдно, но повторил бы",
            "description": "Ты — тот самый опыт, о котором не рассказывают новым партнёрам. С тобой весело, неловко и немного против здравого смысла. Ты не лучший вариант, ты самый запоминающийся. После тебя люди либо берут паузу, либо пишут ночью. Ты исчезаешь вовремя — до разговоров о чувствах. И появляешься тоже вовремя. Карма тебя найдёт. Но не сегодня.",
            "advice": "",
        },
    },
    "uk": {
        "bad_decision": {
            "name": "Ходяче погане рішення",
            "description": "Ти — та сама людина, після якої друзі кажуть «ну я ж казав». Тебе заводить не секс, а момент, коли все починає йти не за планом. Ти вмієш дивитися так, що в людей різко псуються моральні орієнтири. З тобою легко зробити дурницю і складно зробити висновки. Ти не тиснеш — ти створюєш умови. Іноді ти сам не пам’ятаєш, як усе почалося. Зате фінал зазвичай ніяково згадувати. І так, ти цим пишаєшся.",
            "advice": "",
        },
        "passive_aggressive": {
            "name": "Пасивно-агресивна спокуса",
            "description": "Ти нічого не пропонуєш напряму — ти просто «жартував». Потім ще раз «жартував». А потім усі раптом залишилися без ілюзій. Ти майстер двозначних фраз і надто довгих пауз. Люди поряд з тобою починають сумніватися у своїй силі волі. Ти робиш вигляд, що ні до чого, і формально — так і є. Але ми ж розуміємо. Ангел з алібі.",
            "advice": "",
        },
        "emotional_wrecker": {
            "name": "Емоційний шкідник",
            "description": "Ти приходиш за близькістю, а йдеш, залишивши запитання. Тебе тягне туди, де «не варто», і це твій улюблений маршрут. Ти можеш бути ніжним(ою), але лише до першого внутрішнього сигналу «мені нудно». Після тебе часто залишається фраза «що це взагалі було?». Ти нічого не обіцяєш — і все одно розчаровуєш. Талант, треба визнати. Зате чесно.",
            "advice": "",
        },
        "logic_sabotage": {
            "name": "Флірт як форма насильства над логікою",
            "description": "З тобою люди роблять те, що зранку самі б собі заборонили. Ти чудово відчуваєш момент, коли розум здається. Твоя сексуальність — це не пристрасть, це підривна діяльність. Ти не підвищуєш голос, ти знижуєш стандарти. Іноді здається, що ти просто розмовляєш. А потім — бац, і репутація пішла тріщинами. Ти називаєш це «хімією». Інші — «помилкою».",
            "advice": "",
        },
        "shame_repeat": {
            "name": "Соромно, але повторив(ла) б",
            "description": "Ти — той самий досвід, про який не розповідають новим партнерам. З тобою весело, ніяково і трохи всупереч здоровому глузду. Ти не найкращий варіант, ти найпам’ятніший. Після тебе люди або беруть паузу, або пишуть вночі. Ти зникаєш вчасно — до розмов про почуття. І з’являєшся теж вчасно. Карма тебе знайде. Але не сьогодні.",
            "advice": "",
        },
    },
    "fr": {
        "bad_decision": {
            "name": "Mauvaise décision sur pattes",
            "description": "Tu es cette personne après laquelle les amis disent « je l’avais dit ». Ce qui t’excite, ce n’est pas le sexe, c’est le moment où tout part de travers. Tu sais regarder de façon à faire fondre les repères moraux. Avec toi, on fait facilement une bêtise et difficilement un bilan. Tu ne forces pas — tu crées les conditions. Parfois, tu ne sais même plus comment tout a commencé. La fin, elle, est souvent gênante à raconter. Et oui, tu en es fier(ère).",
            "advice": "",
        },
        "passive_aggressive": {
            "name": "Séduction passive‑agressive",
            "description": "Tu ne proposes rien frontalement — tu « plaisantais », c’est tout. Puis tu « plaisantes » encore. Et soudain, plus personne n’a d’illusions. Tu maîtrises les phrases ambiguës et les silences trop longs. Les gens autour de toi doutent de leur volonté. Tu fais comme si tu n’y étais pour rien, et techniquement — c’est vrai. Mais on sait. Un ange avec un alibi.",
            "advice": "",
        },
        "emotional_wrecker": {
            "name": "Saboteur émotionnel",
            "description": "Tu viens pour la proximité, tu repars en laissant des questions. Tu es attiré(e) par ce qui « ne devrait pas » et c’est ton itinéraire préféré. Tu peux être tendre, jusqu’au premier signal interne « je m’ennuie ». Après toi, il reste souvent un « c’était quoi, au juste ? ». Tu ne promets rien — et tu déçois quand même. Un talent, il faut l’admettre. Mais au moins, tu es honnête.",
            "advice": "",
        },
        "logic_sabotage": {
            "name": "Le flirt comme violence contre la logique",
            "description": "Avec toi, les gens font ce qu’ils se seraient interdit le matin. Tu sens parfaitement le moment où la raison lâche. Ta sexualité n’est pas une passion, c’est une opération de sabotage. Tu ne hausses pas la voix, tu abaisses les standards. Parfois on croit que tu discutes juste. Et puis — bam, la réputation se fissure. Tu appelles ça de la « chimie ». Les autres — une « erreur ».",
            "advice": "",
        },
        "shame_repeat": {
            "name": "Honteux, mais je recommencerais",
            "description": "Tu es cette expérience dont on ne parle pas aux nouveaux partenaires. Avec toi, c’est fun, gênant et un peu contre le bon sens. Tu n’es pas le meilleur choix, tu es le plus mémorable. Après toi, soit on prend une pause, soit on écrit la nuit. Tu disparais au bon moment — avant les discussions de sentiments. Et tu réapparais aussi au bon moment. Le karma te trouvera. Mais pas aujourd’hui.",
            "advice": "",
        },
    },
}


class TestBot:
    def __init__(self):
        self.current_question = {}
        self.user_answers = {}

    def calculate_profile(self, answers, numeric_answers):
        """Вычисляет профиль на основе ответов"""
        scores = {
            "bad_decision": 0,
            "passive_aggressive": 0,
            "emotional_wrecker": 0,
            "logic_sabotage": 0,
            "shame_repeat": 0,
        }

        age_first = numeric_answers.get(1, 0)
        partners_total = numeric_answers.get(2, 0)
        partners_now = numeric_answers.get(3, 0)
        orgasms = numeric_answers.get(5, 0)
        duration = numeric_answers.get(6, 0)

        freq = answers.get(4)
        has_bf = answers.get(7)
        cheated = answers.get(8)
        dissatisfied = answers.get(9)
        masturbation = answers.get(10)
        porn = answers.get(11)
        porn_type = answers.get(12)
        want_type = answers.get(13)
        same_sex = answers.get(14)
        sex_with_woman = answers.get(15)
        fantasy = answers.get(16)
        fantasy_want = answers.get(17)

        extreme_types = {"anal", "group", "sadomaso", "perversions"}

        if cheated == "yes":
            scores["bad_decision"] += 4
            scores["logic_sabotage"] += 1
            if partners_now and partners_now > 1:
                scores["bad_decision"] += 1

        if dissatisfied == "yes":
            scores["emotional_wrecker"] += 2
            scores["shame_repeat"] += 1

        if freq == "often":
            scores["logic_sabotage"] += 2
            scores["shame_repeat"] += 1
        elif freq == "sometimes":
            scores["shame_repeat"] += 1
        elif freq == "rarely":
            scores["passive_aggressive"] += 2
        elif freq == "never":
            scores["passive_aggressive"] += 3

        if orgasms >= 3:
            scores["logic_sabotage"] += 1
        elif orgasms == 2:
            scores["shame_repeat"] += 1
        elif orgasms == 0:
            scores["emotional_wrecker"] += 1

        if duration >= 5 and duration <= 20:
            scores["shame_repeat"] += 1
        elif duration > 30:
            scores["logic_sabotage"] += 1

        if partners_total > 10:
            scores["bad_decision"] += 2
        elif partners_total >= 5:
            scores["logic_sabotage"] += 1
        elif partners_total <= 2:
            scores["passive_aggressive"] += 1

        if partners_now and partners_now > 1:
            scores["bad_decision"] += 1
        elif partners_now == 1:
            scores["emotional_wrecker"] += 1
        elif partners_now == 0:
            scores["passive_aggressive"] += 1

        if has_bf == "yes":
            scores["emotional_wrecker"] += 1
        elif has_bf == "no":
            scores["passive_aggressive"] += 1

        if masturbation == "often":
            scores["passive_aggressive"] += 1
        elif masturbation == "sometimes":
            scores["shame_repeat"] += 1
        elif masturbation == "rarely":
            scores["emotional_wrecker"] += 1
        elif masturbation == "never":
            scores["emotional_wrecker"] += 1

        if porn == "yes":
            scores["logic_sabotage"] += 1
            scores["shame_repeat"] += 1
        elif porn == "no":
            scores["passive_aggressive"] += 1

        if porn_type in extreme_types:
            scores["logic_sabotage"] += 2
        if want_type in extreme_types:
            scores["logic_sabotage"] += 2

        if same_sex == "yes":
            scores["logic_sabotage"] += 1
        if sex_with_woman == "yes":
            scores["bad_decision"] += 1

        if fantasy == "yes":
            scores["shame_repeat"] += 2
        if fantasy_want == "yes":
            scores["shame_repeat"] += 1

        if age_first and age_first >= 18 and partners_total <= 2:
            scores["passive_aggressive"] += 1

        profile = max(scores, key=scores.get)
        return profile if scores[profile] > 0 else "shame_repeat"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start: предлагает выбрать язык"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    if user_id in context.user_data and context.user_data[user_id].get("completed"):
        lang = context.user_data[user_id].get("lang", "ru")
        await update.message.reply_text(tr(lang, "already_completed"))
        return ConversationHandler.END

    context.user_data[user_id] = {
        "username": username,
        "answers": {},
        "numeric_answers": {},
        "text_answers": {},
        "current_question": 0,
        "completed": False,
        "lang": None,
    }

    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"lang_{code}")]
        for code, name in LANGUAGES.items()
    ]

    await update.message.reply_text(
        "Выберите язык / Оберіть мову / Choisissez la langue",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фиксирует выбранный язык и выводит приветствие"""
    query = update.callback_query
    user_id = update.effective_user.id
    lang = query.data.split("_", 1)[1]

    username = update.effective_user.username or update.effective_user.first_name
    context.user_data[user_id] = {
        "username": username,
        "answers": {},
        "numeric_answers": {},
        "text_answers": {},
        "current_question": 0,
        "completed": False,
        "lang": lang,
    }

    await query.answer()
    await query.edit_message_text(tr(lang, "welcome"))


async def begin_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало теста"""
    user_id = update.effective_user.id

    if user_id not in context.user_data or not context.user_data[user_id].get("lang"):
        await update.message.reply_text(tr("ru", "begin_first"))
        return ConversationHandler.END

    context.user_data[user_id]['current_question'] = 0
    await send_question(update, context, user_id)
    return ANSWERING_QUESTIONS


async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    """Отправляет очередной вопрос"""
    question_idx = context.user_data[user_id]['current_question']
    lang = context.user_data[user_id]['lang']
    
    if question_idx >= len(QUESTIONS):
        # Все вопросы пройдены - переходим к результатам
        await show_results(update, context, user_id)
        return RESULTS
    
    question = QUESTIONS[question_idx]
    context.user_data[user_id]['current_question'] = question_idx + 1
    
    prefix = tr(lang, "question_prefix")
    total_questions = len(QUESTIONS)
    question_text = f"{prefix} {question['id']}/{total_questions}:\n\n{question['text'][lang]}"

    if question['type'] == 'choice':
        keyboard = [
            [InlineKeyboardButton(question['labels'][lang][opt], callback_data=f"q{question['id']}:{opt}")]
            for opt in question['options']
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query:
            await update.callback_query.edit_message_text(question_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(question_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(question_text)
        context.user_data[user_id]['awaiting_input'] = {
            "id": question['id'],
            "type": question['type'],
        }


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ответа на вопрос"""
    user_id = update.effective_user.id
    query = update.callback_query
    
    if user_id not in context.user_data:
        await query.answer(tr("ru", "error_restart"))
        return ConversationHandler.END
    
    lang = context.user_data[user_id]['lang']

    # Парсим callback_data
    data_parts = query.data.split(':', 1)
    question_id = int(data_parts[0][1:])  # убираем 'q'
    answer_key = data_parts[1]
    
    question = next((q for q in QUESTIONS if q['id'] == question_id), None)
    if not question:
        await query.answer(tr(lang, "answer_error"))
        return ANSWERING_QUESTIONS
    
    # Сохраняем ответ
    context.user_data[user_id]['answers'][question_id] = answer_key
    
    question_idx = context.user_data[user_id]['current_question']
    
    if question_idx >= len(QUESTIONS):
        await show_results(update, context, user_id)
        return RESULTS
    
    # Отправляем следующий вопрос
    next_question = QUESTIONS[question_idx]
    total_questions = len(QUESTIONS)
    question_text = f"{tr(lang, 'question_prefix')} {next_question['id']}/{total_questions}:\n\n{next_question['text'][lang]}"
    
    if next_question['type'] == 'choice':
        keyboard = [
            [InlineKeyboardButton(next_question['labels'][lang][opt], callback_data=f"q{next_question['id']}:{opt}")]
            for opt in next_question['options']
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data[user_id]['current_question'] = question_idx + 1
        await query.edit_message_text(question_text, reply_markup=reply_markup)
    else:
        context.user_data[user_id]['current_question'] = question_idx + 1
        await query.edit_message_text(question_text)
        context.user_data[user_id]['awaiting_input'] = {
            "id": next_question['id'],
            "type": next_question['type'],
        }
    
    return ANSWERING_QUESTIONS


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых и числовых ответов"""
    user_id = update.effective_user.id
    
    if user_id not in context.user_data:
        await update.message.reply_text(tr("ru", "error_restart"))
        return ConversationHandler.END
    
    if 'awaiting_input' not in context.user_data[user_id]:
        return ANSWERING_QUESTIONS
    
    lang = context.user_data[user_id]['lang']
    pending = context.user_data[user_id]['awaiting_input']
    question_id = pending['id']
    question_type = pending['type']
    user_text = update.message.text.strip()

    if question_type == 'numeric':
        try:
            numeric_value = int(user_text)
            context.user_data[user_id]['numeric_answers'][question_id] = numeric_value
        except ValueError:
            await update.message.reply_text(tr(lang, "numeric_error"))
            return ANSWERING_QUESTIONS
    else:
        context.user_data[user_id]['text_answers'][question_id] = user_text

    del context.user_data[user_id]['awaiting_input']
    
    question_idx = context.user_data[user_id]['current_question']
    
    if question_idx >= len(QUESTIONS):
        await show_results(update, context, user_id)
        return RESULTS
    
    # Отправляем следующий вопрос
    next_question = QUESTIONS[question_idx]
    total_questions = len(QUESTIONS)
    question_text = f"{tr(lang, 'question_prefix')} {next_question['id']}/{total_questions}:\n\n{next_question['text'][lang]}"
    
    if next_question['type'] == 'choice':
        keyboard = [
            [InlineKeyboardButton(next_question['labels'][lang][opt], callback_data=f"q{next_question['id']}:{opt}")]
            for opt in next_question['options']
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data[user_id]['current_question'] = question_idx + 1
        await update.message.reply_text(question_text, reply_markup=reply_markup)
    else:
        context.user_data[user_id]['current_question'] = question_idx + 1
        await update.message.reply_text(question_text)
        context.user_data[user_id]['awaiting_input'] = {
            "id": next_question['id'],
            "type": next_question['type'],
        }
    
    return ANSWERING_QUESTIONS


async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    """Показывает результаты теста и отправляет их админу"""
    user_data = context.user_data[user_id]
    answers = user_data['answers']
    numeric_answers = user_data['numeric_answers']
    text_answers = user_data['text_answers']
    username = user_data['username']
    lang = user_data['lang']
    
    # Вычисляем профиль
    test_bot = TestBot()
    profile_key = test_bot.calculate_profile(answers, numeric_answers)
    profile = PROFILES[lang][profile_key]
    
    # Формируем результат для пользователя
    if profile.get("advice"):
        result_text = f"{profile['name']}\n\n{profile['description']}\n\n💡 {profile['advice']}"
    else:
        result_text = f"{profile['name']}\n\n{profile['description']}"
    
    # Отправляем результат пользователю
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(f"{tr(lang, 'thank_you')}\n\n{result_text}")
        else:
            await update.message.reply_text(f"{tr(lang, 'thank_you')}\n\n{result_text}")
    except Exception as e:
        print(f"Ошибка при отправке результата пользователю: {e}")
    
    # Формируем отчет для админа
    admin_report = f"📋 РЕЗУЛЬТАТЫ ТЕСТА\n\n"
    admin_report += f"👤 Пользователь: @{username} (ID: {user_id})\n"
    admin_report += f"🕐 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n"
    admin_report += f"Язык: {LANGUAGES.get(lang, lang)}\n\nОТВЕТЫ:\n"
    
    for i, question in enumerate(QUESTIONS, 1):
        q_id = question['id']
        if q_id in answers:
            label = question['labels'][lang][answers[q_id]]
            admin_report += f"{i}. {question['text'][lang]}\n"
            admin_report += f"   Ответ: {label}\n\n"
        elif q_id in numeric_answers:
            admin_report += f"{i}. {question['text'][lang]}\n"
            admin_report += f"   Ответ: {numeric_answers[q_id]}\n\n"
        elif q_id in text_answers:
            admin_report += f"{i}. {question['text'][lang]}\n"
            admin_report += f"   Ответ: {text_answers[q_id]}\n\n"
    
    admin_report += f"📊 ПРОФИЛЬ: {profile['name']}\n"
    
    # Отправляем отчет админу
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_report
        )
    except Exception as e:
        print(f"Ошибка при отправке результата админу: {e}")
    
    # Отмечаем, что пользователь завершил тест
    user_data['completed'] = True
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена теста"""
    user_id = update.effective_user.id
    lang = context.user_data.get(user_id, {}).get("lang", "ru")
    await update.message.reply_text(tr(lang, "cancelled"))
    return ConversationHandler.END


def main():
    """Запуск бота"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    
    # Выбор языка
    app.add_handler(CallbackQueryHandler(handle_language, pattern=r"^lang_"))

    # Обработчик команды начала теста
    app.add_handler(CommandHandler("begin", begin_test))
    
    # Обработчик callback-кнопок для выбора ответов
    app.add_handler(CallbackQueryHandler(handle_answer, pattern=r"^q\d+:"))
    
    # Обработчик текстовых сообщений (для числовых и текстовых ответов)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    
    print("🚀 Бот запущен и готов к работе...")
    app.run_polling()


if __name__ == '__main__':
    main()
