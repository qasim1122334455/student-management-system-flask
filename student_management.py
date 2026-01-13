# Project 2 - Student Management System (Final)
# Features:
# - Add, view, search, update, delete students
# - Prevent duplicate IDs
# - Save/load data to a JSON file automatically
# - Input validation + clean menu

import json
from typing import List, Dict, Optional

DATA_FILE = "students.json"
students: List[Dict[str, object]] = []


def load_students() -> None:
    global students
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                # ensure expected keys exist
                cleaned = []
                for s in data:
                    if isinstance(s, dict) and "id" in s and "name" in s:
                        cleaned.append({
                            "id": str(s.get("id", "")).strip(),
                            "name": str(s.get("name", "")).strip(),
                            "age": int(s.get("age", 0)) if str(s.get("age", "0")).isdigit() else 0,
                            "degree": str(s.get("degree", "")).strip(),
                        })
                students = cleaned
            else:
                students = []
    except FileNotFoundError:
        students = []
    except json.JSONDecodeError:
        print("Warning: students.json is corrupted. Starting with an empty list.")
        students = []


def save_students() -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=2)


def show_menu() -> None:
    print("\n--- Student Management System ---")
    print("1) Add student")
    print("2) View all students")
    print("3) Search student by name")
    print("4) Update student by ID")
    print("5) Delete student by ID")
    print("6) Exit")


def find_by_id(student_id: str) -> Optional[Dict[str, object]]:
    sid = student_id.strip()
    for s in students:
        if s["id"] == sid:
            return s
    return None


def get_int(prompt: str, min_value: int = 0, max_value: int = 200) -> int:
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return 0  # allow blank to mean 0
        if raw.isdigit():
            value = int(raw)
            if min_value <= value <= max_value:
                return value
        print(f"Please enter a valid number between {min_value} and {max_value} (or press Enter to skip).")


def add_student() -> None:
    name = input("Enter student name: ").strip()
    student_id = input("Enter student ID: ").strip()

    if name == "" or student_id == "":
        print("Name and ID cannot be empty.")
        return

    if find_by_id(student_id) is not None:
        print("That student ID already exists. Please use a unique ID.")
        return

    age = get_int("Enter age (optional, press Enter to skip): ", 0, 120)
    degree = input("Enter degree (optional): ").strip()

    students.append({
        "id": student_id,
        "name": name,
        "age": age,
        "degree": degree
    })
    save_students()
    print("Student added and saved.")


def view_students() -> None:
    if len(students) == 0:
        print("No students found.")
        return

    print("\nStudents:")
    for s in students:
        age_text = f", Age: {s['age']}" if s.get("age", 0) else ""
        degree_text = f", Degree: {s['degree']}" if s.get("degree") else ""
        print(f"- {s['name']} (ID: {s['id']}{age_text}{degree_text})")


def search_student() -> None:
    keyword = input("Enter name to search: ").strip().lower()
    if keyword == "":
        print("Search term cannot be empty.")
        return

    matches = [s for s in students if keyword in str(s["name"]).lower()]

    if not matches:
        print("No matching student found.")
        return

    print("\nMatches:")
    for s in matches:
        print(f"- {s['name']} (ID: {s['id']})")


def update_student() -> None:
    student_id = input("Enter student ID to update: ").strip()
    s = find_by_id(student_id)
    if s is None:
        print("Student not found.")
        return

    print("Press Enter to keep current value.")
    new_name = input(f"New name (current: {s['name']}): ").strip()
    if new_name != "":
        s["name"] = new_name

    new_age_raw = input(f"New age (current: {s.get('age', 0)}): ").strip()
    if new_age_raw != "":
        if new_age_raw.isdigit() and 0 <= int(new_age_raw) <= 120:
            s["age"] = int(new_age_raw)
        else:
            print("Invalid age. Keeping previous value.")

    new_degree = input(f"New degree (current: {s.get('degree', '')}): ").strip()
    if new_degree != "":
        s["degree"] = new_degree

    save_students()
    print("Student updated and saved.")


def delete_student() -> None:
    student_id = input("Enter student ID to delete: ").strip()
    s = find_by_id(student_id)
    if s is None:
        print("Student not found.")
        return

    confirm = input(f"Are you sure you want to delete {s['name']} (ID: {s['id']})? (y/n): ").strip().lower()
    if confirm == "y":
        students.remove(s)
        save_students()
        print("Student deleted and saved.")
    else:
        print("Delete cancelled.")


def main() -> None:
    load_students()

    while True:
        show_menu()
        choice = input("Choose (1-6): ").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            view_students()
        elif choice == "3":
            search_student()
        elif choice == "4":
            update_student()
        elif choice == "5":
            delete_student()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1 to 6.")


if __name__ == "__main__":
    main()
