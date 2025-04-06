import os
import zipfile

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
zipout = os.path.join(ROOT_DIR, "media", "downloads", "all_translations.zip")

private_dirs_basepath = os.path.join(
    ROOT_DIR, "media", "downloads", "delegations_private_dirs"
)

files_to_zip = []

for private_dir in os.listdir(private_dirs_basepath):
    try:
        pdfs_path = os.path.join(private_dirs_basepath, private_dir, "takehome", "pdf")
        for pdf in os.listdir(pdfs_path):
            if not "_solution.pdf" in pdf and (
                f"_english_{private_dir[:3]}_.pdf" not in pdf
                or len(os.listdir(pdfs_path)) == 4
            ):
                print(f"ADDING {pdf} from {private_dir}")
                files_to_zip.append((os.path.join(pdfs_path, pdf), pdf))
    except Exception as e:
        print(f"ERROR: {e}")

print(f"Zipping {len(files_to_zip)} files to {zipout}")
with zipfile.ZipFile(zipout, "w") as zipf:
    for file in files_to_zip:
        zipf.write(file[0], arcname=file[1])
print("Done")
