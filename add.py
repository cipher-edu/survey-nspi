import re

input_file = "seed_data_super_full.sql"
output_file = "seed_data_super_full_clean.sql"

student_ids = set()
survey_ids = set()
used_response_ids = set()

# 1. Avval barcha student va survey id-larni yig‘ib olamiz
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()
    for line in lines:
        # Student id-lar
        if line.startswith("INSERT INTO auth_app_student"):
            ids = re.findall(r"\((\d+),", line)
            student_ids.update(map(int, ids))
        # Survey id-lar
        if line.startswith("INSERT INTO auth_app_survey"):
            ids = re.findall(r"\((\d+),", line)
            survey_ids.update(map(int, ids))

# 2. Endi faylni tozalab, faqat to‘g‘ri qatorlarni yozamiz
with open(output_file, "w", encoding="utf-8") as out:
    for line in lines:
        if line.startswith("INSERT INTO auth_app_surveyresponse"):
            m = re.search(r"VALUES \((\d+), '[^']+', (\d+), (\d+)\);", line)
            if m:
                rid, sid, suid = map(int, m.groups())
                if (sid in student_ids) and (suid in survey_ids) and (rid not in used_response_ids):
                    out.write(line)
                    used_response_ids.add(rid)
        else:
            out.write(line)

print("Tozalangan fayl:", output_file)