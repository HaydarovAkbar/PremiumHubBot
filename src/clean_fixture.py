import re

input_file = "data.xml"
output_file = "cleaned_data.xml"

with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()

# Barcha contenttypes.contenttype objectlarini o‘chiradi
pattern = re.compile(
    r'<object model="contenttypes\.contenttype" pk=".*?">.*?</object>',
    re.DOTALL
)

new_content = re.sub(pattern, "", content)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(new_content)

print("✅ Barcha contenttypes.contenttype obyektlari o‘chirildi. Saqlangan:", output_file)