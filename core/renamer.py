import os


def build_new_name(ref):
    parts = [p.strip() for p in ref.split("/")]

    if len(parts) >= 8:
        name = f"{parts[1]} {parts[4]} {parts[6]} {parts[7]}.pdf"
        return "".join(c for c in name if c not in r'\/:*?"<>|')

    return None


def get_unique_path(folder, new_name):
    new_path = os.path.join(folder, new_name)
    counter = 1

    while os.path.exists(new_path):
        new_path = os.path.join(folder, new_name.replace(".pdf", f"_({counter}).pdf"))
        counter += 1

    return new_path
