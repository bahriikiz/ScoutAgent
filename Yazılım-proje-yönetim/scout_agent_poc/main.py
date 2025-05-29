from agent import parse_instruction, confirm_task
from db import init_db, add_task, get_active_tasks
from scheduler import start_scheduler

RECRUITER_ID = "recruiter_1"  # placeholder ID

def handle_add_command(cmd: str):
    """
    Handles the 'add' command, supporting inline instructions or prompting separately.
    """
    if cmd.strip().lower().startswith("add "):
        user_input = cmd.strip()[len("add "):].strip()
    else:
        user_input = input("Enter monitoring instruction: ")

    try:
        details = parse_instruction(user_input)
    except Exception as e:
        print(f"❌ Error parsing instruction: {e}")
        return

    if confirm_task(details):
        task_id = add_task(
            RECRUITER_ID,
            details["url"],
            details["frequency"],
            details["task_prompt"],
        )
        print(f"✅ Task {task_id} added and active.")
    else:
        print("⚠️ Task cancelled. Not saved.")


def main():
    # Initialize DB
    init_db()
    print("=== Scout Agent CLI ===")

    while True:
        cmd = input("\nCommands: [add] instruction, [list] tasks, [run] monitor, [quit]: ")
        cmd_lower = cmd.strip().lower()

        if cmd_lower == "add" or cmd_lower.startswith("add "):
            handle_add_command(cmd)

        elif cmd_lower == "list":
            tasks = get_active_tasks()
            if not tasks:
                print("No active tasks.")
            else:
                print("Active Tasks:")
                for t in tasks:
                    print(f" • [ID {t['task_id']}] {t['url']} every {t['frequency']}h — {t['task_prompt']}")

        elif cmd_lower == "run":
            print("Starting monitor scheduler...")
            start_scheduler()
            break  # scheduler will block until exit

        elif cmd_lower in ("quit", "exit"):
            print("Exiting. Bye!")
            break

        else:
            print("Unknown command. Please use 'add', 'list', 'run', or 'quit'.")


if __name__ == "__main__":
    main()
