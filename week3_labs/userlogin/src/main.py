import flet as ft
import mysql.connector
from db_connection import connect_db

def main(page: ft.Page):

    page.window.center()
    page.window.frameless = True
    page.title = "User Login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.height = 350
    page.window.width = 400
    page.shape=ft.BoxDecoration
    page.bgcolor = "#FFD506"  #I prefer this color Sir hehe (it's more closerrr nabother po ako ng slight)

    # Login Title
    login_title = ft.Text(
        "User Login",
        size=20,
        weight=ft.FontWeight.BOLD,
        font_family="Arial",
        color = "Black",
        text_align=ft.TextAlign.CENTER
    )
    
    # Username Input Field
    username_field = ft.TextField(
        label="User name",
        hint_text="Enter your user name",
        helper_text="This is your unique identifier",
        width=300,
        autofocus=True,
        disabled=False,
        icon=ft.Icon ("person",
       color ="#4C4C4C"),
        bgcolor="#03C0FF" #I prefer this color Sir hehe (it's more closerrr)
    )

    # Password Input Field
    password_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        helper_text="This is your secret key",
        width=300,
        disabled=False,
        password=True,
        can_reveal_password=True,
        icon=ft.Icon ("password",
       color ="#4C4C4C"),
        bgcolor="#03C0FF" #I prefer this color Sir hehe (it's more closerrr)
    )
    
    def login_click(e):
        # Create Dialogs for Feedback
        success_dialog = ft.AlertDialog(
            title=ft.Text("Login Successful",
            text_align =ft.TextAlign.CENTER), 
            content=ft.Container(
                content=ft.Text(f"Welcome, {username_field.value}!", text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.center),
            actions=[ft.ElevatedButton("OK", on_click=lambda e: close_dialog(success_dialog))],
            icon=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN)
        )
        
        failure_dialog = ft.AlertDialog(
            title=ft.Text("Login Failed", text_align =ft.TextAlign.CENTER),
            content=ft.Container(
                content=ft.Text("Invalid username or password", text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.center),
            actions=[ft.ElevatedButton("OK", on_click=lambda e: close_dialog(failure_dialog))],
            icon=ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED)
        )
        
        invalid_input_dialog = ft.AlertDialog(
            title=ft.Text("Input Error", text_align =ft.TextAlign.CENTER),
            content=ft.Container(
                content=ft.Text("Please enter username and password", text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.center),
            actions=[ft.ElevatedButton("OK", on_click=lambda e: close_dialog(invalid_input_dialog))],
            icon=ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE)
        )
        
        database_error_dialog = ft.AlertDialog(
            title=ft.Text("Database Error"),
            content=ft.Container(
                content=ft.Text("An error occurred while connecting to the database", text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.center),
            actions=[ft.ElevatedButton("OK", on_click=lambda e: close_dialog(database_error_dialog))]
        )
        
        def close_dialog(dialog):
            dialog.open = False
            page.update()
        
        # Validation and Database Logic that checks if the username or password are empty
        if not username_field.value or not password_field.value:
            page.overlay.append(invalid_input_dialog)
            invalid_input_dialog.open = True
            page.update()
            return
        
        try:
            # Establish database connection
            connection = connect_db()
            cursor = connection.cursor()
            
            # Execute parameterized SQL query to prevent SQL injection
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username_field.value, password_field.value))
            
            # Fetch the result
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if result:
                page.overlay.append(success_dialog)
                success_dialog.open = True
            else:
                page.overlay.append(failure_dialog)
                failure_dialog.open = True
            
            page.update()
            
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            page.overlay.append(database_error_dialog)
            database_error_dialog.open = True
            page.update()
    
    # Login Button
    login_button = ft.ElevatedButton(
        text="Login",
        on_click=login_click,
        width=100,
        icon=ft.Icons.LOGIN
    )
    
    # Add all controls to the page
    page.add(
        login_title,
        ft.Container(
            content=ft.Column(
                [username_field, password_field],
                spacing=20
            )
        ),
        ft.Container(
            content=login_button,
            alignment=ft.alignment.top_right,
            margin=ft.margin.only(top=20, right=40, bottom=40, left=0)
        )
    )

ft.app(target=main)