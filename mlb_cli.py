import pytermgui as ptg
from app.models.data_service import fetch_teams
from app.screens.main_screens import get_yesterday_widgets, get_today_widgets, get_standings_widgets

def main():
    fetch_teams()
    
    with ptg.WindowManager() as manager:
        # Create a single persistent window with a static size
        static_width = 80  # Increased slightly for standings
        static_height = min(30, manager.terminal.height - 2)
        
        main_window = ptg.Window(width=static_width, height=static_height, is_static=True, is_noresize=True)
        manager.add(main_window)

        def update_to_yesterday(button=None, *args):
            widgets, title = get_yesterday_widgets(update_to_today, update_to_standings)
            main_window.set_widgets(widgets)
            main_window.set_title(title)
            main_window.width = static_width
            main_window.height = static_height
            main_window.center()
            return True

        def update_to_today(button=None, *args):
            widgets, title = get_today_widgets(update_to_yesterday, update_to_standings)
            main_window.set_widgets(widgets)
            main_window.set_title(title)
            main_window.width = static_width
            main_window.height = static_height
            main_window.center()
            return True

        def update_to_standings(button=None, *args):
            widgets, title = get_standings_widgets(update_to_yesterday)
            main_window.set_widgets(widgets)
            main_window.set_title(title)
            main_window.width = static_width
            main_window.height = static_height
            main_window.center()
            return True

        def exit_app(*args):
            manager.stop()
            return True

        # Initial content
        update_to_yesterday()
        
        # Global bindings
        manager.bind("[", update_to_yesterday)
        manager.bind("]", update_to_today)
        manager.bind("s", update_to_standings)
        manager.bind(ptg.keys.ESC, exit_app)
        
        manager.run()

if __name__ == "__main__":
    main()
