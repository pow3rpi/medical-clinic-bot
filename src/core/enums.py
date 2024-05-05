from enum import Enum, unique
from typing import Union, List, Dict


class CompanyInfo(Enum):
    name: str = 'Название Компании'
    email: str = 'xxxxx@yandex.ru'
    phone_1: str = '+7(xxx)xxx-xx-xx'
    phone_2: str = '+7(xxx)xxx-xx-xx'
    website_1: str = 'https://website-1.ru'
    website_2: str = 'https://website-2.su'
    two_gis_maps: str = 'https://go.2gis.com/xxxxx'
    yandex_maps: str = 'https://clck.ru/xxxxx'
    address: str = 'Город, улица, дом, этаж'
    work_schedule: str = 'Пн-Сб с 09:00 до 19:00'


class Numbers(Enum):
    specialities_per_page: int = 10
    specialities_in_row: int = 2


@unique
class CacheKeys(Enum):
    admins: str = 'admins'
    specialities: str = 'specialities'
    priv_admins: str = 'priv_admins'


class DateFormat(Enum):
    input: str = '%d-%m-%Y'
    system: str = '%Y-%m-%d %H:%M:%S.%f'
    output: str = '%d/%m/%Y'


@unique
class AdminPrivilegeType(Enum):
    high: str = 'high'
    low: str = 'low'


@unique
class ConsultationType(Enum):
    online: str = 'online'
    offline: str = 'offline'


@unique
class CommunicationType(Enum):
    call: str = 'call'
    chat: str = 'chat'


@unique
class ScienceDegree(Enum):
    phd: str = 'Доктор мед. наук'
    pre_phd: str = 'Кандидат мед. наук'


@unique
class QualCategory(Enum):
    highest: str = 'Высшая'
    first: str = 'Первая'
    second: str = 'Вторая'


class Symbols(Enum):
    separator: str = ':'


class NavigationType(Enum):
    next: str = 'next'
    prev: str = 'prev'
    prev_next: str = 'prev-next'


class Statistic(Enum):
    statistic: str = 'statistic'
    change: str = 'change'


class ButtonText(Enum):
    # main menu
    callback_form: str = 'Заказать звонок ☎'
    appointment_form: str = 'Записаться на прием 📅'
    feedback: str = 'Оставить отзыв 📝'
    contacts: str = 'Контакты ℹ'
    instruction: str = 'Инструкция 🛠'
    admin_panel: str = '❗Админская панель❗'

    # admin panel
    doctors: str = 'Специалисты 🩺'
    statistics: str = 'Статистика 📊'
    admins: str = 'Администраторы ⚠'

    # statistics
    day_statistic: str = 'за 24 ЧАСА'
    week_statistic: str = 'за НЕДЕЛЮ'
    month_statistic: str = 'за МЕСЯЦ'
    quarter_statistic: str = 'за КВАРТАЛ'
    year_statistic: str = 'за ГОД'
    custom_statistic: str = 'Указать период'

    # doctor info sections (update info)
    full_name: str = 'ФИО 🔤'
    photo: str = 'Фотография 📷'
    description: str = 'Описание 📃'
    specialities: str = 'Специальности 💼'
    experience: str = 'Стаж 📚'
    science_degree: str = 'Степень 🔬'
    qual_category: str = 'Категория 🏅'
    price: str = 'Цена 💰'

    # consultation types
    online: str = 'Онлайн 💻 (20 минут)'
    offline: str = 'Очно в клинике 🏥'

    # communication types
    chat: str = 'Чат 💬'
    call: str = 'Звонок 📞'

    # science degrees
    phd: str = 'Доктор наук 🥇'
    pre_phd: str = 'Кандидат наук 🥈'

    # qualification categories
    highest_category: str = 'Высшая 🥇'
    first_category: str = 'Первая 🥈'
    second_category: str = 'Вторая 🥉'

    # admin privilige types
    high_privilege: str = 'Высокий ⬆'
    low_privilege: str = 'Низкий ⬇'

    # ReplyKeyboard
    start: str = 'ГЛАВНОЕ МЕНЮ'
    user_contact: str = 'Поделиться контактом 📞'

    # navigation
    next: str = 'Вперед ➡'
    prev: str = '⬅ Назад'
    back_to_menu: str = '↩ Вернуться в меню'

    # general
    create: str = 'Добавить ➕'
    delete: str = 'Удалить ➖'
    yes: str = '✅ Да'
    no: str = '❌ Нет'
    experience_yes: str = 'Указать'
    experience_no: str = 'Не указывать ❌'
    selection_completed: str = 'ГОТОВО ✅'
    confirmation: str = '❗ Подтвердить ❗'
    no_specification: str = 'Отсутствует ❌'
    change: str = 'Изменить'
    add_specialities: str = 'Добавить специальности ➕'

    # other
    update_info: str = 'Обновить информацию 🔄'
    cards: str = 'Карточки 🗂'
    edit: str = 'Редактировать'
    choose_doctor: str = '⬆ Выбрать ⬆'
    pay: str = 'Оплатить'


class Payment(Enum):
    title: str = 'Оплата консультации'
    # you can find available types of currency on official telegram page
    currency: str = 'RUB'
    label: str = 'Онлайн консультация'
    prefix: str = 'payment_'
    appointment: str = 'online_appointment'

    instruction: str = f'{"<b>"}{ButtonText.appointment_form.value}{"</b>"}  —  {"<b>"}Шаг 5/5{"</b>"}\n' \
                       f'\n\n' \
                       f'{"<b>"}Что дальше{"</b>"}?\n' \
                       f'\n' \
                       f'{"<b>"}1 шаг{"</b>"}:  В ближайшее (рабочее) время с вами свяжется администратор для ' \
                       f'согласованиявремени консультации\n' \
                       f'   - если в качестве типа связи вы указали «{"<b>"}{ButtonText.chat.value}{"</b>"}», ' \
                       f'то убедитесь, что ваши настройки конфиденциальности Telegram позволяют принимать сообщения ' \
                       f'от посторонних пользователей\n' \
                       f'\n' \
                       f'{"<b>"}2 шаг{"</b>"}:  После согласования времени вернитесь сюда и оплатите консультацию, ' \
                       f'нажав кнопку «{"<b>"}Оплатить{"</b>"}» в конце данного сообщения\n' \
                       f'   · если вы всё-таки планируете получить консультацию, то убедительная просьба {"<b>"}НЕ ' \
                       f'покидать данный раздел{"</b>"} до совершения оплаты❗\n' \
                       f'\n' \
                       f'{"<b>"}3 шаг{"</b>"}:  После оплаты БОТ пришлет вам ссылку на консультацию, по которой ' \
                       f'вам нужно будет перейти во время начала приема\n' \
                       f'\n\n' \
                       f'В случае, если консультация по каким-либо причинам не состоится:\n' \
                       f'   - уплаченные средства будут возвразщены в полном объеме в ближайшее время\n' \
                       f'   - возврат осуществляется на ту же карту, с которой была произведена оплата\n' \
                       f'\n\n' \
                       f'{"<b>"}Обращаем Ваше внимание, что длительность консультации не превышает 20 минут{"</b>"}❗❗❗'

    successful_payment: str = f'✅✅✅\n' \
                              f'Оплата прошла успешно!\n' \
                              f'Спасибо, что выбрали {"<b>"}{CompanyInfo.name.value}{"</b>"}!\n' \
                              f'✅✅✅\n' \
                              f'\n\n' \
                              f'Для проведения консультации подключайтесь по ссылке в согласованное время\n' \
                              f'\n' \
                              f'Ссылка будет прикреплена к данному сообщению в течение 2 минут (не покидайте данную ' \
                              f'страницу, не сохранив себе ссылку❗)\n' \
                              f'\n' \
                              f'{"<b>"}Убедитесь{"</b>"}, что:\n' \
                              f'   - ваше интернет соединение стабильно\n' \
                              f'   - необходимые документы/анализы/заключения подготовлены (если это необходимо)\n' \
                              f'   - вы тщательно подготовили вопросы перед началом консультации, чтобы эффективно ' \
                              f'провести диалог со специалистом\n' \
                              f'\n' \
                              f'Если, вдруг, во время консультации соединение прервется, не волнуйтесь и используйте ' \
                              f'ссылку для повторного подключения\n' \
                              f'\n' \
                              f'В случае, {"<b>"}если{"</b>"}:\n' \
                              f'   - вам не пришла ссылка на консультацию в течение 2 минут\n' \
                              f'   - вы хотите изменить дату/время приема\n' \
                              f'   - вы хотите отменить консультацию\n' \
                              f'   - у вас имеются какие-либо вопросы по проведению консультации\n' \
                              f'⇒ Обратитесь к администратору, с которым вы согласовывали время и дату приема или ' \
                              f'позвоните нам в клинику по номеру:\n' \
                              f'{CompanyInfo.phone_1.value}  или  {CompanyInfo.phone_2.value}'

    transaction_code: str = f'✅ Консультация успешно оплачена\n' \
                            f'🆔 {"<b>"}ЮMoney код{"</b>"} транзакции: '

    transaction_sum: str = f'💰 {"<b>"}Сумма{"</b>"}: '


class CallbackData(Enum):
    # main menu
    appointment_request: str = 'appointment request'
    callback_request: str = 'callback request'
    leave_feedback: str = 'leave feedback'
    show_contacts: str = 'show all contacts'
    send_instruction: str = 'send user instruction'
    admin_panel: str = 'admin panel'

    # admin panel
    doctors_settings: str = 'doctors settings menu'
    statistics: str = 'statistics menu'
    admins: str = 'admins config menu'

    # doctors settings menu
    create_doctor: str = 'create doctor'
    update_doctor: str = 'update doctor'
    delete_doctor: str = 'del doctor'
    show_doctor: str = 'show_doctor'

    # admins config menu
    create_admin: str = 'create admin'
    delete_admin: str = 'del admin'

    # navigation
    main_menu: str = 'main menu'
    admin_menu_nav: str = 'admin navigation'
    back_to_menu: str = 'back to menu'
    prev: str = 'prev'
    next: str = 'next'

    # statistic
    day: str = 'день'
    week: str = 'неделя'
    month: str = 'месяц'
    quarter: str = 'квартал'
    year: str = 'год'
    custom_statistics: str = 'custom statistics'

    # appointment
    choose_offline: str = 'choose offline cons'
    choose_online: str = 'choose online cons'
    choose_call: str = 'choose call'
    choose_chat: str = 'choose chat'
    initialize_payment: str = 'initialize payment'

    # general
    confirmation: str = 'confirm the action'
    change_choice: str = 'change the choice'
    selection_completed: str = 'selection completed'
    yes: str = 'yes'
    no: str = 'no'

    # doctor creation/update
    doctor: str = 'doc'
    speciality_title: str = 'spec. title'
    choose_section: str = 'choose section'
    edit: str = 'edit doc info'
    change_info: str = 'change doc info'
    cur_value: str = 'cur_value'
    new_specialities: str = 'add new specialities'
    add_specialities: str = 'add specialities'
    delete_specialities: str = 'delete specialities'
    back_to_doctors: str = 'back to doctors'
    choose_science_degree: str = 'choose science degree'
    choose_phd: str = 'choose phd'
    choose_pre_phd: str = 'choose pre phd'
    choose_qual_category: str = 'choose qual category'
    choose_highest_category: str = 'choose highest category'
    choose_first_category: str = 'choose first category'
    choose_second_category: str = 'choose second category'
    no_specification: str = 'no specification'

    # admin creation/deletion
    privilege: str = 'privilege'
    high: str = 'high'
    low: str = 'low'

    # admins/doctors deletion
    choose_person: str = 'choose person'

    # doctor info sections
    # values below must have the same value as corresponding columns in table "Doctors"
    photo: str = 'photo'
    full_name: str = 'full_name'
    description: str = 'description'
    speciality_id: str = 'speciality_id'
    speciality: str = 'speciality'
    experience: str = 'experience'
    science_degree: str = 'science_degree'
    qual_category: str = 'qual_category'
    price: str = 'price'


class BotMessageText(Enum):
    # user instruction
    instruction: str = f'{"<b>"}{ButtonText.instruction.value}{"</b>"}\n' \
                       f'\n' \
                       f'1⃣ Если вы не знаете что делать, хотите начать все сначала или БОТ не реагирует, просто ' \
                       f'воспользуйтесь командой «{"<b>"}/start{"</b>"}» из меню слева в вашей панели ввода\n' \
                       f'\n' \
                       f'2⃣ Чтобы ответить на любой вопрос БОТа вам необходимо:\n' \
                       f'  · либо выбрать один из предложенных вариантов под сообщением с вопросом\n' \
                       f'  · либо отправить ответ в виде текстового сообщения\n' \
                       f'\n' \
                       f'3⃣ Когда БОТ спрашивает у вас номер телефона, вместо того, чтобы вводить его вручную, ' \
                       f'вы можете:\n' \
                       f'  · нажать «{"<b>"}{ButtonText.user_contact.value}{"</b>"}» в самом низу вашего экрана\n' \
                       f'  · нажать на {"<b>"}значок рядом с{"</b>"} 📎 на панели ввода текста, если указазанная ' \
                       f'выше кнопка не высветилась автоматически\n' \
                       f'\n' \
                       f'4⃣ На каждом шаге опроса вам доступна кнопка ' \
                       f'«{"<b>"}{ButtonText.back_to_menu.value}{"</b>"}», которая в любой момент вернет вас в ' \
                       f'главное меню\n' \
                       f'\n\n\n\n\n\n\n\n\n\n' \
                       f'⬇⬇⬇⬇⬇'

    # contacts
    contacts: str = f'{"<b>"}{ButtonText.contacts.value}{"</b>"}\n' \
                    f'\n' \
                    f'📞Телефон📞\n' \
                    f'{CompanyInfo.phone_1.value} {CompanyInfo.phone_2.value}\n' \
                    f'\n' \
                    f'📧Email📧\n' \
                    f'{CompanyInfo.email.value}\n' \
                    f'\n' \
                    f'🌐Сайт🌐\n' \
                    f'{CompanyInfo.website_1.value}\n' \
                    f'\n' \
                    f'💻Портал онлайн консультаций💻\n' \
                    f'{CompanyInfo.website_2.value}\n' \
                    f'\n' \
                    f'📍2ГИС📍\n' \
                    f'{CompanyInfo.two_gis_maps.value}\n' \
                    f'\n' \
                    f'📍Яндекс.Карты📍\n' \
                    f'{CompanyInfo.yandex_maps.value}\n' \
                    f'\n' \
                    f'🏢Адрес🏢\n' \
                    f'{CompanyInfo.address.value}\n' \
                    f'\n' \
                    f'🕣Режим работы🕢\n' \
                    f'{CompanyInfo.work_schedule.value}'

    # feedback
    ask_feedback: str = f'{"<b>"}{ButtonText.feedback.value}{"</b>"}  —  {"<b>"}Шаг 1/1{"</b>"}\n' \
                        f'\n' \
                        f'Напишите текст вашего обращения, это может быть:\n' \
                        f'   — отзыв\n' \
                        f'   — обращение к администрации\n' \
                        f'   — предложение по улучшению сервиса, в том числе данного бота'

    confirm_feedback_success: str = f'✅✅✅\n' \
                                    f'Ваш отзыв успешно отправлен администраторам!\n' \
                                    f'✅✅✅'

    # appointment request
    ask_cons_type: str = f'{"<b>"}{ButtonText.appointment_form.value}{"</b>"}\n' \
                         f'\n' \
                         f'Выберите тип консультации'

    ask_request: str = f'{"<b>"}{ButtonText.appointment_form.value}{"</b>"}  —  {"<b>"}Шаг 1/4{"</b>"}\n' \
                       f'\n' \
                       f'Укажите нужного специалиста или услугу'

    ask_speciality: str = f'{"<b>"}{ButtonText.appointment_form.value}{"</b>"}  —  {"<b>"}Шаг 1/5{"</b>"}\n' \
                          f'\n' \
                          f'Выберите нужную специальность'

    username_warning: str = f'❗❗❗\n' \
                            f'Убедительная просьба:\n' \
                            f'   - {"<b>"}не менять @username{"</b>"} в Telegram до того, как с вами свяжется ' \
                            f'администратор\n' \
                            f'   - проверить, что ваши настройки конфиденциальности Telegram позволяют людям, ' \
                            f'не находящимся у вас в контактах, писать вам\n' \
                            f'❗❗❗'

    video_conf_link: str = f'{"<b>"}Ссылка{"</b>"} для подключения:\n'

    confirm_request_success: str = f'✅✅✅\n' \
                                   f'Ваша заявка успешно зарегистрирована!\n' \
                                   f'В ближайшее время с Вами свяжется администратор.\n' \
                                   f'Спасибо, что выбрали {"<b>"}{CompanyInfo.name.value}{"</b>"}!\n' \
                                   f'✅✅✅'

    # doctor creation/update
    ask_to_choose_doctor: str = 'Выберите специалиста, для обновления информации'

    ask_to_choose_specialities: str = f'Выберите {"<b>"}специальности{"</b>"}, ' \
                                      f'по которым будет консультировать специалист'

    ask_to_add_new_specialities: str = f'Введите через запятую "," {"<b>"}новые специальности{"</b>"}, ' \
                                       f'которые отсутствуют в списке'

    ask_to_specify_specialities_to_add: str = 'Укажите специальности, которые необходимо добавить'

    ask_to_specify_specialities_to_del: str = 'Укажите специальности, которые необходимо удалить'

    warn_not_to_choose_all_specialities: str = f'Нельзя удалить все специальности❗\n' \
                                               f'  - Если вы хотите удалить специалиста, то сделайте это в ' \
                                               f'соответствующем разделе\n' \
                                               f'  - Если же вы редактируете набор специальностей, то сначала ' \
                                               f'добавьте новые специальности, так как нельзя оставлять набор пустым'

    ask_doctor_name: str = f'Введите {"<b>"}ФИО{"</b>"}'

    ask_doctor_photo: str = f'Отправьте {"<b>"}фото{"</b>"} как ДОКУМЕНТ'

    ask_doctor_photo_again: str = f'Отправьте фото в корректном формате {"<b>"}как ДОКУМЕНТ{"</b>"}, НЕ как КАРТИНКУ'

    ask_doctor_description: str = f'Введите {"<b>"}описание{"</b>"} (полный спектр специальностей, ' \
                                  f'которыми владеет специалист)'

    ask_to_choose_experience: str = f'Хотите ли указать {"<b>"}опыт/стаж{"</b>"} специалиста?'

    ask_doctor_experience: str = f'Введите {"<b>"}опыт/стаж{"</b>"} специалиста в числовом формате (просто число)'

    ask_doctor_experience_again: str = f'Пожалуйста введите {"<b>"}целое число{"</b>"}, ' \
                                       f'эквивалетное рабочему стажу специалиста'

    ask_doctor_science_degree: str = f'Выберите {"<b>"}ученую степень{"</b>"}'

    ask_doctor_qual_category: str = f'Выберите {"<b>"}квалификационную категорию{"</b>"}'

    successful_doctor_creation: str = f'✅✅✅\n' \
                                      f'Специалист успешно добавлен!\n' \
                                      f'✅✅✅'

    successful_parameter_change: str = f'✅✅✅\n' \
                                       f'Данные успешно обновлены!\n' \
                                       f'✅✅✅'

    # doctor deletion
    ask_to_choose_doctors: str = f'Выберите {"<b>"}специалистов{"</b>"}, которых необходимо {"<b>"}удалить{"</b>"}'

    successful_doctors_deletion: str = f'✅✅✅\n' \
                                       f'Специалисты успешно удалены!\n' \
                                       f'✅✅✅'

    # doctors info cards
    ask_to_choose_card: str = 'Выберите специалиста, чью карточку хотите посмотреть'

    # statistic
    ask_period: str = f'Укажите период, за который необходимо предоставить статистику, в формате:\n' \
                      f'{"<b>"}ДД-ММ-ГГГГ ДД-ММ-ГГГГ{"</b>"}'

    ask_period_again: str = f'Введите временной период в корректном формате:\n' \
                            f'{"<b>"}ДД-ММ-ГГГГ ДД-ММ-ГГГГ{"</b>"}'

    # admin creation
    ask_uid: str = f'Введите {"<b>"}уникальный id{"</b>"} пользователя в Telegram'

    ask_uid_again: str = f'Введите уникальный id пользователя в Telegram в виде ' \
                         f'{"<b>"}целого числа без лишних символов{"</b>"}'

    admin_already_exists: str = f'❌❌❌\n' \
                                f'Администратор с указанным id уже существует\n' \
                                f'❌❌❌'

    ask_admin_name: str = f'Введите {"<b>"}имя{"</b>"} администратора, желательно в форме ФИО'

    ask_privilege_type: str = 'Выберите уровень привилегий'

    successful_admin_creation: str = f'✅✅✅\n' \
                                     f'Администратор успешно добавлен!\n' \
                                     f'✅✅✅'

    # admin deletion
    ask_to_choose_admins: str = f'Выберите {"<b>"}администраторов{"</b>"}, которых необходимо {"<b>"}удалить{"</b>"}'

    successful_admins_deletion: str = f'✅✅✅\n' \
                                      f'Администраторы успешно удалены!\n' \
                                      f'✅✅✅'

    # access
    lack_of_privileges: str = f'У вас нет доступа к этому разделу ❌'

    # health check
    html_page_layout_changed: str = f'⚠️{"<b>"}Макет HTML страницы изменился{"</b>"}❗\n' \
                                    f'Необходимо поправить генерацию ссылки'

    """
    Bot messages which require input content
    Many of them are universal and are used in several sections
    """

    # menu description
    @staticmethod
    def menu_desc(instruction: bool = False) -> str:
        instruction_text: str
        instruction_text = f'Перед началом работы ознакомьтесь с разделом ' \
                           f'«{"<b>"}{ButtonText.instruction.value}{"</b>"}», ' \
                           f'доступном в самом низу главного меню\n\n'
        return f'Добро пожаловать!\n' \
               f'\n' \
               f'Теперь записаться в клинику {"<b>"}{CompanyInfo.name.value}{"</b>"} стало ещё проще!\n' \
               f'\n' \
               f'{instruction_text if instruction else ""}' \
               f'Ниже выберите то, что вас интересует:'

    # appointment/callback request
    @staticmethod
    def ask_name(section: str, stage: str) -> str:
        title: str
        title = ButtonText.callback_form.value if section == CallbackData.callback_request.value \
            else ButtonText.appointment_form.value
        return f'{"<b>"}{title}{"</b>"}  —  {"<b>"}Шаг {stage}{"</b>"}\n' \
               f'\n' \
               f'Введите ваше имя'

    @staticmethod
    def ask_phone(section: str, stage: str, again: bool = False, instead: bool = False) -> str:
        title: str
        no_username: str

        title = ButtonText.callback_form.value if section == CallbackData.callback_request.value \
            else ButtonText.appointment_form.value
        no_username = f'❌ К сожалению, у вас {"<b>"}отсутствует @username{"</b>"} в Telegram\n\n'
        return f'{"<b>"}{title}{"</b>"}  —  {"<b>"}Шаг {stage}{"</b>"}\n' \
               f'\n' \
               f'{no_username if instead else ""}' \
               f'{"Пожалуйста введите корректный номер (сотовый номер оператора РФ)" if again else "Введите контактный номер телефона"}'

    @staticmethod
    def chosen_speciality(speciality: str) -> str:
        return f'Специалисты из раздела "{"<b>"}{speciality}{"</b>"}"\n' \
               f'⬇⬇⬇⬇⬇'

    @staticmethod
    def chosen_doctor(doctor: str, speciality: str) -> str:
        return f'{"<b>"}{ButtonText.appointment_form.value}{"</b>"}  —  {"<b>"}Шаг 1/5{"</b>"}\n' \
               f'\n' \
               f'Выбран {speciality} — {doctor} ✅'

    @staticmethod
    def ask_dt_choice(stage: str) -> str:
        return f'{"<b>"}{ButtonText.appointment_form.value}{"</b>"}  —  {"<b>"}Шаг {stage}{"</b>"}\n' \
               f'\n' \
               f'Желаете ли сейчас указать предпочтительное время/дату приема?'

    @staticmethod
    def no_dt(stage: str) -> str:
        return f'{"<b>"}{ButtonText.appointment_form.value}{"</b>"}  —  {"<b>"}Шаг {stage}{"</b>"}\n' \
               f'\n' \
               f'Предпочтительные дата/время не указаны 👌'

    @staticmethod
    def ask_dt(stage: str) -> str:
        return f'{"<b>"}{ButtonText.appointment_form.value}{"</b>"}  —  {"<b>"}Шаг {stage}{"</b>"}\n' \
               f'\n' \
               f'Введите удобные дату/время приема\n' \
               f'{"<u>"}Лучше указать несколько вариантов{"</u>"}'

    @staticmethod
    def ask_com_type(stage: str) -> str:
        return f'{"<b>"}{ButtonText.appointment_form.value}{"</b>"}  —  {"<b>"}Шаг {stage}{"</b>"}\n' \
               f'\n' \
               f'Выберите тип коммуникации с администратором'

    @staticmethod
    def com_type_choice(stage: str, com_type: str) -> str:
        return f'{"<b>"}{ButtonText.appointment_form.value}{"</b>"}  —  {"<b>"}Шаг {stage}{"</b>"}\n' \
               f'\n' \
               f'Выбран тип коммуникации ' \
               f'«{"<b>"}' \
               f'{ButtonText.call.value if com_type == CommunicationType.call.value else ButtonText.chat.value}' \
               f'{"</b>"}»'

    @staticmethod
    def appointment_request(details: Dict[str, str]) -> str:
        return f'{"<b>"}📅Запись📅{"</b>"}\n' \
               f'{"<em>"}Имя{"</em>"}:  {details["name"]}\n' \
               f'{"<em>"}Контакт{"</em>"}:  ' \
               f'{"+" + details["phone"] if details["phone"] else "@" + details["username"]}\n' \
               f'{"<em>"}Тип консультации{"</em>"}:  ' \
               f'{"<b>"}{"❗Онлайн❗" if details["consultation_type"] == ConsultationType.online.value else "Очно"}{"</b>"}\n' \
               f'{"<em>"}Тип связи{"</em>"}:  ' \
               f'{"Звонок" if details["communication_type"] == CommunicationType.call.value else "Чат"}\n' \
               f'{"<em>"}Специалист/Услуга{"</em>"}:  {details["user_request"]}' \
               f'{" как " + details["speciality_title"] if details["speciality_title"] else ""}\n' \
               f'{"<em>"}Пожелания по времени/дате{"</em>"}:  {"-" if not details["datetime"] else details["datetime"]}'

    @staticmethod
    def callback_request(details: Dict[str, str]) -> str:
        return f'{"<b>"}☎Обратный звонок☎{"</b>"}\n' \
               f'{"<em>"}Имя{"</em>"}:  {details["name"]}\n' \
               f'{"<em>"}Телефон{"</em>"}:  {"+" + details["phone"]}'

    # feedback request
    @staticmethod
    def feedback_request(details: Dict[str, str]) -> str:
        return f'{"<b>"}📝Обратная связь📝{"</b>"}\n' \
               f'{"<em>"}Имя-Фамилия{"</em>"}:  {details["full_name"]}\n' \
               f'{"<em>"}username{"</em>"}:  {"@" + details["username"] if details["username"] else "-"}\n' \
               f'{"<em>"}id{"</em>"}:  {details["user_uid"]}\n' \
               f'{"<em>"}Сообщение{"</em>"}:\n' \
               f'{details["message"]}'

    # doctor creation/update
    @staticmethod
    def ask_doctor_price(speciality: str, again: bool = False) -> str:
        if again:
            return f'Пожалуйста введите {"<b>"}целое число{"</b>"}, эквивалетное цене (₽) приема ' \
                   f'по специальности "{"<b>"}{speciality}{"</b>"}"'
        else:
            return f'Введите {"<b>"}цену (₽){"</b>"} за прием по специальности ' \
                   f'"{"<b>"}{speciality}{"</b>"}" в числовом формате (просто число)'

    @staticmethod
    def ask_to_choose_section(doc_name: str) -> str:
        return f'Специалист "{"<b>"}{doc_name}{"</b>"}"\n' \
               f'\n' \
               f'Выберите {"<b>"}параметр{"</b>"}, который необходимо {"<b>"}изменить{"</b>"}'

    @staticmethod
    def current_value(doc_name: str, value: Union[str, List[str], None], section: str) -> str:
        if section == CallbackData.photo.value:
            return f'Вы хотите изменить {"<b>"}фото{"</b>"} у специалиста "{"<b>"}{doc_name}{"</b>"}"? '
        else:
            value: str = ", ".join(value) if type(value) is list else value
            return f'Специалист "{"<b>"}{doc_name}{"</b>"}"\n' \
                   f'\n' \
                   f'Текущее значение выбранноого параметра "{"<b>"}{"Отсутствует" if not value else value}{"</b>"}"'

    @staticmethod
    def doc_specialities(doc_name: str) -> str:
        return f'Специалист "{"<b>"}{doc_name}{"</b>"}"\n' \
               f'\n' \
               f'Выберите {"<b>"}специальность{"</b>"}, для которой нужно изменить {"<b>"}цену (₽){"</b>"}'

    @staticmethod
    def ask_to_choose_action(doc_name: str) -> str:
        return f'Специалист "{"<b>"}{doc_name}{"</b>"}"\n' \
               f'\n' \
               f'Пожалуйста выберите действие со специальностями'

    # doctors info cards
    @staticmethod
    def doctor_info(full_name: str, description: str, experience: int, science_degree: str,
                    qual_category: str, price: Union[int, List[int]], speciality: str = None) -> str:
        ex_line: str
        sd_line: str
        qc_line: str
        space: str
        new_line: str
        price_list: str

        ex_line = f'{"<b>"}📚 Стаж(лет){"</b>"}: '
        sd_line = f'{"<b>"}🔬 Степень{"</b>"}: '
        qc_line = f'{"<b>"}🏅 Категория{"</b>"}: '
        space = ''
        new_line = "\n"
        if hasattr(price, '__len__'):
            price_list = f'{"<b>"}💰 Цены{"</b>"}'
            for i in range(len(price)):
                price_list += f'\n — {"<em>"}{speciality[i]}{"</em>"} — {price[i]} ₽'
        else:
            price_list = f'{"<b>"}✅ Цена{"</b>"}: {price} ₽'
        return f'{"<b>"}{full_name}{"</b>"}\n' \
               f'{description}\n' \
               f'{new_line + ex_line + space + str(experience) if experience else ""}' \
               f'{new_line + sd_line + space + science_degree if science_degree else ""}' \
               f'{new_line + qc_line + space + qual_category if qual_category else ""}' \
               f'{new_line if not experience and not science_degree and not qual_category else 2 * new_line}' \
               f'{price_list}'

    # statistic
    @staticmethod
    def statistic(n_callback: int, n_appointment_offline: int, n_appointment_online: int, n_feedback: int,
                  n_new_users: int, callback_change: float = None, offline_change: float = None,
                  online_change: float = None, new_users_change: float = None, period_type: str = None,
                  start_date: str = None, end_date: str = None, scheduler: bool = False) -> str:

        stat_period: Dict[str, str] = {
            CallbackData.day.value: ButtonText.day_statistic.value,
            CallbackData.week.value: ButtonText.week_statistic.value,
            CallbackData.month.value: ButtonText.month_statistic.value,
            CallbackData.quarter.value: ButtonText.quarter_statistic.value,
            CallbackData.year.value: ButtonText.year_statistic.value
        }

        def check_trend(value: float) -> str:
            if value > 0:
                return f'{"<b>"}+ {value}%{"</b>"} ⬆'
            elif value < 0:
                return f'{"<b>"}- {abs(value)}%{"</b>"} ⬇'
            else:
                return f'{"<b>"}+ {value}%{"</b>"}'

        return f'{"#отчет #" + period_type + " #бот" if scheduler else ""}\n' \
               f'📊 Статистика {"<b>"}{stat_period[period_type] if period_type else start_date + " - " + end_date}{"</b>"}\n' \
               f'\n' \
               f'Обратный звонок = {n_callback} ' \
               f'{"⇒ " + check_trend(callback_change) if callback_change is not None else ""}\n' \
               f'Очная консульт. = {n_appointment_offline} ' \
               f'{"⇒ " + check_trend(offline_change) if offline_change is not None else ""}\n' \
               f'Онлайн консульт. = {n_appointment_online} ' \
               f'{"⇒ " + check_trend(online_change) if online_change is not None else ""}\n' \
               f'Обратная связь = {n_feedback}\n\n' \
               f'Новые польз-ли = {n_new_users} ' \
               f'{"⇒ " + check_trend(new_users_change) if new_users_change is not None else ""}'

    # admin creation/deletion, doctor deletion
    @staticmethod
    def confirm_deletion(employees: List[str]) -> str:
        employees_list: str = "- " + "\n- ".join(employees)
        return f'Подтвердите удаление следующих сотрудников:\n' \
               f'{"<b>"}{employees_list}{"</b>"}'

    @staticmethod
    def confirm_creation(uid: int, name: str, privilege_type: str = None) -> str:
        privilege_lvl: str
        privilege_lvl = f'- {"<b>"}Тип привилегий{"</b>"}:  ' \
                        f'{ButtonText.high_privilege.value if privilege_type == CallbackData.high.value else ButtonText.low_privilege.value}'
        return f'Подтвердите создание администратора с:\n' \
               f'- {"<b>"}id{"</b>"}:  {uid}\n' \
               f'- {"<b>"}Имя{"</b>"}:  {name}\n' \
               f'{privilege_lvl}'
