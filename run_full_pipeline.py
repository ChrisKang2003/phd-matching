import subprocess
import sys


def run_command(command):
    print(f"\nRunning: {command}")
    result = subprocess.run(command, shell=True)

    if result.returncode != 0:
        print(f"Command failed: {command}")
        sys.exit(result.returncode)


def main():
    # Step 1: Run original GitHub data collection pipeline
    run_command("python main.py")

    # Step 2: Convert collected professor JSON into CSV
    run_command("python utils/export_professors_csv.py")

    # Step 3: Optional test recommendation
    run_command("python model/rank_professors.py")


if __name__ == "__main__":
    main()