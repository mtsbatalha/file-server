"""
CLI Main Menu
Interactive command-line interface for File Server Management
"""

import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import questionary
from questionary import Style

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

console = Console()

# Custom style
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#f44336 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#cc5454'),
    ('separator', 'fg:#cc5454'),
    ('instruction', ''),
    ('text', ''),
])


def show_banner():
    """Display application banner"""
    banner = """
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║     📦 FILE SERVER MANAGEMENT SYSTEM                               ║
║                                                                    ║
║     Multi-Protocol File Server Management                          ║
║     Version 1.0.0                                                  ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def show_protocol_status():
    """Show status of all protocols"""
    # TODO: Fetch actual status from API
    table = Table(title="Protocol Status", box=box.ROUNDED)
    
    table.add_column("Protocol", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Port", style="green")
    table.add_column("SSL", style="yellow")
    
    protocols = [
        ("FTP/FTPS", "Not Installed", "21", "❌"),
        ("SFTP", "Not Installed", "22", "✅"),
        ("SMB/CIFS", "Not Installed", "445", "❌"),
        ("NFS", "Not Installed", "2049", "❌"),
        ("WebDAV", "Not Installed", "8080", "❌"),
        ("S3 (MinIO)", "Not Installed", "9000", "❌"),
        ("NextCloud", "Not Installed", "8081", "✅"),
    ]
    
    for name, status, port, ssl in protocols:
        table.add_row(name, status, port, ssl)
    
    console.print(table)


def manage_protocols():
    """Protocol management submenu"""
    while True:
        console.clear()
        show_banner()
        
        choice = questionary.select(
            "Protocol Management:",
            choices=[
                "📄 View Protocol Status",
                "📥 Install Protocol",
                "▶️  Start Protocol",
                "⏹️  Stop Protocol",
                "⚙️  Configure Protocol",
                "🗑️  Uninstall Protocol",
                "⬅️  Back to Main Menu"
            ],
            style=custom_style
        ).ask()
        
        if not choice or "Back" in choice:
            break
        elif "View" in choice:
            show_protocol_status()
            questionary.press_any_key_to_continue().ask()
        elif "Install" in choice:
            install_protocol_menu()
        else:
            console.print("[yellow]Feature not implemented yet[/yellow]")
            questionary.press_any_key_to_continue().ask()


def install_protocol_menu():
    """Install protocol submenu"""
    protocol = questionary.select(
        "Select protocol to install:",
        choices=[
            "FTP/FTPS",
            "SFTP",
            "SMB/CIFS",
            "NFS",
            "WebDAV",
            "S3 (MinIO)",
            "NextCloud",
            "Cancel"
        ],
        style=custom_style
    ).ask()
    
    if protocol and protocol != "Cancel":
        with console.status(f"[bold green]Installing {protocol}..."):
            # TODO: Call API to install protocol
            import time
            time.sleep(2)
        
        console.print(f"[green]✅ {protocol} installed successfully![/green]")
        questionary.press_any_key_to_continue().ask()


def manage_users():
    """User management submenu"""
    console.print("[yellow]User management not implemented yet[/yellow]")
    questionary.press_any_key_to_continue().ask()


def manage_paths():
    """Shared paths management submenu"""
    console.print("[yellow]Path management not implemented yet[/yellow]")
    questionary.press_any_key_to_continue().ask()


def manage_quotas():
    """Quotas management submenu"""
    console.print("[yellow]Quota management not implemented yet[/yellow]")
    questionary.press_any_key_to_continue().ask()


def view_logs():
    """View logs submenu"""
    console.print("[yellow]Log viewing not implemented yet[/yellow]")
    questionary.press_any_key_to_continue().ask()


def ssl_config():
    """SSL/TLS configuration submenu"""
    console.print("[yellow]SSL configuration not implemented yet[/yellow]")
    questionary.press_any_key_to_continue().ask()


def start_web_interface():
    """Start web interface"""
    console.print("[bold green]Starting Web Interface...[/bold green]")
    console.print("[cyan]Web interface would start at: http://localhost:8000[/cyan]")
    console.print("[yellow]This will be implemented with actual API server[/yellow]")
    questionary.press_any_key_to_continue().ask()


def system_settings():
    """System settings submenu"""
    console.print("[yellow]System settings not implemented yet[/yellow]")
    questionary.press_any_key_to_continue().ask()


def main_menu():
    """Main application menu"""
    while True:
        console.clear()
        show_banner()
        
        choice = questionary.select(
            "Main Menu:",
            choices=[
                "📦 Install/Manage Protocols",
                "👥 User Management",
                "📁 Shared Paths Configuration",
                "💾 Quotas & Usage",
                "📊 View Logs & Statistics",
                "🔐 SSL/TLS Configuration",
                "🌐 Start Web Interface",
                "⚙️  System Settings",
                "❌ Exit"
            ],
            style=custom_style
        ).ask()
        
        if not choice or "Exit" in choice:
            console.print("\n[bold cyan]Thank you for using File Server Management System![/bold cyan]\n")
            break
        elif "Protocols" in choice:
            manage_protocols()
        elif "User" in choice:
            manage_users()
        elif "Paths" in choice:
            manage_paths()
        elif "Quotas" in choice:
            manage_quotas()
        elif "Logs" in choice:
            view_logs()
        elif "SSL" in choice:
            ssl_config()
        elif "Web" in choice:
            start_web_interface()
        elif "Settings" in choice:
            system_settings()


def main():
    """Entry point"""
    try:
        # Check if running as root/admin
        import platform
        if platform.system() != "Windows":
            if os.geteuid() != 0:
                console.print("[bold red]⚠️  Warning: This tool should be run as root (sudo)[/bold red]\n")
                if not questionary.confirm("Continue anyway?", default=False).ask():
                    return
        
        main_menu()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user[/yellow]\n")
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]\n")


if __name__ == "__main__":
    main()
