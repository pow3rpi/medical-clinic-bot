from typing import Any, List, Dict, Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.keyboards.client_kb import (
    appointment_form, callback_form, feedback,
    contacts, instruction, back_to_menu_btn
)
from src.core.enums import (
    CallbackData, ButtonText, ScienceDegree,
    QualCategory, Symbols, AdminPrivilegeType
)
from src.core.processing import transform_name

"""
----------------------------------------------------
BUTTONS
----------------------------------------------------
"""
admin_panel = InlineKeyboardButton(
    text=ButtonText.admin_panel.value,
    callback_data=CallbackData.admin_menu_nav.value + Symbols.separator.value + CallbackData.admin_panel.value
)
doctors_settings = InlineKeyboardButton(
    text=ButtonText.doctors.value,
    callback_data=CallbackData.admin_menu_nav.value + Symbols.separator.value + CallbackData.doctors_settings.value
)
statistics = InlineKeyboardButton(
    text=ButtonText.statistics.value,
    callback_data=CallbackData.admin_menu_nav.value + Symbols.separator.value + CallbackData.statistics.value
)
admins_settings = InlineKeyboardButton(
    text=ButtonText.admins.value,
    callback_data=CallbackData.admin_menu_nav.value + Symbols.separator.value + CallbackData.admins.value
)
create_doctor = InlineKeyboardButton(
    text=ButtonText.create.value,
    callback_data=CallbackData.create_doctor.value
)
update_doctor = InlineKeyboardButton(
    text=ButtonText.update_info.value,
    callback_data=CallbackData.update_doctor.value
)
delete_doctor = InlineKeyboardButton(
    text=ButtonText.delete.value,
    callback_data=CallbackData.delete_doctor.value
)
show_doctor = InlineKeyboardButton(
    text=ButtonText.cards.value,
    callback_data=CallbackData.show_doctor.value
)
day_statistics = InlineKeyboardButton(
    text=ButtonText.day_statistic.value,
    callback_data=CallbackData.statistics.value + Symbols.separator.value + CallbackData.day.value
)
week_statistics = InlineKeyboardButton(
    text=ButtonText.week_statistic.value,
    callback_data=CallbackData.statistics.value + Symbols.separator.value + CallbackData.week.value
)
month_statistics = InlineKeyboardButton(
    text=ButtonText.month_statistic.value,
    callback_data=CallbackData.statistics.value + Symbols.separator.value + CallbackData.month.value
)
quarter_statistics = InlineKeyboardButton(
    text=ButtonText.quarter_statistic.value,
    callback_data=CallbackData.statistics.value + Symbols.separator.value + CallbackData.quarter.value
)
year_statistics = InlineKeyboardButton(
    text=ButtonText.year_statistic.value,
    callback_data=CallbackData.statistics.value + Symbols.separator.value + CallbackData.year.value
)
custom_statistics = InlineKeyboardButton(
    text=ButtonText.custom_statistic.value,
    callback_data=CallbackData.custom_statistics.value
)
create_admin = InlineKeyboardButton(
    text=ButtonText.create.value,
    callback_data=CallbackData.create_admin.value
)
delete_admin = InlineKeyboardButton(
    text=ButtonText.delete.value,
    callback_data=CallbackData.delete_admin.value
)
phd = InlineKeyboardButton(
    text=ButtonText.phd.value,
    callback_data=CallbackData.choose_science_degree.value + Symbols.separator.value + ScienceDegree.phd.value
)
pre_phd = InlineKeyboardButton(
    text=ButtonText.pre_phd.value,
    callback_data=CallbackData.choose_science_degree.value + Symbols.separator.value + ScienceDegree.pre_phd.value
)
no_specification_sd = InlineKeyboardButton(
    text=ButtonText.no_specification.value,
    callback_data=CallbackData.choose_science_degree.value + Symbols.separator.value + CallbackData.no_specification.value
)
highest_category = InlineKeyboardButton(
    text=ButtonText.highest_category.value,
    callback_data=CallbackData.choose_qual_category.value + Symbols.separator.value + QualCategory.highest.value
)
first_category = InlineKeyboardButton(
    text=ButtonText.first_category.value,
    callback_data=CallbackData.choose_qual_category.value + Symbols.separator.value + QualCategory.first.value
)
second_category = InlineKeyboardButton(
    text=ButtonText.second_category.value,
    callback_data=CallbackData.choose_qual_category.value + Symbols.separator.value + QualCategory.second.value
)
no_specification_qc = InlineKeyboardButton(
    text=ButtonText.no_specification.value,
    callback_data=CallbackData.choose_qual_category.value + Symbols.separator.value + CallbackData.no_specification.value
)
experience_yes = InlineKeyboardButton(
    text=ButtonText.experience_yes.value,
    callback_data=CallbackData.experience.value + Symbols.separator.value + CallbackData.yes.value
)
experience_no = InlineKeyboardButton(
    text=ButtonText.experience_no.value,
    callback_data=CallbackData.experience.value + Symbols.separator.value + CallbackData.no.value
)
selection_completed = InlineKeyboardButton(
    text=ButtonText.selection_completed.value,
    callback_data=CallbackData.selection_completed.value
)
confirmation = InlineKeyboardButton(
    text=ButtonText.confirmation.value,
    callback_data=CallbackData.confirmation.value
)
change_choice = InlineKeyboardButton(
    text=ButtonText.change.value,
    callback_data=CallbackData.change_choice.value
)
high_privilege = InlineKeyboardButton(
    text=ButtonText.high_privilege.value,
    callback_data=CallbackData.privilege.value + Symbols.separator.value + AdminPrivilegeType.high.value
)
low_privilege = InlineKeyboardButton(
    text=ButtonText.low_privilege.value,
    callback_data=CallbackData.privilege.value + Symbols.separator.value + AdminPrivilegeType.low.value
)
full_name = InlineKeyboardButton(
    text=ButtonText.full_name.value,
    callback_data=CallbackData.choose_section.value + Symbols.separator.value + CallbackData.full_name.value
)
photo = InlineKeyboardButton(
    text=ButtonText.photo.value,
    callback_data=CallbackData.choose_section.value + Symbols.separator.value + CallbackData.photo.value
)
description = InlineKeyboardButton(
    text=ButtonText.description.value,
    callback_data=CallbackData.choose_section.value + Symbols.separator.value + CallbackData.description.value
)
doc_specialities = InlineKeyboardButton(
    text=ButtonText.specialities.value,
    callback_data=CallbackData.choose_section.value + Symbols.separator.value + CallbackData.speciality.value
)
experience = InlineKeyboardButton(
    text=ButtonText.experience.value,
    callback_data=CallbackData.choose_section.value + Symbols.separator.value + CallbackData.experience.value
)
science_degree = InlineKeyboardButton(
    text=ButtonText.science_degree.value,
    callback_data=CallbackData.choose_section.value + Symbols.separator.value + CallbackData.science_degree.value
)
qual_category = InlineKeyboardButton(
    text=ButtonText.qual_category.value,
    callback_data=CallbackData.choose_section.value + Symbols.separator.value + CallbackData.qual_category.value
)
price = InlineKeyboardButton(
    text=ButtonText.price.value,
    callback_data=CallbackData.choose_section.value + Symbols.separator.value + CallbackData.price.value
)
change = InlineKeyboardButton(
    text=ButtonText.change.value,
    callback_data=CallbackData.change_info.value
)
edit = InlineKeyboardButton(
    text=ButtonText.edit.value,
    callback_data=CallbackData.edit.value
)
add_specialities = InlineKeyboardButton(
    text=ButtonText.create.value,
    callback_data=CallbackData.add_specialities.value
)
delete_specialities = InlineKeyboardButton(
    text=ButtonText.delete.value,
    callback_data=CallbackData.delete_specialities.value
)


def step_back_button(section: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=ButtonText.prev.value,
        callback_data=section
    )


"""
----------------------------------------------------
KEYBOARDS
----------------------------------------------------
"""
main_menu_admin = InlineKeyboardMarkup(row_width=1) \
    .add(callback_form) \
    .add(appointment_form) \
    .add(feedback) \
    .add(contacts) \
    .add(instruction) \
    .add(admin_panel)

doctors_settings_menu = InlineKeyboardMarkup(row_width=1) \
    .add(create_doctor) \
    .add(update_doctor) \
    .add(delete_doctor) \
    .add(show_doctor) \
    .add(step_back_button(section=CallbackData.admin_menu_nav.value + Symbols.separator.value + CallbackData.admin_panel.value))

admin_panel_menu = InlineKeyboardMarkup(row_width=1) \
    .add(doctors_settings) \
    .add(statistics) \
    .add(admins_settings) \
    .add(step_back_button(section=CallbackData.admin_menu_nav.value + Symbols.separator.value + CallbackData.main_menu.value))

statistics_menu = InlineKeyboardMarkup(row_width=2) \
    .row(day_statistics, week_statistics) \
    .row(month_statistics, year_statistics) \
    .add(custom_statistics) \
    .add(step_back_button(section=CallbackData.admin_menu_nav.value + Symbols.separator.value + CallbackData.admin_panel.value))

admins_config_menu = InlineKeyboardMarkup(row_width=1) \
    .add(create_admin) \
    .add(delete_admin) \
    .add(step_back_button(section=CallbackData.admin_menu_nav.value + Symbols.separator.value + CallbackData.admin_panel.value))

science_degrees_list = InlineKeyboardMarkup(row_width=1) \
    .add(phd) \
    .add(pre_phd) \
    .add(no_specification_sd) \
    .add(back_to_menu_btn(section=CallbackData.doctors_settings.value))

qual_categories_list = InlineKeyboardMarkup(row_width=1) \
    .add(highest_category) \
    .add(first_category) \
    .add(second_category) \
    .add(no_specification_qc) \
    .add(back_to_menu_btn(section=CallbackData.doctors_settings.value))

experience_specification = InlineKeyboardMarkup(row_width=2) \
    .row(experience_yes, experience_no) \
    .add(back_to_menu_btn(section=CallbackData.admins.value))

privilege_type = InlineKeyboardMarkup(row_width=2) \
    .row(high_privilege, low_privilege) \
    .add(back_to_menu_btn(section=CallbackData.admins.value))

doctor_info_sections = InlineKeyboardMarkup(row_width=1) \
    .add(full_name) \
    .add(photo) \
    .add(description) \
    .add(doc_specialities) \
    .add(experience) \
    .add(science_degree) \
    .add(qual_category) \
    .add(price) \
    .add(step_back_button(section=CallbackData.update_doctor.value)) \
    .add(back_to_menu_btn(section=CallbackData.doctors_settings.value))

doctor_card = InlineKeyboardMarkup(row_width=1) \
    .add(edit) \
    .add(step_back_button(section=CallbackData.back_to_doctors.value)) \
    .add(back_to_menu_btn(section=CallbackData.doctors_settings.value))

specialities_config = InlineKeyboardMarkup(row_width=1) \
    .add(add_specialities) \
    .add(delete_specialities) \
    .add(step_back_button(section=CallbackData.cur_value.value)) \
    .add(back_to_menu_btn(section=CallbackData.doctors_settings.value))


def change_info(section: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(row_width=1) \
        .add(change) \
        .add(step_back_button(section=section)) \
        .add(back_to_menu_btn(section=CallbackData.doctors_settings.value))


def show_specialities(specialities: List[str], ids: List[Any], marked_specialities: List[str],
                      delete: bool = False) -> InlineKeyboardMarkup:
    speciality_buttons: List[InlineKeyboardButton]
    speciality_buttons = [InlineKeyboardButton(
        text='■ ' + specialities[i] if specialities[i] in marked_specialities else '□ ' + specialities[i],
        callback_data=CallbackData.speciality_title.value + Symbols.separator.value + str(ids[i])
    ) for i in range(len(specialities))]
    if delete:
        return InlineKeyboardMarkup(row_width=3) \
            .add(*speciality_buttons) \
            .add(selection_completed) \
            .add(back_to_menu_btn(section=CallbackData.doctors_settings.value))
    else:
        return InlineKeyboardMarkup(row_width=3) \
            .add(*speciality_buttons) \
            .add(InlineKeyboardButton(
                text=ButtonText.add_specialities.value,
                callback_data=CallbackData.new_specialities.value
            )) \
            .add(selection_completed) \
            .add(back_to_menu_btn(section=CallbackData.doctors_settings.value))


def show_doc_specialities(specialities: List[str], ids: List[Any]) -> InlineKeyboardMarkup:
    speciality_buttons: List[InlineKeyboardButton]
    speciality_buttons = [InlineKeyboardButton(
        text=specialities[i],
        callback_data=CallbackData.speciality_title.value + Symbols.separator.value + str(ids[i])
    ) for i in range(len(specialities))]
    return InlineKeyboardMarkup(row_width=2) \
        .add(*speciality_buttons) \
        .add(step_back_button(section=CallbackData.choose_section.value)) \
        .add(back_to_menu_btn(section=CallbackData.doctors_settings.value))


def show_admins(admins: Dict[str, str], section: str, marked_uids: List[str],
                accept_btn: bool = True) -> InlineKeyboardMarkup:
    admin_buttons: List[InlineKeyboardButton]
    admin_buttons = [InlineKeyboardButton(
        text=transform_name(name) if marked_uids is None \
            else ('■ ' + transform_name(name) if uid in marked_uids else '□ ' + transform_name(name)),
        callback_data=CallbackData.choose_person.value + Symbols.separator.value + uid
    ) for uid, name in admins.items()]
    if accept_btn:
        return InlineKeyboardMarkup(row_width=3) \
            .add(*admin_buttons) \
            .add(selection_completed) \
            .add(back_to_menu_btn(section=section))
    else:
        return InlineKeyboardMarkup(row_width=3) \
            .add(*admin_buttons) \
            .add(back_to_menu_btn(section=section))


def show_doctors(doctors: Dict[str, str], section: str, marked_uids: Optional[List[str]] = None,
                 accept_btn: bool = True) -> InlineKeyboardMarkup:
    return show_admins(
        admins=doctors,
        section=section,
        marked_uids=marked_uids,
        accept_btn=accept_btn
    )


def step_back(section: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(row_width=1) \
        .add(step_back_button(section=CallbackData.admin_menu_nav.value + Symbols.separator.value + section))


def confirmation_menu(section: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(row_width=2) \
        .row(change_choice, confirmation) \
        .add(back_to_menu_btn(section=section))
