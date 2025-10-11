import flet as ft
from database import (
    update_contact_db,
    delete_contact_db,
    add_contact_db,
    get_all_contacts_db,
)

def theme_change(page, theme_switch, show_snackbar):

    if theme_switch.value:
        page.theme_mode = ft.ThemeMode.DARK
        theme_message = "Dark mode enabled"
    else:
        page.theme_mode = ft.ThemeMode.LIGHT
        theme_message = "Light mode enabled"
    
    show_snackbar(theme_message, ft.Colors.SECONDARY)


def display_contacts(page, contacts_list_view, db_conn, search_query=None, show_snackbar=None):

    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn, search_query)

    if not contacts:
        contacts_list_view.controls.append(
            ft.Container(
                ft.Text(
                    "No contacts found.",
                    size=16,
                    color=ft.Colors.GREY,
                    text_align=ft.TextAlign.CENTER,
                ),
                alignment=ft.alignment.center,
                padding=20,
            )
        )
        page.update()
        return

    for contact in contacts:
        contact_id, name, phone, email = contact

        # FIX: Create a factory function to properly capture contact values
        def make_edit_handler(contact_data):
            def handler(e):
                open_edit_dialog(page, contact_data, db_conn, contacts_list_view, show_snackbar)
            return handler

        def make_delete_handler(cid):
            def handler(e):
                delete_contact_confirmation(page, cid, db_conn, contacts_list_view, show_snackbar)
            return handler

        contact_card = ft.Card(
            ft.Container(
                content=ft.Row(
                    [
                        ft.CircleAvatar(
                            content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE),
                            bgcolor="#39516d",
                        ),
                        ft.Column(
                            [
                                ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(f"📞 {phone}", size=14),
                                ft.Text(f"✉️ {email or 'N/A'}", size=13, color=ft.Colors.OUTLINE),
                            ],
                            spacing=2,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Container(expand=True),
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    tooltip="Edit",
                                    icon_color=ft.Colors.SECONDARY,
                                    on_click=make_edit_handler(contact),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    tooltip="Delete",
                                    icon_color=ft.Colors.SECONDARY,
                                    on_click=make_delete_handler(contact_id),
                                ),
                            ],
                            spacing=0,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=10,
            ),
            color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            elevation=1,
            shadow_color=ft.Colors.OUTLINE_VARIANT,
        )

        contacts_list_view.controls.append(contact_card)

    page.update()


def add_contact(page, inputs, contacts_list_view, db_conn, show_snackbar):
    name_input, phone_input, email_input = inputs

    name = name_input.value.strip()
    phone = phone_input.value.strip()
    email = email_input.value.strip()

    if not name:
        name_input.error_text = "Name is required."
        page.update()
        return

    if not phone:
        phone_input.error_text = "Phone number is required."
        page.update()
        return

    if not phone.isdigit():
        phone_input.error_text = "Phone number must contain only digits."
        page.update()
        return

    name_input.error_text = None
    phone_input.error_text = None

    add_contact_db(db_conn, name, phone, email)

    name_input.value = ""
    phone_input.value = ""
    email_input.value = ""

    display_contacts(page, contacts_list_view, db_conn, None, show_snackbar)
    show_snackbar("Contact added successfully!", ft.Colors.GREEN)


def delete_contact_confirmation(page, contact_id, db_conn, contacts_list_view, show_snackbar):
    delete_contact_confirmation_dialog = ft.AlertDialog(
        icon=ft.Icon(name=ft.Icons.ERROR, color=ft.Colors.RED),
        title=ft.Text("Delete Confirmation", text_align=ft.TextAlign.CENTER),
        content=ft.Text(f"Are you sure you want to delete this contact?", text_align=ft.TextAlign.CENTER),
        alignment=ft.alignment.center,
        actions=[
            ft.TextButton("Yes", on_click=lambda e: (page.close(delete_contact_confirmation_dialog), delete_contact(page, contact_id, db_conn, contacts_list_view, show_snackbar))),
            ft.TextButton("No", on_click=lambda e: page.close(delete_contact_confirmation_dialog)),
        ],
    )
    page.open(delete_contact_confirmation_dialog)


def delete_contact(page, contact_id, db_conn, contacts_list_view, show_snackbar):

    delete_contact_db(db_conn, contact_id)
    display_contacts(page, contacts_list_view, db_conn, None, show_snackbar)
    show_snackbar(" Contact deleted successfully.", ft.Colors.RED)


def open_edit_dialog(page, contact, db_conn, contacts_list_view, show_snackbar):

    contact_id, name, phone, email = contact
    
    edit_name = ft.TextField(label="Name", value=name)
    edit_phone = ft.TextField(label="Phone", value=phone)
    edit_email = ft.TextField(label="Email", value=email or "")

    def save_and_close(e):

        if not edit_name.value.strip():
            edit_name.error_text = "Name cannot be empty."
            page.update()
            return

        if not edit_phone.value.strip():
            edit_phone.error_text = "Phone cannot be empty."
            page.update()
            return

        if not edit_phone.value.strip().isdigit():
            edit_phone.error_text = "Phone must contain only numbers."
            page.update()
            return

        update_contact_db(db_conn, contact_id, edit_name.value.strip(), edit_phone.value.strip(), edit_email.value.strip())
        page.close(dialog)
        display_contacts(page, contacts_list_view, db_conn, None, show_snackbar)
        show_snackbar("Contact updated successfully!",ft.Colors.BLUE)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
        content=ft.Column([edit_name, edit_phone, edit_email]),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.close(dialog)),
            ft.TextButton("Save", on_click=save_and_close),
        ],
    )
    page.open(dialog)