import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact, theme_change


def main(page: ft.Page):
    page.title = "Contact Book App"
    page.window.width = 400
    page.window.height = 700
    page.window.center()  
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.resizable = False
    page.padding = 15
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.scroll = ft.ScrollMode.AUTO

    db_conn = init_db()

    def show_snackbar(message, color):
        snackbar = ft.SnackBar(
            content=ft.Text(message,  text_align=ft.TextAlign.CENTER, size=14, color=ft.Colors.WHITE),
            bgcolor=color,
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()

    theme_value = ft.Switch(
        value=False,
        scale=0.9,
        on_change=lambda e: theme_change(page, theme_value, show_snackbar),
    )

    header = ft.Row(
        [
            ft.Icon(ft.Icons.CONTACT_PAGE_OUTLINED, color="#39516d", size=30),
            ft.Text("My Contact Book", color = "#39516d",  size=22, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            theme_value,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    name_input = ft.TextField(label="Full Name", width=350, autofocus=True)
    phone_input = ft.TextField(label="Phone Number", width=350)
    email_input = ft.TextField(label="Email Address", width=350)

    def handle_add_contact(e):
        name = name_input.value.strip()
        phone = phone_input.value.strip()

        if not name:
            name_input.error_text = "Name is required"
            page.update()
            return

        if not phone:
            phone_input.error_text = "Phone number is required"
            page.update()
            return

        if not phone.isdigit():
            phone_input.error_text = "Phone number must be numeric"
            page.update()
            return

        name_input.error_text = None
        phone_input.error_text = None

        add_contact(page, (name_input, phone_input, email_input), contacts_list_view, db_conn, show_snackbar)

    add_button = ft.FilledButton(
        text="Add Contact",
        icon=ft.Icons.ADD,
        style=ft.ButtonStyle(bgcolor="#39516d", color=ft.Colors.WHITE),
        on_click=handle_add_contact,
    )

    input_section = ft.Container(
        content=ft.Column(
            [
                ft.Text("Add New Contact", size=18, weight=ft.FontWeight.W_600),
                name_input,
                phone_input,
                email_input,
                add_button,
            ],
            spacing=10,
        ),
        padding=15,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        border_radius=12,
        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.OUTLINE_VARIANT),
    )

    def handle_search(e):
        query = e.control.value.strip()
        display_contacts(page, contacts_list_view, db_conn, query)

    search_box = ft.TextField(
        label="Search Contacts",
        width=350,
        prefix_icon=ft.Icons.SEARCH,
        on_change=handle_search, 
    )

    contacts_list_view = ft.ListView(
        expand=1,
        spacing=8,
        padding=5,
        auto_scroll=False,
    )

    footer = ft.Container(
        ft.Text("© 2025 Contact Book | Built with Flet", size=12, color=ft.Colors.OUTLINE),
        alignment=ft.alignment.center,
        padding=10,
    )

    page.add(
        ft.Column(
            [
                header,
                ft.Divider(),
                input_section,
                ft.Container(search_box, padding=ft.padding.only(top=10, bottom=10)),
                ft.Text("Saved Contacts", size=18, weight=ft.FontWeight.W_600),
                contacts_list_view,
                footer,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
        )
    )

    display_contacts(page, contacts_list_view, db_conn, None, show_snackbar)
    page.update()


if __name__ == "__main__":
    ft.app(target=main)